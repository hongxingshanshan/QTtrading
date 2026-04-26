"""
技术指标预计算服务 - 单进程批量版本
从日线数据计算所有技术指标并存储到数据库
"""
import sys
import os

# 设置工作目录
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

# 加载环境变量
from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

import pandas as pd
import numpy as np
from loguru import logger
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy import text

from app.core.database import SessionLocal, engine
from app.models.indicator import DailyIndicator
from app.core.logging import setup_logging

# 初始化日志配置
setup_logging()


# ============== 技术指标计算函数 ==============

def calculate_ma(df: pd.DataFrame, periods: list = [5, 10, 20, 30, 60, 120, 250]) -> pd.DataFrame:
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

    df['k_value'] = rsv.ewm(alpha=1/m1, adjust=False).mean()
    df['d_value'] = df['k_value'].ewm(alpha=1/m2, adjust=False).mean()
    df['j_value'] = 3 * df['k_value'] - 2 * df['d_value']

    return df


def calculate_rsi(df: pd.DataFrame, periods: list = [6, 12, 24]) -> pd.DataFrame:
    """计算RSI指标"""
    for n in periods:
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = (-delta).where(delta < 0, 0)

        avg_gain = gain.rolling(window=n, min_periods=n).mean()
        avg_loss = loss.rolling(window=n, min_periods=n).mean()

        # 正确处理 avg_loss = 0 的情况
        # 当 avg_loss = 0 且 avg_gain > 0 时，RSI = 100（全部上涨）
        # 当 avg_loss = 0 且 avg_gain = 0 时，RSI = 50（没有变化）
        rs = np.where(avg_loss == 0,
                      np.where(avg_gain == 0, 1, np.inf),  # 无变化时 rs=1 得 RSI=50，有上涨时 rs=inf 得 RSI=100
                      avg_gain / avg_loss)
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
    std = df['close'].rolling(window=n, min_periods=n).std(ddof=0)
    df['boll_upper'] = df['boll_mid'] + k * std
    df['boll_lower'] = df['boll_mid'] - k * std

    df['boll_position'] = (df['close'] - df['boll_lower']) / (df['boll_upper'] - df['boll_lower'])
    df['boll_width'] = (df['boll_upper'] - df['boll_lower']) / df['boll_mid']

    return df


def calculate_cci(df: pd.DataFrame, n: int = 14) -> pd.DataFrame:
    """计算CCI指标"""
    tp = (df['high'] + df['low'] + df['close']) / 3
    ma = tp.rolling(window=n, min_periods=n).mean()
    md = tp.rolling(window=n, min_periods=n).apply(lambda x: np.abs(x - x.mean()).mean())
    df['cci'] = (tp - ma) / (0.015 * md)
    return df


def calculate_wr(df: pd.DataFrame, periods: list = [10, 14]) -> pd.DataFrame:
    """计算威廉指标"""
    for n in periods:
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
    df['obv_ma10'] = df['obv'].rolling(window=10, min_periods=10).mean()
    return df


def calculate_ma_deviation(df: pd.DataFrame) -> pd.DataFrame:
    """计算均线偏离度"""
    for n in [5, 10, 20, 30, 60, 120, 250]:
        if f'ma{n}' in df.columns:
            df[f'ma{n}_deviation'] = (df['close'] - df[f'ma{n}']) / df[f'ma{n}']

    def check_ma_alignment(row):
        mas = [row.get(f'ma{n}', np.nan) for n in [5, 10, 20, 30, 60]]
        if any(np.isnan(mas)):
            return 0
        if all(mas[i] > mas[i+1] for i in range(len(mas)-1)):
            return 1
        if all(mas[i] < mas[i+1] for i in range(len(mas)-1)):
            return -1
        return 0

    df['ma_alignment'] = df.apply(check_ma_alignment, axis=1)
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

    # 距60日高点回撤
    df['high_60d'] = df['high'].rolling(window=60, min_periods=1).max()
    df['drawdown_60d'] = (df['close'] - df['high_60d']) / df['high_60d']

    # 距20日低点反弹
    df['low_20d'] = df['low'].rolling(window=20, min_periods=1).min()
    df['rebound_20d'] = (df['close'] - df['low_20d']) / df['low_20d']

    # 距60日低点反弹
    df['low_60d'] = df['low'].rolling(window=60, min_periods=1).min()
    df['rebound_60d'] = (df['close'] - df['low_60d']) / df['low_60d']

    # 振幅
    df['amplitude'] = (df['high'] - df['low']) / df['close'].shift(1)

    # 涨跌幅
    df['pct_change'] = df['close'].pct_change()
    df['pct_change_5d'] = df['close'].pct_change(5)
    df['pct_change_10d'] = df['close'].pct_change(10)
    df['pct_change_20d'] = df['close'].pct_change(20)

    return df


def calculate_volume_factors(df: pd.DataFrame) -> pd.DataFrame:
    """计算成交量因子"""
    df['vol_ma5'] = df['vol'].rolling(window=5, min_periods=5).mean()
    df['vol_ma10'] = df['vol'].rolling(window=10, min_periods=10).mean()
    df['vol_ma20'] = df['vol'].rolling(window=20, min_periods=20).mean()

    df['vol_ratio'] = df['vol'] / df['vol_ma5']
    df['vol_ratio_10'] = df['vol'] / df['vol_ma10']

    return df


def calculate_atr(df: pd.DataFrame, n: int = 14) -> pd.DataFrame:
    """计算ATR (真实波动幅度)"""
    high = df['high']
    low = df['low']
    close = df['close'].shift(1)

    tr1 = high - low
    tr2 = abs(high - close)
    tr3 = abs(low - close)

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df['atr14'] = tr.rolling(window=n, min_periods=n).mean()

    return df


def calculate_dma(df: pd.DataFrame) -> pd.DataFrame:
    """计算DMA (平行线差指标)"""
    ma10 = df['close'].rolling(window=10, min_periods=10).mean()
    ma50 = df['close'].rolling(window=50, min_periods=50).mean()

    df['dma_dif'] = ma10 - ma50
    df['dma_ama'] = df['dma_dif'].rolling(window=10, min_periods=10).mean()

    return df


def calculate_vr(df: pd.DataFrame, n: int = 26) -> pd.DataFrame:
    """计算VR (成交量比率)"""
    close = df['close']
    vol = df['vol']

    # 上涨日成交量
    up_vol = vol.where(close > close.shift(1), 0)
    # 下跌日成交量
    down_vol = vol.where(close < close.shift(1), 0)
    # 平盘日成交量
    equal_vol = vol.where(close == close.shift(1), 0)

    up_sum = up_vol.rolling(window=n, min_periods=n).sum()
    down_sum = down_vol.rolling(window=n, min_periods=n).sum()
    equal_sum = equal_vol.rolling(window=n, min_periods=n).sum()

    df['vr'] = (up_sum + equal_sum / 2) / (down_sum + equal_sum / 2) * 100

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
    df = calculate_ma_deviation(df)
    df = calculate_price_factors(df)
    df = calculate_volume_factors(df)
    df = calculate_atr(df)
    df = calculate_dma(df)
    df = calculate_vr(df)
    return df


def run_indicator_calculation(batch_size: int = 100):
    """
    运行指标预计算 - 单进程批量版本

    Args:
        batch_size: 每批处理的股票数量
    """
    logger.info("=" * 60)
    logger.info("技术指标预计算 (单进程批量版本)")
    logger.info("=" * 60)

    start_time = datetime.now()

    # 1. 获取所有股票代码
    db = SessionLocal()
    result = db.execute(text("SELECT DISTINCT ts_code FROM daily_data ORDER BY ts_code"))
    stock_codes = [row[0] for row in result.fetchall()]
    db.close()

    total_stocks = len(stock_codes)
    logger.info(f"待处理股票数: {total_stocks}")

    # 2. 批量处理
    success_count = 0
    error_count = 0
    skipped_count = 0
    total_records = 0

    for batch_start in range(0, total_stocks, batch_size):
        batch_end = min(batch_start + batch_size, total_stocks)
        batch_codes = stock_codes[batch_start:batch_end]

        db = SessionLocal()

        for ts_code in batch_codes:
            try:
                # 获取该股票的所有日线数据
                query = text("""
                    SELECT ts_code, trade_date, open, high, low, close, vol
                    FROM daily_data
                    WHERE ts_code = :ts_code
                    ORDER BY trade_date ASC
                """)
                df = pd.read_sql(query, db.bind, params={'ts_code': ts_code})

                if len(df) < 60:
                    skipped_count += 1
                    continue

                # 计算所有指标
                df = calculate_all_indicators(df)

                # 删除旧数据
                db.execute(text("DELETE FROM daily_indicator WHERE ts_code = :ts_code"), {'ts_code': ts_code})

                # 准备插入数据
                indicator_columns = [
                    'ts_code', 'trade_date',
                    'k_value', 'd_value', 'j_value',
                    'rsi6', 'rsi12', 'rsi24',
                    'macd_dif', 'macd_dea', 'macd_hist',
                    'boll_upper', 'boll_mid', 'boll_lower', 'boll_width', 'boll_position',
                    'ma5', 'ma10', 'ma20', 'ma30', 'ma60', 'ma120', 'ma250',
                    'ma5_deviation', 'ma10_deviation', 'ma20_deviation', 'ma30_deviation', 'ma60_deviation', 'ma120_deviation', 'ma250_deviation',
                    'ma_alignment',
                    'cci', 'wr10', 'wr14',
                    'obv', 'obv_ma5', 'obv_ma10',
                    'vol_ma5', 'vol_ma10', 'vol_ma20', 'vol_ratio', 'vol_ratio_10',
                    'consecutive_down', 'consecutive_up',
                    'drawdown_20d', 'drawdown_60d', 'rebound_20d', 'rebound_60d',
                    'amplitude', 'pct_change', 'pct_change_5d', 'pct_change_10d', 'pct_change_20d',
                    'atr14', 'dma_dif', 'dma_ama', 'vr'
                ]

                available_columns = [col for col in indicator_columns if col in df.columns]
                df_insert = df[available_columns].copy()

                # 正确处理 NaN 值：使用 replace 方法
                df_insert = df_insert.replace({np.nan: None})

                records = df_insert.to_dict('records')
                if records:
                    try:
                        db.bulk_insert_mappings(DailyIndicator, records)
                        db.commit()
                        total_records += len(records)
                    except Exception as insert_error:
                        db.rollback()
                        raise insert_error

                success_count += 1

            except Exception as e:
                db.rollback()
                error_count += 1
                logger.error(f"处理失败: {ts_code} - {e}")

        db.close()

        # 进度日志
        elapsed = (datetime.now() - start_time).total_seconds()
        speed = batch_end / elapsed if elapsed > 0 else 0
        remaining = (total_stocks - batch_end) / speed if speed > 0 else 0
        logger.info(
            f"进度: {batch_end}/{total_stocks} ({batch_end*100/total_stocks:.1f}%) | "
            f"成功: {success_count} | 跳过: {skipped_count} | 错误: {error_count} | "
            f"速度: {speed:.1f}股/秒 | 剩余: {remaining:.0f}秒"
        )

    # 3. 统计结果
    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info("-" * 60)
    logger.info("计算完成!")
    logger.info(f"总耗时: {elapsed:.1f}秒")
    logger.info(f"成功: {success_count}, 跳过: {skipped_count}, 错误: {error_count}")
    logger.info(f"总记录数: {total_records}")
    logger.info("=" * 60)

    return {
        'success': success_count,
        'skipped': skipped_count,
        'error': error_count,
        'total_records': total_records,
        'elapsed_seconds': elapsed
    }


def run_incremental_calculation(days: int = 30, batch_size: int = 100):
    """
    增量计算 - 只更新最近N天有新数据的股票

    Args:
        days: 检查最近N天的数据更新
        batch_size: 每批处理的股票数量
    """
    logger.info("=" * 60)
    logger.info(f"技术指标增量计算 (最近{days}天)")
    logger.info("=" * 60)

    start_time = datetime.now()

    # 计算检查的起始日期
    check_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

    # 1. 获取最近N天有新日线数据的股票
    db = SessionLocal()
    result = db.execute(text("""
        SELECT DISTINCT ts_code
        FROM daily_data
        WHERE trade_date >= :check_date
        ORDER BY ts_code
    """), {'check_date': check_date})
    stock_codes = [row[0] for row in result.fetchall()]
    db.close()

    total_stocks = len(stock_codes)
    logger.info(f"待处理股票数: {total_stocks} (有新数据的股票)")

    if total_stocks == 0:
        logger.info("没有需要更新的股票")
        return {'success': 0, 'skipped': 0, 'error': 0, 'total_records': 0, 'elapsed_seconds': 0}

    # 2. 批量处理
    success_count = 0
    error_count = 0
    skipped_count = 0
    total_records = 0

    for batch_start in range(0, total_stocks, batch_size):
        batch_end = min(batch_start + batch_size, total_stocks)
        batch_codes = stock_codes[batch_start:batch_end]

        db = SessionLocal()

        for ts_code in batch_codes:
            try:
                # 获取该股票的所有日线数据（需要全部数据来计算指标）
                query = text("""
                    SELECT ts_code, trade_date, open, high, low, close, vol
                    FROM daily_data
                    WHERE ts_code = :ts_code
                    ORDER BY trade_date ASC
                """)
                df = pd.read_sql(query, db.bind, params={'ts_code': ts_code})

                if len(df) < 60:
                    skipped_count += 1
                    continue

                # 计算所有指标
                df = calculate_all_indicators(df)

                # 只删除并重新插入该股票的指标数据
                db.execute(text("DELETE FROM daily_indicator WHERE ts_code = :ts_code"), {'ts_code': ts_code})

                # 准备插入数据
                indicator_columns = [
                    'ts_code', 'trade_date',
                    'k_value', 'd_value', 'j_value',
                    'rsi6', 'rsi12', 'rsi24',
                    'macd_dif', 'macd_dea', 'macd_hist',
                    'boll_upper', 'boll_mid', 'boll_lower', 'boll_width', 'boll_position',
                    'ma5', 'ma10', 'ma20', 'ma30', 'ma60', 'ma120', 'ma250',
                    'ma5_deviation', 'ma10_deviation', 'ma20_deviation', 'ma30_deviation', 'ma60_deviation', 'ma120_deviation', 'ma250_deviation',
                    'ma_alignment',
                    'cci', 'wr10', 'wr14',
                    'obv', 'obv_ma5', 'obv_ma10',
                    'vol_ma5', 'vol_ma10', 'vol_ma20', 'vol_ratio', 'vol_ratio_10',
                    'consecutive_down', 'consecutive_up',
                    'drawdown_20d', 'drawdown_60d', 'rebound_20d', 'rebound_60d',
                    'amplitude', 'pct_change', 'pct_change_5d', 'pct_change_10d', 'pct_change_20d',
                    'atr14', 'dma_dif', 'dma_ama', 'vr'
                ]

                available_columns = [col for col in indicator_columns if col in df.columns]
                df_insert = df[available_columns].copy()
                df_insert = df_insert.replace({np.nan: None})

                records = df_insert.to_dict('records')
                if records:
                    try:
                        db.bulk_insert_mappings(DailyIndicator, records)
                        db.commit()
                        total_records += len(records)
                    except Exception as insert_error:
                        db.rollback()
                        raise insert_error

                success_count += 1

            except Exception as e:
                db.rollback()
                error_count += 1
                logger.error(f"处理失败: {ts_code} - {e}")

        db.close()

        # 进度日志
        elapsed = (datetime.now() - start_time).total_seconds()
        speed = batch_end / elapsed if elapsed > 0 else 0
        remaining = (total_stocks - batch_end) / speed if speed > 0 else 0
        logger.info(
            f"进度: {batch_end}/{total_stocks} ({batch_end*100/total_stocks:.1f}%) | "
            f"成功: {success_count} | 跳过: {skipped_count} | 错误: {error_count} | "
            f"速度: {speed:.1f}股/秒 | 剩余: {remaining:.0f}秒"
        )

    # 3. 统计结果
    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info("-" * 60)
    logger.info("增量计算完成!")
    logger.info(f"总耗时: {elapsed:.1f}秒")
    logger.info(f"成功: {success_count}, 跳过: {skipped_count}, 错误: {error_count}")
    logger.info(f"总记录数: {total_records}")
    logger.info("=" * 60)

    return {
        'success': success_count,
        'skipped': skipped_count,
        'error': error_count,
        'total_records': total_records,
        'elapsed_seconds': elapsed
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='技术指标预计算')
    parser.add_argument('--incremental', action='store_true', help='增量更新模式')
    parser.add_argument('--days', type=int, default=30, help='增量更新检查天数')
    parser.add_argument('--batch-size', type=int, default=50, help='每批处理的股票数量')

    args = parser.parse_args()

    if args.incremental:
        run_incremental_calculation(days=args.days, batch_size=args.batch_size)
    else:
        run_indicator_calculation(batch_size=args.batch_size)
