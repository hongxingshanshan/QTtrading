"""
策略参数优化 - 优化版本（进程池初始化器 + 预计算指标）
优化点：
1. 使用进程池初始化器，每个子进程只加载一次数据
2. 预计算技术指标，避免重复计算
3. 预计算买入信号，大幅减少回测时间
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

# 初始化日志
log_dir = os.path.join(SCRIPT_DIR, "logs")
os.makedirs(log_dir, exist_ok=True)
logger.add(
    os.path.join(log_dir, "strategy_optimized.log"),
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    rotation="10 MB",
    retention="30 days",
    encoding="utf-8",
)

# 全局变量（子进程初始化后使用）
_global_stock_data = None
_global_trade_dates = None
_global_signals = None  # 预计算的信号


# ============== 技术指标计算 ==============


def calculate_kdj(
    df: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3
) -> pd.DataFrame:
    """计算KDJ指标"""
    low_n = df["low"].rolling(window=n, min_periods=n).min()
    high_n = df["high"].rolling(window=n, min_periods=n).max()
    rsv = (df["close"] - low_n) / (high_n - low_n) * 100
    rsv = rsv.fillna(50)

    df["k"] = rsv.ewm(alpha=1 / m1, adjust=False).mean()
    df["d"] = df["k"].ewm(alpha=1 / m2, adjust=False).mean()
    df["j"] = 3 * df["k"] - 2 * df["d"]

    return df


def calculate_rsi(df: pd.DataFrame, n: int = 6) -> pd.DataFrame:
    """计算RSI指标"""
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = (-delta).where(delta < 0, 0)
    avg_gain = gain.rolling(window=n, min_periods=n).mean()
    avg_loss = loss.rolling(window=n, min_periods=n).mean()
    df["rsi6"] = 100 - (100 / (1 + avg_gain / avg_loss.replace(0, np.inf)))
    return df


def calculate_vol_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """计算成交量比率"""
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


def precompute_signals(stock_data: dict, trade_dates: list,
                       j_threshold: float = -10,
                       rsi_threshold: float = 15,
                       vol_ratio_min: float = 1.0) -> dict:
    """
    预计算所有买入信号
    返回: {trade_date: [(ts_code, signal_info), ...]}
    """
    signals_by_date = {}

    for ts_code, df in stock_data.items():
        # 创建日期到索引的映射
        date_to_idx = {str(row["trade_date"]): idx for idx, row in df.iterrows()}

        for idx in range(len(df)):
            row = df.iloc[idx]

            # 检查买入信号条件
            j_val = row["j"]
            rsi_val = row["rsi6"]
            vol_ratio = row["vol_ratio"]

            if pd.isna(j_val) or pd.isna(rsi_val) or pd.isna(vol_ratio):
                continue

            # 信号条件: J < j_threshold AND RSI < rsi_threshold AND VOL > vol_ratio_min
            if j_val < j_threshold and rsi_val < rsi_threshold and vol_ratio > vol_ratio_min:
                trade_date = str(row["trade_date"])

                # 存储信号信息
                signal_info = {
                    "ts_code": ts_code,
                    "idx": idx,
                    "j": j_val,
                    "rsi": rsi_val,
                    "vol_ratio": vol_ratio,
                    "close": row["close"],
                    "open": row["open"],
                    "high": row["high"],
                    "low": row["low"],
                }

                if trade_date not in signals_by_date:
                    signals_by_date[trade_date] = []
                signals_by_date[trade_date].append(signal_info)

    return signals_by_date


# ============== 进程池初始化 ==============


def init_worker(stock_data_dict: dict, trade_dates_list: list, signals_dict: dict):
    """
    子进程初始化函数
    每个子进程启动时调用一次，加载数据到全局变量
    """
    global _global_stock_data, _global_trade_dates, _global_signals
    _global_stock_data = stock_data_dict
    _global_trade_dates = trade_dates_list
    _global_signals = signals_dict


# ============== 买入时机检查 ==============


def check_buy_timing_fast(df: pd.DataFrame, current_idx: int, buy_timing: str,
                          j_threshold: float, rsi_threshold: float) -> tuple:
    """快速检查买入时机"""
    if current_idx < 1:
        return False, "数据不足"

    row = df.iloc[current_idx]
    prev_row = df.iloc[current_idx - 1]

    if buy_timing == "immediate":
        return True, "立即买入"

    elif buy_timing == "next_day":
        j_still_oversold = row["j"] < j_threshold
        rsi_still_oversold = row["rsi6"] < rsi_threshold
        price_up = row["close"] > prev_row["close"]
        if (j_still_oversold and rsi_still_oversold) or price_up:
            return True, "次日确认"
        return False, "次日未确认"

    elif buy_timing == "turn_up":
        if row["j"] > prev_row["j"]:
            return True, "J值拐头"
        return False, "J值未拐头"

    elif buy_timing == "yang_line":
        if row["close"] > row["open"]:
            return True, "收阳线"
        return False, "未收阳线"

    elif buy_timing == "break_high":
        if row["high"] > prev_row["high"]:
            return True, "突破前高"
        return False, "未突破前高"

    elif buy_timing == "turn_up_yang":
        j_turn_up = row["j"] > prev_row["j"]
        yang_line = row["close"] > row["open"]
        if j_turn_up and yang_line:
            return True, "J拐头+阳线"
        return False, f"J拐头={j_turn_up}, 阳线={yang_line}"

    elif buy_timing == "turn_up_break":
        j_turn_up = row["j"] > prev_row["j"]
        break_high = row["high"] > prev_row["high"]
        if j_turn_up and break_high:
            return True, "J拐头+突破"
        return False, f"J拐头={j_turn_up}, 突破={break_high}"

    return False, "未知策略"


# ============== 回测核心 ==============


def run_single_backtest_optimized(
    params: dict,
    debug: bool = False,
) -> dict:
    """优化版单次回测 - 使用预计算信号"""
    stock_data = _global_stock_data
    trade_dates = _global_trade_dates
    signals_by_date = _global_signals

    # 解包参数
    j_threshold = params["j_threshold"]
    rsi_threshold = params["rsi_threshold"]
    vol_ratio_min = params["vol_ratio_min"]
    max_positions = params["max_positions"]
    stop_loss = params["stop_loss"]
    take_profit_fixed = params["take_profit_fixed"]
    take_profit_trigger = params["take_profit_trigger"]
    take_profit_trailing = params["take_profit_trailing"]
    max_hold_days = params["max_hold_days"]
    buy_timing = params["buy_timing"]

    positions = []
    trades = []
    cash = 1.0
    portfolio_value = [1.0]
    daily_returns = []

    # 待确认信号池 {ts_code: (signal_date, signal_idx)}
    pending_signals = {}

    # 统计
    total_signals = 0
    timing_pass = 0
    timing_fail = 0

    for date_idx, trade_date in enumerate(trade_dates):
        # 1. 更新持仓价格
        for pos in positions:
            ts_code = pos["ts_code"]
            if ts_code in stock_data:
                df = stock_data[ts_code]
                date_rows = df[df["trade_date"].astype(str) == trade_date]
                if not date_rows.empty:
                    pos["current_price"] = float(date_rows.iloc[0]["close"])
                    pos["current_high"] = float(date_rows.iloc[0]["high"])
                    pos["hold_days"] += 1

        # 2. 检查卖出条件
        new_positions = []
        for pos in positions:
            should_sell = False
            sell_reason = ""
            sell_price = pos["current_price"]

            # 止损
            if pos["current_price"] / pos["buy_price"] - 1 < stop_loss:
                should_sell = True
                sell_reason = "止损"
                sell_price = pos["buy_price"] * (1 + stop_loss)

            # 固定止盈
            elif pos["current_price"] / pos["buy_price"] - 1 > take_profit_fixed:
                should_sell = True
                sell_reason = "止盈"
                sell_price = pos["buy_price"] * (1 + take_profit_fixed)

            # 移动止盈
            elif pos["current_price"] / pos["buy_price"] - 1 > take_profit_trigger:
                if pos["max_price"] < pos["current_price"]:
                    pos["max_price"] = pos["current_price"]

                if pos["current_price"] / pos["max_price"] - 1 < -take_profit_trailing:
                    should_sell = True
                    sell_reason = "移动止盈"
                    sell_price = pos["max_price"] * (1 - take_profit_trailing)

            # 最大持仓天数
            if max_hold_days > 0 and pos["hold_days"] >= max_hold_days:
                should_sell = True
                sell_reason = "到期"

            if should_sell:
                profit = sell_price / pos["buy_price"] - 1
                trades.append({
                    "ts_code": pos["ts_code"],
                    "buy_date": pos["buy_date"],
                    "sell_date": trade_date,
                    "buy_price": pos["buy_price"],
                    "sell_price": sell_price,
                    "profit": profit,
                    "reason": sell_reason,
                })
                cash += pos["shares"] * (sell_price - pos["buy_price"])
            else:
                new_positions.append(pos)

        positions = new_positions

        # 3. 检查买入信号（使用预计算信号）
        if trade_date in signals_by_date:
            for signal in signals_by_date[trade_date]:
                total_signals += 1
                ts_code = signal["ts_code"]

                # 检查是否已持仓
                if any(p["ts_code"] == ts_code for p in positions):
                    continue

                # 检查买入时机
                df = stock_data[ts_code]
                signal_idx = signal["idx"]

                can_buy, reason = check_buy_timing_fast(
                    df, signal_idx, buy_timing, j_threshold, rsi_threshold
                )

                if can_buy:
                    timing_pass += 1

                    # 检查持仓限制
                    if len(positions) >= max_positions:
                        continue

                    # 买入
                    buy_price = signal["close"]
                    position_value = cash / max_positions
                    shares = position_value / buy_price

                    positions.append({
                        "ts_code": ts_code,
                        "buy_date": trade_date,
                        "buy_price": buy_price,
                        "shares": shares,
                        "current_price": buy_price,
                        "current_high": buy_price,
                        "max_price": buy_price,
                        "hold_days": 0,
                    })
                    cash -= position_value
                else:
                    timing_fail += 1

        # 4. 计算组合价值
        total_value = cash
        for pos in positions:
            total_value += pos["shares"] * pos["current_price"]
        portfolio_value.append(total_value)

        if len(portfolio_value) > 1:
            daily_return = (portfolio_value[-1] / portfolio_value[-2]) - 1
            daily_returns.append(daily_return)

    # 计算绩效指标
    if len(trades) == 0:
        return {
            "trades": 0,
            "win_rate": 0,
            "pl_ratio": 0,
            "return": 0,
            "drawdown": 0,
            "sharpe": 0,
            "total_signals": total_signals,
            "timing_pass": timing_pass,
            "timing_fail": timing_fail,
        }

    wins = [t for t in trades if t["profit"] > 0]
    losses = [t for t in trades if t["profit"] <= 0]
    win_rate = len(wins) / len(trades) if trades else 0

    avg_win = np.mean([t["profit"] for t in wins]) if wins else 0
    avg_loss = np.mean([abs(t["profit"]) for t in losses]) if losses else 0
    pl_ratio = avg_win / avg_loss if avg_loss > 0 else 0

    total_return = portfolio_value[-1] - 1

    # 最大回撤
    peak = portfolio_value[0]
    max_dd = 0
    for v in portfolio_value:
        if v > peak:
            peak = v
        dd = (peak - v) / peak
        if dd > max_dd:
            max_dd = dd

    # 夏普比率
    if len(daily_returns) > 1 and np.std(daily_returns) > 0:
        sharpe = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252)
    else:
        sharpe = 0

    return {
        "trades": len(trades),
        "win_rate": win_rate,
        "pl_ratio": pl_ratio,
        "return": total_return,
        "drawdown": -max_dd,
        "sharpe": sharpe,
        "total_signals": total_signals,
        "timing_pass": timing_pass,
        "timing_fail": timing_fail,
    }


def run_backtest_task_optimized(args):
    """优化版回测任务（在子进程中执行）"""
    params, combo_idx, total_combos, debug = args

    # 直接使用全局变量（已通过初始化器加载）
    metrics = run_single_backtest_optimized(params, debug=debug)

    result = {**params, **metrics}
    return combo_idx, result, debug


# ============== 主优化函数 ==============


def run_optimization(max_workers: int = 8):
    logger.info("=" * 60)
    logger.info("策略参数优化 (优化版 - 进程池初始化器)")
    logger.info("=" * 60)
    logger.info(f"并发进程数: {max_workers}")

    start_time = time.time()

    # 1. 主进程加载数据（只加载一次）
    logger.info("加载数据...")
    daily_df = pd.read_pickle(os.path.join(DATA_DIR, "daily_data.pkl"))
    trade_dates_raw = pd.read_csv(os.path.join(DATA_DIR, "trade_dates.csv"))["trade_date"].tolist()
    trade_dates = [str(d) for d in trade_dates_raw]

    logger.info(f"数据加载完成: {len(daily_df)} 条日线数据, {len(trade_dates)} 个交易日")

    # 2. 预计算技术指标
    logger.info("预计算技术指标...")
    stock_data = prepare_stock_data(daily_df)
    logger.info(f"技术指标计算完成: {len(stock_data)} 只股票")

    # 3. 预计算买入信号
    logger.info("预计算买入信号...")
    signals_by_date = precompute_signals(stock_data, trade_dates)
    total_signals = sum(len(v) for v in signals_by_date.values())
    logger.info(f"信号预计算完成: {total_signals} 个信号, 分布在 {len(signals_by_date)} 个交易日")

    # 4. 参数空间
    param_grid = {
        "j_threshold": [-10],
        "rsi_threshold": [15],
        "vol_ratio_min": [1.0],
        "buy_timing": [
            "immediate",
            "next_day",
            "turn_up",
            "yang_line",
            "break_high",
            "turn_up_yang",
            "turn_up_break",
        ],
        "max_positions": [3, 5, 8],
        "stop_loss": [-0.03, -0.05],
        "take_profit_fixed": [0.05, 0.08, 0.10],
        "take_profit_trigger": [0.03, 0.05],
        "take_profit_trailing": [0.02, 0.03],
        "max_hold_days": [0, 2, 3, 5, 10, 20],
    }

    total = 1
    for v in param_grid.values():
        total *= len(v)

    logger.info(f"参数组合总数: {total}")
    logger.info("-" * 60)

    # 5. 生成所有参数组合
    param_names = list(param_grid.keys())
    param_values = list(param_grid.values())
    all_combos = list(product(*param_values))

    tasks = []
    for i, combo in enumerate(all_combos):
        params = dict(zip(param_names, combo))
        tasks.append((params, i, total, True))

    # 6. 使用进程池初始化器运行优化
    logger.info("开始多进程网格搜索...")
    logger.info("-" * 60)

    results = []
    best_result = None
    best_sharpe = -999

    # 将数据转换为可pickle的格式
    # 注意：DataFrame需要特殊处理
    stock_data_serializable = {}
    for ts_code, df in stock_data.items():
        stock_data_serializable[ts_code] = df.to_dict('list')

    with ProcessPoolExecutor(
        max_workers=max_workers,
        initializer=init_worker,
        initargs=(stock_data_serializable, trade_dates, signals_by_date)
    ) as executor:
        futures = {executor.submit(run_backtest_task_optimized, task): task for task in tasks}

        completed = 0
        for future in as_completed(futures):
            completed += 1
            try:
                combo_idx, result, debug = future.result()
                results.append(result)

                # 更新最佳结果
                if result["sharpe"] > best_sharpe:
                    best_sharpe = result["sharpe"]
                    best_result = result

                # 打印进度
                if completed % 50 == 0 or completed == total:
                    elapsed = time.time() - start_time
                    speed = completed / elapsed if elapsed > 0 else 0
                    remaining = (total - completed) / speed if speed > 0 else 0

                    logger.info(
                        f"[{completed}/{total}] "
                        f"买入时机={result['buy_timing']}, "
                        f"持仓{result['max_positions']}支, "
                        f"止损{result['stop_loss']:.0%}, "
                        f"止盈{result['take_profit_fixed']:.0%}, "
                        f"持仓{result['max_hold_days']}天 | "
                        f"交易数={result['trades']}, "
                        f"收益={result['return']:.2%}, "
                        f"胜率={result['win_rate']:.1%}, "
                        f"夏普={result['sharpe']:.2f}"
                    )
                    logger.info(
                        f"  进度: {completed/total*100:.1f}% | "
                        f"速度: {speed:.1f}组/秒 | "
                        f"剩余: {remaining:.0f}秒"
                    )
                    logger.info("-" * 40)

            except Exception as e:
                logger.error(f"回测出错: {e}")

    # 7. 保存结果
    elapsed = time.time() - start_time
    logger.info("=" * 60)
    logger.info(f"优化完成! 总耗时: {elapsed:.1f}秒")
    logger.info("=" * 60)

    # 排序结果
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values("sharpe", ascending=False)

    # 保存到CSV
    output_path = os.path.join(SCRIPT_DIR, "optimization_results_optimized.csv")
    results_df.to_csv(output_path, index=False)
    logger.info(f"结果已保存到: {output_path}")

    # 打印最佳结果
    if best_result:
        logger.info("=" * 60)
        logger.info("最佳参数组合:")
        logger.info(f"  买入时机: {best_result['buy_timing']}")
        logger.info(f"  最大持仓: {best_result['max_positions']}支")
        logger.info(f"  止损: {best_result['stop_loss']:.0%}")
        logger.info(f"  止盈: {best_result['take_profit_fixed']:.0%}")
        logger.info(f"  最大持仓天数: {best_result['max_hold_days']}天")
        logger.info("-" * 40)
        logger.info(f"  交易数: {best_result['trades']}")
        logger.info(f"  收益率: {best_result['return']:.2%}")
        logger.info(f"  胜率: {best_result['win_rate']:.1%}")
        logger.info(f"  夏普比率: {best_result['sharpe']:.2f}")
        logger.info(f"  最大回撤: {best_result['drawdown']:.2%}")
        logger.info("=" * 60)

    return results_df


if __name__ == "__main__":
    # 获取CPU信息
    cpu_count = multiprocessing.cpu_count()
    physical_cores = cpu_count // 2  # 假设超线程

    logger.info(f"CPU: 物理核心: {physical_cores}, 逻辑核心: {cpu_count}")
    logger.info(f"内存: 32GB, 使用进程数: 8")

    # 运行优化
    run_optimization(max_workers=8)
