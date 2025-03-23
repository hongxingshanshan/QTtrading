from backend import DataBase as db

def get_daily_sector_limit_data(sector_code=None, sector_name=None, sector_type=None, start_date=None, end_date=None):
    # 获取数据库连接
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)

    # 构建查询语句
    query = """
    SELECT 
        sector_code,
        sector_name,
        sector_type,
        trade_date,
        up_limit_count,
        down_limit_count
    FROM 
        daily_sector_limit_data
    WHERE 
        1=1 
    """
    
    # 添加查询条件
    params = []
    if sector_code:
        query += " AND sector_code = %s"
        params.append(sector_code)
    if sector_name:
        query += " AND sector_name = %s"
        params.append(sector_name)
    if sector_type:
        query += " AND sector_type = %s"
        params.append(sector_type)
    if start_date:
        query += " AND trade_date >= %s"
        params.append(start_date)
    if end_date:
        query += " AND trade_date <= %s"
        params.append(end_date)
    
    # 添加排序条件
    query += " ORDER BY trade_date ASC"
    
    # 执行查询
    cursor.execute(query, params)
    data = cursor.fetchall()

    # 关闭数据库连接
    cursor.close()
    conn.close()

    return data
