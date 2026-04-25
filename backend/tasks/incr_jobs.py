"""增量任务 - 交易日执行"""
from datetime import datetime, timedelta
from loguru import logger
from tqdm import tqdm
from sqlalchemy import text
from app.core.database import SessionLocal
from .tushare_client import pro


def import_daily_limit_data(start_date: str, end_date: str):
    """获取每日涨跌停数据"""
    logger.info(f"开始导入涨跌停数据: {start_date} ~ {end_date}")

    try:
        db = SessionLocal()
        try:
            limit = 1000
            offset = 0

            while True:
                df = pro.limit_list_d(
                    start_date=start_date, end_date=end_date,
                    limit=limit, offset=offset,
                    fields='trade_date,ts_code,industry,name,close,pct_chg,amount,limit_amount,float_mv,total_mv,turnover_ratio,fd_amount,first_time,last_time,open_times,up_stat,limit_times,limit'
                )

                if df.empty:
                    break

                df = df.fillna(None)
                data = df.to_dict(orient='records')

                for record in data:
                    record['limit_status'] = record.pop('limit')
                    db.execute(text("""
                        INSERT INTO daily_limit_data
                        (trade_date, ts_code, industry, name, close, pct_chg, amount, limit_amount,
                         float_mv, total_mv, turnover_ratio, fd_amount, first_time, last_time,
                         open_times, up_stat, limit_times, limit_status)
                        VALUES (:trade_date, :ts_code, :industry, :name, :close, :pct_chg, :amount,
                                :limit_amount, :float_mv, :total_mv, :turnover_ratio, :fd_amount,
                                :first_time, :last_time, :open_times, :up_stat, :limit_times, :limit_status)
                        ON DUPLICATE KEY UPDATE
                            industry=VALUES(industry), name=VALUES(name), close=VALUES(close),
                            pct_chg=VALUES(pct_chg), amount=VALUES(amount), limit_amount=VALUES(limit_amount),
                            float_mv=VALUES(float_mv), total_mv=VALUES(total_mv),
                            turnover_ratio=VALUES(turnover_ratio), fd_amount=VALUES(fd_amount),
                            first_time=VALUES(first_time), last_time=VALUES(last_time),
                            open_times=VALUES(open_times), up_stat=VALUES(up_stat),
                            limit_times=VALUES(limit_times), limit_status=VALUES(limit_status)
                    """), record)

                db.commit()
                offset += limit

            logger.info(f"涨跌停数据导入完成")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"导入涨跌停数据出错: {e}")


def import_hm_detail_data(start_date: str, end_date: str):
    """获取每日游资交易数据"""
    logger.info(f"开始导入游资交易数据: {start_date} ~ {end_date}")

    try:
        db = SessionLocal()
        try:
            limit = 2000
            offset = 0

            while True:
                df = pro.hm_detail(
                    trade_date=start_date, limit=limit, offset=offset,
                    fields='trade_date,ts_code,ts_name,buy_amount,sell_amount,net_amount,hm_name,hm_orgs,tag'
                )

                if df.empty:
                    break

                df = df.fillna(None)
                data = df.to_dict(orient='records')

                for record in data:
                    db.execute(text("""
                        INSERT INTO daily_hot_money_trading
                        (trade_date, ts_code, ts_name, buy_amount, sell_amount, net_amount, hm_name, hm_orgs, tag)
                        VALUES (:trade_date, :ts_code, :ts_name, :buy_amount, :sell_amount,
                                :net_amount, :hm_name, :hm_orgs, :tag)
                        ON DUPLICATE KEY UPDATE
                            ts_name=VALUES(ts_name), buy_amount=VALUES(buy_amount),
                            sell_amount=VALUES(sell_amount), net_amount=VALUES(net_amount),
                            hm_name=VALUES(hm_name), hm_orgs=VALUES(hm_orgs), tag=VALUES(tag)
                    """), record)

                db.commit()
                offset += limit

            logger.info(f"游资交易数据导入完成")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"导入游资交易数据出错: {e}")


def import_daily_sector_limit_data(start_date: str, end_date: str):
    """计算板块涨跌停数据"""
    logger.info(f"开始计算板块涨跌停数据: {start_date} ~ {end_date}")

    try:
        db = SessionLocal()
        try:
            db.execute(text("""
                INSERT INTO daily_sector_limit_data
                (sector_code, sector_name, sector_type, trade_date, up_limit_count, down_limit_count)
                SELECT
                    ti.ts_code AS sector_code,
                    ti.name AS sector_name,
                    ti.type AS sector_type,
                    dld.trade_date,
                    SUM(CASE WHEN dld.limit_status = 'U' THEN 1 ELSE 0 END) AS up_limit_count,
                    SUM(CASE WHEN dld.limit_status = 'D' THEN 1 ELSE 0 END) AS down_limit_count
                FROM ths_index ti
                JOIN ths_member tm ON ti.ts_code = tm.ts_code
                JOIN daily_limit_data dld ON tm.con_code = dld.ts_code
                WHERE dld.trade_date >= :start_date AND dld.trade_date <= :end_date
                GROUP BY ti.ts_code, ti.name, ti.type, dld.trade_date
                ON DUPLICATE KEY UPDATE
                    sector_name=VALUES(sector_name), sector_type=VALUES(sector_type),
                    up_limit_count=VALUES(up_limit_count), down_limit_count=VALUES(down_limit_count)
            """), {"start_date": start_date, "end_date": end_date})
            db.commit()
            logger.info(f"板块涨跌停数据计算完成")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"计算板块涨跌停数据出错: {e}")


def import_all_daily_data(start_date: str, end_date: str):
    """导入所有股票日线数据"""
    logger.info(f"开始导入所有股票日线数据: {start_date} ~ {end_date}")

    try:
        db = SessionLocal()
        try:
            # 获取所有股票
            result = db.execute(text("SELECT ts_code, list_date FROM stock_basic_info"))
            stocks = result.fetchall()

            start_dt = datetime.strptime(start_date, '%Y%m%d').date()

            for idx, stock in enumerate(stocks):
                ts_code = stock[0]
                list_date = stock[1]

                if idx % 500 == 0:
                    logger.info(f"日线数据导入进度: {idx}/{len(stocks)}")

                # 确定起始日期
                current_start = start_date
                if list_date and start_dt < list_date:
                    current_start = list_date.strftime('%Y%m%d')

                # 拉取日线数据
                offset = 0
                limit = 6000

                while True:
                    df = pro.daily(
                        ts_code=ts_code,
                        start_date=current_start, end_date=end_date,
                        offset=offset, limit=limit
                    )

                    if df.empty:
                        break

                    df = df.fillna(None)
                    data = df.to_dict(orient='records')

                    for record in data:
                        record['price_change'] = record.pop('change')
                        db.execute(text("""
                            INSERT INTO daily_data
                            (ts_code, trade_date, open, high, low, close, pre_close,
                             price_change, pct_chg, vol, amount)
                            VALUES (:ts_code, :trade_date, :open, :high, :low, :close,
                                    :pre_close, :price_change, :pct_chg, :vol, :amount)
                            ON DUPLICATE KEY UPDATE
                                open=VALUES(open), high=VALUES(high), low=VALUES(low),
                                close=VALUES(close), pre_close=VALUES(pre_close),
                                price_change=VALUES(price_change), pct_chg=VALUES(pct_chg),
                                vol=VALUES(vol), amount=VALUES(amount)
                        """), record)

                    db.commit()
                    offset += limit

            logger.info(f"所有股票日线数据导入完成")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"导入日线数据出错: {e}")


def run_incr_jobs():
    """运行所有增量任务"""
    today = datetime.now().strftime('%Y%m%d')
    logger.info(f"========== 开始执行增量任务 ({today}) ==========")

    import_daily_limit_data(today, today)
    import_hm_detail_data(today, today)
    import_daily_sector_limit_data(today, today)
    import_all_daily_data(today, today)

    logger.info("========== 增量任务执行完成 ==========")
