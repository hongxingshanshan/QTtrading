"""初始化任务 - 每天凌晨3点执行"""
from loguru import logger
from tqdm import tqdm
from sqlalchemy import text
from app.core.database import SessionLocal
from .tushare_client import pro


def import_stock_basic_info():
    """获取股票基本信息并导入stock_basic_info表"""
    logger.info("开始导入股票基本信息...")

    try:
        df = pro.stock_basic(fields=[
            "ts_code", "symbol", "name", "area", "industry", "cnspell",
            "market", "list_date", "act_name", "act_ent_type", "fullname",
            "enname", "exchange", "curr_type", "list_status", "delist_date", "is_hs"
        ])

        df = df.fillna(None)
        data = df.to_dict(orient='records')

        db = SessionLocal()
        try:
            for record in data:
                db.execute(text("""
                    INSERT INTO stock_basic_info
                    (ts_code, symbol, name, area, industry, cnspell, market,
                     list_date, act_name, act_ent_type, fullname, enname, exchange,
                     curr_type, list_status, delist_date, is_hs)
                    VALUES (:ts_code, :symbol, :name, :area, :industry, :cnspell, :market,
                            :list_date, :act_name, :act_ent_type, :fullname, :enname, :exchange,
                            :curr_type, :list_status, :delist_date, :is_hs)
                    ON DUPLICATE KEY UPDATE
                        name=VALUES(name), area=VALUES(area), industry=VALUES(industry),
                        cnspell=VALUES(cnspell), market=VALUES(market), list_date=VALUES(list_date),
                        act_name=VALUES(act_name), act_ent_type=VALUES(act_ent_type),
                        fullname=VALUES(fullname), enname=VALUES(enname), exchange=VALUES(exchange),
                        curr_type=VALUES(curr_type), list_status=VALUES(list_status),
                        delist_date=VALUES(delist_date), is_hs=VALUES(is_hs)
                """), record)
            db.commit()
            logger.info(f"股票基本信息导入完成，共 {len(data)} 条")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"导入股票基本信息出错: {e}")


def import_hot_money_info():
    """获取游资信息并导入hot_money_info表"""
    logger.info("开始导入游资信息...")

    try:
        df = pro.hm_list(fields=["name", "desc", "orgs"])
        df = df.fillna(None)
        data = df.to_dict(orient='records')

        db = SessionLocal()
        try:
            for record in data:
                db.execute(text("""
                    INSERT INTO hot_money_info (name, `desc`, orgs)
                    VALUES (:name, :desc, :orgs)
                    ON DUPLICATE KEY UPDATE
                        `desc`=VALUES(`desc`), orgs=VALUES(orgs)
                """), record)
            db.commit()
            logger.info(f"游资信息导入完成，共 {len(data)} 条")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"导入游资信息出错: {e}")


def import_ths_index_data():
    """获取同花顺概念和行业指数数据并导入ths_index表"""
    logger.info("开始导入同花顺指数数据...")

    try:
        df = pro.ths_index()
        df = df.fillna(None)
        data = df.to_dict(orient='records')

        db = SessionLocal()
        try:
            for record in data:
                db.execute(text("""
                    INSERT INTO ths_index (ts_code, name, count, exchange, list_date, type)
                    VALUES (:ts_code, :name, :count, :exchange, :list_date, :type)
                    ON DUPLICATE KEY UPDATE
                        name=VALUES(name), count=VALUES(count),
                        exchange=VALUES(exchange), list_date=VALUES(list_date), type=VALUES(type)
                """), record)
            db.commit()
            logger.info(f"同花顺指数数据导入完成，共 {len(data)} 条")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"导入同花顺指数出错: {e}")


def import_ths_member_data():
    """获取同花顺概念板块成分数据并导入ths_member表"""
    logger.info("开始导入同花顺概念板块成分数据...")

    try:
        # 获取所有板块指数代码
        ths_index_df = pro.ths_index()
        ts_codes = ths_index_df['ts_code'].tolist()

        db = SessionLocal()
        try:
            total = len(ts_codes)
            for idx, ts_code in enumerate(ts_codes):
                if idx % 50 == 0:
                    logger.info(f"导入进度: {idx}/{total}")

                offset = 0
                limit = 5000

                while True:
                    df = pro.ths_member(ts_code=ts_code, limit=limit, offset=offset)
                    if df.empty:
                        break

                    df = df.fillna(None)
                    data = df.to_dict(orient='records')

                    for record in data:
                        db.execute(text("""
                            INSERT INTO ths_member (ts_code, con_code, con_name, weight, in_date, out_date, is_new)
                            VALUES (:ts_code, :con_code, :con_name, :weight, :in_date, :out_date, :is_new)
                            ON DUPLICATE KEY UPDATE
                                con_name=VALUES(con_name), weight=VALUES(weight),
                                in_date=VALUES(in_date), out_date=VALUES(out_date), is_new=VALUES(is_new)
                        """), record)

                    db.commit()
                    offset += limit

            logger.info(f"同花顺概念板块成分数据导入完成")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"导入同花顺概念板块成分出错: {e}")


def run_init_jobs():
    """运行所有初始化任务"""
    logger.info("========== 开始执行初始化任务 ==========")

    import_hot_money_info()
    import_stock_basic_info()
    import_ths_index_data()
    import_ths_member_data()

    logger.info("========== 初始化任务执行完成 ==========")
