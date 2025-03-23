from backend import DataBase as db

def get_adj_factor_data(ts_code):
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)

    query = '''
    select trade_date, adj_factor from adj_factor where ts_code = %s order by trade_date asc
    '''
    cursor.execute(query, (ts_code,))
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data