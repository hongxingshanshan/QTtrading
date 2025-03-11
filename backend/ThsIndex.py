import mysql.connector
import DataBase as db 

def get_all_ths_index():
    """
    查询所有同花顺板块信息
    """
    # 获取数据库连接
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)

    # 构建查询语句
    query = '''
    SELECT 
        ts_code,
        name,
        count,
        exchange,
        list_date,
        type
    FROM 
        ths_index where type in ('I','N')
        and exchange='A'
        and list_date is not null
    '''

    # 执行查询
    cursor.execute(query)
    data = cursor.fetchall()

    # 关闭数据库连接
    cursor.close()
    conn.close()

    return data