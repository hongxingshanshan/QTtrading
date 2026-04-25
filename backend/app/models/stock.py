from sqlalchemy import Column, String
from app.models.base import Base


class StockBasicInfo(Base):
    __tablename__ = "stock_basic_info"

    ts_code = Column(String(20), primary_key=True, comment="股票代码")
    symbol = Column(String(10), comment="股票代码简写")
    name = Column(String(50), comment="股票名称")
    area = Column(String(20), comment="地域")
    industry = Column(String(50), comment="行业")
    cnspell = Column(String(20), comment="拼音缩写")
    market = Column(String(10), comment="市场类型")
    list_date = Column(String(10), comment="上市日期")
    act_name = Column(String(100), comment="实控人名称")
    act_ent_type = Column(String(50), comment="实控人企业性质")
    fullname = Column(String(100), comment="股票全称")
    enname = Column(String(100), comment="英文全称")
    exchange = Column(String(20), comment="交易所")
    curr_type = Column(String(10), comment="交易货币")
    list_status = Column(String(2), comment="上市状态")
    delist_date = Column(String(10), comment="退市日期")
    is_hs = Column(String(2), comment="是否沪深港通标的")