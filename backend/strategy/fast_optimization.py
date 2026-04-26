"""
策略参数优化 - 从本地文件读取数据，快速优化（多进程版本）
"""

import sys
import os

# 获取脚本所在目录的绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")

sys.path.insert(0, ".")

import pandas as pd
import numpy as np
from loguru import logger
from itertools import product
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
from datetime import datetime

from app.core.logging import setup_logging

# 初始化日志配置（统一日志管理）
setup_logging()


# ============== 技术指标计算 ==============


def calculate_kdj(
    df: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3
) -> pd.DataFrame:
    """
    计算KDJ指标
    标准公式:
    RSV = (Close - LowN) / (HighN - LowN) × 100
    K = EMA(RSV, m1)
    D = EMA(K, m2)
    J = 3K - 2D
    """
    low_n = df["low"].rolling(window=n, min_periods=n).min()
    high_n = df["high"].rolling(window=n, min_periods=n).max()
    rsv = (df["close"] - low_n) / (high_n - low_n) * 100
    rsv = rsv.fillna(50)

    # 分别计算K和D
    df["k"] = rsv.ewm(alpha=1 / m1, adjust=False).mean()  # K线
    df["d"] = df["k"].ewm(alpha=1 / m2, adjust=False).mean()  # D线
    df["j"] = 3 * df["k"] - 2 * df["d"]  # J线

    return df


def calculate_rsi(df: pd.DataFrame, n: int = 6) -> pd.DataFrame:
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = (-delta).where(delta < 0, 0)
    avg_gain = gain.rolling(window=n, min_periods=n).mean()
    avg_loss = loss.rolling(window=n, min_periods=n).mean()
    df["rsi6"] = 100 - (100 / (1 + avg_gain / avg_loss.replace(0, np.inf)))
    return df


def calculate_vol_ratio(df: pd.DataFrame) -> pd.DataFrame:
    df["vol_ma5"] = df["vol"].rolling(window=5, min_periods=5).mean()
    df["vol_ratio"] = df["vol"] / df["vol_ma5"]
    return df


def prepare_stock_data(daily_df: pd.DataFrame) -> dict:
    """预处理所有股票数据，计算指标"""
    stock_data = {}

    for ts_code, group in daily_df.groupby("ts_code"):
        group = group.sort_values("trade_date").copy()
        group = calculate_kdj(group)
        group = calculate_rsi(group)
        group = calculate_vol_ratio(group)
        stock_data[ts_code] = group

    return stock_data


# ============== 回测核心 ==============


def check_buy_timing(
    df: pd.DataFrame,
    current_idx: int,
    buy_timing: str,
    j_threshold: float,
    rsi_threshold: float,
) -> tuple[bool, str]:
    """
    检查买入时机
    返回: (是否买入, 原因)

    buy_timing 策略:
    - immediate: 信号出现立即买入
    - next_day: 次日确认（次日仍满足超卖条件或开始反弹）
    - turn_up: J值拐头向上（J值比前一日高）
    - yang_line: 收阳线（收盘价 > 开盘价）
    - break_high: 突破前一日高点
    - turn_up_yang: J值拐头 + 阳线
    - turn_up_break: J值拐头 + 突破前高
    """
    if current_idx < 1:
        return False, "数据不足"

    row = df.iloc[current_idx]
    prev_row = df.iloc[current_idx - 1]

    if buy_timing == "immediate":
        return True, "立即买入"

    elif buy_timing == "next_day":
        # 次日确认：仍满足超卖条件 或 开始反弹
        j_still_oversold = row["j"] < j_threshold
        rsi_still_oversold = row["rsi6"] < rsi_threshold
        price_up = row["close"] > prev_row["close"]

        if (j_still_oversold and rsi_still_oversold) or price_up:
            return True, "次日确认"
        return False, "次日未确认"

    elif buy_timing == "turn_up":
        # J值拐头向上
        if row["j"] > prev_row["j"]:
            return True, "J值拐头"
        return False, "J值未拐头"

    elif buy_timing == "yang_line":
        # 收阳线
        if row["close"] > row["open"]:
            return True, "收阳线"
        return False, "未收阳线"

    elif buy_timing == "break_high":
        # 突破前一日高点
        if row["high"] > prev_row["high"]:
            return True, "突破前高"
        return False, "未突破前高"

    elif buy_timing == "turn_up_yang":
        # J值拐头 + 阳线
        j_turn_up = row["j"] > prev_row["j"]
        yang_line = row["close"] > row["open"]
        if j_turn_up and yang_line:
            return True, "J拐头+阳线"
        return False, f"J拐头={j_turn_up}, 阳线={yang_line}"

    elif buy_timing == "turn_up_break":
        # J值拐头 + 突破前高
        j_turn_up = row["j"] > prev_row["j"]
        break_high = row["high"] > prev_row["high"]
        if j_turn_up and break_high:
            return True, "J拐头+突破"
        return False, f"J拐头={j_turn_up}, 突破={break_high}"

    return False, "未知策略"


def run_single_backtest(
    stock_data: dict,
    trade_dates: list,
    j_threshold: float,
    rsi_threshold: float,
    vol_ratio_min: float,
    max_positions: int,
    stop_loss: float,
    take_profit_fixed: float,
    take_profit_trigger: float,
    take_profit_trailing: float,
    max_hold_days: int = 0,
    buy_timing: str = "immediate",
    debug: bool = False,
) -> dict:
    """单次回测"""
    positions = []
    trades = []
    cash = 1.0
    portfolio_value = [1.0]
    daily_returns = []

    # 待确认信号池 {ts_code: signal_date_idx}
    pending_signals = {}

    # 统计信号数量
    total_signals = 0
    j_pass = 0
    rsi_pass = 0
    vol_pass = 0
    timing_pass = 0
    timing_fail = 0

    for i, current_date in enumerate(trade_dates):
        # 1. 检查持仓
        new_positions = []
        for pos in positions:
            df = stock_data[pos["ts_code"]]
            current_row = df[df["trade_date"] == current_date]

            if current_row.empty:
                new_positions.append(pos)
                continue

            current_price = current_row["close"].iloc[0]
            max_price = max(pos["max_price"], current_price)
            pnl = (current_price - pos["buy_price"]) / pos["buy_price"]
            hold_days = i - pos["buy_date_idx"]

            # 持仓时间止损
            if max_hold_days > 0 and hold_days >= max_hold_days:
                trades.append({"pnl": pnl, "sell_reason": "time_stop"})
                cash += pos["size"] * (1 + pnl)
                continue

            # 固定止盈
            if pnl >= take_profit_fixed:
                trades.append({"pnl": pnl, "sell_reason": "fixed_take_profit"})
                cash += pos["size"] * (1 + pnl)
                continue

            # 止损
            if pnl <= stop_loss:
                trades.append({"pnl": pnl, "sell_reason": "stop_loss"})
                cash += pos["size"] * (1 + pnl)
                continue

            # 移动止盈
            if pos["trailing_active"]:
                trailing_pnl = (current_price - max_price) / max_price
                if trailing_pnl <= -take_profit_trailing:
                    trades.append({"pnl": pnl, "sell_reason": "trailing_take_profit"})
                    cash += pos["size"] * (1 + pnl)
                    continue
            elif pnl >= take_profit_trigger:
                pos["trailing_active"] = True

            pos["max_price"] = max_price
            new_positions.append(pos)

        positions = new_positions

        # 2. 检查待确认信号（次日确认策略）
        if buy_timing != "immediate" and pending_signals:
            signals_to_remove = []
            for ts_code, signal_idx in pending_signals.items():
                if any(p["ts_code"] == ts_code for p in positions):
                    signals_to_remove.append(ts_code)
                    continue

                df = stock_data[ts_code]
                current_row = df[df["trade_date"] == current_date]
                if current_row.empty:
                    continue

                # 获取当前数据在df中的索引
                current_df_idx = df.index.get_loc(current_row.index[0])

                # 检查买入时机
                should_buy, reason = check_buy_timing(
                    df, current_df_idx, buy_timing, j_threshold, rsi_threshold
                )

                if debug:
                    if should_buy:
                        timing_pass += 1
                    else:
                        timing_fail += 1

                if should_buy:
                    # 满足买入时机，执行买入
                    buy_price = current_row["close"].iloc[0]
                    position_size = cash / (max_positions - len(positions))

                    positions.append(
                        {
                            "ts_code": ts_code,
                            "buy_date_idx": i,
                            "buy_price": buy_price,
                            "max_price": buy_price,
                            "size": position_size,
                            "trailing_active": False,
                        }
                    )
                    cash -= position_size
                    signals_to_remove.append(ts_code)

            for ts_code in signals_to_remove:
                pending_signals.pop(ts_code, None)

        # 3. 寻找新信号
        if len(positions) < max_positions:
            signals_today = []
            for ts_code, df in stock_data.items():
                if any(p["ts_code"] == ts_code for p in positions):
                    continue
                if ts_code in pending_signals:
                    continue

                signal_row = df[df["trade_date"] == current_date]
                if signal_row.empty:
                    continue

                row = signal_row.iloc[0]

                # 统计各条件通过情况
                j_ok = row["j"] < j_threshold
                rsi_ok = row["rsi6"] < rsi_threshold
                vol_ok = row["vol_ratio"] > vol_ratio_min

                if debug:
                    if j_ok:
                        j_pass += 1
                    if rsi_ok:
                        rsi_pass += 1
                    if vol_ok:
                        vol_pass += 1

                if j_ok and rsi_ok and vol_ok:
                    signals_today.append({"ts_code": ts_code, "j": row["j"]})
                    total_signals += 1

            signals_today.sort(key=lambda x: x["j"])
            available_slots = max_positions - len(positions)

            for signal in signals_today[:available_slots]:
                df = stock_data[signal["ts_code"]]
                signal_row = df[df["trade_date"] == current_date]

                if signal_row.empty:
                    continue

                if buy_timing == "immediate":
                    # 立即买入策略：当日收盘价买入
                    buy_price = signal_row["close"].iloc[0]
                    position_size = cash / (max_positions - len(positions))

                    positions.append(
                        {
                            "ts_code": signal["ts_code"],
                            "buy_date_idx": i,
                            "buy_price": buy_price,
                            "max_price": buy_price,
                            "size": position_size,
                            "trailing_active": False,
                        }
                    )
                    cash -= position_size
                else:
                    # 其他策略：加入待确认池，次日检查
                    pending_signals[signal["ts_code"]] = i

        # 4. 计算净值
        total_value = cash
        for pos in positions:
            df = stock_data[pos["ts_code"]]
            current_row = df[df["trade_date"] == current_date]
            if not current_row.empty:
                total_value += pos["size"] * (
                    current_row["close"].iloc[0] / pos["buy_price"]
                )

        daily_return = (total_value - portfolio_value[-1]) / portfolio_value[-1]
        daily_returns.append(daily_return)
        portfolio_value.append(total_value)

    # 平仓
    for pos in positions:
        df = stock_data[pos["ts_code"]]
        last_row = df.iloc[-1]
        pnl = (last_row["close"] - pos["buy_price"]) / pos["buy_price"]
        trades.append({"pnl": pnl, "sell_reason": "end"})

    metrics = calculate_metrics(trades, portfolio_value, daily_returns)

    # 添加诊断信息
    if debug:
        metrics["total_signals"] = total_signals
        metrics["j_pass"] = j_pass
        metrics["rsi_pass"] = rsi_pass
        metrics["vol_pass"] = vol_pass
        metrics["timing_pass"] = timing_pass
        metrics["timing_fail"] = timing_fail

    return metrics


def calculate_metrics(trades: list, portfolio_value: list, daily_returns: list) -> dict:
    if not trades:
        return {
            "trades": 0,
            "win_rate": 0,
            "pl_ratio": 0,
            "return": 0,
            "drawdown": 0,
            "sharpe": 0,
        }

    df = pd.DataFrame(trades)
    total = len(df)
    wins = len(df[df["pnl"] > 0])
    win_rate = wins / total if total > 0 else 0

    avg_win = df[df["pnl"] > 0]["pnl"].mean() if wins > 0 else 0
    avg_lose = df[df["pnl"] <= 0]["pnl"].mean() if total > wins else 0
    pl_ratio = abs(avg_win / avg_lose) if avg_lose != 0 else 0

    total_return = portfolio_value[-1] - 1

    series = pd.Series(portfolio_value)
    drawdown = ((series - series.expanding().max()) / series.expanding().max()).min()

    daily = pd.Series(daily_returns)
    sharpe = daily.mean() / daily.std() * np.sqrt(252) if daily.std() > 0 else 0

    return {
        "trades": total,
        "win_rate": win_rate,
        "pl_ratio": pl_ratio,
        "return": total_return,
        "drawdown": drawdown,
        "sharpe": sharpe,
    }


# ============== 多进程优化 ==============


def run_backtest_task(args):
    """单个回测任务（在子进程中执行）"""
    params, combo_idx, total_combos, debug = args

    # 每个子进程自己加载数据（避免进程间传递大数据）
    daily_df = pd.read_pickle(os.path.join(DATA_DIR, "daily_data.pkl"))
    # trade_dates.csv 中日期是整数 YYYYMMDD 格式，转换为字符串保持与 daily_data 一致
    trade_dates_raw = pd.read_csv(os.path.join(DATA_DIR, "trade_dates.csv"))[
        "trade_date"
    ].tolist()
    trade_dates = [str(d) for d in trade_dates_raw]
    stock_data = prepare_stock_data(daily_df)

    # 执行回测
    metrics = run_single_backtest(stock_data, trade_dates, debug=debug, **params)

    # 返回结果
    result = {**params, **metrics}
    return combo_idx, result, debug


def run_optimization(max_workers: int = 4):
    logger.info("=" * 60)
    logger.info("策略参数优化 (多进程版本)")
    logger.info("=" * 60)
    logger.info(f"并发进程数: {max_workers}")

    # 1. 参数空间
    # 参数空间定义
    param_grid = {
        # 买入信号参数（固定条件：J<-10 + RSI<15 + 放量）
        "j_threshold": [-10],  # KDJ的J值阈值，J<阈值时触发买入信号
        "rsi_threshold": [15],  # RSI阈值，RSI<阈值时触发买入信号
        "vol_ratio_min": [1.0],  # 最小成交量比率，成交量/5日均量 > 该值时有效
        # 买入时机策略
        # immediate: 信号出现立即买入
        # next_day: 次日确认（次日仍满足超卖或开始反弹）
        # turn_up: J值拐头向上
        # yang_line: 收阳线
        # break_high: 突破前一日高点
        # turn_up_yang: J值拐头 + 阳线
        # turn_up_break: J值拐头 + 突破前高
        "buy_timing": [
            "immediate",
            "next_day",
            "turn_up",
            "yang_line",
            "break_high",
            "turn_up_yang",
            "turn_up_break",
        ],
        # 仓位管理参数
        "max_positions": [3, 5, 8],  # 最大持仓数量
        # 止盈止损参数
        "stop_loss": [-0.03, -0.05],  # 止损比例，亏损达到该比例时卖出
        "take_profit_fixed": [0.05, 0.08, 0.10],  # 固定止盈比例，盈利达到该比例时卖出
        "take_profit_trigger": [
            0.03,
            0.05,
        ],  # 移动止盈触发点，盈利达到该比例后启动移动止盈
        "take_profit_trailing": [
            0.02,
            0.03,
        ],  # 移动止盈回撤比例，从最高点回撤该比例时卖出
        # 持仓时间参数
        "max_hold_days": [0, 2, 3, 5, 10, 20],  # 最大持仓天数，0表示不限制
    }

    total = 1
    for v in param_grid.values():
        total *= len(v)

    logger.info(f"参数组合总数: {total}")
    logger.info("-" * 60)

    # 打印参数空间详情
    logger.info("参数空间详情:")
    for key, values in param_grid.items():
        logger.info(f"  {key}: {values}")
    logger.info("-" * 60)

    # 2. 生成所有参数组合
    param_names = list(param_grid.keys())
    param_values = list(param_grid.values())
    all_combos = list(product(*param_values))

    # 准备任务参数（所有组合都开启debug模式）
    tasks = []
    for i, combo in enumerate(all_combos):
        params = dict(zip(param_names, combo))
        tasks.append((params, i + 1, total, True))  # 全部开启debug

    logger.info("开始多进程网格搜索...")
    logger.info("-" * 60)

    # 3. 多进程执行
    results = [None] * total  # 预分配结果列表
    start_time = time.time()
    completed = 0
    error_count = 0

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(run_backtest_task, task): task for task in tasks}

        for future in as_completed(futures):
            try:
                combo_idx, result, debug = future.result()
                results[combo_idx - 1] = result
                completed += 1

                # 计算进度和速度
                elapsed = time.time() - start_time
                speed = completed / elapsed if elapsed > 0 else 0
                remaining = (total - completed) / speed if speed > 0 else 0

                # 打印详细日志（包含所有关键参数和诊断信息）
                logger.info(
                    f"[{completed}/{total}] "
                    f"买入时机={result['buy_timing']}, "
                    f"持仓{result['max_positions']}支, "
                    f"止损{result['stop_loss']*100:.0f}%, "
                    f"止盈{result['take_profit_fixed']*100:.0f}%, "
                    f"持仓{result['max_hold_days']}天 | "
                    f"交易数={result['trades']}, "
                    f"收益={result['return']*100:.2f}%, "
                    f"胜率={result['win_rate']*100:.1f}%, "
                    f"夏普={result['sharpe']:.2f}"
                )

                # 打印诊断信息
                if "total_signals" in result:
                    timing_info = ""
                    if "timing_pass" in result:
                        timing_info = f", 时机通过={result['timing_pass']}, 时机失败={result['timing_fail']}"
                    logger.info(
                        f"  信号统计: 总信号={result['total_signals']}, "
                        f"J通过={result['j_pass']}, RSI通过={result['rsi_pass']}, VOL通过={result['vol_pass']}"
                        f"{timing_info}"
                    )

                # 打印进度摘要
                logger.info(
                    f"  进度: {completed*100/total:.1f}% | "
                    f"速度: {speed:.1f}组/秒 | "
                    f"剩余: {remaining:.0f}秒"
                )
                logger.info("-" * 40)

            except Exception as e:
                error_count += 1
                logger.error(f"回测出错: {e}")

    elapsed = time.time() - start_time
    logger.info("-" * 60)
    logger.info(
        f"优化完成! 总耗时: {elapsed:.1f}秒, 平均速度: {total/elapsed:.1f}组/秒"
    )
    logger.info(f"成功: {completed}, 错误: {error_count}")

    # 4. 分析结果
    results_df = pd.DataFrame(results)

    print("\n" + "=" * 80)
    print("优化结果")
    print("=" * 80)

    # 按买入时机分组统计
    print("\n【买入时机策略对比】")
    timing_stats = (
        results_df.groupby("buy_timing")
        .agg(
            {
                "return": ["mean", "max"],
                "win_rate": "mean",
                "sharpe": "mean",
                "trades": "sum",
            }
        )
        .round(3)
    )
    for timing in results_df["buy_timing"].unique():
        subset = results_df[results_df["buy_timing"] == timing]
        print(
            f"  {timing}: 平均收益={subset['return'].mean()*100:.2f}%, "
            f"最高收益={subset['return'].max()*100:.2f}%, "
            f"平均胜率={subset['win_rate'].mean()*100:.1f}%, "
            f"平均夏普={subset['sharpe'].mean():.2f}, "
            f"总交易数={subset['trades'].sum()}"
        )

    # 按收益排序
    print("\n【Top 10 - 按收益率】")
    top = results_df.sort_values("return", ascending=False).head(10)
    for _, row in top.iterrows():
        print(
            f"  收益={row['return']*100:.2f}%, 胜率={row['win_rate']*100:.1f}%, "
            f"盈亏比={row['pl_ratio']:.2f}, 回撤={row['drawdown']*100:.1f}%, 夏普={row['sharpe']:.2f}"
        )
        print(
            f"    买入时机={row['buy_timing']}, "
            f"持仓{row['max_positions']}支, 止损{row['stop_loss']*100:.0f}%, 止盈{row['take_profit_fixed']*100:.0f}%"
        )

    # 按夏普排序
    print("\n【Top 10 - 按夏普比率】")
    top = results_df.sort_values("sharpe", ascending=False).head(10)
    for _, row in top.iterrows():
        print(
            f"  夏普={row['sharpe']:.2f}, 收益={row['return']*100:.2f}%, 胜率={row['win_rate']*100:.1f}%, 回撤={row['drawdown']*100:.1f}%"
        )
        print(
            f"    买入时机={row['buy_timing']}, "
            f"持仓{row['max_positions']}支, 止损{row['stop_loss']*100:.0f}%, 止盈{row['take_profit_fixed']*100:.0f}%"
        )

    # 综合评分
    results_df["score"] = (
        results_df["return"]
        * results_df["sharpe"]
        / abs(results_df["drawdown"] + 0.001)
    )
    print("\n【Top 10 - 综合评分】")
    top = results_df.sort_values("score", ascending=False).head(10)
    for _, row in top.iterrows():
        print(
            f"  评分={row['score']:.3f}, 收益={row['return']*100:.2f}%, 夏普={row['sharpe']:.2f}, 回撤={row['drawdown']*100:.1f}%"
        )
        print(
            f"    买入时机={row['buy_timing']}, "
            f"持仓{row['max_positions']}支, 止损{row['stop_loss']*100:.0f}%, 止盈{row['take_profit_fixed']*100:.0f}%, "
            f"持仓{row['max_hold_days']}天"
        )

    results_df.to_csv("strategy/optimization_results.csv", index=False)
    print(f"\n结果已保存: strategy/optimization_results.csv")

    return results_df


if __name__ == "__main__":
    # 使用多进程，根据CPU物理核心数设置
    # i9-10850K: 10物理核心, 20逻辑核心, 32GB内存
    # 建议使用8-10个进程（接近物理核心数）
    cpu_count = multiprocessing.cpu_count()  # 20 (逻辑核心)
    physical_cores = 10  # 物理核心数

    # 对于CPU密集型任务，使用物理核心数的80%最佳
    recommended_workers = int(physical_cores * 0.8)  # 8进程
    logger.info(f"CPU: i9-10850K, 物理核心: {physical_cores}, 逻辑核心: {cpu_count}")
    logger.info(f"内存: 32GB, 使用进程数: {recommended_workers}")
    run_optimization(max_workers=recommended_workers)
