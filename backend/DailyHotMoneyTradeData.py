import mysql.connector
import DataBase as db

def get_daily_hotmoney_trade_data(hm_name=None, trade_date=None, ts_name=None, ts_code=None, page=1, page_size=10):
    """
    获取每日游资交易数据（支持分页和查询条件）
    参数:
        hm_name: 游资名称（模糊查询）
        trade_date: 交易日期（精确匹配，格式：YYYYMMDD）
        ts_name: 股票名称（模糊查询）
        ts_code: 股票代码（精确匹配）
        page: 页码（默认第1页）
        page_size: 每页条数（默认10条）
    返回:
        data: 查询结果列表
        total: 总条数
    """
    # 获取数据库连接
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)

    # 构建查询条件
    conditions = []
    params = []

    if hm_name:
        conditions.append("hm_name LIKE %s")
        params.append(f'%{hm_name}%')

    if trade_date:
        conditions.append("trade_date = %s")
        params.append(trade_date)

    if ts_name:
        conditions.append("ts_name LIKE %s")
        params.append(f'%{ts_name}%')

    if ts_code:
        conditions.append("ts_code = %s")
        params.append(ts_code)

    # 构建查询语句
    query = '''
    SELECT *
    FROM daily_hot_money_trading
    '''
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " order by trade_date desc LIMIT %s OFFSET %s"
    params.extend([page_size, (page - 1) * page_size])

    # 执行查询
    cursor.execute(query, params)
    data = cursor.fetchall()

    # 获取总条数
    count_query = '''
    SELECT COUNT(*) as total
    FROM daily_hot_money_trading
    '''
    if conditions:
        count_query += " WHERE " + " AND ".join(conditions)
    cursor.execute(count_query, params[:-2])
    total = cursor.fetchone()['total']

    # 关闭数据库连接
    cursor.close()
    conn.close()

    return data, total