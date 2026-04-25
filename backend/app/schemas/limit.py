from pydantic import BaseModel
from typing import Optional


class DailyLimitItem(BaseModel):
    trade_date: Optional[str] = None
    ts_code: Optional[str] = None
    name: Optional[str] = None
    close: Optional[float] = None
    pct_chg: Optional[float] = None
    limit_price: Optional[float] = None

    class Config:
        from_attributes = True
