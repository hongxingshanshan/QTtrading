import mysql.connector


def get_db():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='369225',
        database='quant_trading'
    )
    return conn