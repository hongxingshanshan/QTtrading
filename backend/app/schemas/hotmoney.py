from pydantic import BaseModel
from typing import Optional


class HotMoneyInfoItem(BaseModel):
    name: Optional[str] = None
    desc: Optional[str] = None
    orgs: Optional[str] = None

    class Config:
        from_attributes = True


class HotMoneyQuery(BaseModel):
    name: Optional[str] = ""
    page: int = 1
    pageSize: int = 10


class DailyHotMoneyTradeItem(BaseModel):
    trade_date: Optional[str] = None
    ts_code: Optional[str] = None
    ts_name: Optional[str] = None
    hm_name: Optional[str] = None
    buy_amount: Optional[str] = None
    sell_amount: Optional[str] = None
    net_amount: Optional[str] = None

    class Config:
        from_attributes = True


class DailyHotMoneyTradeQuery(BaseModel):
    hmName: Optional[str] = ""
    tradeDate: Optional[str] = ""
    tsName: Optional[str] = ""
    tsCode: Optional[str] = ""
    page: int = 1
    pageSize: int = 10
