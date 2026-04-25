"""
K线周期数据导入任务 - 周K线、月K线
每周/每月执行一次
"""
import pandas as pd
from datetime import datetime
from loguru import logger
from sqlalchemy import text
from app.core.database import SessionLocal
from app.models.kline import WeeklyData, MonthlyData
from .tushare_client import get_pro_api


def import_weekly_data(start_date: str = "20200101", end_date: str = None):
    """导入周K线数据"""
    if end_date is None:
        end_date = datetime.now().strftime("%Y%m%d")

    logger.info(f"开始导入周K线数据: {start_date} ~ {end_date}")

    try:
        pro = get_pro_api()
        db = SessionLocal()
        try:
            stocks = db.execute(text("SELECT ts_code FROM stock_basic_info")).fetchall()
            ts_codes = [s[0] for s in stocks]

            total = 0
            for i, ts_code in enumerate(ts_codes):
                try:
                    df = pro.weekly(ts_code=ts_code, start_date=start_date, end_date=end_date)
                    if df.empty:
                        continue

                    df = df.where(pd.notna(df), None)
                    records = df.to_dict('records')

                    for record in records:
                        db.merge(WeeklyData(
                            ts_code=record['ts_code'],
                            trade_date=record['trade_date'],
                            open=record['open'],
                            high=record['high'],
                            low=record['low'],
                            close=record['close'],
                            pre_close=record['pre_close'],
                            price_change=record['change'],
                            pct_chg=record['pct_chg'],
                            vol=record['vol'],
                            amount=record['amount'],
                        ))
                        total += 1

                    if (i + 1) % 100 == 0:
                        db.commit()
                        logger.info(f"周K线进度: {i + 1}/{len(ts_codes)}, 共 {total} 条")

                except Exception as e:
                    logger.warning(f"导入周K线 {ts_code} 失败: {e}")

            db.commit()
            logger.info(f"周K线导入完成, 共 {total} 条")

        finally:
            db.close()
    except Exception as e:
        logger.error(f"导入周K线出错: {e}")


def import_monthly_data(start_date: str = "20200101", end_date: str = None):
    """导入月K线数据"""
    if end_date is None:
        end_date = datetime.now().strftime("%Y%m%d")

    logger.info(f"开始导入月K线数据: {start_date} ~ {end_date}")

    try:
        pro = get_pro_api()
        db = SessionLocal()
        try:
            stocks = db.execute(text("SELECT ts_code FROM stock_basic_info")).fetchall()
            ts_codes = [s[0] for s in stocks]

            total = 0
            for i, ts_code in enumerate(ts_codes):
                try:
                    df = pro.monthly(ts_code=ts_code, start_date=start_date, end_date=end_date)
                    if df.empty:
                        continue

                    df = df.where(pd.notna(df), None)
                    records = df.to_dict('records')

                    for record in records:
                        db.merge(MonthlyData(
                            ts_code=record['ts_code'],
                            trade_date=record['trade_date'],
                            open=record['open'],
                            high=record['high'],
                            low=record['low'],
                            close=record['close'],
                            pre_close=record['pre_close'],
                            price_change=record['change'],
                            pct_chg=record['pct_chg'],
                            vol=record['vol'],
                            amount=record['amount'],
                        ))
                        total += 1

                    if (i + 1) % 100 == 0:
                        db.commit()
                        logger.info(f"月K线进度: {i + 1}/{len(ts_codes)}, 共 {total} 条")

                except Exception as e:
                    logger.warning(f"导入月K线 {ts_code} 失败: {e}")

            db.commit()
            logger.info(f"月K线导入完成, 共 {total} 条")

        finally:
            db.close()
    except Exception as e:
        logger.error(f"导入月K线出错: {e}")


def run_kline_jobs():
    """运行K线周期数据导入任务"""
    logger.info("========== 开始执行K线周期数据导入 ==========")

    import_weekly_data()
    import_monthly_data()

    logger.info("========== K线周期数据导入完成 ==========")
