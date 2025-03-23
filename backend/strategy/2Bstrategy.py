from tqdm import tqdm
import pandas as pd
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
    """回测策略"""
    trades = []  # 存储交易记录

    # 遍历每只股票的数据
    for i in range(2, len(data) - 1):  # 从第2天开始，确保有前两天的数据
        today = data[i]
        yesterday = data[i - 1]
        day_before_yesterday = data[i - 2]  # 前一天的前一天
        tomorrow = data[i + 1]

        # 条件1：上一交易日首次涨停
        if yesterday['pct_chg'] >= 9.9 and day_before_yesterday['pct_chg'] < 9.9:
            # 条件2：次日开盘涨幅在 0%~3%
            open_chg = (today['open'] - yesterday['close']) / yesterday['close'] * 100
            if 0 <= open_chg <= 3:
                # 买入价格为次日开盘价
                buy_price = today['open']
                # 卖出价格为隔天开盘价
                sell_price = tomorrow['open']
                # 计算盈亏
                profit = (sell_price - buy_price) / buy_price
                trades.append(profit)

    # 统计结果
    total_trades = len(trades)
    winning_trades = len([t for t in trades if t > 0])
    losing_trades = total_trades - winning_trades

    # 避免除以 0 的情况
    win_rate = winning_trades / total_trades if total_trades > 0 else 0
    avg_win = sum([t for t in trades if t > 0]) / winning_trades if winning_trades > 0 else 0
    avg_loss = abs(sum([t for t in trades if t < 0]) / losing_trades) if losing_trades > 0 else 0

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

def main():
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)

    # 获取所有股票的 ts_code 和上市时间
    cursor.execute('SELECT ts_code, list_date, name FROM stock_basic_info')
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
                        if 0 <= trade < 0.03:
                            profit_ranges["0%~3%"] += 1
                            overall_profit_ranges["0%~3%"] += 1
                        elif 0.03 <= trade < 0.05:
                            profit_ranges["3%~5%"] += 1
                            overall_profit_ranges["3%~5%"] += 1
                        elif 0.05 <= trade < 0.1:
                            profit_ranges["5%~10%"] += 1
                            overall_profit_ranges["5%~10%"] += 1
                        elif trade >= 0.1:
                            profit_ranges[">10%"] += 1
                            overall_profit_ranges[">10%"] += 1
                        elif -0.03 <= trade < 0:
                            profit_ranges["-0%~-3%"] += 1
                            overall_profit_ranges["-0%~-3%"] += 1
                        elif -0.05 <= trade < -0.03:
                            profit_ranges["-3%~-5%"] += 1
                            overall_profit_ranges["-3%~-5%"] += 1
                        elif -0.1 <= trade < -0.05:
                            profit_ranges["-5%~-10%"] += 1
                            overall_profit_ranges["-5%~-10%"] += 1
                        elif trade < -0.1:
                            profit_ranges["<-10%"] += 1
                            overall_profit_ranges["<-10%"] += 1

                    results.append({
                        "ts_code": ts_code,
                        "total_trades": result["total_trades"],
                        "win_rate": result["win_rate"],
                        "profit_loss_ratio": result["profit_loss_ratio"],
                        "profit_ranges": profit_ranges
                    })

                    # 汇总整体结果
                    overall_trades += result["total_trades"]
                    overall_winning_trades += len([t for t in result["trades"] if t > 0])
                    overall_losing_trades += len([t for t in result["trades"] if t < 0])

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
        print(f"股票代码: {result['ts_code']}, 总交易次数: {result['total_trades']}, 胜率: {result['win_rate']:.2%}, 盈亏比: {result['profit_loss_ratio']}")
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

if __name__ == "__main__":
    main()