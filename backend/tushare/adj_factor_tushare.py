from backend import DataBase as db
from tqdm import tqdm 
from datetime import datetime, timedelta
from backend.tushare import token

# 初始化 Tushare 接口
pro = token.get_tushare().pro_api()

def fetch_adj_factor(ts_code, start_date, end_date):
    """
    获取单只股票的复权因子
    :param ts_code: 股票代码
    :param start_date: 开始日期 (格式: YYYYMMDD)
    :param end_date: 结束日期 (格式: YYYYMMDD)
    :return: DataFrame 包含复权因子数据
    """
    try:
        df = pro.adj_factor(ts_code=ts_code, start_date=start_date, end_date=end_date)
        return df
    except Exception as e:
        print(f"获取股票 {ts_code} 的复权因子失败: {e}")
        return None

def update_adj_factor(ts_code, start_date, end_date, conn):
    """
    更新单只股票的复权因子到数据库
    :param ts_code: 股票代码
    :param start_date: 开始日期 (格式: YYYYMMDD)
    :param end_date: 结束日期 (格式: YYYYMMDD)
    :param conn: 数据库连接
    """
    df = fetch_adj_factor(ts_code, start_date, end_date)
    if df is None or df.empty:
        return

    # 将 NaN 值替换为 None
    df = df.replace({float('nan'): None})

    # 转换为字典列表
    data = df.to_dict(orient='records')

    # 插入数据到数据库
    cursor = conn.cursor()
    for record in data:
        cursor.execute("""
            INSERT INTO adj_factor (ts_code, trade_date, adj_factor)
            VALUES (%(ts_code)s, %(trade_date)s, %(adj_factor)s)
            ON DUPLICATE KEY UPDATE
            adj_factor = VALUES(adj_factor)
        """, record)

    # 提交事务
    conn.commit()
    cursor.close()

def sync_adj_factors(start_date, end_date):
    """
    同步所有股票的复权因子
    :param start_date: 开始日期 (格式: YYYYMMDD)
    :param end_date: 结束日期 (格式: YYYYMMDD)
    """
    # 获取数据库连接
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)

    # 获取所有股票的 ts_code
    cursor.execute('SELECT ts_code FROM stock_basic_info')
    stocks = cursor.fetchall()

    # 遍历所有股票
    for stock in tqdm(stocks, desc="同步复权因子"):
        ts_code = stock['ts_code']
        update_adj_factor(ts_code, start_date, end_date, conn)

    # 关闭数据库连接
    cursor.close()
    conn.close()

    print(f"复权因子同步完成，时间范围：{start_date} 至 {end_date}")

if __name__ == "__main__":
    # 示例：同步复权因子
    start_date = '19000101'  # 开始日期
    end_date = datetime.now().strftime('%Y%m%d')  # 结束日期为当前日期
    sync_adj_factors(start_date, end_date)