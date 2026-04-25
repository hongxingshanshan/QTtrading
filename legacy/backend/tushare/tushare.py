
from backend.tushare import incr_tushare_service as its
from backend.tushare import token
pro=token.get_tushare().pro_api()

def get_stock_daily_data(ts_code, start_date, end_date):
    """
    获取某只股票的日线行情数据（前复权）
    :param ts_code: 股票代码
    :param start_date: 开始日期 (格式：YYYYMMDD)
    :param end_date: 结束日期 (格式：YYYYMMDD)
    :return: DataFrame 包含日线行情数据
    """
    try:
        # 调用通用行情接口获取日线数据
        df = token.get_tushare().pro_bar(
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date,
            asset='E',  # 股票
            adj='qfq',  # 前复权
            freq='D'    # 日线
        )
        return df
    except Exception as e:
        print(f"获取股票 {ts_code} 的日线行情数据失败: {e}")
        return None

# 示例：获取某只股票的日线行情数据
if __name__ == "__main__":
    # 设置参数
    ts_code = '000001.SZ'  # 股票代码
    start_date = '20230101'  # 开始日期
    end_date = '20231231'    # 结束日期
    limit = 10  # 限制返回的行数
    offset = 0  # 偏移量
    # 拉取最强板块数据
    df = pro.limit_cpt_list(
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
            fields='ts_code,name,trade_date,days,up_stat,cons_nums,up_nums,pct_chg,rank'
        )
    print(df)
    # its.import_daily_data_for_stock(ts_code, start_date, end_date)
    # its.import_all_daily_data('19000101', '20250321')
    
