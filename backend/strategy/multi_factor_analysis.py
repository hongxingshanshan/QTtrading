"""
寻找高胜率策略组合
数据源：CSV + PKL 本地文件（已通过数据校验）
"""
import sys
sys.path.insert(0, '.')

import pandas as pd
import numpy as np
from loguru import logger
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

from app.core.logging import setup_logging

# 初始化日志配置
setup_logging()

# ============== 数据加载（本地文件） ==============

def load_local_data() -> tuple:
    """加载本地数据文件"""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')

    # 加载股票列表
    stocks_df = pd.read_csv(os.path.join(data_dir, 'stocks.csv'))
    stocks = list(zip(stocks_df['ts_code'], stocks_df['name']))

    # 加载日线数据（已应用前复权）
    daily_df = pd.read_pickle(os.path.join(data_dir, 'daily_data.pkl'))

    logger.info(f"加载本地数据: {len(stocks)} 只股票, {len(daily_df)} 条日线数据")

    return stocks, daily_df


def get_daily_data_local(daily_df: pd.DataFrame, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """从本地数据获取单只股票的日线数据"""
    # 转换日期格式（兼容字符串和datetime.date）
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)

    # 确保 trade_date 列为 datetime 类型
    if daily_df['trade_date'].dtype == 'object':
        daily_df['trade_date'] = pd.to_datetime(daily_df['trade_date'])

    mask = (
        (daily_df['ts_code'] == ts_code) &
        (daily_df['trade_date'] >= start_dt) &
        (daily_df['trade_date'] <= end_dt)
    )
    df = daily_df[mask].copy()
    df = df.sort_values('trade_date').reset_index(drop=True)
    return df


# ============== 技术指标计算 ==============

def calculate_ma(df: pd.DataFrame, periods: list = [5, 10, 20, 30, 60]) -> pd.DataFrame:
    """计算均线"""
    for n in periods:
        df[f'ma{n}'] = df['close'].rolling(window=n, min_periods=n).mean()
    return df


def calculate_kdj(df: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3) -> pd.DataFrame:
    """计算KDJ指标"""
    low_n = df['low'].rolling(window=n, min_periods=n).min()
    high_n = df['high'].rolling(window=n, min_periods=n).max()

    rsv = (df['close'] - low_n) / (high_n - low_n) * 100
    rsv = rsv.fillna(50)

    df['k'] = rsv.ewm(alpha=1/m1, adjust=False).mean()
    df['d'] = df['k'].ewm(alpha=1/m2, adjust=False).mean()
    df['j'] = 3 * df['k'] - 2 * df['d']

    return df


def calculate_rsi(df: pd.DataFrame, periods: list = [6, 12, 24]) -> pd.DataFrame:
    """计算RSI指标"""
    for n in periods:
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = (-delta).where(delta < 0, 0)

        avg_gain = gain.rolling(window=n, min_periods=n).mean()
        avg_loss = loss.rolling(window=n, min_periods=n).mean()

        rs = avg_gain / avg_loss.replace(0, np.inf)
        df[f'rsi{n}'] = 100 - (100 / (1 + rs))

    return df


def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """计算MACD指标"""
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()

    df['macd_dif'] = ema_fast - ema_slow
    df['macd_dea'] = df['macd_dif'].ewm(span=signal, adjust=False).mean()
    df['macd_hist'] = 2 * (df['macd_dif'] - df['macd_dea'])

    return df


def calculate_boll(df: pd.DataFrame, n: int = 20, k: float = 2) -> pd.DataFrame:
    """计算布林带"""
    df['boll_mid'] = df['close'].rolling(window=n, min_periods=n).mean()
    # 使用总体标准差（ddof=0），与前端保持一致
    std = df['close'].rolling(window=n, min_periods=n).std(ddof=0)
    df['boll_upper'] = df['boll_mid'] + k * std
    df['boll_lower'] = df['boll_mid'] - k * std

    # 布林带位置 (0=下轨, 0.5=中轨, 1=上轨)
    df['boll_position'] = (df['close'] - df['boll_lower']) / (df['boll_upper'] - df['boll_lower'])

    # 布林带宽度
    df['boll_width'] = (df['boll_upper'] - df['boll_lower']) / df['boll_mid']

    return df


def calculate_cci(df: pd.DataFrame, n: int = 14) -> pd.DataFrame:
    """计算CCI指标"""
    tp = (df['high'] + df['low'] + df['close']) / 3
    ma = tp.rolling(window=n, min_periods=n).mean()
    md = tp.rolling(window=n, min_periods=n).apply(lambda x: np.abs(x - x.mean()).mean())
    df['cci'] = (tp - ma) / (0.015 * md)
    return df


def calculate_wr(df: pd.DataFrame, n: int = 14) -> pd.DataFrame:
    """计算威廉指标"""
    high_n = df['high'].rolling(window=n, min_periods=n).max()
    low_n = df['low'].rolling(window=n, min_periods=n).min()
    df[f'wr{n}'] = (high_n - df['close']) / (high_n - low_n) * 100
    return df


def calculate_obv(df: pd.DataFrame) -> pd.DataFrame:
    """计算OBV指标"""
    direction = np.where(df['close'] > df['close'].shift(1), 1, -1)
    direction[0] = 0
    df['obv'] = (df['vol'] * direction).cumsum()
    df['obv_ma5'] = df['obv'].rolling(window=5, min_periods=5).mean()
    return df


def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """计算所有技术指标"""
    df = calculate_ma(df)
    df = calculate_kdj(df)
    df = calculate_rsi(df)
    df = calculate_macd(df)
    df = calculate_boll(df)
    df = calculate_cci(df)
    df = calculate_wr(df)
    df = calculate_obv(df)
    return df


def calculate_price_factors(df: pd.DataFrame) -> pd.DataFrame:
    """计算价格形态因子"""
    # 连续下跌天数
    df['down_days'] = (df['close'] < df['close'].shift(1)).astype(int)
    df['consecutive_down'] = df['down_days'].groupby(
        (df['down_days'] != df['down_days'].shift()).cumsum()
    ).cumsum()

    # 连续上涨天数
    df['up_days'] = (df['close'] > df['close'].shift(1)).astype(int)
    df['consecutive_up'] = df['up_days'].groupby(
        (df['up_days'] != df['up_days'].shift()).cumsum()
    ).cumsum()

    # 距20日高点回撤
    df['high_20d'] = df['high'].rolling(window=20, min_periods=1).max()
    df['drawdown_20d'] = (df['close'] - df['high_20d']) / df['high_20d']

    # 距20日低点反弹
    df['low_20d'] = df['low'].rolling(window=20, min_periods=1).min()
    df['rebound_20d'] = (df['close'] - df['low_20d']) / df['low_20d']

    # 振幅
    df['amplitude'] = (df['high'] - df['low']) / df['close'].shift(1)

    # 涨跌幅
    df['pct_change'] = df['close'].pct_change()

    # 5日累计涨跌幅
    df['pct_change_5d'] = df['close'].pct_change(5)

    # 10日累计涨跌幅
    df['pct_change_10d'] = df['close'].pct_change(10)

    return df


def calculate_volume_factors(df: pd.DataFrame) -> pd.DataFrame:
    """计算成交量因子"""
    # 成交量均线
    df['vol_ma5'] = df['vol'].rolling(window=5, min_periods=5).mean()
    df['vol_ma10'] = df['vol'].rolling(window=10, min_periods=10).mean()

    # 成交量放大倍数
    df['vol_ratio'] = df['vol'] / df['vol_ma5']

    # 缩量标志 (成交量低于5日均量的50%)
    df['is_shrink_vol'] = (df['vol'] < df['vol_ma5'] * 0.5).astype(int)

    # 放量标志 (成交量高于5日均量的200%)
    df['is_expand_vol'] = (df['vol'] > df['vol_ma5'] * 2).astype(int)

    # 量价关系
    df['vol_price_up'] = ((df['close'] > df['close'].shift(1)) & (df['vol'] > df['vol_ma5'])).astype(int)
    df['vol_price_down'] = ((df['close'] < df['close'].shift(1)) & (df['vol'] > df['vol_ma5'])).astype(int)

    return df


def calculate_ma_deviation(df: pd.DataFrame) -> pd.DataFrame:
    """计算均线偏离度"""
    for n in [5, 10, 20, 30, 60]:
        if f'ma{n}' in df.columns:
            df[f'ma{n}_deviation'] = (df['close'] - df[f'ma{n}']) / df[f'ma{n}']

    # 均线排列 (1=多头, -1=空头, 0=混乱)
    def check_ma_alignment(row):
        mas = [row.get(f'ma{n}', np.nan) for n in [5, 10, 20, 30, 60]]
        if any(np.isnan(mas)):
            return 0
        if all(mas[i] > mas[i+1] for i in range(len(mas)-1)):
            return 1  # 多头排列
        if all(mas[i] < mas[i+1] for i in range(len(mas)-1)):
            return -1  # 空头排列
        return 0

    df['ma_alignment'] = df.apply(check_ma_alignment, axis=1)

    return df

# ============== 信号识别与分析 ==============

def process_single_stock(args):
    """处理单只股票的信号识别（用于多进程）"""
    ts_code, name, start_date, end_date, hold_days = args

    try:
        # 每个子进程自己加载数据（避免进程间传递大数据）
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        daily_df = pd.read_pickle(os.path.join(data_dir, 'daily_data.pkl'))

        df = get_daily_data_local(daily_df, ts_code, start_date, end_date)
        if len(df) < 60:
            return []

        # 计算所有因子
        df = calculate_all_indicators(df)
        df = calculate_price_factors(df)
        df = calculate_volume_factors(df)
        df = calculate_ma_deviation(df)
        df = identify_signals(df)

        signals = []
        # 收集信号
        for idx in range(60, len(df) - hold_days):
            row = df.iloc[idx]

            if not row['any_signal']:
                continue

            signal_date = row['trade_date']
            signal_price = row['close']  # 信号当天收盘价作为买入价

            # 计算后续收益
            future = df.iloc[idx + 1: idx + 1 + hold_days]
            if len(future) < hold_days:
                continue

            returns = {}
            for d in [3, 5, 10, 20]:
                future_price = future.iloc[d - 1]['close']
                returns[f'd{d}_pnl'] = (future_price - signal_price) / signal_price

            returns['max_pnl'] = (future['high'].max() - signal_price) / signal_price
            returns['min_pnl'] = (future['low'].min() - signal_price) / signal_price

            # 信号类型
            signal_types = []
            if row['kdj_signal']:
                signal_types.append('KDJ')
            if row['rsi_signal']:
                signal_types.append('RSI')
            if row['cci_signal']:
                signal_types.append('CCI')
            if row['wr_signal']:
                signal_types.append('WR')
            if row['boll_signal']:
                signal_types.append('BOLL')
            if row['macd_signal']:
                signal_types.append('MACD金叉')
            if row['macd_hist_signal']:
                signal_types.append('MACD柱')

            signals.append({
                'ts_code': ts_code,
                'name': name,
                'signal_date': signal_date,
                'signal_price': signal_price,
                'signal_type': '+'.join(signal_types),
                # 技术指标
                'j_value': row['j'],
                'k_value': row['k'],
                'rsi6': row['rsi6'],
                'rsi12': row['rsi12'],
                'cci': row['cci'],
                'wr14': row['wr14'],
                'macd_dif': row['macd_dif'],
                'macd_dea': row['macd_dea'],
                'macd_hist': row['macd_hist'],
                'boll_position': row['boll_position'],
                'boll_width': row['boll_width'],
                # 均线偏离
                'ma5_deviation': row['ma5_deviation'],
                'ma10_deviation': row['ma10_deviation'],
                'ma20_deviation': row['ma20_deviation'],
                'ma_alignment': row['ma_alignment'],
                # 价格形态
                'consecutive_down': row['consecutive_down'],
                'drawdown_20d': row['drawdown_20d'],
                'rebound_20d': row['rebound_20d'],
                'amplitude': row['amplitude'],
                'pct_change_5d': row['pct_change_5d'],
                'pct_change_10d': row['pct_change_10d'],
                # 成交量
                'vol_ratio': row['vol_ratio'],
                'is_shrink_vol': row['is_shrink_vol'],
                'is_expand_vol': row['is_expand_vol'],
                # 收益
                **returns
            })

        return signals
    except Exception as e:
        # 返回错误信息
        return {'error': str(e), 'ts_code': ts_code, 'name': name}


def identify_signals(df: pd.DataFrame) -> pd.DataFrame:
    """识别超卖信号"""
    # KDJ J值下破0轴
    df['kdj_signal'] = (df['j'] < 0) & (df['j'].shift(1) >= 0)

    # RSI6 下破20
    df['rsi_signal'] = (df['rsi6'] < 20) & (df['rsi6'].shift(1) >= 20)

    # CCI 下破-100
    df['cci_signal'] = (df['cci'] < -100) & (df['cci'].shift(1) >= -100)

    # WR 上破80 (注意WR是反向的，大于80是超卖)
    df['wr_signal'] = (df['wr14'] > 80) & (df['wr14'].shift(1) <= 80)

    # 布林带下轨突破
    df['boll_signal'] = df['close'] < df['boll_lower']

    # MACD 金叉信号 (DIF上穿DEA，且都在零轴下方 - 底部金叉)
    df['macd_signal'] = (
        (df['macd_dif'] > df['macd_dea']) &
        (df['macd_dif'].shift(1) <= df['macd_dea'].shift(1)) &
        (df['macd_dif'] < 0)  # 零轴下方的金叉更可靠
    )

    # MACD 柱状图由负转正（底背离信号）
    df['macd_hist_signal'] = (
        (df['macd_hist'] > 0) &
        (df['macd_hist'].shift(1) <= 0) &
        (df['macd_dif'] < 0)
    )

    # 综合信号
    df['any_signal'] = (
        df['kdj_signal'] | df['rsi_signal'] | df['cci_signal'] |
        df['wr_signal'] | df['macd_signal'] | df['macd_hist_signal']
    )

    return df


def analyze_factor_groups(signals_df: pd.DataFrame, factor_col: str, bins: list, labels: list) -> pd.DataFrame:
    """分析单因子分组收益"""
    signals_df = signals_df.copy()
    signals_df['factor_group'] = pd.cut(signals_df[factor_col], bins=bins, labels=labels)

    results = []
    for group in labels:
        subset = signals_df[signals_df['factor_group'] == group]
        if len(subset) < 10:
            continue

        results.append({
            'factor': factor_col,
            'group': group,
            'count': len(subset),
            'win_rate_5d': (subset['d5_pnl'] > 0).sum() / len(subset) * 100,
            'avg_pnl_5d': subset['d5_pnl'].mean() * 100,
            'win_rate_20d': (subset['d20_pnl'] > 0).sum() / len(subset) * 100,
            'avg_pnl_20d': subset['d20_pnl'].mean() * 100,
        })

    return pd.DataFrame(results)


def analyze_combined_factors(signals_df: pd.DataFrame, conditions: dict) -> dict:
    """分析组合条件收益"""
    mask = pd.Series([True] * len(signals_df), index=signals_df.index)

    for col, condition in conditions.items():
        if col not in signals_df.columns:
            return None
        if isinstance(condition, tuple):
            op, val = condition
            if op == '<':
                mask &= (signals_df[col] < val)
            elif op == '<=':
                mask &= (signals_df[col] <= val)
            elif op == '>':
                mask &= (signals_df[col] > val)
            elif op == '>=':
                mask &= (signals_df[col] >= val)
            elif op == 'between':
                mask &= (signals_df[col] >= val[0]) & (signals_df[col] <= val[1])
        else:
            mask &= (signals_df[col] == condition)

    subset = signals_df[mask]
    if len(subset) < 10:
        return None

    return {
        'conditions': str(conditions),
        'count': len(subset),
        'win_rate_5d': (subset['d5_pnl'] > 0).sum() / len(subset) * 100,
        'avg_pnl_5d': subset['d5_pnl'].mean() * 100,
        'win_rate_20d': (subset['d20_pnl'] > 0).sum() / len(subset) * 100,
        'avg_pnl_20d': subset['d20_pnl'].mean() * 100,
        'max_pnl_avg': subset['max_pnl'].mean() * 100,
        'min_pnl_avg': subset['min_pnl'].mean() * 100,
    }


def run_analysis(start_date: str = '20250425', end_date: str = '20260424', hold_days: int = 20, max_workers: int = 8):
    """运行多因子分析（多进程版本）"""
    import time

    logger.info("=" * 60)
    logger.info("多因子超卖信号分析")
    logger.info("=" * 60)
    logger.info(f"分析区间: {start_date} ~ {end_date}")
    logger.info(f"持有天数: {hold_days}")
    logger.info(f"并发进程: {max_workers}")

    # 加载本地数据（仅用于获取股票列表）
    stocks, _ = load_local_data()
    logger.info(f"有效股票数: {len(stocks)}")

    # 准备任务参数（不传递 daily_df，让子进程自己加载）
    tasks = [(ts_code, name, start_date, end_date, hold_days)
             for ts_code, name in stocks]

    all_signals = []
    completed = 0
    error_count = 0
    start_time = time.time()

    logger.info("开始多进程处理...")
    logger.info("-" * 60)

    # 多进程处理
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_single_stock, task): i for i, task in enumerate(tasks)}

        for future in as_completed(futures):
            completed += 1
            try:
                result = future.result()

                # 检查是否是错误结果
                if isinstance(result, dict) and 'error' in result:
                    error_count += 1
                    logger.error(f"[{completed}/{len(stocks)}] {result['ts_code']} {result['name']} 错误: {result['error']}")
                elif isinstance(result, list):
                    all_signals.extend(result)
            except Exception as e:
                error_count += 1
                logger.error(f"[{completed}/{len(stocks)}] 处理异常: {e}")

            # 每100个输出进度
            if completed % 100 == 0:
                elapsed = time.time() - start_time
                speed = completed / elapsed
                remaining = (len(stocks) - completed) / speed if speed > 0 else 0
                logger.info(f"进度: {completed}/{len(stocks)} ({completed*100/len(stocks):.1f}%) | "
                           f"信号数: {len(all_signals)} | 错误: {error_count} | "
                           f"速度: {speed:.1f}股/秒 | 剩余: {remaining:.0f}秒")

    elapsed = time.time() - start_time
    logger.info("-" * 60)
    logger.info(f"处理完成! 总耗时: {elapsed:.1f}秒")
    logger.info(f"处理股票: {completed}, 成功: {completed - error_count}, 错误: {error_count}")

    if not all_signals:
        logger.warning("未找到任何信号")
        return None

    signals_df = pd.DataFrame(all_signals)
    logger.info(f"共找到 {len(signals_df)} 个信号")

    # ============== 分析结果 ==============

    print("\n" + "=" * 80)
    print("多因子超卖信号分析")
    print("=" * 80)

    # 1. 单因子分组分析
    print("\n【单因子分组分析】")

    factor_groups = [
        ('j_value', [-100, -20, -10, 0, 20], ['<-20', '-20~-10', '-10~0', '>0']),
        ('rsi6', [0, 10, 15, 20, 30], ['<10', '10~15', '15~20', '>20']),
        ('cci', [-300, -200, -100, 0, 100], ['<-200', '-200~-100', '-100~0', '>0']),
        ('macd_dif', [-0.5, -0.2, -0.1, 0, 0.1, 0.5], ['<-0.2', '-0.2~-0.1', '-0.1~0', '0~0.1', '>0.1']),
        ('macd_hist', [-0.3, -0.1, 0, 0.1, 0.3], ['<-0.1', '-0.1~0', '0~0.1', '>0.1']),
        ('consecutive_down', [-1, 1, 2, 3, 5, 20], ['1天', '2天', '3天', '4天', '5天+']),
        ('drawdown_20d', [-0.5, -0.2, -0.1, -0.05, 0], ['<-20%', '-20%~-10%', '-10%~-5%', '-5%~0%']),
        ('vol_ratio', [0, 0.5, 1, 1.5, 2, 10], ['<0.5', '0.5~1', '1~1.5', '1.5~2', '>2']),
        ('ma_alignment', [-1.5, -0.5, 0.5, 1.5], ['空头排列', '混乱', '多头排列']),
    ]

    all_group_results = []
    for factor_col, bins, labels in factor_groups:
        if factor_col in signals_df.columns:
            result = analyze_factor_groups(signals_df, factor_col, bins, labels)
            if result is not None and len(result) > 0:
                all_group_results.append(result)
                print(f"\n  {factor_col}:")
                for _, row in result.iterrows():
                    print(f"    {row['group']}: 次数={row['count']}, 5天胜率={row['win_rate_5d']:.1f}%, 5天收益={row['avg_pnl_5d']:.2f}%")

    # 2. 组合条件分析
    print("\n【组合条件分析】")

    combined_conditions = [
        {'j_value': ('<', -10), 'rsi6': ('<', 15)},
        {'j_value': ('<', -10), 'consecutive_down': ('>=', 3)},
        {'j_value': ('<', -10), 'vol_ratio': ('>', 1)},
        {'rsi6': ('<', 15), 'drawdown_20d': ('<', -0.1)},
        {'j_value': ('<', -10), 'rsi6': ('<', 15), 'consecutive_down': ('>=', 2)},
        {'j_value': ('<', -10), 'ma_alignment': ('==', -1)},
        {'rsi6': ('<', 15), 'vol_ratio': ('between', (0.5, 1.5))},
        {'j_value': ('<', -20), 'rsi6': ('<', 10)},
        {'cci': ('<', -200), 'wr14': ('>', 90)},
        {'j_value': ('<', -10), 'rsi6': ('<', 15), 'vol_ratio': ('>', 1)},
        # J值小于0的超卖组合
        {'j_value': ('<', 0), 'rsi6': ('<', 20)},           # J超卖 + RSI超卖
        {'j_value': ('<', 0), 'vol_ratio': ('>', 1)},       # J超卖 + 放量
        {'j_value': ('<', 0), 'macd_hist': ('>', 0)},       # J超卖 + MACD金叉
        {'j_value': ('<', 0), 'consecutive_down': ('>=', 3)},  # J超卖 + 连续下跌
        {'j_value': ('<', 0), 'rsi6': ('<', 20), 'vol_ratio': ('>', 1)},  # J超卖 + RSI超卖 + 放量
        # MACD 相关组合
        {'macd_dif': ('<', 0), 'macd_hist': ('between', (-0.05, 0.05))},  # MACD底部收敛
        {'macd_dif': ('<', -0.1), 'rsi6': ('<', 20)},  # MACD超卖+RSI超卖
        {'j_value': ('<', -10), 'macd_dif': ('<', 0), 'macd_hist': ('>', 0)},  # KDJ超卖+MACD金叉
        {'rsi6': ('<', 15), 'macd_hist': ('>', 0)},  # RSI超卖+MACD柱转正
        {'cci': ('<', -100), 'macd_dif': ('<', 0), 'macd_hist': ('>', 0)},  # CCI超卖+MACD金叉
        {'j_value': ('<', -20), 'macd_dif': ('<', -0.1)},  # 深度超卖
        {'drawdown_20d': ('<', -0.15), 'macd_hist': ('>', 0)},  # 深度回撤+MACD金叉
    ]

    combined_results = []
    for conditions in combined_conditions:
        result = analyze_combined_factors(signals_df, conditions)
        if result:
            combined_results.append(result)
            print(f"\n  {result['conditions']}")
            print(f"    次数: {result['count']}")
            print(f"    5天胜率: {result['win_rate_5d']:.1f}%, 5天收益: {result['avg_pnl_5d']:.2f}%")
            print(f"    20天胜率: {result['win_rate_20d']:.1f}%, 20天收益: {result['avg_pnl_20d']:.2f}%")

    # 3. 找出最优组合
    print("\n【最优组合排序 (按5天胜率)】")
    combined_df = pd.DataFrame(combined_results)
    if len(combined_df) > 0:
        combined_df = combined_df.sort_values('win_rate_5d', ascending=False)
        for i, row in combined_df.head(5).iterrows():
            print(f"  {row['conditions']}")
            print(f"    次数={row['count']}, 5天胜率={row['win_rate_5d']:.1f}%, 5天收益={row['avg_pnl_5d']:.2f}%")

    # 保存结果
    signals_df.to_csv('strategy/multi_factor_signals.csv', index=False, encoding='utf-8-sig')
    print(f"\n详细数据已保存到: strategy/multi_factor_signals.csv")

    return signals_df, combined_df


if __name__ == "__main__":
    run_analysis()
