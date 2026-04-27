"""
每日基本面数据采集任务
数据来源: Tushare daily_basic 接口
包含: PE/PB/市值/换手率等
"""
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy import text
from app.core.database import SessionLocal
from .tushare_client import get_pro_api


def import_daily_basic(start_date: str, end_date: str):
    """
    导入每日基本面数据

    Args:
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
    """
    logger.info(f"开始导入每日基本面数据: {start_date} ~ {end_date}")

    try:
        pro = get_pro_api()
        db = SessionLocal()

        try:
            current_date = datetime.strptime(start_date, '%Y%m%d')
            end_dt = datetime.strptime(end_date, '%Y%m%d')
            imported_count = 0
            error_count = 0

            while current_date <= end_dt:
                date_str = current_date.strftime('%Y%m%d')

                # 跳过周末
                if current_date.weekday() >= 5:
                    current_date += timedelta(days=1)
                    continue

                try:
                    # 调用 Tushare daily_basic 接口
                    df = pro.daily_basic(
                        trade_date=date_str,
                        fields='ts_code,trade_date,close,turnover_rate,turnover_rate_f,'
                               'volume_ratio,pe,pe_ttm,pb,ps,ps_ttm,dv_ratio,dv_ttm,'
                               'total_share,float_share,free_share,total_mv,circ_mv'
                    )

                    if df.empty:
                        logger.debug(f"{date_str} 无基本面数据")
                        current_date += timedelta(days=1)
                        continue

                    # 处理 NaN 值 - 使用 numpy 的 nan
                    import numpy as np
                    df = df.replace({np.nan: None})
                    data = df.to_dict(orient='records')

                    # 批量插入
                    for record in data:
                        db.execute(text("""
                            INSERT INTO daily_basic
                            (ts_code, trade_date, close, turnover_rate, turnover_rate_f,
                             volume_ratio, pe, pe_ttm, pb, ps, ps_ttm, dv_ratio, dv_ttm,
                             total_share, float_share, free_share, total_mv, circ_mv)
                            VALUES (:ts_code, :trade_date, :close, :turnover_rate, :turnover_rate_f,
                                    :volume_ratio, :pe, :pe_ttm, :pb, :ps, :ps_ttm,
                                    :dv_ratio, :dv_ttm, :total_share, :float_share,
                                    :free_share, :total_mv, :circ_mv)
                            ON DUPLICATE KEY UPDATE
                                close=VALUES(close), turnover_rate=VALUES(turnover_rate),
                                turnover_rate_f=VALUES(turnover_rate_f), volume_ratio=VALUES(volume_ratio),
                                pe=VALUES(pe), pe_ttm=VALUES(pe_ttm), pb=VALUES(pb),
                                ps=VALUES(ps), ps_ttm=VALUES(ps_ttm), dv_ratio=VALUES(dv_ratio),
                                dv_ttm=VALUES(dv_ttm), total_share=VALUES(total_share),
                                float_share=VALUES(float_share), free_share=VALUES(free_share),
                                total_mv=VALUES(total_mv), circ_mv=VALUES(circ_mv)
                        """), record)

                    db.commit()
                    imported_count += len(data)

                    if imported_count % 2000 == 0:
                        logger.info(f"基本面数据导入进度: {imported_count} 条")

                except Exception as e:
                    error_count += 1
                    logger.warning(f"导入 {date_str} 基本面数据失败: {e}")

                current_date += timedelta(days=1)

            logger.info(f"每日基本面数据导入完成: 成功={imported_count}, 失败={error_count}")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"导入每日基本面数据出错: {e}")


def run_basic_incremental_job():
    """运行增量基本面数据采集（每天执行）"""
    today = datetime.now().strftime('%Y%m%d')
    logger.info(f"开始执行增量基本面数据采集 ({today})")

    import_daily_basic(today, today)

    logger.info("增量基本面数据采集完成")


def run_basic_full_job(start_date: str = None):
    """
    运行全量基本面数据采集

    Args:
        start_date: 开始日期，默认为2020年1月1日
    """
    if start_date is None:
        start_date = '20200101'

    end_date = datetime.now().strftime('%Y%m%d')
    logger.info(f"开始执行全量基本面数据采集: {start_date} ~ {end_date}")

    import_daily_basic(start_date, end_date)

    logger.info("全量基本面数据采集完成")
