"""复权因子同步任务"""
from datetime import datetime
from loguru import logger
from sqlalchemy import text
from app.core.database import SessionLocal
from .tushare_client import pro


def sync_adj_factors(start_date: str, end_date: str):
    """同步所有股票的复权因子"""
    logger.info(f"开始同步复权因子: {start_date} ~ {end_date}")

    try:
        db = SessionLocal()
        try:
            # 获取所有股票
            result = db.execute(text("SELECT ts_code FROM stock_basic_info"))
            stocks = result.fetchall()

            total = len(stocks)
            for idx, stock in enumerate(stocks):
                ts_code = stock[0]

                if idx % 500 == 0:
                    logger.info(f"复权因子同步进度: {idx}/{total}")

                try:
                    df = pro.adj_factor(ts_code=ts_code, start_date=start_date, end_date=end_date)

                    if df.empty:
                        continue

                    df = df.fillna(None)
                    data = df.to_dict(orient='records')

                    for record in data:
                        db.execute(text("""
                            INSERT INTO adj_factor (ts_code, trade_date, adj_factor)
                            VALUES (:ts_code, :trade_date, :adj_factor)
                            ON DUPLICATE KEY UPDATE adj_factor=VALUES(adj_factor)
                        """), record)

                    db.commit()
                except Exception as e:
                    logger.warning(f"同步 {ts_code} 复权因子失败: {e}")
                    continue

            logger.info(f"复权因子同步完成")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"同步复权因子出错: {e}")


def run_adj_factor_job():
    """运行复权因子同步任务"""
    today = datetime.now().strftime('%Y%m%d')
    logger.info(f"========== 开始同步复权因子 ({today}) ==========")

    sync_adj_factors('19000101', today)

    logger.info("========== 复权因子同步完成 ==========")
