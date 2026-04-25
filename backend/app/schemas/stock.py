from pydantic import BaseModel
from typing import Optional, Any


class StockBasicInfoItem(BaseModel):
    ts_code: Optional[str] = None
    symbol: Optional[str] = None
    name: Optional[str] = None
    area: Optional[str] = None
    industry: Optional[str] = None
    cnspell: Optional[str] = None
    market: Optional[str] = None
    list_date: Optional[Any] = None
    act_name: Optional[str] = None
    act_ent_type: Optional[str] = None
    fullname: Optional[str] = None
    enname: Optional[str] = None
    exchange: Optional[str] = None
    curr_type: Optional[str] = None
    list_status: Optional[str] = None
    delist_date: Optional[Any] = None
    is_hs: Optional[str] = None

    class Config:
        from_attributes = True


class StockQuery(BaseModel):
    symbol: Optional[str] = ""
    name: Optional[str] = ""
    industry: Optional[str] = ""
    startDate: Optional[str] = ""
    endDate: Optional[str] = ""
    page: int = 1
    pageSize: int = 10
