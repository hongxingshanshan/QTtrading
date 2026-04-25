from pydantic import BaseModel
from typing import Optional, Any


class DailyDataItem(BaseModel):
    ts_code: Optional[str] = None
    trade_date: Optional[Any] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    pre_close: Optional[float] = None
    price_change: Optional[float] = None
    pct_chg: Optional[float] = None
    vol: Optional[Any] = None
    amount: Optional[float] = None

    class Config:
        from_attributes = True
