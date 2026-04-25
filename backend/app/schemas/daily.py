from pydantic import BaseModel
from typing import Optional


class DailyDataItem(BaseModel):
    trade_date: Optional[str] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    pre_close: Optional[float] = None
    price_change: Optional[float] = None
    pct_chg: Optional[float] = None
    vol: Optional[int] = None
    amount: Optional[float] = None

    class Config:
        from_attributes = True
