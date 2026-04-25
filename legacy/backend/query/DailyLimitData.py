from backend import DataBase as db

def get_daily_limit_data():
    """
    获取每日涨跌停统计数据，包括：
    - 涨停数量
    - 最高连板数量
    - 最大连板高度（MAX(limit_times)）
    - 跌停数量
    - 炸板数量
    """
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)

    query = '''
    SELECT 
        trade_date,
        SUM(CASE WHEN limit_status = 'U' THEN 1 ELSE 0 END) AS up_count,  -- 涨停数量
        MAX(limit_times) AS highest_consecutive_limit,  -- 最高连板数量
        MAX(limit_times) AS max_limit_height,  -- 最大连板高度
        SUM(CASE WHEN limit_status = 'D' THEN 1 ELSE 0 END) AS down_count,  -- 跌停数量
        SUM(CASE WHEN limit_status = 'Z' THEN 1 ELSE 0 END) AS z_count,  -- 炸板数量
        SUM(CASE WHEN limit_status = 'U' AND market = '主板' THEN 1 ELSE 0 END) AS up_main,  -- 主板涨停数量
        SUM(CASE WHEN limit_status = 'U' AND market = '创业板' THEN 1 ELSE 0 END) AS up_chuang,  -- 创业板涨停数量
        SUM(CASE WHEN limit_status = 'U' AND market = '科创板' THEN 1 ELSE 0 END) AS up_kechuang,  -- 科创板涨停数量
        SUM(CASE WHEN limit_status = 'U' AND market = '北交所' THEN 1 ELSE 0 END) AS up_beijiao,  -- 北交所涨停数量
        SUM(CASE WHEN limit_status = 'D' AND market = '主板' THEN 1 ELSE 0 END) AS down_main,  -- 主板跌停数量
        SUM(CASE WHEN limit_status = 'D' AND market = '创业板' THEN 1 ELSE 0 END) AS down_chuang,  -- 创业板跌停数量
        SUM(CASE WHEN limit_status = 'D' AND market = '科创板' THEN 1 ELSE 0 END) AS down_kechuang,  -- 科创板跌停数量
        SUM(CASE WHEN limit_status = 'D' AND market = '北交所' THEN 1 ELSE 0 END) AS down_beijiao  -- 北交所跌停数量
    FROM daily_limit_data
    LEFT JOIN stock_basic_info ON daily_limit_data.ts_code = stock_basic_info.ts_code
    GROUP BY trade_date
    ORDER BY trade_date ASC;
    '''
    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data