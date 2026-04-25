"""初始化历史数据 - 复用已有任务模块"""
import sys
sys.path.insert(0, '.')
from datetime import datetime, timedelta
from loguru import logger
from tasks.init_jobs import import_stock_basic_info, import_hot_money_info
from tasks.incr_jobs import import_daily_limit_data, import_hm_detail_data, import_all_daily_data


def import_history_data(start_date: str, end_date: str):
    """导入历史数据"""
    logger.info(f"========== 开始导入历史数据 ({start_date} ~ {end_date}) ==========")

    # 1. 导入基础数据
    import_stock_basic_info()
    import_hot_money_info()

    # 2. 按日期导入历史数据
    current_date = datetime.strptime(start_date, '%Y%m%d')
    end_dt = datetime.strptime(end_date, '%Y%m%d')
    total_days = (end_dt - current_date).days + 1
    processed = 0

    while current_date <= end_dt:
        date_str = current_date.strftime('%Y%m%d')

        # 跳过周末
        if current_date.weekday() >= 5:
            current_date += timedelta(days=1)
            continue

        processed += 1
        if processed % 10 == 0:
            logger.info(f"进度: {processed}/{total_days} 天 - {date_str}")

        # 导入当日数据
        import_daily_limit_data(date_str, date_str)
        import_hm_detail_data(date_str, date_str)
        import_all_daily_data(date_str, date_str)

        current_date += timedelta(days=1)

    logger.info(f"========== 历史数据导入完成，共处理 {processed} 个交易日 ==========")


if __name__ == "__main__":
    # 最近3年
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=3*365)).strftime('%Y%m%d')
    import_history_data(start_date, end_date)
