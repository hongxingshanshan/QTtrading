import chinese_calendar as calendar
from datetime import datetime


def is_trading_day(date: datetime = None) -> bool:
    """判断是否为交易日"""
    if date is None:
        date = datetime.now()
    return calendar.is_workday(date) and not calendar.is_holiday(date)
