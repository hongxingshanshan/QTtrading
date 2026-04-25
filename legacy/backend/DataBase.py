import mysql.connector

def get_db():
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='369225',
            database='quant_trading',
            connection_timeout=10,  # 设置连接超时时间为5秒
        )
    except mysql.connector.Error as err:
        import traceback
        traceback.print_exc()  # 打印完整的异常堆栈
        return None
    return conn