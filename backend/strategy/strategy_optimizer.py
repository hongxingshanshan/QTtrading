"""
策略优化分析
寻找收益+胜率+回撤最优的策略组合
"""
import sys
import os
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from loguru import logger
from sqlalchemy import text
from datetime import datetime

from app.core.database import get_db_context
from strategy.signal_engine import SignalEngine, SignalStrategy, FactorCondition
from strategy.backtest_engine import BacktestEngine, BacktestConfig


def run_strategy_optimization():
    """
    运行策略优化分析
    测试不同策略组合，找到最优配置
    """
    logger.info("=" * 80)
    logger.info("策略优化分析 - 寻找最优策略组合")
    logger.info("=" * 80)

    # 定义测试的策略组合
    strategy_combinations = [
        # 单因子策略
        ['kdj_oversold'],
        ['kdj_deep_oversold'],
        ['rsi_oversold'],
        ['cci_oversold'],
        ['wr_oversold'],
        ['boll_lower'],
        ['macd_golden_cross'],

        # 双因子组合
        ['kdj_oversold', 'rsi_oversold'],
        ['kdj_deep_oversold', 'rsi_oversold'],
        ['kdj_oversold', 'cci_oversold'],
        ['kdj_oversold', 'boll_lower'],
        ['rsi_oversold', 'cci_oversold'],
        ['rsi_oversold', 'wr_oversold'],

        # 三因子组合
        ['kdj_oversold', 'rsi_oversold', 'cci_oversold'],
        ['kdj_deep_oversold', 'rsi_oversold', 'cci_oversold'],
        ['kdj_oversold', 'rsi_oversold', 'wr_oversold'],

        # 内置组合策略
        ['kdj_rsi_oversold'],
        ['kdj_rsi_volume'],
        ['deep_oversold_combo'],
        ['oversold_resonance'],
        ['oversold_reversal'],
        ['full_buy_signal'],

        # 趋势+超跌组合
        ['kdj_oversold', 'macd_golden_cross'],
        ['rsi_oversold', 'macd_golden_cross'],
        ['kdj_oversold', 'macd_hist_turn'],

        # 量价+超跌组合
        ['kdj_oversold', 'volume_price_down'],
        ['kdj_deep_oversold', 'shrink_volume_stable'],
    ]

    # 定义不同的回测配置
    configs = [
        BacktestConfig(
            initial_capital=1000000,
            max_positions=5,
            position_size=0.15,
            max_hold_days=10,
            stop_loss_pct=-0.05,
            take_profit_pct=0.08,
            commission_rate=0.0003,
            stamp_duty_rate=0.001,
            slippage=0.001
        ),
        BacktestConfig(
            initial_capital=1000000,
            max_positions=8,
            position_size=0.12,
            max_hold_days=15,
            stop_loss_pct=-0.08,
            take_profit_pct=0.12,
            commission_rate=0.0003,
            stamp_duty_rate=0.001,
            slippage=0.001
        ),
        BacktestConfig(
            initial_capital=1000000,
            max_positions=10,
            position_size=0.10,
            max_hold_days=20,
            stop_loss_pct=-0.10,
            take_profit_pct=0.15,
            commission_rate=0.0003,
            stamp_duty_rate=0.001,
            slippage=0.001
        ),
    ]

    # 回测参数
    start_date = '20240101'
    end_date = '20260424'

    results = []

    with get_db_context() as db:
        total_tests = len(strategy_combinations) * len(configs)
        test_count = 0

        for config_idx, config in enumerate(configs):
            logger.info(f"\n测试配置 {config_idx + 1}: 持仓{config.max_positions}只, 止损{config.stop_loss_pct:.0%}, 止盈{config.take_profit_pct:.0%}")

            for strategies in strategy_combinations:
                test_count += 1

                try:
                    engine = BacktestEngine(config)
                    performance = engine.run_backtest(
                        db, start_date, end_date,
                        strategy_names=strategies,
                        min_score=0.3
                    )

                    if performance and performance.get('total_trades', 0) > 0:
                        result = {
                            'strategies': '|'.join(strategies),
                            'config': f"持仓{config.max_positions}_止损{config.stop_loss_pct:.0%}_止盈{config.take_profit_pct:.0%}",
                            'max_positions': config.max_positions,
                            'stop_loss': config.stop_loss_pct,
                            'take_profit': config.take_profit_pct,
                            'max_hold_days': config.max_hold_days,
                            'total_return': performance['total_return'],
                            'annual_return': performance['annual_return'],
                            'max_drawdown': performance['max_drawdown'],
                            'sharpe_ratio': performance['sharpe_ratio'],
                            'win_rate': performance['win_rate'],
                            'total_trades': performance['total_trades'],
                            'avg_profit_pct': performance['avg_profit_pct'],
                            'final_value': performance['final_value'],
                        }
                        results.append(result)

                        logger.info(
                            f"[{test_count}/{total_tests}] {strategies}: "
                            f"收益={performance['total_return']:.2%}, "
                            f"胜率={performance['win_rate']:.2%}, "
                            f"回撤={performance['max_drawdown']:.2%}"
                        )

                except Exception as e:
                    logger.error(f"[{test_count}/{total_tests}] {strategies} 失败: {e}")

    # 分析结果
    if len(results) == 0:
        logger.warning("没有有效的回测结果")
        return None

    results_df = pd.DataFrame(results)

    # 计算综合评分
    # 评分公式: 收益权重0.4 + 胜率权重0.3 + (1-回撤绝对值)权重0.3
    results_df['score'] = (
        results_df['total_return'] * 0.4 +
        results_df['win_rate'] * 0.3 +
        (1 - results_df['max_drawdown'].abs()) * 0.3
    )

    # 排序
    results_df = results_df.sort_values('score', ascending=False)

    # 输出结果
    print("\n" + "=" * 100)
    print("策略优化分析结果")
    print("=" * 100)

    # Top 10 策略
    print("\n【Top 10 最优策略组合】")
    print("-" * 100)

    top10 = results_df.head(10)
    for i, row in top10.iterrows():
        print(f"\n排名 {top10.index.get_loc(i) + 1}:")
        print(f"  策略组合: {row['strategies']}")
        print(f"  配置: {row['config']}")
        print(f"  总收益: {row['total_return']:.2%}")
        print(f"  年化收益: {row['annual_return']:.2%}")
        print(f"  最大回撤: {row['max_drawdown']:.2%}")
        print(f"  夏普比率: {row['sharpe_ratio']:.4f}")
        print(f"  胜率: {row['win_rate']:.2%}")
        print(f"  交易次数: {row['total_trades']}")
        print(f"  平均盈亏: {row['avg_profit_pct']:.2%}")
        print(f"  综合评分: {row['score']:.4f}")

    # 按策略类型汇总
    print("\n" + "-" * 100)
    print("【各策略类型表现汇总】")
    print("-" * 100)

    # 单因子策略
    single_factor = results_df[results_df['strategies'].str.count('|') == 0]
    if len(single_factor) > 0:
        print("\n单因子策略平均表现:")
        print(f"  平均收益: {single_factor['total_return'].mean():.2%}")
        print(f"  平均胜率: {single_factor['win_rate'].mean():.2%}")
        print(f"  平均回撤: {single_factor['max_drawdown'].mean():.2%}")
        best_single = single_factor.iloc[0]
        print(f"  最佳单因子: {best_single['strategies']} (收益={best_single['total_return']:.2%})")

    # 双因子组合
    double_factor = results_df[results_df['strategies'].str.count('|') == 1]
    if len(double_factor) > 0:
        print("\n双因子组合平均表现:")
        print(f"  平均收益: {double_factor['total_return'].mean():.2%}")
        print(f"  平均胜率: {double_factor['win_rate'].mean():.2%}")
        print(f"  平均回撤: {double_factor['max_drawdown'].mean():.2%}")
        best_double = double_factor.iloc[0]
        print(f"  最佳双因子: {best_double['strategies']} (收益={best_double['total_return']:.2%})")

    # 三因子组合
    triple_factor = results_df[results_df['strategies'].str.count('|') == 2]
    if len(triple_factor) > 0:
        print("\n三因子组合平均表现:")
        print(f"  平均收益: {triple_factor['total_return'].mean():.2%}")
        print(f"  平均胜率: {triple_factor['win_rate'].mean():.2%}")
        print(f"  平均回撤: {triple_factor['max_drawdown'].mean():.2%}")
        best_triple = triple_factor.iloc[0]
        print(f"  最佳三因子: {best_triple['strategies']} (收益={best_triple['total_return']:.2%})")

    # 内置组合策略
    builtin = results_df[results_df['strategies'].isin([
        'kdj_rsi_oversold', 'kdj_rsi_volume', 'deep_oversold_combo',
        'oversold_resonance', 'oversold_reversal', 'full_buy_signal'
    ])]
    if len(builtin) > 0:
        print("\n内置组合策略表现:")
        print(f"  平均收益: {builtin['total_return'].mean():.2%}")
        print(f"  平均胜率: {builtin['win_rate'].mean():.2%}")
        print(f"  平均回撤: {builtin['max_drawdown'].mean():.2%}")
        best_builtin = builtin.iloc[0]
        print(f"  最佳内置策略: {best_builtin['strategies']} (收益={best_builtin['total_return']:.2%})")

    # 按配置汇总
    print("\n" + "-" * 100)
    print("【各配置表现汇总】")
    print("-" * 100)

    for config_idx in range(3):
        config_results = results_df[results_df['max_positions'] == configs[config_idx].max_positions]
        if len(config_results) > 0:
            print(f"\n配置 {config_idx + 1} (持仓{configs[config_idx].max_positions}只, 止损{configs[config_idx].stop_loss_pct:.0%}, 止盈{configs[config_idx].take_profit_pct:.0%}):")
            print(f"  平均收益: {config_results['total_return'].mean():.2%}")
            print(f"  平均胜率: {config_results['win_rate'].mean():.2%}")
            print(f"  平均回撤: {config_results['max_drawdown'].mean():.2%}")
            print(f"  平均夏普: {config_results['sharpe_ratio'].mean():.4f}")

    # 保存结果
    output_dir = 'strategy/optimization_results'
    import os
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_df.to_csv(f'{output_dir}/strategy_optimization_{timestamp}.csv', index=False, encoding='utf-8-sig')

    print(f"\n详细结果已保存: {output_dir}/strategy_optimization_{timestamp}.csv")

    # 最终推荐
    print("\n" + "=" * 100)
    print("【最终推荐策略】")
    print("=" * 100)

    best = results_df.iloc[0]
    print(f"""
最优策略组合:
  策略: {best['strategies']}
  配置: 持仓{best['max_positions']}只, 止损{best['stop_loss']:.0%}, 止盈{best['take_profit']:.0%}, 持仓{best['max_hold_days']}天

绩效表现:
  总收益: {best['total_return']:.2%}
  年化收益: {best['annual_return']:.2%}
  最大回撤: {best['max_drawdown']:.2%}
  夏普比率: {best['sharpe_ratio']:.4f}
  胜率: {best['win_rate']:.2%}
  交易次数: {best['total_trades']}
  平均盈亏: {best['avg_profit_pct']:.2%}

综合评分: {best['score']:.4f}
""")

    return results_df


if __name__ == "__main__":
    run_strategy_optimization()