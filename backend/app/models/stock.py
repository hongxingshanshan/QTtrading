from sqlalchemy import Column, String, Date
from app.models.base import Base


class StockBasicInfo(Base):
    __tablename__ = "stock_basic_info"

    ts_code = Column(String(20), primary_key=True, comment="股票代码")
    symbol = Column(String(10), comment="股票代码简写")
    name = Column(String(50), comment="股票名称")
    area = Column(String(20), comment="地域")
    industry = Column(String(50), comment="行业")
    market = Column(String(10), comment="市场类型")
    list_date = Column(Date, comment="上市日期")
