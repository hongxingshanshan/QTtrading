"""
技术指标预计算模块
将策略分析中常用的技术指标预计算并存储到数据库
"""
from sqlalchemy import Column, String, Float, Integer, PrimaryKeyConstraint
from app.models.base import Base


class DailyIndicator(Base):
    """日线技术指标表 - 存储预计算的所有技术指标"""
    __tablename__ = "daily_indicator"
    __table_args__ = (
        PrimaryKeyConstraint('ts_code', 'trade_date'),
    )

    # 基础信息
    ts_code = Column(String(20), comment="股票代码")
    trade_date = Column(String(10), comment="交易日期")

    # ============== KDJ 指标 ==============
    k_value = Column(Float, comment="KDJ K值")
    d_value = Column(Float, comment="KDJ D值")
    j_value = Column(Float, comment="KDJ J值")

    # ============== RSI 指标 ==============
    rsi6 = Column(Float, comment="RSI 6日")
    rsi12 = Column(Float, comment="RSI 12日")
    rsi24 = Column(Float, comment="RSI 24日")

    # ============== MACD 指标 ==============
    macd_dif = Column(Float, comment="MACD DIF线")
    macd_dea = Column(Float, comment="MACD DEA线")
    macd_hist = Column(Float, comment="MACD 柱状图 (2*(DIF-DEA))")

    # ============== 布林带 BOLL ==============
    boll_upper = Column(Float, comment="布林带上轨")
    boll_mid = Column(Float, comment="布林带中轨")
    boll_lower = Column(Float, comment="布林带下轨")
    boll_width = Column(Float, comment="布林带宽度 (上轨-下轨)/中轨")
    boll_position = Column(Float, comment="布林带位置 (0=下轨, 0.5=中轨, 1=上轨)")

    # ============== 均线 MA ==============
    ma5 = Column(Float, comment="5日均线")
    ma10 = Column(Float, comment="10日均线")
    ma20 = Column(Float, comment="20日均线")
    ma30 = Column(Float, comment="30日均线")
    ma60 = Column(Float, comment="60日均线")
    ma120 = Column(Float, comment="120日均线")
    ma250 = Column(Float, comment="250日均线")

    # 均线偏离度
    ma5_deviation = Column(Float, comment="5日均线偏离度")
    ma10_deviation = Column(Float, comment="10日均线偏离度")
    ma20_deviation = Column(Float, comment="20日均线偏离度")
    ma30_deviation = Column(Float, comment="30日均线偏离度")
    ma60_deviation = Column(Float, comment="60日均线偏离度")
    ma120_deviation = Column(Float, comment="120日均线偏离度")
    ma250_deviation = Column(Float, comment="250日均线偏离度")

    # 均线排列状态 (1=多头排列, -1=空头排列, 0=混乱)
    ma_alignment = Column(Integer, comment="均线排列状态")

    # ============== CCI 指标 ==============
    cci = Column(Float, comment="CCI 14日")

    # ============== WR 威廉指标 ==============
    wr10 = Column(Float, comment="WR 10日")
    wr14 = Column(Float, comment="WR 14日")

    # ============== OBV 指标 ==============
    obv = Column(Float, comment="OBV 累计能量线")
    obv_ma5 = Column(Float, comment="OBV 5日均线")
    obv_ma10 = Column(Float, comment="OBV 10日均线")

    # ============== 成交量因子 ==============
    vol_ma5 = Column(Float, comment="成交量5日均线")
    vol_ma10 = Column(Float, comment="成交量10日均线")
    vol_ma20 = Column(Float, comment="成交量20日均线")
    vol_ratio = Column(Float, comment="量比 (当日成交量/5日均量)")
    vol_ratio_10 = Column(Float, comment="量比10 (当日成交量/10日均量)")

    # ============== 价格形态因子 ==============
    consecutive_down = Column(Integer, comment="连续下跌天数")
    consecutive_up = Column(Integer, comment="连续上涨天数")
    drawdown_20d = Column(Float, comment="距20日高点回撤")
    drawdown_60d = Column(Float, comment="距60日高点回撤")
    rebound_20d = Column(Float, comment="距20日低点反弹")
    rebound_60d = Column(Float, comment="距60日低点反弹")
    amplitude = Column(Float, comment="振幅 (最高-最低)/昨收")
    pct_change = Column(Float, comment="当日涨跌幅")
    pct_change_5d = Column(Float, comment="5日累计涨跌幅")
    pct_change_10d = Column(Float, comment="10日累计涨跌幅")
    pct_change_20d = Column(Float, comment="20日累计涨跌幅")

    # ============== 换手率因子 ==============
    turnover_rate = Column(Float, comment="换手率")
    turnover_rate_ma5 = Column(Float, comment="5日平均换手率")

    # ============== ATR (真实波动幅度) ==============
    atr14 = Column(Float, comment="ATR 14日")

    # ============== DMA (平行线差指标) ==============
    dma_dif = Column(Float, comment="DMA DIF线 (MA10-MA50)")
    dma_ama = Column(Float, comment="DMA AMA线 (DIF的10日均线)")

    # ============== VR (成交量比率) ==============
    vr = Column(Float, comment="VR 成交量比率")