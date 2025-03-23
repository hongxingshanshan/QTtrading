import mysql.connector
from backend import DataBase as db

def get_daily_limit_data_by_sector():
    # 获取数据库连接
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)

    # 查询根据板块聚合的每日涨停跌停股票数量
    query = """
    SELECT 
        ti.ts_code AS sector_code,
        ti.name AS sector_name,
        ti.type AS sector_type,
        dld.trade_date,
        SUM(CASE WHEN dld.limit_status = 'U' THEN 1 ELSE 0 END) AS up_limit_count,
        SUM(CASE WHEN dld.limit_status = 'D' THEN 1 ELSE 0 END) AS down_limit_count
    FROM 
        ths_index ti
    JOIN 
        ths_member tm ON ti.ts_code = tm.ts_code
    JOIN 
        daily_limit_data dld ON tm.con_code = dld.ts_code
    GROUP BY 
        ti.ts_code, ti.name, ti.type, dld.trade_date
    ORDER BY 
        dld.trade_date, ti.ts_code
    """
    cursor.execute(query)
    data = cursor.fetchall()

    # 关闭数据库连接
    cursor.close()
    conn.close()

    return data

def get_sector_data():
    # 获取数据库连接
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)

    # 查询行业数据
    query = "SELECT * FROM sector_data"
    cursor.execute(query)
    data = cursor.fetchall()

    # 关闭数据库连接
    cursor.close()
    conn.close()

    return data

# get_sector_data()