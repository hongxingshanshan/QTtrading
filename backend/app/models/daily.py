from sqlalchemy import Column, String, Float, BigInteger, PrimaryKeyConstraint
from app.models.base import Base


class DailyData(Base):
    __tablename__ = "daily_data"
    __table_args__ = (
        PrimaryKeyConstraint('ts_code', 'trade_date'),
    )

    ts_code = Column(String(20), comment="股票代码")
    trade_date = Column(String(10), comment="交易日期")
    open = Column(Float, comment="开盘价")
    high = Column(Float, comment="最高价")
    low = Column(Float, comment="最低价")
    close = Column(Float, comment="收盘价")
    pre_close = Column(Float, comment="昨收价")
    price_change = Column(Float, comment="涨跌额")
    pct_chg = Column(Float, comment="涨跌幅")
    vol = Column(BigInteger, comment="成交量")
    amount = Column(Float, comment="成交额")