"""
超短线模式回测分析
持仓1-3天，快进快出
"""
import sys
import os
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

import pandas as pd
from loguru import logger
from datetime import datetime

from app.core.database import get_db_context
from strategy.signal_engine import SignalEngine, SignalStrategy, SignalType, FactorCondition
from strategy.backtest_engine import BacktestEngine, BacktestConfig


def run_ultrashort_backtest():
    """超短线模式回测分析"""
    logger.info("=" * 80)
    logger.info("超短线模式回测分析")
    logger.info("=" * 80)

    # 测试两个策略
    strategies_to_test = [
        {
            'name': 'oversold_reversal',
            'conditions': [
                FactorCondition('j_value', '<', -10),
                FactorCondition('macd_hist', '>', 0),
                FactorCondition('vol_ratio', '>', 1.0),
            ],
            'description': 'J<-10 + MACD金叉 + 放量'
        },
        {
            'name': 'custom_j_rsi_vol',
            'conditions': [
                FactorCondition('j_value', '<', -10),
                FactorCondition('rsi6', '<', 15),
                FactorCondition('vol_ratio', '>', 1.0),
            ],
            'description': 'J<-10 + RSI<15 + 放量'
        }
    ]

    # 超短线配置组
    ultra_short_configs = [
        # 配置1: 极端超短线 - 持仓1天
        BacktestConfig(
            initial_capital=1000000,
            max_positions=5,
            position_size=0.18,
            max_hold_days=1,          # 只持仓1天
            stop_loss_pct=-0.03,      # 3%止损
            take_profit_pct=0.05,     # 5%止盈
            commission_rate=0.0003,
            stamp_duty_rate=0.001,
            slippage=0.001
        ),
        # 配置2: 标准超短线 - 持仓2天
        BacktestConfig(
            initial_capital=1000000,
            max_positions=5,
            position_size=0.18,
            max_hold_days=2,          # 持仓2天
            stop_loss_pct=-0.04,      # 4%止损
            take_profit_pct=0.06,     # 6%止盈
            commission_rate=0.0003,
            stamp_duty_rate=0.001,
            slippage=0.001
        ),
        # 配置3: 宽松超短线 - 持仓3天
        BacktestConfig(
            initial_capital=1000000,
            max_positions=5,
            position_size=0.18,
            max_hold_days=3,          # 持仓3天
            stop_loss_pct=-0.05,      # 5%止损
            take_profit_pct=0.08,     # 8%止盈
            commission_rate=0.0003,
            stamp_duty_rate=0.001,
            slippage=0.001
        ),
    ]

    config_names = ['持仓1天(3%止损/5%止盈)', '持仓2天(4%止损/6%止盈)', '持仓3天(5%止损/8%止盈)']

    start_date = '20240101'
    end_date = '20260424'

    results = []

    with get_db_context() as db:
        for strat in strategies_to_test:
            logger.info(f"\n测试策略: {strat['name']}")

            for config_idx, config in enumerate(ultra_short_configs):
                logger.info(f"  配置: {config_names[config_idx]}")

                # 创建策略
                custom_strategy = SignalStrategy(
                    name=strat['name'],
                    signal_type=SignalType.CUSTOM,
                    conditions=strat['conditions'],
                    combine_mode='and',
                    description=strat['description']
                )

                engine = BacktestEngine(config)
                engine.signal_engine.register_strategy(custom_strategy)

                # 运行回测
                performance = engine.run_backtest(
                    db, start_date, end_date,
                    strategy_names=[strat['name']],
                    min_score=0.3
                )

                results.append({
                    'strategy': strat['name'],
                    'config': config_names[config_idx],
                    'max_hold_days': config.max_hold_days,
                    'stop_loss': config.stop_loss_pct,
                    'take_profit': config.take_profit_pct,
                    'performance': performance,
                })

    # 输出对比报告
    print("\n" + "=" * 100)
    print("超短线模式回测分析报告")
    print("=" * 100)

    # 按策略分组输出
    for strat_name in ['oversold_reversal', 'custom_j_rsi_vol']:
        print(f"\n{'=' * 100}")
        print(f"策略: {strat_name}")
        print("=" * 100)

        strat_results = [r for r in results if r['strategy'] == strat_name]

        print(f"\n{'配置':<30}{'总收益':<12}{'年化收益':<12}{'最大回撤':<12}{'夏普':<12}{'胜率':<12}{'交易次数':<10}")
        print("-" * 100)

        for r in strat_results:
            perf = r['performance']
            print(f"{r['config']:<30}{perf['total_return']:>10.2%}  {perf['annual_return']:>10.2%}  "
                  f"{perf['max_drawdown']:>10.2%}  {perf['sharpe_ratio']:>10.4f}  "
                  f"{perf['win_rate']:>10.2%}  {perf['total_trades']:>8d}")

        # 找出该策略最佳配置
        best = max(strat_results, key=lambda x: x['performance']['total_return'])
        print(f"\n最佳配置: {best['config']}")
        print(f"  总收益: {best['performance']['total_return']:.2%}")
        print(f"  胜率: {best['performance']['win_rate']:.2%}")
        print(f"  夏普比率: {best['performance']['sharpe_ratio']:.4f}")

    # 策略横向对比
    print("\n" + "=" * 100)
    print("【策略横向对比】")
    print("=" * 100)

    # 找出每个策略的最佳配置
    best_results = {}
    for strat_name in ['oversold_reversal', 'custom_j_rsi_vol']:
        strat_results = [r for r in results if r['strategy'] == strat_name]
        best = max(strat_results, key=lambda x: x['performance']['total_return'])
        best_results[strat_name] = best

    print(f"\n{'策略':<25}{'最佳配置':<30}{'总收益':<12}{'胜率':<12}{'夏普':<12}{'交易次数':<10}")
    print("-" * 100)
    for strat_name, best in best_results.items():
        perf = best['performance']
        print(f"{strat_name:<25}{best['config']:<30}{perf['total_return']:>10.2%}  "
              f"{perf['win_rate']:>10.2%}  {perf['sharpe_ratio']:>10.4f}  {perf['total_trades']:>8d}")

    # 与原配置对比
    print("\n" + "=" * 100)
    print("【超短线 vs 原配置(持仓10天)对比】")
    print("=" * 100)

    print(f"\n{'策略':<25}{'模式':<20}{'总收益':<12}{'胜率':<12}{'夏普':<12}{'交易次数':<10}")
    print("-" * 100)

    # 原配置数据（从之前的回测结果）
    original_results = {
        'oversold_reversal': {'total_return': 0.3321, 'win_rate': 0.5694, 'sharpe_ratio': 1.7095, 'total_trades': 290},
        'custom_j_rsi_vol': {'total_return': -0.2682, 'win_rate': 0.4119, 'sharpe_ratio': -1.1795, 'total_trades': 705}
    }

    for strat_name in ['oversold_reversal', 'custom_j_rsi_vol']:
        # 原配置
        orig = original_results[strat_name]
        print(f"{strat_name:<25}{'原配置(10天)':<20}{orig['total_return']:>10.2%}  "
              f"{orig['win_rate']:>10.2%}  {orig['sharpe_ratio']:>10.4f}  {orig['total_trades']:>8d}")

        # 最佳超短线配置
        best = best_results[strat_name]
        perf = best['performance']
        print(f"{'':<25}{'超短线最佳':<20}{perf['total_return']:>10.2%}  "
              f"{perf['win_rate']:>10.2%}  {perf['sharpe_ratio']:>10.4f}  {perf['total_trades']:>8d}")
        print()

    # 结论
    print("\n" + "=" * 100)
    print("【超短线模式分析结论】")
    print("=" * 100)

    best_overall = max(results, key=lambda x: x['performance']['total_return'])
    print(f"""
最优超短线配置:
  策略: {best_overall['strategy']}
  配置: {best_overall['config']}

绩效表现:
  总收益: {best_overall['performance']['total_return']:.2%}
  年化收益: {best_overall['performance']['annual_return']:.2%}
  最大回撤: {best_overall['performance']['max_drawdown']:.2%}
  夏普比率: {best_overall['performance']['sharpe_ratio']:.4f}
  胜率: {best_overall['performance']['win_rate']:.2%}
  交易次数: {best_overall['performance']['total_trades']}

超短线模式特点:
  1. 交易频率大幅增加，需要更高的胜率才能盈利
  2. 手续费和滑点成本对收益影响更大
  3. 止损更严格，单笔亏损更小但止损次数更多
  4. 适合波动较大的市场环境
""")

    return results


if __name__ == "__main__":
    run_ultrashort_backtest()
