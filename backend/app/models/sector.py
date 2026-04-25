from sqlalchemy import Column, String, Float, Integer, PrimaryKeyConstraint
from app.models.base import Base


class DailySectorLimitData(Base):
    __tablename__ = "daily_sector_limit_data"
    __table_args__ = (
        PrimaryKeyConstraint('sector_code', 'trade_date'),
    )

    trade_date = Column(String(10), comment="交易日期")
    sector_code = Column(String(20), comment="板块代码")
    sector_name = Column(String(50), comment="板块名称")
    sector_type = Column(String(20), comment="板块类型")
    up_limit_count = Column(Integer, comment="涨停家数")
    down_limit_count = Column(Integer, comment="跌停家数")


class ThsIndex(Base):
    __tablename__ = "ths_index"

    ts_code = Column(String(20), primary_key=True, comment="指数代码")
    name = Column(String(50), comment="指数名称")