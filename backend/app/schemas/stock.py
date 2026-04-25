from pydantic import BaseModel
from typing import Optional
from datetime import date


class StockBasicInfoItem(BaseModel):
    ts_code: str
    symbol: Optional[str] = None
    name: Optional[str] = None
    area: Optional[str] = None
    industry: Optional[str] = None
    market: Optional[str] = None
    list_date: Optional[str] = None

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
