"""
信号引擎
定义多种信号策略模板，支持灵活组合因子条件
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger


class SignalType(Enum):
    """信号类型"""
    OVERSOLD = "oversold"      # 超跌信号
    TREND = "trend"           # 趋势信号
    VOLUME = "volume"         # 量价信号
    COMBINED = "combined"     # 组合信号
    CUSTOM = "custom"         # 自定义信号


@dataclass
class FactorCondition:
    """因子条件"""
    factor: str                    # 因子名称
    operator: str                  # 操作符: '<', '>', '<=', '>=', '==', 'between'
    value: Any                     # 阈值
    value_max: Optional[float] = None  # between 操作符的上限

    def check(self, factor_value: float) -> bool:
        """检查条件是否满足"""
        if pd.isna(factor_value):
            return False

        if self.operator == '<':
            return factor_value < self.value
        elif self.operator == '<=':
            return factor_value <= self.value
        elif self.operator == '>':
            return factor_value > self.value
        elif self.operator == '>=':
            return factor_value >= self.value
        elif self.operator == '==':
            return factor_value == self.value
        elif self.operator == 'between':
            return self.value <= factor_value <= self.value_max
        return False


@dataclass
class SignalStrategy:
    """信号策略"""
    name: str                           # 策略名称
    signal_type: SignalType             # 信号类型
    conditions: List[FactorCondition]   # 因子条件列表
    combine_mode: str = 'and'           # 组合模式: 'and', 'or'
    weight: float = 1.0                 # 策略权重
    description: str = ""               # 策略描述
    score_func: Optional[Callable] = None  # 自定义评分函数

    def check_signal(self, row: pd.Series) -> bool:
        """检查是否产生信号"""
        results = []
        for cond in self.conditions:
            if cond.factor not in row.index:
                results.append(False)
            else:
                results.append(cond.check(row[cond.factor]))

        if self.combine_mode == 'and':
            return all(results)
        else:  # 'or'
            return any(results)

    def calculate_score(self, row: pd.Series) -> float:
        """计算信号得分"""
        if self.score_func is not None:
            return self.score_func(row)

        # 默认评分：基于满足条件的数量
        score = 0
        for cond in self.conditions:
            if cond.factor in row.index and cond.check(row[cond.factor]):
                score += 1
        return score / len(self.conditions) * self.weight


class SignalEngine:
    """信号引擎"""

    def __init__(self):
        self.strategies: Dict[str, SignalStrategy] = {}
        self._register_builtin_strategies()

    def _register_builtin_strategies(self):
        """注册内置策略"""

        # ============== 超跌策略 ==============

        # KDJ 超跌
        self.register_strategy(SignalStrategy(
            name='kdj_oversold',
            signal_type=SignalType.OVERSOLD,
            conditions=[
                FactorCondition('j_value', '<', 0),
            ],
            description='KDJ J值小于0，超跌信号'
        ))

        # KDJ 深度超跌
        self.register_strategy(SignalStrategy(
            name='kdj_deep_oversold',
            signal_type=SignalType.OVERSOLD,
            conditions=[
                FactorCondition('j_value', '<', -10),
            ],
            description='KDJ J值小于-10，深度超跌'
        ))

        # RSI 超跌
        self.register_strategy(SignalStrategy(
            name='rsi_oversold',
            signal_type=SignalType.OVERSOLD,
            conditions=[
                FactorCondition('rsi6', '<', 20),
            ],
            description='RSI6小于20，超跌信号'
        ))

        # CCI 超跌
        self.register_strategy(SignalStrategy(
            name='cci_oversold',
            signal_type=SignalType.OVERSOLD,
            conditions=[
                FactorCondition('cci', '<', -100),
            ],
            description='CCI小于-100，超跌信号'
        ))

        # WR 超跌
        self.register_strategy(SignalStrategy(
            name='wr_oversold',
            signal_type=SignalType.OVERSOLD,
            conditions=[
                FactorCondition('wr14', '>', 80),
            ],
            description='WR14大于80，超跌信号'
        ))

        # ============== 组合超跌策略 ==============

        # KDJ + RSI 双超跌
        self.register_strategy(SignalStrategy(
            name='kdj_rsi_oversold',
            signal_type=SignalType.COMBINED,
            conditions=[
                FactorCondition('j_value', '<', 0),
                FactorCondition('rsi6', '<', 20),
            ],
            combine_mode='and',
            description='KDJ和RSI同时超跌'
        ))

        # KDJ + RSI + 放量
        self.register_strategy(SignalStrategy(
            name='kdj_rsi_volume',
            signal_type=SignalType.COMBINED,
            conditions=[
                FactorCondition('j_value', '<', -10),
                FactorCondition('rsi6', '<', 15),
                FactorCondition('vol_ratio', '>', 1.0),
            ],
            combine_mode='and',
            description='KDJ超跌 + RSI超跌 + 放量'
        ))

        # 深度超跌组合
        self.register_strategy(SignalStrategy(
            name='deep_oversold_combo',
            signal_type=SignalType.COMBINED,
            conditions=[
                FactorCondition('j_value', '<', -20),
                FactorCondition('rsi6', '<', 10),
            ],
            combine_mode='and',
            description='深度超跌组合'
        ))

        # ============== MACD 策略 ==============

        # MACD 金叉
        self.register_strategy(SignalStrategy(
            name='macd_golden_cross',
            signal_type=SignalType.TREND,
            conditions=[
                FactorCondition('macd_hist', '>', 0),
                FactorCondition('macd_dif', '<', 0),
            ],
            combine_mode='and',
            description='MACD底部金叉'
        ))

        # MACD 柱转正
        self.register_strategy(SignalStrategy(
            name='macd_hist_turn',
            signal_type=SignalType.TREND,
            conditions=[
                FactorCondition('macd_hist', '>', 0),
            ],
            description='MACD柱状图转正'
        ))

        # ============== 布林带策略 ==============

        # 布林带下轨
        self.register_strategy(SignalStrategy(
            name='boll_lower',
            signal_type=SignalType.OVERSOLD,
            conditions=[
                FactorCondition('boll_position', '<', 0),
            ],
            description='价格跌破布林带下轨'
        ))

        # 布林带低位
        self.register_strategy(SignalStrategy(
            name='boll_low_position',
            signal_type=SignalType.OVERSOLD,
            conditions=[
                FactorCondition('boll_position', '<', 0.2),
            ],
            description='价格在布林带下轨附近'
        ))

        # ============== 均线策略 ==============

        # 均线多头排列
        self.register_strategy(SignalStrategy(
            name='ma_bullish',
            signal_type=SignalType.TREND,
            conditions=[
                FactorCondition('ma_alignment', '==', 1),
            ],
            description='均线多头排列'
        ))

        # 均线空头排列
        self.register_strategy(SignalStrategy(
            name='ma_bearish',
            signal_type=SignalType.TREND,
            conditions=[
                FactorCondition('ma_alignment', '==', -1),
            ],
            description='均线空头排列'
        ))

        # 均线偏离超卖
        self.register_strategy(SignalStrategy(
            name='ma_deviation_oversold',
            signal_type=SignalType.OVERSOLD,
            conditions=[
                FactorCondition('ma20_deviation', '<', -0.1),
            ],
            description='价格偏离20日均线超过-10%'
        ))

        # ============== 价格形态策略 ==============

        # 连续下跌后反弹
        self.register_strategy(SignalStrategy(
            name='consecutive_down_rebound',
            signal_type=SignalType.OVERSOLD,
            conditions=[
                FactorCondition('consecutive_down', '>=', 3),
                FactorCondition('drawdown_20d', '<', -0.1),
            ],
            combine_mode='and',
            description='连续下跌3天以上且回撤超过10%'
        ))

        # 深度回撤
        self.register_strategy(SignalStrategy(
            name='deep_drawdown',
            signal_type=SignalType.OVERSOLD,
            conditions=[
                FactorCondition('drawdown_20d', '<', -0.15),
            ],
            description='距20日高点回撤超过15%'
        ))

        # ============== 量价策略 ==============

        # 放量下跌
        self.register_strategy(SignalStrategy(
            name='volume_price_down',
            signal_type=SignalType.VOLUME,
            conditions=[
                FactorCondition('vol_ratio', '>', 1.5),
                FactorCondition('pct_change', '<', 0),
            ],
            combine_mode='and',
            description='放量下跌'
        ))

        # 缩量企稳
        self.register_strategy(SignalStrategy(
            name='shrink_volume_stable',
            signal_type=SignalType.VOLUME,
            conditions=[
                FactorCondition('vol_ratio', '<', 0.5),
                FactorCondition('amplitude', '<', 0.02),
            ],
            combine_mode='and',
            description='缩量企稳'
        ))

        # ============== 综合策略 ==============

        # 超跌共振
        self.register_strategy(SignalStrategy(
            name='oversold_resonance',
            signal_type=SignalType.COMBINED,
            conditions=[
                FactorCondition('j_value', '<', 0),
                FactorCondition('rsi6', '<', 20),
                FactorCondition('cci', '<', -100),
            ],
            combine_mode='and',
            description='KDJ+RSI+CCI三指标超跌共振'
        ))

        # 超跌+趋势反转
        self.register_strategy(SignalStrategy(
            name='oversold_reversal',
            signal_type=SignalType.COMBINED,
            conditions=[
                FactorCondition('j_value', '<', -10),
                FactorCondition('macd_hist', '>', 0),
                FactorCondition('vol_ratio', '>', 1.0),
            ],
            combine_mode='and',
            description='超跌+MACD金叉+放量'
        ))

        # 完整买入信号
        self.register_strategy(SignalStrategy(
            name='full_buy_signal',
            signal_type=SignalType.COMBINED,
            conditions=[
                FactorCondition('j_value', '<', -10),
                FactorCondition('rsi6', '<', 15),
                FactorCondition('vol_ratio', '>', 1.0),
                FactorCondition('drawdown_20d', '<', -0.05),
            ],
            combine_mode='and',
            description='完整买入信号：超跌+放量+回撤'
        ))

    def register_strategy(self, strategy: SignalStrategy):
        """注册策略"""
        self.strategies[strategy.name] = strategy

    def get_strategy(self, name: str) -> Optional[SignalStrategy]:
        """获取策略"""
        return self.strategies.get(name)

    def list_strategies(self, signal_type: Optional[SignalType] = None) -> List[SignalStrategy]:
        """列出策略"""
        strategies = list(self.strategies.values())
        if signal_type:
            strategies = [s for s in strategies if s.signal_type == signal_type]
        return strategies

    def detect_signals(
        self,
        df: pd.DataFrame,
        strategy_names: Optional[List[str]] = None,
        min_score: float = 0.0
    ) -> pd.DataFrame:
        """
        检测信号

        Args:
            df: 指标数据
            strategy_names: 策略名称列表，None 表示全部
            min_score: 最小得分阈值

        Returns:
            添加了信号列的 DataFrame
        """
        result_df = df.copy()

        if strategy_names is None:
            strategy_names = list(self.strategies.keys())

        # 为每个策略添加信号列
        for name in strategy_names:
            strategy = self.strategies.get(name)
            if strategy is None:
                logger.warning(f"策略 {name} 不存在，跳过")
                continue

            result_df[f'signal_{name}'] = result_df.apply(
                lambda row: strategy.check_signal(row), axis=1
            )
            result_df[f'score_{name}'] = result_df.apply(
                lambda row: strategy.calculate_score(row), axis=1
            )

        # 综合信号
        signal_cols = [f'signal_{name}' for name in strategy_names]
        result_df['has_signal'] = result_df[signal_cols].any(axis=1)

        # 信号数量
        result_df['signal_count'] = result_df[signal_cols].sum(axis=1)

        # 综合得分
        score_cols = [f'score_{name}' for name in strategy_names]
        result_df['total_score'] = result_df[score_cols].sum(axis=1)

        # 信号类型列表
        def get_signal_types(row):
            types = []
            for name in strategy_names:
                if row.get(f'signal_{name}', False):
                    types.append(name)
            return '|'.join(types) if types else ''

        result_df['signal_types'] = result_df.apply(get_signal_types, axis=1)

        return result_df

    def get_signals_by_date(
        self,
        df: pd.DataFrame,
        trade_date: str,
        strategy_names: Optional[List[str]] = None,
        sort_by: str = 'total_score',
        ascending: bool = False
    ) -> pd.DataFrame:
        """
        获取指定日期的信号股票

        Args:
            df: 已检测信号的指标数据
            trade_date: 交易日期
            strategy_names: 策略名称列表
            sort_by: 排序字段
            ascending: 是否升序

        Returns:
            信号股票列表
        """
        day_df = df[df['trade_date'] == trade_date].copy()
        day_df = day_df[day_df['has_signal'] == True]

        if len(day_df) == 0:
            return pd.DataFrame()

        return day_df.sort_values(sort_by, ascending=ascending)

    def create_custom_strategy(
        self,
        name: str,
        conditions: List[Dict],
        combine_mode: str = 'and',
        description: str = ""
    ) -> SignalStrategy:
        """
        创建自定义策略

        Args:
            name: 策略名称
            conditions: 条件列表，格式: [{'factor': 'j_value', 'operator': '<', 'value': 0}]
            combine_mode: 组合模式
            description: 描述

        Returns:
            SignalStrategy 对象
        """
        factor_conditions = []
        for cond in conditions:
            fc = FactorCondition(
                factor=cond['factor'],
                operator=cond['operator'],
                value=cond['value'],
                value_max=cond.get('value_max')
            )
            factor_conditions.append(fc)

        strategy = SignalStrategy(
            name=name,
            signal_type=SignalType.CUSTOM,
            conditions=factor_conditions,
            combine_mode=combine_mode,
            description=description
        )

        self.register_strategy(strategy)
        return strategy


def run_signal_detection(
    start_date: str = '20240101',
    end_date: str = '20260424',
    strategies: Optional[List[str]] = None
):
    """运行信号检测"""
    from app.core.database import get_db_context
    from sqlalchemy import text

    with get_db_context() as db:
        # 加载指标数据
        query = text("""
            SELECT * FROM daily_indicator
            WHERE trade_date >= :start_date
              AND trade_date <= :end_date
            ORDER BY ts_code, trade_date
        """)
        df = pd.read_sql(query, db.bind, params={'start_date': start_date, 'end_date': end_date})
        logger.info(f"加载数据: {len(df)} 条")

        # 初始化信号引擎
        engine = SignalEngine()

        # 检测信号
        logger.info("检测信号...")
        result_df = engine.detect_signals(df, strategies)

        # 统计
        signal_count = result_df['has_signal'].sum()
        logger.info(f"检测到信号: {signal_count} 条")

        # 按策略统计
        print("\n【各策略信号统计】")
        for name in engine.strategies.keys():
            col = f'signal_{name}'
            if col in result_df.columns:
                count = result_df[col].sum()
                print(f"  {name}: {count} 条")

        return result_df


if __name__ == "__main__":
    run_signal_detection()
