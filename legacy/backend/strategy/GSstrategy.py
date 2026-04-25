import pandas as pd
from tqdm import tqdm
from backend import DataBase as db
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_daily_data(ts_code):
    """
    从数据库获取指定股票的每日交易数据
    :param ts_code: 股票代码
    :return: 包含每日交易数据的列表
    """
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)

    query = '''
    SELECT trade_date, open, high, low, close, pre_close, price_change, pct_chg, vol, amount
    FROM daily_data
    WHERE ts_code = %s
    ORDER BY trade_date ASC
    '''
    cursor.execute(query, (ts_code,))
    data = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return data

def backtest_strategy(data):
     # 计算 MACD 指标
    data = compute_macd(data) 
    """回测策略"""
    trades = []  # 存储交易记录
    buy_price = None  # 初始化买入价格
    buy_date = None  # 初始化买入日期

    # 遍历每只股票的数据
    for i in range(30, len(data) - 1):  # 从第10天开始，确保有足够的历史数据计算均线
        today = data[i]
        yesterday = data[i - 1]
        ma5 = sum([d['close'] for d in data[i - 5:i]]) / 5  # 计算5日均线
        ma10 = sum([d['close'] for d in data[i - 10:i]]) / 10  # 计算10日均线
        ma30 = sum([d['close'] for d in data[i - 30:i]]) / 30  # 计算30日均线
        ma5_vol = sum([d['vol'] for d in data[i - 5:i]]) / 5  # 计算5日平均成交量
        ma10_vol = sum([d['vol'] for d in data[i - 10:i]]) / 10  # 计算10日平均成交量
        ma30_vol = sum([d['vol'] for d in data[i - 30:i]]) / 30  # 计算30日平均成交量
        macd = today['macd']
        macd_signal = today['macd_signal']
        hist = today['macd_hist']

        # 买入信号
        if buy_price is None:
            bullish_trend = ma5 > ma10 > ma30
            volume_boost = today['vol'] > 1.5 * ma10_vol
            moderate_gain = today['pct_chg'] < 5
            macd_bull = macd > macd_signal and hist > 0  # MACD金叉 + 红柱增强

            if bullish_trend and volume_boost and moderate_gain and macd_bull:
                buy_price = today['close']
                buy_date = today['trade_date']
                peak_price = buy_price  # 初始化峰值

        else:
            current_price = today['close']
            peak_price = max(peak_price, current_price)
            profit = (current_price - buy_price) / buy_price
            drawdown = (peak_price - current_price) / peak_price if peak_price > 0 else 0

            # 卖出信号
            death_cross = ma5 < ma10
            stop_loss = profit <= -0.03
            take_profit = profit >= 0.2
            close_below_ma10 = current_price < ma10
            max_drawdown_exit = drawdown > 0.03  # 回撤超过5%则止盈
            sell_date = today['trade_date'] 
            sell_price = today['close']

            if death_cross or stop_loss or take_profit or close_below_ma10 or max_drawdown_exit:
                trades.append({
                    "ma5": ma5,
                    "ma10": ma10,
                    "ma30": ma30,
                    "ma5_vol": ma5_vol,
                    "ma10_vol": ma10_vol,
                    "ma30_vol": ma30_vol,
                    "buy_date": buy_date,
                    "buy_price": buy_price,
                    "sell_date": sell_date,
                    "sell_price": sell_price,
                    "profit": profit
                })

                # 重置买入价格和日期
                buy_price = None
                buy_date = None

    # 统计结果
    total_trades = len(trades)
    winning_trades = len([t for t in trades if t["profit"] > 0])
    losing_trades = total_trades - winning_trades

    # 避免除以 0 的情况
    win_rate = winning_trades / total_trades if total_trades > 0 else 0
    avg_win = sum([t["profit"] for t in trades if t["profit"] > 0]) / winning_trades if winning_trades > 0 else 0
    avg_loss = abs(sum([t["profit"] for t in trades if t["profit"] < 0]) / losing_trades) if losing_trades > 0 else 0

    # 盈亏比显示为 x:y 格式
    profit_loss_ratio = f"{winning_trades}:{losing_trades}"

    trades_result = {
        "total_trades": total_trades,
        "win_rate": win_rate,
        "profit_loss_ratio": profit_loss_ratio,
        "trades": trades
    }

    return trades_result
def process_stock(stock):
    """处理单支股票的回测"""
    ts_code = stock['ts_code']
    ts_name = stock['name']
    data = get_daily_data(ts_code)
    result = backtest_strategy(data)
    stock_result = {
        "ts_code": ts_code,
        "ts_name": ts_name,
        "result": result
    }
    return stock_result

def save_trades_to_excel(all_trades, output_file="trading_records.xlsx"):
    """
    将交易记录保存到 Excel 文件
    :param all_trades: 所有交易记录的列表
    :param output_file: 输出的 Excel 文件名
    """
    if all_trades:
        trades_df = pd.DataFrame(all_trades)
        trades_df.to_excel(output_file, index=False)
        print(f"交易记录已保存到 {output_file}")
    else:
        print("没有交易记录生成。")

def compute_macd(data, fast=12, slow=26, signal=9):
    closes = [d['close'] for d in data]
    ema_fast = []
    ema_slow = []
    macd_line = []
    signal_line = []
    hist = []

    k_fast = 2 / (fast + 1)
    k_slow = 2 / (slow + 1)
    k_signal = 2 / (signal + 1)

    for i in range(len(closes)):
        close = closes[i]
        if i == 0:
            ema_fast.append(close)
            ema_slow.append(close)
        else:
            ema_fast.append(ema_fast[-1] * (1 - k_fast) + close * k_fast)
            ema_slow.append(ema_slow[-1] * (1 - k_slow) + close * k_slow)

        macd_val = ema_fast[-1] - ema_slow[-1]
        macd_line.append(macd_val)

        if i == 0:
            signal_line.append(macd_val)
        else:
            signal_line.append(signal_line[-1] * (1 - k_signal) + macd_val * k_signal)

        hist.append(macd_val - signal_line[-1])

    for i in range(len(data)):
        data[i]['macd'] = macd_line[i]
        data[i]['macd_signal'] = signal_line[i]
        data[i]['macd_hist'] = hist[i]

    return data


def main():
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)

    # 获取所有股票的 ts_code 和上市时间
    cursor.execute('SELECT ts_code, list_date, name FROM stock_basic_info limit 10')
    stocks = cursor.fetchall()
    # 剔除ST、*ST、北交所、科创板股票
    stocks = [
        stock for stock in stocks
        if not stock['name'].startswith(('ST', '*ST')) and
        not stock['ts_code'].endswith('.BJ') and  # 剔除以 .BJ 结尾的股票
        not stock['ts_code'].startswith('688')   # 剔除科创板股票
    ]

    cursor.close()
    conn.close()

    overall_trades = 0
    overall_winning_trades = 0
    overall_losing_trades = 0

    # 初始化整体盈利区间计数
    overall_profit_ranges = {
        "0%~3%": 0,
        "3%~5%": 0,
        "5%~10%": 0,
        ">10%": 0,
        "-0%~-3%": 0,
        "-3%~-5%": 0,
        "-5%~-10%": 0,
        "<-10%": 0
    }

    results = []
    all_trades_records = []

    # 使用多线程处理每支股票
    with ThreadPoolExecutor(max_workers=8) as executor:  # 设置线程数
        # 创建进度条
        with tqdm(total=len(stocks), desc="Processing stocks", unit="stock") as pbar:
            # 提交任务
            future_to_stock = {executor.submit(process_stock, stock): stock for stock in stocks}

            # 处理完成的任务
            for future in as_completed(future_to_stock):
                stock = future_to_stock[future]
                try:
                    stock_result = future.result()
                    ts_code = stock_result["ts_code"]
                    ts_name = stock_result["ts_name"]
                    result = stock_result["result"]

                    # 初始化单支股票的盈利区间计数
                    profit_ranges = {
                        "0%~3%": 0,
                        "3%~5%": 0,
                        "5%~10%": 0,
                        ">10%": 0,
                        "-0%~-3%": 0,
                        "-3%~-5%": 0,
                        "-5%~-10%": 0,
                        "<-10%": 0
                    }

                    # 统计每笔交易的盈利区间
                    for trade in result["trades"]:
                        profit = trade["profit"]
                        if 0 <= profit < 0.03:
                            profit_ranges["0%~3%"] += 1
                            overall_profit_ranges["0%~3%"] += 1
                        elif 0.03 <= profit < 0.05:
                            profit_ranges["3%~5%"] += 1
                            overall_profit_ranges["3%~5%"] += 1
                        elif 0.05 <= profit < 0.1:
                            profit_ranges["5%~10%"] += 1
                            overall_profit_ranges["5%~10%"] += 1
                        elif profit >= 0.1:
                            profit_ranges[">10%"] += 1
                            overall_profit_ranges[">10%"] += 1
                        elif -0.03 <= profit < 0:
                            profit_ranges["-0%~-3%"] += 1
                            overall_profit_ranges["-0%~-3%"] += 1
                        elif -0.05 <= profit < -0.03:
                            profit_ranges["-3%~-5%"] += 1
                            overall_profit_ranges["-3%~-5%"] += 1
                        elif -0.1 <= profit < -0.05:
                            profit_ranges["-5%~-10%"] += 1
                            overall_profit_ranges["-5%~-10%"] += 1
                        elif profit < -0.1:
                            profit_ranges["<-10%"] += 1
                            overall_profit_ranges["<-10%"] += 1

                    for trade in result["trades"]:
                        all_trades_records.append({
                            "ts_code": ts_code,
                            "ts_name": ts_name,
                            "ma30": trade["ma30"],
                            "ma30_vol": trade["ma30_vol"],
                            "buy_date": trade["buy_date"],
                            "buy_price": trade["buy_price"],
                            "sell_date": trade["sell_date"],
                            "sell_price": trade["sell_price"],
                            "profit": trade["profit"]
                        })
                    results.append({
                        "ts_code": ts_code,
                        "ts_name": ts_name,
                        "total_trades": result["total_trades"],
                        "win_rate": result["win_rate"],
                        "profit_loss_ratio": result["profit_loss_ratio"],
                        "profit_ranges": profit_ranges
                    })

                    # 汇总整体结果
                    overall_trades += result["total_trades"]
                    overall_winning_trades += len([t for t in result["trades"] if t["profit"] > 0])
                    overall_losing_trades += len([t for t in result["trades"] if t["profit"] < 0])

                except Exception as e:
                    print(f"股票 {stock['ts_code']} 处理失败: {e}")
                finally:
                    # 更新进度条
                    pbar.update(1)

    # 计算整体胜率和盈亏比
    overall_win_rate = overall_winning_trades / overall_trades if overall_trades > 0 else 0
    overall_profit_loss_ratio = f"{overall_winning_trades}:{overall_losing_trades}"

    # 输出每支股票的结果
    for result in results:
        print(f"股票代码: {result['ts_code']}, 股票名称: {result['ts_name']}, 总交易次数: {result['total_trades']}, 胜率: {result['win_rate']:.2%}, 盈亏比: {result['profit_loss_ratio']}")
        print("盈利区间分布：")
        for range_name, count in result["profit_ranges"].items():
            print(f"  {range_name}: {count} 次")

    # 输出整体结果
    print("\n整体回测结果：")
    print(f"总交易次数: {overall_trades}")
    print(f"整体胜率: {overall_win_rate:.2%}")
    print(f"整体盈亏比: {overall_profit_loss_ratio}")
    print("整体盈利区间分布：")
    for range_name, count in overall_profit_ranges.items():
        print(f"  {range_name}: {count} 次")

    # 将交易记录保存到 Excel
    save_trades_to_excel(all_trades_records)

if __name__ == "__main__":
    main()