"""
每日基本面指标模型
数据来源: Tushare daily_basic 接口
"""
from sqlalchemy import Column, String, Float, PrimaryKeyConstraint
from app.models.base import Base


class DailyBasic(Base):
    """每日基本面指标表 - PE/PB/市值等"""
    __tablename__ = "daily_basic"
    __table_args__ = (
        PrimaryKeyConstraint('ts_code', 'trade_date'),
    )

    # 基础信息
    ts_code = Column(String(20), comment="TS股票代码")
    trade_date = Column(String(10), comment="交易日期")
    close = Column(Float, comment="当日收盘价")

    # 换手率
    turnover_rate = Column(Float, comment="换手率（%）")
    turnover_rate_f = Column(Float, comment="换手率（自由流通股）")
    volume_ratio = Column(Float, comment="量比")

    # 估值指标
    pe = Column(Float, comment="市盈率（总市值/净利润）")
    pe_ttm = Column(Float, comment="市盈率TTM")
    pb = Column(Float, comment="市净率（总市值/净资产）")
    ps = Column(Float, comment="市销率")
    ps_ttm = Column(Float, comment="市销率TTM")

    # 股息率
    dv_ratio = Column(Float, comment="股息率（%）")
    dv_ttm = Column(Float, comment="股息率TTM（%）")

    # 股本结构
    total_share = Column(Float, comment="总股本（万股）")
    float_share = Column(Float, comment="流通股本（万股）")
    free_share = Column(Float, comment="自由流通股本（万）")

    # 市值
    total_mv = Column(Float, comment="总市值（万元）")
    circ_mv = Column(Float, comment="流通市值（万元）")