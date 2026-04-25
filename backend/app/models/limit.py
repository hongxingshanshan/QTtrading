from sqlalchemy import Column, String, Float, PrimaryKeyConstraint
from app.models.base import Base


class DailyLimitData(Base):
    __tablename__ = "daily_limit_data"
    __table_args__ = (
        PrimaryKeyConstraint('trade_date', 'ts_code'),
    )

    trade_date = Column(String(10), comment="交易日期")
    ts_code = Column(String(20), comment="股票代码")
    name = Column(String(50), comment="股票名称")
    close = Column(Float, comment="收盘价")
    pct_chg = Column(Float, comment="涨跌幅")
    limit_price = Column(Float, comment="涨停价")
