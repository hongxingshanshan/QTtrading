"""
财务指标模型
数据来源: Tushare fina_indicator 接口
"""
from sqlalchemy import Column, String, Float, PrimaryKeyConstraint
from app.models.base import Base


class FinaIndicator(Base):
    """财务指标表 - ROE/毛利率/负债率等"""
    __tablename__ = "fina_indicator"
    __table_args__ = (
        PrimaryKeyConstraint('ts_code', 'end_date'),
    )

    # 基础信息
    ts_code = Column(String(20), comment="TS股票代码")
    ann_date = Column(String(10), comment="公告日期")
    end_date = Column(String(10), comment="报告期")

    # ============== 每股指标 ==============
    eps = Column(Float, comment="基本每股收益")
    dt_eps = Column(Float, comment="稀释每股收益")
    bps = Column(Float, comment="每股净资产")
    ocfps = Column(Float, comment="每股经营活动现金流量净额")
    cfps = Column(Float, comment="每股现金流量净额")
    revenue_ps = Column(Float, comment="每股营业收入")
    capital_rese_ps = Column(Float, comment="每股资本公积")
    surplus_rese_ps = Column(Float, comment="每股盈余公积")
    undist_profit_ps = Column(Float, comment="每股未分配利润")
    retainedps = Column(Float, comment="每股留存收益")

    # ============== 盈利能力 ==============
    roe = Column(Float, comment="净资产收益率")
    roe_waa = Column(Float, comment="加权平均净资产收益率")
    roe_dt = Column(Float, comment="净资产收益率(扣非)")
    roa = Column(Float, comment="总资产报酬率")
    roic = Column(Float, comment="投入资本回报率")
    netprofit_margin = Column(Float, comment="销售净利率")
    grossprofit_margin = Column(Float, comment="销售毛利率")
    ebit = Column(Float, comment="息税前利润")
    ebitda = Column(Float, comment="息税折旧摊销前利润")

    # ============== 营运能力 ==============
    invturn_days = Column(Float, comment="存货周转天数")
    arturn_days = Column(Float, comment="应收账款周转天数")
    inv_turn = Column(Float, comment="存货周转率")
    ar_turn = Column(Float, comment="应收账款周转率")
    assets_turn = Column(Float, comment="总资产周转率")
    turn_days = Column(Float, comment="营业周期")

    # ============== 偿债能力 ==============
    current_ratio = Column(Float, comment="流动比率")
    quick_ratio = Column(Float, comment="速动比率")
    cash_ratio = Column(Float, comment="保守速动比率")
    debt_to_assets = Column(Float, comment="资产负债率")
    debt_to_eqt = Column(Float, comment="产权比率")
    ebit_to_interest = Column(Float, comment="已获利息倍数")

    # ============== 成长能力 ==============
    or_yoy = Column(Float, comment="营业收入同比增长率(%)")
    tr_yoy = Column(Float, comment="营业总收入同比增长率(%)")
    netprofit_yoy = Column(Float, comment="净利润同比增长率(%)")
    dt_netprofit_yoy = Column(Float, comment="扣非净利润同比增长率(%)")
    basic_eps_yoy = Column(Float, comment="基本每股收益同比增长率(%)")
    roe_yoy = Column(Float, comment="净资产收益率同比增长率(%)")
    equity_yoy = Column(Float, comment="净资产同比增长率(%)")
    assets_yoy = Column(Float, comment="资产总计增长率(%)")

    # ============== 现金流量 ==============
    fcff = Column(Float, comment="企业自由现金流量")
    fcfe = Column(Float, comment="股权自由现金流量")
    ocf_to_or = Column(Float, comment="经营现金流/营业收入")
    ocf_to_opincome = Column(Float, comment="经营现金流/营业利润")

    # ============== 其他重要指标 ==============
    profit_dedt = Column(Float, comment="扣非净利润")
    gross_margin = Column(Float, comment="毛利")
    working_capital = Column(Float, comment="营运资金")
    tangible_asset = Column(Float, comment="有形资产")
    invest_capital = Column(Float, comment="全部投入资本")
    retained_earnings = Column(Float, comment="留存收益")
    rd_exp = Column(Float, comment="研发费用")

    # ============== 单季度指标 ==============
    q_eps = Column(Float, comment="每股收益(单季度)")
    q_netprofit_margin = Column(Float, comment="销售净利率(单季度)")
    q_gsprofit_margin = Column(Float, comment="销售毛利率(单季度)")
    q_roe = Column(Float, comment="净资产收益率(单季度)")
    q_gr_yoy = Column(Float, comment="营业总收入同比增长(单季度)")
    q_sales_yoy = Column(Float, comment="营业收入同比增长(单季度)")
    q_profit_yoy = Column(Float, comment="净利润同比增长(单季度)")
    q_netprofit_yoy = Column(Float, comment="归属母公司净利润同比增长(单季度)")