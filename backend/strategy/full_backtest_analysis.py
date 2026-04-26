"""
完整策略回测分析
包含买入时机、卖出时机、持仓详情
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


def run_full_backtest():
    """完整策略回测分析"""
    logger.info("=" * 80)
    logger.info("完整策略回测分析")
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

    results = {}

    with get_db_context() as db:
        for strat in strategies_to_test:
            logger.info(f"\n测试策略: {strat['name']}")
            logger.info(f"条件: {strat['description']}")

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

            results[strat['name']] = {
                'performance': performance,
                'trades': performance.get('trades', pd.DataFrame()),
                'daily_values': performance.get('daily_values', pd.DataFrame())
            }

    # 输出详细分析
    print("\n" + "=" * 100)
    print("完整回测分析报告")
    print("=" * 100)

    for strat_name, data in results.items():
        perf = data['performance']
        trades_df = data['trades']
        daily_df = data['daily_values']

        print(f"\n{'=' * 100}")
        print(f"策略: {strat_name}")
        print("=" * 100)

        # 绩效摘要
        print("\n【绩效摘要】")
        print(f"  总收益: {perf['total_return']:.2%}")
        print(f"  年化收益: {perf['annual_return']:.2%}")
        print(f"  最大回撤: {perf['max_drawdown']:.2%}")
        print(f"  夏普比率: {perf['sharpe_ratio']:.4f}")
        print(f"  胜率: {perf['win_rate']:.2%}")
        print(f"  交易次数: {perf['total_trades']}")

        if len(trades_df) == 0:
            print("\n  无交易记录")
            continue

        # 买入时机分析
        buy_trades = trades_df[trades_df['trade_type'] == 'buy']
        print("\n【买入时机分析】")
        print(f"  总买入次数: {len(buy_trades)}")

        # 按月份统计买入
        buy_trades['month'] = buy_trades['trade_date'].astype(str).str[:6]
        monthly_buy = buy_trades.groupby('month').size()
        print("\n  月度买入分布:")
        for month, count in monthly_buy.items():
            print(f"    {month}: {count} 次")

        # 买入价格分布
        print(f"\n  买入价格统计:")
        print(f"    平均买入价: {buy_trades['price'].mean():.2f}")
        print(f"    最高买入价: {buy_trades['price'].max():.2f}")
        print(f"    最低买入价: {buy_trades['price'].min():.2f}")

        # 最近10次买入
        print("\n  最近10次买入记录:")
        print(f"{'日期':<12}{'股票':<12}{'价格':<10}{'数量':<10}{'金额':<12}{'原因':<30}")
        print("-" * 86)
        for _, row in buy_trades.tail(10).iterrows():
            reason = row['reason'][:28] if len(row['reason']) > 28 else row['reason']
            print(f"{row['trade_date']:<12}{row['ts_code']:<12}{row['price']:<10.2f}{row['shares']:<10}{row['amount']:<12.2f}{reason:<30}")

        # 卖出时机分析
        sell_trades = trades_df[trades_df['trade_type'] == 'sell']
        print("\n【卖出时机分析】")
        print(f"  总卖出次数: {len(sell_trades)}")

        # 卖出原因统计
        sell_reasons = sell_trades['reason'].value_counts()
        print("\n  卖出原因分布:")
        for reason, count in sell_reasons.items():
            print(f"    {reason}: {count} 次")

        # 盈亏分布
        print(f"\n  卖出盈亏统计:")
        print(f"    平均盈亏: {sell_trades['profit'].mean():.2f}")
        print(f"    平均盈亏比例: {sell_trades['profit_pct'].mean():.2%}")
        print(f"    最大盈利: {sell_trades['profit'].max():.2f}")
        print(f"    最大亏损: {sell_trades['profit'].min():.2f}")

        # 最近10次卖出
        print("\n  最近10次卖出记录:")
        print(f"{'日期':<12}{'股票':<12}{'价格':<10}{'盈亏':<10}{'盈亏%':<10}{'原因':<30}")
        print("-" * 86)
        for _, row in sell_trades.tail(10).iterrows():
            reason = row['reason'][:28] if len(row['reason']) > 28 else row['reason']
            print(f"{row['trade_date']:<12}{row['ts_code']:<12}{row['price']:<10.2f}{row['profit']:<10.2f}{row['profit_pct']:<10.2%}{reason:<30}")

        # 持仓分析
        if len(daily_df) > 0:
            print("\n【持仓分析】")
            print(f"  平均持仓数量: {daily_df['position_count'].mean():.2f}")
            print(f"  最大持仓数量: {daily_df['position_count'].max()}")
            print(f"  最小持仓数量: {daily_df['position_count'].min()}")

            # 持仓天数分布（从卖出记录计算）
            if len(sell_trades) > 0:
                # 计算每笔交易的持仓天数
                trade_pairs = []
                for ts_code in sell_trades['ts_code'].unique():
                    code_buys = buy_trades[buy_trades['ts_code'] == ts_code]
                    code_sells = sell_trades[sell_trades['ts_code'] == ts_code]
                    for sell in code_sells.itertuples():
                        # 找对应的买入
                        matching_buys = code_buys[code_buys['trade_date'] < sell.trade_date]
                        if len(matching_buys) > 0:
                            buy_date = matching_buys.iloc[-1]['trade_date']
                            hold_days = int(sell.trade_date) - int(buy_date)
                            trade_pairs.append(hold_days)

                if trade_pairs:
                    print(f"\n  持仓天数统计:")
                    print(f"    平均持仓: {sum(trade_pairs)/len(trade_pairs):.1f} 天")
                    print(f"    最短持仓: {min(trade_pairs)} 天")
                    print(f"    最长持仓: {max(trade_pairs)} 天")

                    # 持仓天数分布
                    hold_dist = pd.Series(trade_pairs).value_counts().sort_index()
                    print(f"\n  持仓天数分布:")
                    for days, count in hold_dist.head(15).items():
                        print(f"    {days}天: {count} 次")

        # 资金曲线分析
        if len(daily_df) > 0:
            print("\n【资金曲线分析】")
            print(f"  初始资金: {config.initial_capital:,.2f}")
            print(f"  最终市值: {daily_df['total_value'].iloc[-1]:,.2f}")
            print(f"  最高市值: {daily_df['total_value'].max():,.2f}")
            print(f"  最低市值: {daily_df['total_value'].min():,.2f}")

            # 按季度统计收益
            daily_df['quarter'] = daily_df['trade_date'].astype(str).str[:4] + 'Q' + \
                ((daily_df['trade_date'].astype(str).str[4:6].astype(int) // 3 + 1).astype(str))
            quarterly_returns = daily_df.groupby('quarter').apply(
                lambda x: (x['total_value'].iloc[-1] / x['total_value'].iloc[0] - 1) if len(x) > 1 else 0
            )
            print(f"\n  季度收益:")
            for quarter, ret in quarterly_returns.items():
                print(f"    {quarter}: {ret:.2%}")

    # 策略对比
    print("\n" + "=" * 100)
    print("【策略对比】")
    print("=" * 100)
    print(f"\n{'指标':<20}{'oversold_reversal':<20}{'custom_j_rsi_vol':<20}")
    print("-" * 60)

    metrics = ['total_return', 'annual_return', 'max_drawdown', 'sharpe_ratio', 'win_rate', 'total_trades', 'avg_profit_pct']
    metric_names = ['总收益', '年化收益', '最大回撤', '夏普比率', '胜率', '交易次数', '平均盈亏']

    for metric, name in zip(metrics, metric_names):
        val1 = results['oversold_reversal']['performance'][metric]
        val2 = results['custom_j_rsi_vol']['performance'][metric]
        if metric in ['total_return', 'annual_return', 'max_drawdown', 'win_rate', 'avg_profit_pct']:
            print(f"{name:<20}{val1:>18.2%}  {val2:>18.2%}")
        elif metric == 'sharpe_ratio':
            print(f"{name:<20}{val1:>18.4f}  {val2:>18.4f}")
        else:
            print(f"{name:<20}{val1:>18d}  {val2:>18d}")

    # 保存详细交易记录
    output_dir = 'strategy/backtest_results'
    import os
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    for strat_name, data in results.items():
        trades_df = data['trades']
        daily_df = data['daily_values']

        if len(trades_df) > 0:
            trades_df.to_csv(f'{output_dir}/{strat_name}_trades_{timestamp}.csv', index=False, encoding='utf-8-sig')
        if len(daily_df) > 0:
            daily_df.to_csv(f'{output_dir}/{strat_name}_daily_{timestamp}.csv', index=False, encoding='utf-8-sig')

    print(f"\n详细交易记录已保存到: {output_dir}/")


if __name__ == "__main__":
    run_full_backtest()