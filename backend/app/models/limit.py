from sqlalchemy import Column, String, Float, Integer, PrimaryKeyConstraint
from app.models.base import Base


class DailyLimitData(Base):
    __tablename__ = "daily_limit_data"
    __table_args__ = (
        PrimaryKeyConstraint('trade_date', 'ts_code'),
    )

    trade_date = Column(String(10), comment="交易日期")
    ts_code = Column(String(20), comment="股票代码")
    industry = Column(String(50), comment="所属行业")
    name = Column(String(50), comment="股票名称")
    close = Column(Float, comment="收盘价")
    pct_chg = Column(Float, comment="涨跌幅")
    amount = Column(Float, comment="总成交额")
    limit_amount = Column(Float, comment="涨停/跌停金额")
    float_mv = Column(Float, comment="流通市值")
    total_mv = Column(Float, comment="总市值")
    turnover_ratio = Column(Float, comment="换手率")
    fd_amount = Column(Float, comment="封单金额")
    first_time = Column(String(10), comment="首次涨停时间")
    last_time = Column(String(10), comment="最后涨停时间")
    open_times = Column(Integer, comment="打开次数")
    up_stat = Column(String(20), comment="涨停统计")
    limit_times = Column(Integer, comment="涨停次数")
    limit_status = Column(String(2), comment="涨跌停状态 U涨停 D跌停")