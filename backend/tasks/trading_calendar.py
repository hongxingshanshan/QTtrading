"""交易日历工具"""
import chinese_calendar as calendar
from datetime import datetime


def is_trading_day(date: datetime = None) -> bool:
    """判断是否为交易日（工作日且非节假日）"""
    if date is None:
        date = datetime.now()
    return calendar.is_workday(date) and not calendar.is_holiday(date)


def get_recent_trading_days(days: int = 10) -> list:
    """获取最近N个交易日"""
    result = []
    current = datetime.now()
    while len(result) < days:
        if is_trading_day(current):
            result.append(current.strftime('%Y%m%d'))
        current = current.replace(hour=0, minute=0, second=0, microsecond=0)
        from datetime import timedelta
        current = current - timedelta(days=1)
    return result
