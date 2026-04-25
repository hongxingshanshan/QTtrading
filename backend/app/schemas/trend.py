from pydantic import BaseModel
from typing import Optional, Any, List


class StockTrendBasic(BaseModel):
    ts_code: Optional[str] = None
    name: Optional[str] = None
    industry: Optional[str] = None


class StockTrendLatest(BaseModel):
    close: Optional[float] = None
    pct_chg: Optional[float] = None
    vol: Optional[Any] = None
    amount: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    pre_close: Optional[float] = None
    price_change: Optional[float] = None


class StockTrendKlineItem(BaseModel):
    trade_date: Optional[Any] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    pre_close: Optional[float] = None  # 前收盘价
    vol: Optional[Any] = None
    amount: Optional[float] = None
    pct_chg: Optional[float] = None


class StockTrendMA(BaseModel):
    ma5: List[Optional[float]] = []
    ma10: List[Optional[float]] = []
    ma20: List[Optional[float]] = []
    ma30: List[Optional[float]] = []
    ma60: List[Optional[float]] = []
    ma90: List[Optional[float]] = []
    ma125: List[Optional[float]] = []
    ma250: List[Optional[float]] = []


class StockTrendResponse(BaseModel):
    basic: StockTrendBasic
    latest: StockTrendLatest
    kline: List[StockTrendKlineItem] = []
    ma: StockTrendMA


class StockTrendQuery(BaseModel):
    ts_code: str
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""