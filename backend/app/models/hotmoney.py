from sqlalchemy import Column, String, Integer, Text, PrimaryKeyConstraint
from app.models.base import Base


class HotMoneyInfo(Base):
    __tablename__ = "hot_money_info"

    name = Column(String(50), primary_key=True, comment="游资名称")
    desc = Column(Text, comment="描述")
    orgs = Column(Text, comment="关联机构")


class DailyHotMoneyTradeData(Base):
    __tablename__ = "daily_hot_money_trading"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    trade_date = Column(String(10), comment="交易日期")
    ts_code = Column(String(20), comment="股票代码")
    ts_name = Column(String(50), comment="股票名称")
    buy_amount = Column(String(50), comment="买入金额")
    sell_amount = Column(String(50), comment="卖出金额")
    net_amount = Column(String(50), comment="净买入")
    hm_name = Column(String(50), comment="游资名称")
    hm_orgs = Column(Text, comment="游资机构")
    tag = Column(String(50), comment="标签")
