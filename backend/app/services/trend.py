from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.repositories.daily import DailyDataRepository
from app.repositories.stock import StockBasicInfoRepository
from app.schemas.trend import (
    StockTrendResponse,
    StockTrendBasic,
    StockTrendLatest,
    StockTrendKlineItem,
    StockTrendMA,
)
from app.models.kline import WeeklyData, MonthlyData, AdjFactor


class StockTrendService:
    def __init__(self, db: Session):
        self.daily_repo = DailyDataRepository(db)
        self.stock_repo = StockBasicInfoRepository(db)
        self.db = db

    def get_trend_data(
        self, ts_code: str, start_date: str = "", end_date: str = "",
        period: str = "daily", adj_type: str = "qfq"
    ) -> StockTrendResponse:
        """获取股票走势图数据

        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            period: 周期 (daily/weekly/monthly)
            adj_type: 复权类型 (qfq前复权/hfq后复权/none不复权)
        """
        # 获取股票基本信息
        stock_info = self.stock_repo.get_by_ts_code(ts_code)
        basic = StockTrendBasic(
            ts_code=stock_info.ts_code if stock_info else ts_code,
            name=stock_info.name if stock_info else "",
            industry=stock_info.industry if stock_info else "",
        )

        # 根据周期获取K线数据
        daily_data = self._get_kline_data(ts_code, start_date, end_date, period)

        # 应用复权
        if adj_type != "none" and period == "daily":
            daily_data = self._apply_adj_factor(ts_code, daily_data, adj_type)

        # 构建K线数据
        kline = [
            StockTrendKlineItem(
                trade_date=item.trade_date,
                open=item.open,
                high=item.high,
                low=item.low,
                close=item.close,
                pre_close=item.pre_close,
                vol=item.vol,
                amount=item.amount,
                pct_chg=item.pct_chg,
            )
            for item in daily_data
        ]

        # 计算均线
        closes = [item.close for item in daily_data if item.close]
        ma = self._calculate_ma(closes)

        # 获取最新行情
        latest = StockTrendLatest()
        if daily_data:
            last = daily_data[-1]
            latest = StockTrendLatest(
                close=last.close,
                pct_chg=last.pct_chg,
                vol=last.vol,
                amount=last.amount,
                open=last.open,
                high=last.high,
                low=last.low,
                pre_close=last.pre_close,
                price_change=last.price_change,
            )

        return StockTrendResponse(
            basic=basic,
            latest=latest,
            kline=kline,
            ma=ma,
        )

    def _get_kline_data(self, ts_code: str, start_date: str, end_date: str, period: str):
        """根据周期获取K线数据"""
        if period == "weekly":
            model = WeeklyData
        elif period == "monthly":
            model = MonthlyData
        else:
            model = self.daily_repo.model

        query = self.db.query(model).filter(model.ts_code == ts_code)
        if start_date:
            query = query.filter(model.trade_date >= start_date)
        if end_date:
            query = query.filter(model.trade_date <= end_date)

        return query.order_by(model.trade_date.asc()).all()

    def _apply_adj_factor(self, ts_code: str, daily_data: list, adj_type: str) -> list:
        """应用复权因子"""
        if not daily_data:
            return daily_data

        # 获取复权因子
        first_date = daily_data[0].trade_date
        last_date = daily_data[-1].trade_date

        adj_factors = self.db.query(AdjFactor).filter(
            AdjFactor.ts_code == ts_code,
            AdjFactor.trade_date >= first_date,
            AdjFactor.trade_date <= last_date,
        ).order_by(AdjFactor.trade_date.asc()).all()

        if not adj_factors:
            return daily_data

        # 构建复权因子字典
        adj_dict = {af.trade_date: af.adj_factor for af in adj_factors}

        # 确定基准因子
        if adj_type == "qfq":
            # 前复权：以最新价格为基准
            base_factor = adj_factors[-1].adj_factor if adj_factors else 1
        else:
            # 后复权：以上市价格为基准
            base_factor = adj_factors[0].adj_factor if adj_factors else 1

        # 应用复权
        for item in daily_data:
            adj = adj_dict.get(item.trade_date, 1)
            if adj and base_factor:
                ratio = base_factor / adj
                if item.open:
                    item.open = item.open * ratio
                if item.high:
                    item.high = item.high * ratio
                if item.low:
                    item.low = item.low * ratio
                if item.close:
                    item.close = item.close * ratio
                if item.pre_close:
                    item.pre_close = item.pre_close * ratio

        return daily_data

    def _calculate_ma(self, closes: List[float]) -> StockTrendMA:
        """计算均线数据"""
        ma5 = self._calculate_ma_line(closes, 5)
        ma10 = self._calculate_ma_line(closes, 10)
        ma20 = self._calculate_ma_line(closes, 20)
        ma30 = self._calculate_ma_line(closes, 30)
        ma60 = self._calculate_ma_line(closes, 60)
        ma90 = self._calculate_ma_line(closes, 90)
        ma125 = self._calculate_ma_line(closes, 125)
        ma250 = self._calculate_ma_line(closes, 250)

        return StockTrendMA(
            ma5=ma5, ma10=ma10, ma20=ma20, ma30=ma30, ma60=ma60,
            ma90=ma90, ma125=ma125, ma250=ma250
        )

    def _calculate_ma_line(
        self, data: List[float], period: int
    ) -> List[Optional[float]]:
        """计算指定周期的均线"""
        result: List[Optional[float]] = []
        for i in range(len(data)):
            if i < period - 1:
                result.append(None)
            else:
                sum_val = sum(data[i - period + 1 : i + 1])
                result.append(round(sum_val / period, 2))
        return result