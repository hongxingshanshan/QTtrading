"""
回测引擎
基于信号引擎进行策略回测
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy import text

from strategy.signal_engine import SignalEngine, SignalStrategy


@dataclass
class Position:
    """持仓信息"""
    ts_code: str           # 股票代码
    buy_date: str          # 买入日期
    buy_price: float       # 买入价格
    shares: int            # 持仓股数
    current_price: float   # 当前价格
    current_value: float   # 当前市值
    profit: float          # 浮动盈亏
    profit_pct: float      # 盈亏比例
    hold_days: int = 0     # 持仓天数


@dataclass
class Trade:
    """交易记录"""
    ts_code: str           # 股票代码
    trade_type: str        # 'buy' or 'sell'
    trade_date: str        # 交易日期
    price: float           # 交易价格
    shares: int            # 交易股数
    amount: float          # 交易金额
    profit: float = 0.0    # 卖盈亏（卖出时）
    profit_pct: float = 0.0  # 盈亏比例
    reason: str = ""       # 交易原因


@dataclass
class BacktestConfig:
    """回测配置"""
    initial_capital: float = 1000000.0    # 初始资金
    max_positions: int = 10               # 最大持仓数量
    position_size: float = 0.1            # 单只股票仓位比例
    min_position_value: float = 5000.0    # 最小持仓金额
    commission_rate: float = 0.0003       # 佣金费率
    stamp_duty_rate: float = 0.001        # 印花税（仅卖出）
    slippage: float = 0.001               # 滑点
    max_hold_days: int = 20               # 最大持仓天数
    stop_loss_pct: float = -0.08          # 止损比例
    take_profit_pct: float = 0.15         # 止盈比例


class BacktestEngine:
    """回测引擎"""

    def __init__(self, config: Optional[BacktestConfig] = None):
        self.config = config or BacktestConfig()
        self.signal_engine = SignalEngine()

        # 回测状态
        self.cash = self.config.initial_capital
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.daily_values: List[Dict] = []

    def load_data(
        self,
        db,
        start_date: str,
        end_date: str
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        加载回测数据

        Args:
            db: 数据库会话
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            (指标数据, 价格数据)
        """
        # 加载指标数据
        indicator_query = text("""
            SELECT * FROM daily_indicator
            WHERE trade_date >= :start_date
              AND trade_date <= :end_date
            ORDER BY ts_code, trade_date
        """)
        indicator_df = pd.read_sql(
            indicator_query, db.bind,
            params={'start_date': start_date, 'end_date': end_date}
        )
        logger.info(f"加载指标数据: {len(indicator_df)} 条")

        # 加载价格数据
        price_query = text("""
            SELECT ts_code, trade_date, open, high, low, close, vol, pct_chg
            FROM daily_data
            WHERE trade_date >= :start_date
              AND trade_date <= :end_date
            ORDER BY ts_code, trade_date
        """)
        price_df = pd.read_sql(
            price_query, db.bind,
            params={'start_date': start_date, 'end_date': end_date}
        )
        logger.info(f"加载价格数据: {len(price_df)} 条")

        return indicator_df, price_df

    def get_trade_dates(self, price_df: pd.DataFrame) -> List[str]:
        """获取交易日列表"""
        return sorted(price_df['trade_date'].unique().tolist())

    def get_next_trade_date(self, trade_dates: List[str], current_date: str) -> Optional[str]:
        """获取下一个交易日"""
        try:
            idx = trade_dates.index(current_date)
            if idx + 1 < len(trade_dates):
                return trade_dates[idx + 1]
        except ValueError:
            pass
        return None

    def calculate_buy_amount(self, price: float) -> Tuple[int, float]:
        """
        计算买入数量和金额

        Args:
            price: 股票价格

        Returns:
            (股数, 实际金额)
        """
        # 目标金额
        target_value = self.cash * self.config.position_size

        # 计算股数（A股一手100股）
        shares = int(target_value / price / 100) * 100

        # 最小持仓检查
        if shares * price < self.config.min_position_value:
            shares = int(self.config.min_position_value / price / 100) * 100

        # 实际金额（含滑点）
        actual_price = price * (1 + self.config.slippage)
        amount = shares * actual_price

        # 佣金
        commission = max(amount * self.config.commission_rate, 5.0)
        total_cost = amount + commission

        # 检查资金是否足够
        if total_cost > self.cash:
            shares = int(self.cash / (actual_price * (1 + self.config.commission_rate)) / 100) * 100
            amount = shares * actual_price
            commission = max(amount * self.config.commission_rate, 5.0)
            total_cost = amount + commission

        return shares, total_cost

    def buy(
        self,
        ts_code: str,
        trade_date: str,
        price: float,
        reason: str = ""
    ) -> Optional[Trade]:
        """买入股票"""
        if len(self.positions) >= self.config.max_positions:
            return None

        shares, total_cost = self.calculate_buy_amount(price)
        if shares <= 0:
            return None

        # 执行买入
        self.cash -= total_cost

        trade = Trade(
            ts_code=ts_code,
            trade_type='buy',
            trade_date=trade_date,
            price=price * (1 + self.config.slippage),
            shares=shares,
            amount=shares * price * (1 + self.config.slippage),
            reason=reason
        )
        self.trades.append(trade)

        # 创建持仓
        self.positions[ts_code] = Position(
            ts_code=ts_code,
            buy_date=trade_date,
            buy_price=trade.price,
            shares=shares,
            current_price=price,
            current_value=shares * price,
            profit=0.0,
            profit_pct=0.0,
            hold_days=0
        )

        logger.debug(f"买入 {ts_code}: 价格={price:.2f}, 数量={shares}, 金额={total_cost:.2f}")
        return trade

    def sell(
        self,
        ts_code: str,
        trade_date: str,
        price: float,
        reason: str = ""
    ) -> Optional[Trade]:
        """卖出股票"""
        if ts_code not in self.positions:
            return None

        position = self.positions[ts_code]

        # 计算卖出金额（含滑点）
        actual_price = price * (1 - self.config.slippage)
        amount = position.shares * actual_price

        # 佣金和印花税
        commission = max(amount * self.config.commission_rate, 5.0)
        stamp_duty = amount * self.config.stamp_duty_rate
        total_cost = commission + stamp_duty

        # 实际收入
        net_amount = amount - total_cost
        self.cash += net_amount

        # 计算盈亏
        profit = net_amount - position.shares * position.buy_price
        profit_pct = profit / (position.shares * position.buy_price)

        trade = Trade(
            ts_code=ts_code,
            trade_type='sell',
            trade_date=trade_date,
            price=actual_price,
            shares=position.shares,
            amount=amount,
            profit=profit,
            profit_pct=profit_pct,
            reason=reason
        )
        self.trades.append(trade)

        logger.debug(
            f"卖出 {ts_code}: 价格={price:.2f}, 数量={position.shares}, "
            f"盈亏={profit:.2f} ({profit_pct:.2%})"
        )

        # 移除持仓
        del self.positions[ts_code]
        return trade

    def update_positions(
        self,
        price_df: pd.DataFrame,
        trade_date: str
    ):
        """更新持仓市值"""
        day_prices = price_df[price_df['trade_date'] == trade_date]

        for ts_code, position in self.positions.items():
            stock_price = day_prices[day_prices['ts_code'] == ts_code]
            if len(stock_price) > 0:
                current_price = stock_price['close'].iloc[0]
                position.current_price = current_price
                position.current_value = position.shares * current_price
                position.profit = position.current_value - position.shares * position.buy_price
                position.profit_pct = position.profit / (position.shares * position.buy_price)

    def check_sell_signals(
        self,
        price_df: pd.DataFrame,
        trade_date: str,
        trade_dates: List[str]
    ) -> List[str]:
        """
        检查卖出信号

        Returns:
            需要卖出的股票代码列表
        """
        sell_codes = []
        day_prices = price_df[price_df['trade_date'] == trade_date]

        for ts_code, position in self.positions.items():
            # 更新持仓天数
            position.hold_days += 1

            # 止损
            if position.profit_pct <= self.config.stop_loss_pct:
                sell_codes.append(ts_code)
                logger.debug(f"{ts_code} 触发止损: {position.profit_pct:.2%}")
                continue

            # 止盈
            if position.profit_pct >= self.config.take_profit_pct:
                sell_codes.append(ts_code)
                logger.debug(f"{ts_code} 触发止盈: {position.profit_pct:.2%}")
                continue

            # 最大持仓天数
            if position.hold_days >= self.config.max_hold_days:
                sell_codes.append(ts_code)
                logger.debug(f"{ts_code} 达到最大持仓天数: {position.hold_days}")
                continue

        return sell_codes

    def run_backtest(
        self,
        db,
        start_date: str,
        end_date: str,
        strategy_names: Optional[List[str]] = None,
        min_score: float = 0.5
    ) -> Dict:
        """
        运行回测

        Args:
            db: 数据库会话
            start_date: 开始日期
            end_date: 结束日期
            strategy_names: 策略名称列表
            min_score: 最小信号得分

        Returns:
            回测结果
        """
        logger.info("=" * 60)
        logger.info("开始回测")
        logger.info("=" * 60)
        logger.info(f"回测区间: {start_date} ~ {end_date}")
        logger.info(f"初始资金: {self.config.initial_capital:,.2f}")
        logger.info(f"策略: {strategy_names or '全部'}")

        # 加载数据
        indicator_df, price_df = self.load_data(db, start_date, end_date)

        # 检测信号
        logger.info("检测信号...")
        signal_df = self.signal_engine.detect_signals(indicator_df, strategy_names)

        # 获取交易日列表
        trade_dates = self.get_trade_dates(price_df)
        logger.info(f"交易日数量: {len(trade_dates)}")

        # 逐日回测
        for i, trade_date in enumerate(trade_dates):
            # 更新持仓市值
            self.update_positions(price_df, trade_date)

            # 计算当日总市值
            position_value = sum(p.current_value for p in self.positions.values())
            total_value = self.cash + position_value

            # 记录每日市值
            self.daily_values.append({
                'trade_date': trade_date,
                'cash': self.cash,
                'position_value': position_value,
                'total_value': total_value,
                'position_count': len(self.positions)
            })

            # 检查卖出信号
            sell_codes = self.check_sell_signals(price_df, trade_date, trade_dates)
            day_prices = price_df[price_df['trade_date'] == trade_date]

            # 执行卖出
            for ts_code in sell_codes:
                stock_price = day_prices[day_prices['ts_code'] == ts_code]
                if len(stock_price) > 0:
                    self.sell(ts_code, trade_date, stock_price['close'].iloc[0], "止损/止盈/到期")

            # 检查买入信号
            if len(self.positions) < self.config.max_positions:
                day_signals = signal_df[signal_df['trade_date'] == trade_date]
                day_signals = day_signals[day_signals['has_signal'] == True]
                day_signals = day_signals[day_signals['total_score'] >= min_score]

                # 排除已持仓股票
                day_signals = day_signals[~day_signals['ts_code'].isin(self.positions.keys())]

                # 按得分排序
                day_signals = day_signals.sort_values('total_score', ascending=False)

                # 买入
                for _, row in day_signals.iterrows():
                    if len(self.positions) >= self.config.max_positions:
                        break

                    ts_code = row['ts_code']
                    stock_price = day_prices[day_prices['ts_code'] == ts_code]
                    if len(stock_price) > 0:
                        self.buy(
                            ts_code, trade_date,
                            stock_price['close'].iloc[0],
                            f"信号: {row['signal_types']}"
                        )

            # 进度显示
            if (i + 1) % 50 == 0:
                logger.info(f"进度: {i+1}/{len(trade_dates)}, 总市值: {total_value:,.2f}")

        # 清算剩余持仓
        last_date = trade_dates[-1]
        last_prices = price_df[price_df['trade_date'] == last_date]
        for ts_code in list(self.positions.keys()):
            stock_price = last_prices[last_prices['ts_code'] == ts_code]
            if len(stock_price) > 0:
                self.sell(ts_code, last_date, stock_price['close'].iloc[0], "回测结束")

        # 计算绩效
        performance = self.calculate_performance()

        return performance

    def calculate_performance(self) -> Dict:
        """计算回测绩效"""
        if len(self.daily_values) == 0:
            return {}

        values_df = pd.DataFrame(self.daily_values)
        trades_df = pd.DataFrame(self.trades) if self.trades else pd.DataFrame()

        # 收益率序列
        values_df['return'] = values_df['total_value'].pct_change()
        values_df['cum_return'] = (1 + values_df['return']).cumprod() - 1

        # 总收益率
        total_return = (values_df['total_value'].iloc[-1] / self.config.initial_capital - 1)

        # 年化收益率
        days = len(values_df)
        annual_return = (1 + total_return) ** (252 / days) - 1

        # 最大回撤
        cummax = values_df['total_value'].cummax()
        drawdown = (values_df['total_value'] - cummax) / cummax
        max_drawdown = drawdown.min()

        # 夏普比率
        if values_df['return'].std() > 0:
            sharpe = values_df['return'].mean() / values_df['return'].std() * np.sqrt(252)
        else:
            sharpe = 0

        # 交易统计
        buy_trades = trades_df[trades_df['trade_type'] == 'buy'] if len(trades_df) > 0 else pd.DataFrame()
        sell_trades = trades_df[trades_df['trade_type'] == 'sell'] if len(trades_df) > 0 else pd.DataFrame()

        win_trades = sell_trades[sell_trades['profit'] > 0] if len(sell_trades) > 0 else pd.DataFrame()
        lose_trades = sell_trades[sell_trades['profit'] <= 0] if len(sell_trades) > 0 else pd.DataFrame()

        performance = {
            'total_return': total_return,
            'annual_return': annual_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe,
            'total_trades': len(trades_df),
            'buy_count': len(buy_trades),
            'sell_count': len(sell_trades),
            'win_rate': len(win_trades) / len(sell_trades) if len(sell_trades) > 0 else 0,
            'win_count': len(win_trades),
            'lose_count': len(lose_trades),
            'avg_profit': sell_trades['profit'].mean() if len(sell_trades) > 0 else 0,
            'avg_profit_pct': sell_trades['profit_pct'].mean() if len(sell_trades) > 0 else 0,
            'total_profit': sell_trades['profit'].sum() if len(sell_trades) > 0 else 0,
            'final_value': values_df['total_value'].iloc[-1],
            'daily_values': values_df,
            'trades': trades_df
        }

        return performance

    def print_performance(self, performance: Dict):
        """打印绩效报告"""
        print("\n" + "=" * 80)
        print("回测绩效报告")
        print("=" * 80)

        print(f"\n【收益指标】")
        print(f"  总收益率: {performance['total_return']:.2%}")
        print(f"  年化收益率: {performance['annual_return']:.2%}")
        print(f"  最大回撤: {performance['max_drawdown']:.2%}")
        print(f"  夏普比率: {performance['sharpe_ratio']:.4f}")

        print(f"\n【交易统计】")
        print(f"  总交易次数: {performance['total_trades']}")
        print(f"  买入次数: {performance['buy_count']}")
        print(f"  卖出次数: {performance['sell_count']}")
        print(f"  胜率: {performance['win_rate']:.2%}")
        print(f"  盈利次数: {performance['win_count']}")
        print(f"  亏损次数: {performance['lose_count']}")

        print(f"\n【盈亏统计】")
        print(f"  平均盈亏: {performance['avg_profit']:.2f}")
        print(f"  平均盈亏比例: {performance['avg_profit_pct']:.2%}")
        print(f"  总盈亏: {performance['total_profit']:.2f}")
        print(f"  最终市值: {performance['final_value']:,.2f}")

    def save_results(self, performance: Dict, output_dir: str = 'strategy/backtest_results'):
        """保存回测结果"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # 保存每日市值
        if 'daily_values' in performance:
            performance['daily_values'].to_csv(
                f'{output_dir}/daily_values_{timestamp}.csv',
                index=False, encoding='utf-8-sig'
            )

        # 保存交易记录
        if 'trades' in performance and len(performance['trades']) > 0:
            performance['trades'].to_csv(
                f'{output_dir}/trades_{timestamp}.csv',
                index=False, encoding='utf-8-sig'
            )

        logger.info(f"结果已保存到: {output_dir}/")


def run_backtest(
    start_date: str = '20240101',
    end_date: str = '20260424',
    strategies: Optional[List[str]] = None,
    config: Optional[BacktestConfig] = None
):
    """运行回测"""
    from app.core.database import get_db_context

    with get_db_context() as db:
        engine = BacktestEngine(config)
        performance = engine.run_backtest(db, start_date, end_date, strategies)
        engine.print_performance(performance)
        engine.save_results(performance)
        return performance


if __name__ == "__main__":
    # 示例：使用超跌策略回测
    config = BacktestConfig(
        initial_capital=1000000,
        max_positions=5,
        position_size=0.15,
        max_hold_days=10,
        stop_loss_pct=-0.05,
        take_profit_pct=0.10
    )

    strategies = [
        'kdj_oversold',
        'rsi_oversold',
        'kdj_rsi_oversold',
        'oversold_resonance'
    ]

    run_backtest(
        start_date='20240101',
        end_date='20260424',
        strategies=strategies,
        config=config
    )
