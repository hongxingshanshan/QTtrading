"""
数据校验：对比数据库数据和本地文件数据，确保一致性
"""
import sys
sys.path.insert(0, '.')

import pandas as pd
import numpy as np
from loguru import logger
from sqlalchemy import text
from app.core.database import SessionLocal


def validate_data():
    """验证数据库数据和本地文件数据的一致性"""
    logger.info("开始数据校验...")

    db = SessionLocal()

    # 1. 校验股票列表
    logger.info("=" * 50)
    logger.info("校验股票列表...")

    # 从数据库获取
    db_result = db.execute(text("""
        SELECT ts_code, name FROM stock_basic_info
        WHERE name NOT LIKE '%ST%'
        AND name NOT LIKE '%*ST%'
        AND ts_code NOT LIKE '688%'
        AND ts_code NOT LIKE '8%'
        AND ts_code NOT LIKE '4%'
        AND list_status = 'L'
    """)).fetchall()
    db_stocks = pd.DataFrame(db_result, columns=['ts_code', 'name'])

    # 从文件获取
    file_stocks = pd.read_csv('strategy/data/stocks.csv')

    logger.info(f"数据库股票数: {len(db_stocks)}")
    logger.info(f"文件股票数: {len(file_stocks)}")

    # 对比
    stocks_match = db_stocks['ts_code'].tolist() == file_stocks['ts_code'].tolist()
    if stocks_match:
        logger.info("✓ 股票列表完全一致")
    else:
        diff = set(db_stocks['ts_code']) - set(file_stocks['ts_code'])
        logger.warning(f"✗ 股票列表不一致，差异: {len(diff)} 只")

    # 2. 校验交易日
    logger.info("=" * 50)
    logger.info("校验交易日...")

    db_result = db.execute(text("""
        SELECT DISTINCT trade_date FROM daily_data
        WHERE trade_date >= '20250425' AND trade_date <= '20260424'
        ORDER BY trade_date
    """)).fetchall()
    db_dates = [r[0] for r in db_result]

    file_dates_df = pd.read_csv('strategy/data/trade_dates.csv')
    file_dates = pd.to_datetime(file_dates_df['trade_date']).tolist()

    logger.info(f"数据库交易日数: {len(db_dates)}")
    logger.info(f"文件交易日数: {len(file_dates)}")

    dates_match = len(db_dates) == len(file_dates)
    if dates_match:
        logger.info("✓ 交易日数量一致")
    else:
        logger.warning(f"✗ 交易日数量不一致")

    # 3. 抽样校验日线数据
    logger.info("=" * 50)
    logger.info("抽样校验日线数据...")

    # 从文件加载日线数据
    file_daily = pd.read_pickle('strategy/data/daily_data.pkl')
    logger.info(f"文件日线数据: {len(file_daily)} 条")

    # 抽样几只股票进行详细对比
    sample_stocks = ['000001.SZ', '600000.SH', '300001.SZ', '000002.SZ', '600519.SH']

    all_match = True
    for ts_code in sample_stocks:
        logger.info(f"\n校验股票: {ts_code}")

        # 从数据库获取
        db_result = db.execute(text("""
            SELECT d.trade_date, d.open, d.high, d.low, d.close, d.vol,
                   COALESCE(a.adj_factor, 1) as adj_factor
            FROM daily_data d
            LEFT JOIN adj_factor a ON d.ts_code = a.ts_code AND d.trade_date = a.trade_date
            WHERE d.ts_code = :ts_code
            AND d.trade_date >= '20250425' AND d.trade_date <= '20260424'
            ORDER BY d.trade_date
        """), {"ts_code": ts_code}).fetchall()

        if not db_result:
            logger.warning(f"  数据库无数据")
            continue

        db_df = pd.DataFrame(db_result, columns=['trade_date', 'open', 'high', 'low', 'close', 'vol', 'adj_factor'])
        for col in ['open', 'high', 'low', 'close', 'adj_factor']:
            db_df[col] = pd.to_numeric(db_df[col], errors='coerce')
        db_df['vol'] = pd.to_numeric(db_df['vol'], errors='coerce').round().astype(int)

        # 应用前复权（数据库数据）
        latest_adj_db = db_df['adj_factor'].iloc[-1]
        db_df['open_adj'] = db_df['open'] * db_df['adj_factor'] / latest_adj_db
        db_df['high_adj'] = db_df['high'] * db_df['adj_factor'] / latest_adj_db
        db_df['low_adj'] = db_df['low'] * db_df['adj_factor'] / latest_adj_db
        db_df['close_adj'] = db_df['close'] * db_df['adj_factor'] / latest_adj_db

        # 从文件获取
        file_df = file_daily[file_daily['ts_code'] == ts_code].copy()
        file_df = file_df.sort_values('trade_date')

        if len(db_df) != len(file_df):
            logger.warning(f"  数据条数不一致: DB={len(db_df)}, File={len(file_df)}")
            all_match = False
            continue

        logger.info(f"  数据条数: {len(db_df)}")

        # 对比复权后的价格
        tolerance = 1e-4  # 允许的误差

        for i in range(min(5, len(db_df))):
            db_row = db_df.iloc[i]
            file_row = file_df.iloc[i]

            # 检查日期（统一转为字符串比较）
            db_date = str(db_row['trade_date'])
            file_date = str(file_row['trade_date']).replace('-', '')
            if db_date != file_date:
                logger.warning(f"  日期不一致: {db_date} vs {file_date}")
                all_match = False

            # 检查复权后价格
            price_cols = ['open', 'high', 'low', 'close']
            for col in price_cols:
                db_val = db_row[f'{col}_adj']
                file_val = file_row[col]
                diff = abs(db_val - file_val)
                if diff > tolerance:
                    logger.warning(f"  {col}不一致: DB={db_val:.4f}, File={file_val:.4f}, diff={diff:.4f}")
                    all_match = False

            # 检查成交量
            vol_diff = abs(db_row['vol'] - file_row['vol'])
            if vol_diff > tolerance:
                logger.warning(f"  vol不一致: DB={db_row['vol']:.2f}, File={file_row['vol']:.2f}")
                all_match = False

        if all_match:
            logger.info(f"  ✓ 抽样数据一致")

    # 4. 统计对比
    logger.info("=" * 50)
    logger.info("统计对比...")

    # 数据库统计
    db_count = db.execute(text("""
        SELECT COUNT(*) FROM daily_data
        WHERE trade_date >= '20250425' AND trade_date <= '20260424'
        AND ts_code IN (
            SELECT ts_code FROM stock_basic_info
            WHERE name NOT LIKE '%ST%'
            AND name NOT LIKE '%*ST%'
            AND ts_code NOT LIKE '688%'
            AND ts_code NOT LIKE '8%'
            AND ts_code NOT LIKE '4%'
            AND list_status = 'L'
        )
    """)).fetchone()[0]

    logger.info(f"数据库日线数据条数: {db_count}")
    logger.info(f"文件日线数据条数: {len(file_daily)}")

    count_match = db_count == len(file_daily)
    if count_match:
        logger.info("✓ 数据条数完全一致")
    else:
        logger.warning(f"✗ 数据条数不一致，差异: {abs(db_count - len(file_daily))}")

    db.close()

    # 总结
    logger.info("=" * 50)
    logger.info("校验总结:")
    logger.info(f"  股票列表: {'一致' if stocks_match else '不一致'}")
    logger.info(f"  交易日: {'一致' if dates_match else '不一致'}")
    logger.info(f"  抽样数据: {'一致' if all_match else '不一致'}")
    logger.info(f"  数据条数: {'一致' if count_match else '不一致'}")

    if stocks_match and dates_match and all_match and count_match:
        logger.info("✓✓✓ 所有校验通过，可以安全切换数据源！")
        return True
    else:
        logger.warning("✗✗✗ 校验未完全通过，请检查数据导出流程")
        return False


if __name__ == "__main__":
    validate_data()