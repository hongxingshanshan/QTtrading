import mysql.connector
import DataBase as db

def get_stock_basic_info(symbol, name, industry, start_date, end_date, page, page_size):
    # 获取数据库连接
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)

    # 构建查询条件
    conditions = []
    params = []

    if symbol:
        conditions.append("symbol LIKE %s")
        params.append(f'%{symbol}%')
    if name:
        conditions.append("name LIKE %s")
        params.append(f'%{name}%')
    if industry:
        conditions.append("industry LIKE %s")
        params.append(f'%{industry}%')
    if start_date:
        conditions.append("list_date >= %s")
        params.append(start_date)
    if end_date:
        conditions.append("list_date <= %s")
        params.append(end_date)

    # 构建查询语句
    query = '''
    SELECT ts_code, symbol, name, area, industry, cnspell, market, list_date, act_name, act_ent_type, fullname, enname, exchange, curr_type, list_status, delist_date, is_hs
    FROM stock_basic_info
    '''
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " LIMIT %s OFFSET %s"
    params.extend([page_size, (page - 1) * page_size])

    cursor.execute(query, params)
    data = cursor.fetchall()

    # 获取总条数
    count_query = '''
    SELECT COUNT(*) as total
    FROM stock_basic_info
    '''
    if conditions:
        count_query += " WHERE " + " AND ".join(conditions)
    cursor.execute(count_query, params[:-2])
    total = cursor.fetchone()['total']

    # 关闭数据库连接
    cursor.close()
    conn.close()

    return data, total