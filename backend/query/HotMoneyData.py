import mysql.connector
from backend import DataBase as db


def get_hotmoney_data(name, page, page_size):
    # 获取数据库连接
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)

    # 构建查询条件
    conditions = []
    params = []

    if name:
        conditions.append("name LIKE %s")
        params.append(f'%{name}%')

    # 构建查询语句
    query = '''
    SELECT name, `desc`, orgs
    FROM hot_money_info
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
    FROM hot_money_info
    '''
    if conditions:
        count_query += " WHERE " + " AND ".join(conditions)
    cursor.execute(count_query, params[:-2])
    total = cursor.fetchone()['total']

    # 关闭数据库连接
    cursor.close()
    conn.close()

    return data, total