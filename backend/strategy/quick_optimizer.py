"""
快速策略优化分析
只测试最关键的策略组合，快速找到最优配置
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
from typing import List, Dict
from loguru import logger
from sqlalchemy import text
from datetime import datetime

from app.core.database import get_db_context
from strategy.signal_engine import SignalEngine
from strategy.backtest_engine import BacktestEngine, BacktestConfig


def run_quick_optimization():
    """
    快速策略优化 - 只测试最有潜力的组合
    """
    logger.info("=" * 80)
    logger.info("快速策略优化分析")
    logger.info("=" * 80)

    # 精选策略组合（基于之前的分析，选择最有潜力的）
    strategy_combinations = [
        # 单因子 - 深度超跌类
        ['kdj_deep_oversold'],      # J值<-10
        ['cci_oversold'],           # CCI<-100
        ['wr_oversold'],            # WR>80
        ['boll_lower'],             # 布林带下轨

        # 双因子组合
        ['kdj_deep_oversold', 'rsi_oversold'],
        ['kdj_oversold', 'cci_oversold'],
        ['rsi_oversold', 'wr_oversold'],
        ['kdj_oversold', 'boll_lower'],

        # 三因子组合
        ['kdj_oversold', 'rsi_oversold', 'cci_oversold'],
        ['kdj_deep_oversold', 'rsi_oversold', 'wr_oversold'],

        # 内置组合策略
        ['kdj_rsi_oversold'],
        ['oversold_resonance'],
        ['deep_oversold_combo'],
        ['oversold_reversal'],
        ['full_buy_signal'],

        # 趋势+超跌
        ['kdj_oversold', 'macd_golden_cross'],
        ['rsi_oversold', 'macd_hist_turn'],
    ]

    # 只用一种最优配置
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

    results = []

    with get_db_context() as db:
        total_tests = len(strategy_combinations)
        logger.info(f"测试策略数量: {total_tests}")

        for i, strategies in enumerate(strategy_combinations):
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
                        f"[{i+1}/{total_tests}] {strategies}: "
                        f"收益={performance['total_return']:.2%}, "
                        f"胜率={performance['win_rate']:.2%}, "
                        f"回撤={performance['max_drawdown']:.2%}, "
                        f"夏普={performance['sharpe_ratio']:.4f}"
                    )

            except Exception as e:
                logger.error(f"[{i+1}/{total_tests}] {strategies} 失败: {e}")

    if len(results) == 0:
        logger.warning("没有有效的回测结果")
        return None

    results_df = pd.DataFrame(results)

    # 综合评分
    results_df['score'] = (
        results_df['total_return'] * 0.4 +
        results_df['win_rate'] * 0.3 +
        (1 - results_df['max_drawdown'].abs()) * 0.3
    )

    results_df = results_df.sort_values('score', ascending=False)

    # 输出结果
    print("\n" + "=" * 100)
    print("策略优化分析结果")
    print("=" * 100)

    print("\n【所有策略排名】")
    print("-" * 100)
    print(f"{'排名':<6}{'策略组合':<40}{'收益':<12}{'胜率':<12}{'回撤':<12}{'夏普':<12}{'评分':<10}")
    print("-" * 100)

    for idx, row in enumerate(results_df.iterrows()):
        i, r = row
        print(f"{idx+1:<6}{r['strategies']:<40}{r['total_return']:>10.2%}  {r['win_rate']:>10.2%}  {r['max_drawdown']:>10.2%}  {r['sharpe_ratio']:>10.4f}  {r['score']:>8.4f}")

    # Top 3 详细分析
    print("\n" + "=" * 100)
    print("【Top 3 最优策略详细分析】")
    print("=" * 100)

    for idx, row in enumerate(results_df.head(3).iterrows()):
        i, r = row
        print(f"\n排名 {idx+1}: {r['strategies']}")
        print(f"  总收益: {r['total_return']:.2%}")
        print(f"  年化收益: {r['annual_return']:.2%}")
        print(f"  最大回撤: {r['max_drawdown']:.2%}")
        print(f"  夏普比率: {r['sharpe_ratio']:.4f}")
        print(f"  胜率: {r['win_rate']:.2%}")
        print(f"  交易次数: {r['total_trades']}")
        print(f"  平均盈亏: {r['avg_profit_pct']:.2%}")
        print(f"  最终市值: {r['final_value']:,.2f}")
        print(f"  综合评分: {r['score']:.4f}")

    # 保存结果
    output_dir = 'strategy/optimization_results'
    import os
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_df.to_csv(f'{output_dir}/quick_optimization_{timestamp}.csv', index=False, encoding='utf-8-sig')

    print(f"\n结果已保存: {output_dir}/quick_optimization_{timestamp}.csv")

    # 最终推荐
    print("\n" + "=" * 100)
    print("【最终推荐】")
    print("=" * 100)

    best = results_df.iloc[0]
    print(f"""
最优策略: {best['strategies']}

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
    run_quick_optimization()