import schedule
import time
from datetime import datetime
import chinese_calendar as calendar
from incr_tushare_service import import_daily_limit_data, import_daily_sector_limit_data_by_ts_code, import_all_daily_data, import_hm_detail_data,import_top_list_data,import_top_inst_data
from init_tushare_service import import_hot_money_info,import_stock_basic_info,import_ths_index_data,import_ths_member_data

def incr_job():
    # 获取当前日期
    today = datetime.now().strftime('%Y%m%d')
    # 导入每日涨跌停数据
    try:
        import_daily_limit_data(today, today)
    except Exception as e:
        print(f"Error in import_daily_limit_data_by_month: {e}")

    # 导入每日行业涨跌停数据
    try:
        import_daily_sector_limit_data_by_ts_code('', today, today)
    except Exception as e:
        print(f"Error in import_daily_sector_limit_data_by_ts_code: {e}")

    # 导入所有每日数据
    try:
        import_all_daily_data(today, today)
    except Exception as e:
        print(f"Error in import_all_daily_data: {e}")

    # 导入每日详细数据
    try:
        import_hm_detail_data(today, today)
    except Exception as e:
        print(f"Error in import_hm_detail_data: {e}")
    
    # 导入每日排行榜数据
    try:
        import_top_list_data(today,today)
    except Exception as e:
        print(f"Error in import_top_list_data: {e}")
    
    # 导入每日机构数据
    try:
        import_top_inst_data(today,today)
    except Exception as e:
        print(f"Error in import_top_inst_data: {e}")
    

def is_trading_day(date):
    # 判断是否为交易日
    return calendar.is_workday(date) and not calendar.is_holiday(date)

def check_incr_job():
    today = datetime.now()
    if is_trading_day(today):
        incr_job()

# 每天凌晨3点执行一次 init 的初始化任务
# 定义一个初始化任务的函数
def init_job():
    # 导入热钱信息
    try:
        import_hot_money_info()
    except Exception as e:
        # 如果导入热钱信息出错，打印错误信息
        print(f"Error in import_hot_money_info: {e}")

    # 导入股票基本信息
    try:
        import_stock_basic_info()
    except Exception as e:
        # 如果导入股票基本信息出错，打印错误信息
        print(f"Error in import_stock_basic_info: {e}")

    # 导入同花顺指数数据
    try:
        import_ths_index_data()
    except Exception as e:
        # 如果导入同花顺指数数据出错，打印错误信息
        print(f"Error in import_ths_index_data: {e}")

    # 导入同花顺会员数据
    try:
        import_ths_member_data()
    except Exception as e:
        # 如果导入同花顺会员数据出错，打印错误信息
        print(f"Error in import_ths_member_data: {e}")

def start_scheduled_tasks():
    # 每天检查是否为交易日，并在17,18,19:00执行任务
    schedule.every().day.at("17:00").do(check_incr_job)
    schedule.every().day.at("18:00").do(check_incr_job)
    schedule.every().day.at("19:00").do(check_incr_job)
    # 每天凌晨3点执行一次 init 的初始化任务
    schedule.every().day.at("03:00").do(init_job)

    while True:
        schedule.run_pending()
        time.sleep(10)
        print('Waiting for next schedule...')