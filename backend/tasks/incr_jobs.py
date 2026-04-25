"""
增量任务 - 交易日执行
日线数据、涨跌停数据、游资交易数据、复权因子
"""
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy import text
from app.core.database import SessionLocal
from .tushare_client import get_pro_api


def import_daily_data(start_date: str, end_date: str):
    """导入日线数据"""
    logger.info(f"开始导入日线数据: {start_date} ~ {end_date}")

    try:
        pro = get_pro_api()
        db = SessionLocal()
        try:
            current_date = datetime.strptime(start_date, '%Y%m%d')
            end_dt = datetime.strptime(end_date, '%Y%m%d')
            imported_count = 0
            days_count = 0

            while current_date <= end_dt:
                date_str = current_date.strftime('%Y%m%d')

                if current_date.weekday() >= 5:
                    current_date += timedelta(days=1)
                    continue

                try:
                    df = pro.daily(
                        trade_date=date_str,
                        fields='ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount'
                    )

                    if df.empty:
                        current_date += timedelta(days=1)
                        continue

                    df = df.where(pd.notna(df), None)
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
                    imported_count += len(data)
                    days_count += 1

                    if days_count % 50 == 0:
                        logger.info(f"日线数据导入进度: {days_count} 天, {imported_count} 条")

                except Exception as e:
                    logger.warning(f"导入 {date_str} 日线数据失败: {e}")

                current_date += timedelta(days=1)

            logger.info(f"日线数据导入完成，共 {days_count} 天, {imported_count} 条")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"导入日线数据出错: {e}")


def import_adj_factors(start_date: str, end_date: str):
    """导入复权因子数据"""
    logger.info(f"开始导入复权因子: {start_date} ~ {end_date}")

    try:
        pro = get_pro_api()
        db = SessionLocal()
        try:
            stocks = db.execute(text("SELECT ts_code FROM stock_basic_info")).fetchall()
            ts_codes = [s[0] for s in stocks]

            total = 0
            for i, ts_code in enumerate(ts_codes):
                try:
                    df = pro.adj_factor(ts_code=ts_code, start_date=start_date, end_date=end_date)
                    if df.empty:
                        continue

                    df = df.where(pd.notna(df), None)
                    records = df.to_dict('records')

                    for record in records:
                        db.execute(text("""
                            INSERT INTO adj_factor (ts_code, trade_date, adj_factor)
                            VALUES (:ts_code, :trade_date, :adj_factor)
                            ON DUPLICATE KEY UPDATE adj_factor=VALUES(adj_factor)
                        """), record)

                    db.commit()
                    total += len(records)

                    if (i + 1) % 500 == 0:
                        logger.info(f"复权因子进度: {i + 1}/{len(ts_codes)}, 共 {total} 条")

                except Exception as e:
                    logger.warning(f"导入 {ts_code} 复权因子失败: {e}")

            logger.info(f"复权因子导入完成, 共 {total} 条")

        finally:
            db.close()
    except Exception as e:
        logger.error(f"导入复权因子出错: {e}")


def import_daily_limit_data(start_date: str, end_date: str):
    """导入涨跌停数据"""
    logger.info(f"开始导入涨跌停数据: {start_date} ~ {end_date}")

    try:
        pro = get_pro_api()
        db = SessionLocal()
        try:
            current_date = datetime.strptime(start_date, '%Y%m%d')
            end_dt = datetime.strptime(end_date, '%Y%m%d')
            imported_count = 0

            while current_date <= end_dt:
                date_str = current_date.strftime('%Y%m%d')

                if current_date.weekday() >= 5:
                    current_date += timedelta(days=1)
                    continue

                try:
                    df = pro.limit_list_d(
                        trade_date=date_str,
                        fields='trade_date,ts_code,industry,name,close,pct_chg,amount,limit_amount,float_mv,total_mv,turnover_ratio,fd_amount,first_time,last_time,open_times,up_stat,limit_times,limit'
                    )

                    if df.empty:
                        current_date += timedelta(days=1)
                        continue

                    df = df.where(pd.notna(df), None)
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
                    imported_count += len(data)

                except Exception as e:
                    logger.warning(f"导入 {date_str} 涨跌停数据失败: {e}")

                current_date += timedelta(days=1)

            logger.info(f"涨跌停数据导入完成，共 {imported_count} 条")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"导入涨跌停数据出错: {e}")


def import_hm_detail_data(start_date: str, end_date: str):
    """导入游资交易数据"""
    logger.info(f"开始导入游资交易数据: {start_date} ~ {end_date}")

    try:
        pro = get_pro_api()
        db = SessionLocal()
        try:
            current_date = datetime.strptime(start_date, '%Y%m%d')
            end_dt = datetime.strptime(end_date, '%Y%m%d')
            imported_count = 0

            while current_date <= end_dt:
                date_str = current_date.strftime('%Y%m%d')

                if current_date.weekday() >= 5:
                    current_date += timedelta(days=1)
                    continue

                try:
                    df = pro.hm_detail(
                        trade_date=date_str,
                        fields='trade_date,ts_code,ts_name,buy_amount,sell_amount,net_amount,hm_name,hm_orgs,tag'
                    )

                    if df.empty:
                        current_date += timedelta(days=1)
                        continue

                    df = df.where(pd.notna(df), None)
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
                    imported_count += len(data)

                except Exception as e:
                    logger.warning(f"导入 {date_str} 游资交易数据失败: {e}")

                current_date += timedelta(days=1)

            logger.info(f"游资交易数据导入完成，共 {imported_count} 条")
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
            result = db.execute(text("SELECT COUNT(*) FROM ths_index"))
            count = result.scalar()
            if count == 0:
                logger.warning("ths_index 表为空，跳过板块涨跌停数据计算。需要6000积分权限导入同花顺指数数据。")
                return

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


def run_incr_jobs():
    """运行所有增量任务"""
    today = datetime.now().strftime('%Y%m%d')
    logger.info(f"========== 开始执行增量任务 ({today}) ==========")

    import_daily_data(today, today)
    import_adj_factors(today, today)
    import_daily_limit_data(today, today)
    import_hm_detail_data(today, today)
    import_daily_sector_limit_data(today, today)

    logger.info("========== 增量任务执行完成 ==========")
