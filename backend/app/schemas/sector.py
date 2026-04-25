from pydantic import BaseModel
from typing import Optional


class DailySectorLimitItem(BaseModel):
    trade_date: Optional[str] = None
    sector_code: Optional[str] = None
    sector_name: Optional[str] = None
    sector_type: Optional[str] = None
    pct_chg: Optional[float] = None

    class Config:
        from_attributes = True


class SectorLimitQuery(BaseModel):
    sector_code: Optional[str] = ""
    sector_name: Optional[str] = ""
    sector_type: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""


class ThsIndexItem(BaseModel):
    ts_code: Optional[str] = None
    name: Optional[str] = None

    class Config:
        from_attributes = True
