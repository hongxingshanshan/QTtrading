from sqlalchemy import Column, String, Integer, Text
from app.models.base import Base


class HotMoneyInfo(Base):
    __tablename__ = "hot_money_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), comment="游资名称")
    desc = Column(Text, comment="描述")
    orgs = Column(Text, comment="关联机构")


class DailyHotMoneyTradeData(Base):
    __tablename__ = "daily_hotmoney_trade_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_date = Column(String(10), comment="交易日期")
    ts_code = Column(String(20), comment="股票代码")
    ts_name = Column(String(50), comment="股票名称")
    hm_name = Column(String(100), comment="游资名称")
    buy_amount = Column(String(50), comment="买入金额")
    sell_amount = Column(String(50), comment="卖出金额")
    net_amount = Column(String(50), comment="净买入")
