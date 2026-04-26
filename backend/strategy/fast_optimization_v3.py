"""
策略参数优化 - 使用预计算指标数据（高性能版本）
优化点：
1. 直接从数据库读取预计算的指标数据，无需实时计算
2. 大幅减少计算时间，支持更大参数空间的搜索
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from loguru import logger
from itertools import product
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
from datetime import datetime
from sqlalchemy import text

from app.core.database import SessionLocal, engine
from app.models.indicator import DailyIndicator
from app.models.daily import DailyData


# 初始化日志
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)
logger.add(
    os.path.join(log_dir, "strategy_fast.log"),
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    rotation="10 MB",
    retention="30 days",
    encoding="utf-8",
)


def load_precomputed_indicators(start_date: str = None, end_date: str = None) -> tuple:
    """
    加载预计算的指标数据

    Returns:
        (stock_data_dict, trade_dates_list)
    """
    logger.info("加载预计算指标数据...")

    db = SessionLocal()

    # 构建查询
    query = """
        SELECT i.*, d.open, d.high, d.low, d.close, d.vol
        FROM daily_indicator i
        JOIN daily_data d ON i.ts_code = d.ts_code AND i.trade_date = d.trade_date
        WHERE 1=1
    """
    params = {}

    if start_date:
        query += " AND i.trade_date >= :start_date"
        params['start_date'] = start_date
    if end_date:
        query += " AND i.trade_date <= :end_date"
        params['end_date'] = end_date

    query += " ORDER BY i.ts_code, i.trade_date"

    df = pd.read_sql(text(query), db.bind, params=params)
    db.close()

    logger.info(f"加载完成: {len(df)} 条记录")

    # 按股票分组
    stock_data = {}
    for ts_code, group in df.groupby('ts_code'):
        group = group.sort_values('trade_date').reset_index(drop=True)
        stock_data[ts_code] = group

    # 获取交易日列表
    trade_dates = df['trade_date'].unique().tolist()
    trade_dates.sort()

    logger.info(f"股票数: {len(stock_data)}, 交易日数: {len(trade_dates)}")

    return stock_data, trade_dates


def precompute_signals_fast(stock_data: dict, trade_dates: list,
                           j_threshold: float = -10,
                           rsi_threshold: float = 15,
                           vol_ratio_min: float = 1.0) -> dict:
    """
    使用预计算数据快速筛选信号

    Returns:
        {trade_date: [(ts_code, signal_info), ...]}
    """
    logger.info("预计算买入信号...")
    signals_by_date = {}

    for ts_code, df in stock_data.items():
        for idx in range(len(df)):
            row = df.iloc[idx]

            # 直接使用预计算的指标值
            j_val = row.get('j_value')
            rsi_val = row.get('rsi6')
            vol_ratio = row.get('vol_ratio')

            if pd.isna(j_val) or pd.isna(rsi_val) or pd.isna(vol_ratio):
                continue

            # 信号条件
            if j_val < j_threshold and rsi_val < rsi_threshold and vol_ratio > vol_ratio_min:
                trade_date = str(row['trade_date'])

                signal_info = {
                    'ts_code': ts_code,
                    'idx': idx,
                    'j': j_val,
                    'rsi': rsi_val,
                    'vol_ratio': vol_ratio,
                    'close': row['close'],
                    'open': row['open'],
                    'high': row['high'],
                    'low': row['low'],
                    'k': row.get('k_value'),
                    'd': row.get('d_value'),
                    'macd_dif': row.get('macd_dif'),
                    'macd_hist': row.get('macd_hist'),
                    'drawdown_20d': row.get('drawdown_20d'),
                    'consecutive_down': row.get('consecutive_down'),
                }

                if trade_date not in signals_by_date:
                    signals_by_date[trade_date] = []
                signals_by_date[trade_date].append(signal_info)

    total_signals = sum(len(v) for v in signals_by_date.values())
    logger.info(f"信号预计算完成: {total_signals} 个信号")

    return signals_by_date


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
        j_still_oversold = row.get('j_value', 50) < j_threshold
        rsi_still_oversold = row.get('rsi6', 50) < rsi_threshold
        price_up = row['close'] > prev_row['close']
        if (j_still_oversold and rsi_still_oversold) or price_up:
            return True, "次日确认"
        return False, "次日未确认"

    elif buy_timing == "turn_up":
        if row.get('j_value', 0) > prev_row.get('j_value', 0):
            return True, "J值拐头"
        return False, "J值未拐头"

    elif buy_timing == "yang_line":
        if row['close'] > row['open']:
            return True, "收阳线"
        return False, "未收阳线"

    elif buy_timing == "break_high":
        if row['high'] > prev_row['high']:
            return True, "突破前高"
        return False, "未突破前高"

    elif buy_timing == "turn_up_yang":
        j_turn_up = row.get('j_value', 0) > prev_row.get('j_value', 0)
        yang_line = row['close'] > row['open']
        if j_turn_up and yang_line:
            return True, "J拐头+阳线"
        return False, f"J拐头={j_turn_up}, 阳线={yang_line}"

    elif buy_timing == "turn_up_break":
        j_turn_up = row.get('j_value', 0) > prev_row.get('j_value', 0)
        break_high = row['high'] > prev_row['high']
        if j_turn_up and break_high:
            return True, "J拐头+突破"
        return False, f"J拐头={j_turn_up}, 突破={break_high}"

    return False, "未知策略"


def run_single_backtest_fast(
    stock_data: dict,
    trade_dates: list,
    signals_by_date: dict,
    params: dict,
) -> dict:
    """使用预计算数据的快速回测"""
    j_threshold = params["j_threshold"]
    rsi_threshold = params["rsi_threshold"]
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

    total_signals = 0
    timing_pass = 0
    timing_fail = 0

    for date_idx, trade_date in enumerate(trade_dates):
        # 1. 更新持仓价格
        for pos in positions:
            ts_code = pos["ts_code"]
            if ts_code in stock_data:
                df = stock_data[ts_code]
                date_rows = df[df['trade_date'].astype(str) == str(trade_date)]
                if not date_rows.empty:
                    pos["current_price"] = float(date_rows.iloc[0]['close'])
                    pos["current_high"] = float(date_rows.iloc[0]['high'])
                    pos["hold_days"] += 1

        # 2. 检查卖出条件
        new_positions = []
        for pos in positions:
            should_sell = False
            sell_reason = ""
            sell_price = pos["current_price"]

            pnl = pos["current_price"] / pos["buy_price"] - 1

            # 止损
            if pnl < stop_loss:
                should_sell = True
                sell_reason = "止损"
                sell_price = pos["buy_price"] * (1 + stop_loss)

            # 固定止盈
            elif pnl > take_profit_fixed:
                should_sell = True
                sell_reason = "止盈"
                sell_price = pos["buy_price"] * (1 + take_profit_fixed)

            # 移动止盈
            elif pnl > take_profit_trigger:
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
                    "profit": profit,
                    "reason": sell_reason,
                })
                cash += pos["shares"] * (sell_price - pos["buy_price"])
            else:
                new_positions.append(pos)

        positions = new_positions

        # 3. 检查买入信号（使用预计算信号）
        if str(trade_date) in signals_by_date:
            for signal in signals_by_date[str(trade_date)]:
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


def run_optimization_fast(max_workers: int = 8):
    """使用预计算数据的快速优化"""
    logger.info("=" * 60)
    logger.info("策略参数优化 (预计算数据版本)")
    logger.info("=" * 60)

    start_time = time.time()

    # 1. 加载预计算数据
    stock_data, trade_dates = load_precomputed_indicators()

    # 2. 预计算信号
    signals_by_date = precompute_signals_fast(stock_data, trade_dates)

    # 3. 参数空间
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

    # 4. 生成所有参数组合
    param_names = list(param_grid.keys())
    param_values = list(param_grid.values())
    all_combos = list(product(*param_values))

    # 5. 运行回测
    results = []
    for i, combo in enumerate(all_combos):
        params = dict(zip(param_names, combo))
        metrics = run_single_backtest_fast(stock_data, trade_dates, signals_by_date, params)
        result = {**params, **metrics}
        results.append(result)

        if (i + 1) % 50 == 0 or i + 1 == total:
            elapsed = time.time() - start_time
            speed = (i + 1) / elapsed
            logger.info(
                f"[{i+1}/{total}] 买入时机={params['buy_timing']}, "
                f"交易数={metrics['trades']}, 收益={metrics['return']:.2%}, "
                f"胜率={metrics['win_rate']:.1%}, 夏普={metrics['sharpe']:.2f}"
            )
            logger.info(f"速度: {speed:.1f}组/秒")

    # 6. 分析结果
    elapsed = time.time() - start_time
    logger.info("-" * 60)
    logger.info(f"优化完成! 总耗时: {elapsed:.1f}秒")

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values("sharpe", ascending=False)

    # 保存结果
    output_path = os.path.join(os.path.dirname(__file__), "optimization_results_fast.csv")
    results_df.to_csv(output_path, index=False)
    logger.info(f"结果已保存: {output_path}")

    # 打印最佳结果
    best = results_df.iloc[0]
    logger.info("=" * 60)
    logger.info("最佳参数组合:")
    logger.info(f"  买入时机: {best['buy_timing']}")
    logger.info(f"  最大持仓: {best['max_positions']}支")
    logger.info(f"  止损: {best['stop_loss']:.0%}")
    logger.info(f"  止盈: {best['take_profit_fixed']:.0%}")
    logger.info(f"  最大持仓天数: {best['max_hold_days']}天")
    logger.info("-" * 40)
    logger.info(f"  交易数: {best['trades']}")
    logger.info(f"  收益率: {best['return']:.2%}")
    logger.info(f"  胜率: {best['win_rate']:.1%}")
    logger.info(f"  夏普比率: {best['sharpe']:.2f}")
    logger.info(f"  最大回撤: {best['drawdown']:.2%}")
    logger.info("=" * 60)

    return results_df


if __name__ == "__main__":
    run_optimization_fast(max_workers=8)