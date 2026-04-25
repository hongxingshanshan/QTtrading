import chinadata.ca_data as ts
from backend import DataBase as db
from backend.tushare import token

# 初始化pro接口
pro = token.get_tushare().pro_api()

def import_stock_basic_info():
    """
    获取股票基本信息并导入stock_basic_info表
    """
    # 拉取数据
    df = pro.stock_basic(**{
        "ts_code": "",
        "name": "",
        "exchange": "",
        "market": "",
        "is_hs": "",
        "list_status": "",
        "limit": "",
        "offset": ""
    }, fields=[
        "ts_code",
        "symbol",
        "name",
        "area",
        "industry",
        "cnspell",
        "market",
        "list_date",
        "act_name",
        "act_ent_type",
        "fullname",
        "enname",
        "exchange",
        "curr_type",
        "list_status",
        "delist_date",
        "is_hs"
    ])
    
    data = df.to_dict(orient='records')

    # 获取数据库连接
    conn = db.get_db()
    cursor = conn.cursor()

    # 插入数据到数据库，使用主键存在覆盖逻辑
    for record in data:
        cursor.execute('''
            INSERT INTO stock_basic_info (ts_code, symbol, name, area, industry, cnspell, market, list_date, act_name, act_ent_type, fullname, enname, exchange, curr_type, list_status, delist_date, is_hs)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                ts_code=VALUES(ts_code),
                name=VALUES(name),
                area=VALUES(area),
                industry=VALUES(industry),
                cnspell=VALUES(cnspell),
                market=VALUES(market),
                list_date=VALUES(list_date),
                act_name=VALUES(act_name),
                act_ent_type=VALUES(act_ent_type),
                fullname=VALUES(fullname),
                enname=VALUES(enname),
                exchange=VALUES(exchange),
                curr_type=VALUES(curr_type),
                list_status=VALUES(list_status),
                delist_date=VALUES(delist_date),
                is_hs=VALUES(is_hs)
        ''', (
            record['ts_code'], record['symbol'], record['name'], record['area'], record['industry'], record['cnspell'], record['market'],
            record['list_date'], record['act_name'], record['act_ent_type'], record['fullname'], record['enname'], record['exchange'],
            record['curr_type'], record['list_status'], record['delist_date'], record['is_hs']
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("股票基本信息已成功导入到数据库中")

def import_hot_money_info():
    """
    获取游资信息并导入hot_money_info表
    """
    # 拉取数据
    df = pro.hm_list(**{
        "name": "",
        "limit": "",
        "offset": ""
    }, fields=[
        "name",
        "desc",
        "orgs"
    ])
    
    data = df.to_dict(orient='records')

    # 获取数据库连接
    conn = db.get_db()
    cursor = conn.cursor()

    # 插入数据到数据库，使用主键存在覆盖逻辑
    for record in data:
        cursor.execute('''
            INSERT INTO hot_money_info (name, `desc`, orgs)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                `desc`=VALUES(`desc`),
                orgs=VALUES(orgs)
        ''', (
            record['name'], record['desc'], record['orgs']
        ))

    conn.commit()
    cursor.close()
    conn.close()

def import_ths_index_data():
    """
    获取同花顺概念和行业指数数据并导入ths_index表
    """
    # 拉取数据
    df = pro.ths_index()

    # 将 NaN 值替换为 None
    df = df.replace({float('nan'): None})

    data = df.to_dict(orient='records')

    # 获取数据库连接
    conn = db.get_db()
    cursor = conn.cursor()

    # 插入数据到数据库，使用主键存在覆盖逻辑
    insert_query = """
    INSERT INTO ths_index (ts_code, name, count, exchange, list_date, type)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        count = VALUES(count),
        exchange = VALUES(exchange),
        list_date = VALUES(list_date),
        type = VALUES(type);
    """
    for record in data:
        cursor.execute(insert_query, (
            record['ts_code'],
            record['name'],
            record['count'],
            record['exchange'],
            record['list_date'],
            record['type']
        ))

    conn.commit()
    cursor.close()
    conn.close()

    print("同花顺概念和行业指数数据已成功导入到数据库中")

def import_ths_member_data():
    """
    获取同花顺概念板块成分数据并导入ths_member表
    """
    # 获取所有板块指数代码
    ths_index_df = pro.ths_index()
    ts_codes = ths_index_df['ts_code'].tolist()

    # 获取数据库连接
    conn = db.get_db()
    cursor = conn.cursor()

    # 插入数据到数据库，使用主键存在覆盖逻辑
    insert_query = """
    INSERT INTO ths_member (ts_code, con_code, con_name, weight, in_date, out_date, is_new)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        con_name = VALUES(con_name),
        weight = VALUES(weight),
        in_date = VALUES(in_date),
        out_date = VALUES(out_date),
        is_new = VALUES(is_new);
    """

    for ts_code in ts_codes:
        print(f"开始导入 {ts_code} 的同花顺概念板块成分数据")
        offset = 0
        limit = 5000  # 假设每次请求的最大数据量为5000

        while True:
            # 拉取板块成分数据
            df = pro.ths_member(ts_code=ts_code, limit=limit, offset=offset)

            # 如果没有数据，则退出循环
            if df.empty:
                break

            # 将 NaN 值替换为 None
            df = df.replace({float('nan'): None})

            # 将数据转换为字典列表
            data = df.to_dict(orient='records')

            # 插入数据到数据库
            for record in data:
                cursor.execute(insert_query, (
                    record['ts_code'],
                    record['con_code'],
                    record['con_name'],
                    record.get('weight'),
                    record.get('in_date'),
                    record.get('out_date'),
                    record.get('is_new')
                ))

            # 提交事务
            conn.commit()

            # 更新offset
            offset += limit

    # 关闭数据库连接
    cursor.close()
    conn.close()

    print(f"同花顺概念板块成分数据已成功导入到数据库中")

def init_job():
    # 导入热钱信息
    try:
        import_hot_money_info()
    except Exception as e:
        # 如果导入热钱信息出错，打印错误信息
        print(f"导入热钱信息出错: {e}")

    # 导入股票基本信息
    try:
        import_stock_basic_info()
    except Exception as e:
        # 如果导入股票基本信息出错，打印错误信息
        print(f"导入股票基本信息出错: {e}")

    # 导入同花顺指数数据
    try:
        import_ths_index_data()
    except Exception as e:
        # 如果导入同花顺指数数据出错，打印错误信息
        print(f"导入同花顺指数出错: {e}")

    # 导入同花顺会员数据
    try:
        import_ths_member_data()
    except Exception as e:
        # 如果导入同花顺会员数据出错，打印错误信息
        print(f"Error in 导入同花顺指数股票出错: {e}")
        


# init_job()


# 全局初始化
# 导入股票基本信息
# import_stock_basic_info()
# 导入游资信息
# import_hot_money_info()
# 同花顺概念和行业指数数据&导入同花顺概念板块成分数据
# import_ths_index_data()
# import_ths_member_data()
