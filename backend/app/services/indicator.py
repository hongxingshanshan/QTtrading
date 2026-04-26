"""
技术指标查询服务
提供预计算指标数据的查询接口
"""
from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models.indicator import DailyIndicator
import pandas as pd


class IndicatorService:
    """技术指标查询服务"""

    @staticmethod
    def get_indicator_by_code(
        db: Session,
        ts_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[dict]:
        """
        获取单只股票的技术指标

        Args:
            db: 数据库会话
            ts_code: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)

        Returns:
            指标数据列表
        """
        query = db.query(DailyIndicator).filter(DailyIndicator.ts_code == ts_code)

        if start_date:
            query = query.filter(DailyIndicator.trade_date >= start_date)
        if end_date:
            query = query.filter(DailyIndicator.trade_date <= end_date)

        query = query.order_by(DailyIndicator.trade_date)

        return [
            {
                'ts_code': row.ts_code,
                'trade_date': row.trade_date,
                # KDJ
                'k_value': row.k_value,
                'd_value': row.d_value,
                'j_value': row.j_value,
                # RSI
                'rsi6': row.rsi6,
                'rsi12': row.rsi12,
                'rsi24': row.rsi24,
                # MACD
                'macd_dif': row.macd_dif,
                'macd_dea': row.macd_dea,
                'macd_hist': row.macd_hist,
                # BOLL
                'boll_upper': row.boll_upper,
                'boll_mid': row.boll_mid,
                'boll_lower': row.boll_lower,
                'boll_width': row.boll_width,
                'boll_position': row.boll_position,
                # MA
                'ma5': row.ma5,
                'ma10': row.ma10,
                'ma20': row.ma20,
                'ma30': row.ma30,
                'ma60': row.ma60,
                'ma_alignment': row.ma_alignment,
                # 其他指标
                'cci': row.cci,
                'wr14': row.wr14,
                'obv': row.obv,
                # 成交量因子
                'vol_ratio': row.vol_ratio,
                # 价格形态
                'consecutive_down': row.consecutive_down,
                'drawdown_20d': row.drawdown_20d,
                'rebound_20d': row.rebound_20d,
                'amplitude': row.amplitude,
            }
            for row in query.all()
        ]

    @staticmethod
    def get_indicator_dataframe(
        db: Session,
        ts_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取单只股票的技术指标 DataFrame

        Args:
            db: 数据库会话
            ts_code: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)

        Returns:
            pandas DataFrame
        """
        data = IndicatorService.get_indicator_by_code(db, ts_code, start_date, end_date)
        return pd.DataFrame(data)

    @staticmethod
    def get_signals_by_date(
        db: Session,
        trade_date: str,
        j_threshold: float = -10,
        rsi_threshold: float = 15,
        vol_ratio_min: float = 1.0
    ) -> List[dict]:
        """
        获取指定日期满足条件的信号股票

        Args:
            db: 数据库会话
            trade_date: 交易日期 (YYYYMMDD)
            j_threshold: J值阈值
            rsi_threshold: RSI阈值
            vol_ratio_min: 最小量比

        Returns:
            信号股票列表
        """
        query = text("""
            SELECT ts_code, trade_date, j_value, k_value, d_value,
                   rsi6, rsi12, rsi24, macd_dif, macd_dea, macd_hist,
                   vol_ratio, drawdown_20d, consecutive_down, ma_alignment
            FROM daily_indicator
            WHERE trade_date = :trade_date
              AND j_value < :j_threshold
              AND rsi6 < :rsi_threshold
              AND vol_ratio > :vol_ratio_min
            ORDER BY j_value ASC
        """)

        result = db.execute(query, {
            'trade_date': trade_date,
            'j_threshold': j_threshold,
            'rsi_threshold': rsi_threshold,
            'vol_ratio_min': vol_ratio_min
        })

        return [
            {
                'ts_code': row[0],
                'trade_date': row[1],
                'j_value': row[2],
                'k_value': row[3],
                'd_value': row[4],
                'rsi6': row[5],
                'rsi12': row[6],
                'rsi24': row[7],
                'macd_dif': row[8],
                'macd_dea': row[9],
                'macd_hist': row[10],
                'vol_ratio': row[11],
                'drawdown_20d': row[12],
                'consecutive_down': row[13],
                'ma_alignment': row[14],
            }
            for row in result.fetchall()
        ]

    @staticmethod
    def get_combined_signals(
        db: Session,
        trade_date: str,
        j_threshold: float = -10,
        rsi_threshold: float = 15,
        vol_ratio_min: float = 1.0
    ) -> List[dict]:
        """
        获取满足组合条件的信号

        Args:
            db: 数据库会话
            trade_date: 交易日期 (YYYYMMDD)
            j_threshold: J值阈值
            rsi_threshold: RSI阈值
            vol_ratio_min: 最小量比

        Returns:
            满足条件的股票列表
        """
        query = text("""
            SELECT ts_code, trade_date, j_value, k_value, d_value,
                   rsi6, rsi12, rsi24, macd_dif, macd_dea, macd_hist,
                   vol_ratio, drawdown_20d, consecutive_down, ma_alignment
            FROM daily_indicator
            WHERE trade_date = :trade_date
              AND j_value < :j_threshold
              AND rsi6 < :rsi_threshold
              AND vol_ratio > :vol_ratio_min
            ORDER BY j_value ASC
        """)

        result = db.execute(query, {
            'trade_date': trade_date,
            'j_threshold': j_threshold,
            'rsi_threshold': rsi_threshold,
            'vol_ratio_min': vol_ratio_min
        })

        return [
            {
                'ts_code': row[0],
                'trade_date': row[1],
                'j_value': row[2],
                'k_value': row[3],
                'd_value': row[4],
                'rsi6': row[5],
                'rsi12': row[6],
                'rsi24': row[7],
                'macd_dif': row[8],
                'macd_dea': row[9],
                'macd_hist': row[10],
                'vol_ratio': row[11],
                'drawdown_20d': row[12],
                'consecutive_down': row[13],
                'ma_alignment': row[14],
            }
            for row in result.fetchall()
        ]

    @staticmethod
    def get_all_indicators_batch(
        db: Session,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        批量获取所有股票的指标数据（用于策略回测）

        Args:
            db: 数据库会话
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)

        Returns:
            pandas DataFrame
        """
        query = "SELECT * FROM daily_indicator WHERE 1=1"
        params = {}

        if start_date:
            query += " AND trade_date >= :start_date"
            params['start_date'] = start_date
        if end_date:
            query += " AND trade_date <= :end_date"
            params['end_date'] = end_date

        query += " ORDER BY ts_code, trade_date"

        df = pd.read_sql(text(query), db.bind, params=params)
        return df

    @staticmethod
    def get_indicator_stats(db: Session) -> dict:
        """
        获取指标数据统计信息

        Returns:
            统计信息字典
        """
        # 总记录数
        total_count = db.execute(text("SELECT COUNT(*) FROM daily_indicator")).scalar()

        # 股票数量
        stock_count = db.execute(text("SELECT COUNT(DISTINCT ts_code) FROM daily_indicator")).scalar()

        # 日期范围
        date_range = db.execute(text("""
            SELECT MIN(trade_date), MAX(trade_date) FROM daily_indicator
        """)).fetchone()

        return {
            'total_count': total_count,
            'stock_count': stock_count,
            'date_range': {
                'start': date_range[0],
                'end': date_range[1]
            }
        }
