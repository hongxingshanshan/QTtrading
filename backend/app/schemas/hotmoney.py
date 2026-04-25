from pydantic import BaseModel
from typing import Optional, Any


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
    id: Optional[int] = None
    trade_date: Optional[Any] = None
    ts_code: Optional[str] = None
    ts_name: Optional[str] = None
    buy_amount: Optional[Any] = None
    sell_amount: Optional[Any] = None
    net_amount: Optional[Any] = None
    hm_name: Optional[str] = None
    hm_orgs: Optional[str] = None
    tag: Optional[str] = None

    class Config:
        from_attributes = True


class DailyHotMoneyTradeQuery(BaseModel):
    hmName: Optional[str] = ""
    tradeDate: Optional[str] = ""
    tsName: Optional[str] = ""
    tsCode: Optional[str] = ""
    page: int = 1
    pageSize: int = 10
