"""
测试用户自定义策略：J<-10 + RSI<15 + 量比>1
"""
import sys
import os
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

from loguru import logger
from datetime import datetime

from app.core.database import get_db_context
from strategy.signal_engine import SignalEngine, SignalStrategy, SignalType, FactorCondition
from strategy.backtest_engine import BacktestEngine, BacktestConfig


def test_custom_strategy():
    """测试自定义策略"""
    logger.info("=" * 80)
    logger.info("测试自定义策略: J<-10 + RSI<15 + 量比>1")
    logger.info("=" * 80)

    # 创建自定义策略
    custom_strategy = SignalStrategy(
        name='custom_j_rsi_vol',
        signal_type=SignalType.CUSTOM,
        conditions=[
            FactorCondition('j_value', '<', -10),      # J值 < -10
            FactorCondition('rsi6', '<', 15),          # RSI6 < 15
            FactorCondition('vol_ratio', '>', 1.0),    # 量比 > 1
        ],
        combine_mode='and',
        description='自定义策略: J<-10 + RSI<15 + 量比>1'
    )

    # 回测配置
    config = BacktestConfig(
        initial_capital=1000000,
        max_positions=5,
        position_size=0.15,
        max_hold_days=10,
        stop_loss_pct=-0.05,
        take_profit_pct=0.08,
        commission_rate=0.0003,
        stamp_duty_rate=0.001,
        slippage=0.001
    )

    start_date = '20240101'
    end_date = '20260424'

    with get_db_context() as db:
        engine = BacktestEngine(config)

        # 注册自定义策略
        engine.signal_engine.register_strategy(custom_strategy)

        # 运行回测
        performance = engine.run_backtest(
            db, start_date, end_date,
            strategy_names=['custom_j_rsi_vol'],
            min_score=0.3
        )

        # 打印绩效
        engine.print_performance(performance)

        # 与 oversold_reversal 对比
        logger.info("\n" + "=" * 80)
        logger.info("与 oversold_reversal 策略对比")
        logger.info("=" * 80)

        # 运行 oversold_reversal 作为基准
        engine2 = BacktestEngine(config)
        perf_baseline = engine2.run_backtest(
            db, start_date, end_date,
            strategy_names=['oversold_reversal'],
            min_score=0.3
        )

        print("\n【对比结果】")
        print("-" * 80)
        print(f"{'指标':<20}{'自定义策略':<20}{'oversold_reversal':<20}")
        print("-" * 80)
        print(f"{'总收益':<20}{performance['total_return']:>18.2%}  {perf_baseline['total_return']:>18.2%}")
        print(f"{'年化收益':<20}{performance['annual_return']:>18.2%}  {perf_baseline['annual_return']:>18.2%}")
        print(f"{'最大回撤':<20}{performance['max_drawdown']:>18.2%}  {perf_baseline['max_drawdown']:>18.2%}")
        print(f"{'夏普比率':<20}{performance['sharpe_ratio']:>18.4f}  {perf_baseline['sharpe_ratio']:>18.4f}")
        print(f"{'胜率':<20}{performance['win_rate']:>18.2%}  {perf_baseline['win_rate']:>18.2%}")
        print(f"{'交易次数':<20}{performance['total_trades']:>18d}  {perf_baseline['total_trades']:>18d}")
        print(f"{'平均盈亏':<20}{performance['avg_profit_pct']:>18.2%}  {perf_baseline['avg_profit_pct']:>18.2%}")
        print("-" * 80)

        return performance, perf_baseline


if __name__ == "__main__":
    test_custom_strategy()