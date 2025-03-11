import mysql.connector
import DataBase as db

def get_daily_data(ts_code):
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)

    query = '''
    SELECT trade_date, open, high, low, close, pre_close, price_change, pct_chg, vol, amount
    FROM daily_data
    WHERE ts_code = %s
    ORDER BY trade_date ASC
    '''
    cursor.execute(query, (ts_code,))
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data