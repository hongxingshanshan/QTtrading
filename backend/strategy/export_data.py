"""
导出回测所需数据到本地文件
"""
import sys
sys.path.insert(0, '.')

import pandas as pd
import numpy as np
from loguru import logger
from sqlalchemy import text
from app.core.database import SessionLocal
import os


def export_data(start_date: str = '20250425', end_date: str = '20260424'):
    """导出日线数据到本地"""

    os.makedirs('strategy/data', exist_ok=True)

    db = SessionLocal()

    # 1. 导出股票列表
    logger.info("导出股票列表...")
    result = db.execute(text("""
        SELECT ts_code, name FROM stock_basic_info
        WHERE name NOT LIKE '%ST%'
        AND name NOT LIKE '%*ST%'
        AND ts_code NOT LIKE '688%'
        AND ts_code NOT LIKE '8%'
        AND ts_code NOT LIKE '4%'
        AND list_status = 'L'
    """)).fetchall()

    stocks_df = pd.DataFrame(result, columns=['ts_code', 'name'])
    stocks_df.to_csv('strategy/data/stocks.csv', index=False)
    logger.info(f"股票列表: {len(stocks_df)} 只")

    # 2. 导出交易日
    logger.info("导出交易日...")
    result = db.execute(text("""
        SELECT DISTINCT trade_date FROM daily_data
        WHERE trade_date >= :start_date AND trade_date <= :end_date
        ORDER BY trade_date
    """), {"start_date": start_date, "end_date": end_date}).fetchall()

    trade_dates = [r[0] for r in result]
    pd.DataFrame({'trade_date': trade_dates}).to_csv('strategy/data/trade_dates.csv', index=False)
    logger.info(f"交易日: {len(trade_dates)} 天")

    # 3. 导出日线数据（一次性查询所有股票）
    logger.info("导出日线数据...")
    result = db.execute(text("""
        SELECT d.ts_code, d.trade_date, d.open, d.high, d.low, d.close, d.vol,
               COALESCE(a.adj_factor, 1) as adj_factor
        FROM daily_data d
        LEFT JOIN adj_factor a ON d.ts_code = a.ts_code AND d.trade_date = a.trade_date
        WHERE d.trade_date >= :start_date AND d.trade_date <= :end_date
        AND d.ts_code IN (
            SELECT ts_code FROM stock_basic_info
            WHERE name NOT LIKE '%ST%'
            AND name NOT LIKE '%*ST%'
            AND ts_code NOT LIKE '688%'
            AND ts_code NOT LIKE '8%'
            AND ts_code NOT LIKE '4%'
            AND list_status = 'L'
        )
        ORDER BY d.ts_code, d.trade_date
    """), {"start_date": start_date, "end_date": end_date})

    daily_df = pd.DataFrame(result.fetchall(),
                            columns=['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'vol', 'adj_factor'])

    # 转换数据类型
    for col in ['open', 'high', 'low', 'close', 'vol', 'adj_factor']:
        daily_df[col] = pd.to_numeric(daily_df[col], errors='coerce')

    # 成交量四舍五入为整数
    daily_df['vol'] = daily_df['vol'].round().astype(int)

    # 应用前复权（按股票分组）
    logger.info("应用前复权...")
    daily_df = daily_df.sort_values(['ts_code', 'trade_date'])

    def apply_adj(group):
        latest_adj = group['adj_factor'].iloc[-1]
        group['open'] = group['open'] * group['adj_factor'] / latest_adj
        group['high'] = group['high'] * group['adj_factor'] / latest_adj
        group['low'] = group['low'] * group['adj_factor'] / latest_adj
        group['close'] = group['close'] * group['adj_factor'] / latest_adj
        return group

    daily_df = daily_df.groupby('ts_code', group_keys=False).apply(apply_adj)

    # 确保 trade_date 保持字符串格式
    daily_df['trade_date'] = daily_df['trade_date'].astype(str)

    # 保存
    daily_df.to_pickle('strategy/data/daily_data.pkl')
    logger.info(f"日线数据: {len(daily_df)} 条")

    db.close()

    logger.info("导出完成！")
    logger.info("文件列表:")
    logger.info("  - strategy/data/stocks.csv")
    logger.info("  - strategy/data/trade_dates.csv")
    logger.info("  - strategy/data/daily_data.pkl")

    return daily_df


if __name__ == "__main__":
    export_data()
