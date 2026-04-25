from pydantic import BaseModel
from typing import Optional, Any


class DailyLimitItem(BaseModel):
    trade_date: Optional[Any] = None
    ts_code: Optional[str] = None
    industry: Optional[str] = None
    name: Optional[str] = None
    close: Optional[float] = None
    pct_chg: Optional[float] = None
    amount: Optional[Any] = None
    limit_amount: Optional[Any] = None
    float_mv: Optional[Any] = None
    total_mv: Optional[Any] = None
    turnover_ratio: Optional[Any] = None
    fd_amount: Optional[Any] = None
    first_time: Optional[Any] = None
    last_time: Optional[Any] = None
    open_times: Optional[int] = None
    up_stat: Optional[str] = None
    limit_times: Optional[int] = None
    limit_status: Optional[str] = None

    class Config:
        from_attributes = True
