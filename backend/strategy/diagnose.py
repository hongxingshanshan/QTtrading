"""
诊断脚本 - 检查数据和指标计算是否正确
"""

import sys
sys.path.insert(0, ".")

import pandas as pd
import numpy as np

# 加载数据
print("=" * 60)
print("加载数据...")
print("=" * 60)

daily_df = pd.read_pickle("strategy/data/daily_data.pkl")
trade_dates = pd.read_csv("strategy/data/trade_dates.csv")["trade_date"].tolist()
stocks_df = pd.read_csv("strategy/data/stocks.csv")

print(f"股票数: {len(stocks_df)}")
print(f"交易日数: {len(trade_dates)}")
print(f"日线数据数: {len(daily_df)}")
print(f"日期范围: {trade_dates[0]} ~ {trade_dates[-1]}")

# 检查数据列
print(f"\n日线数据列: {daily_df.columns.tolist()}")

# 检查几只股票的数据
print("\n" + "=" * 60)
print("检查前5只股票的数据...")
print("=" * 60)

sample_stocks = daily_df["ts_code"].unique()[:5]
for ts_code in sample_stocks:
    stock_data = daily_df[daily_df["ts_code"] == ts_code].sort_values("trade_date")
    print(f"\n{ts_code}:")
    print(f"  数据行数: {len(stock_data)}")
    print(f"  日期范围: {stock_data['trade_date'].iloc[0]} ~ {stock_data['trade_date'].iloc[-1]}")
    print(f"  close范围: {stock_data['close'].min():.2f} ~ {stock_data['close'].max():.2f}")
    print(f"  vol范围: {stock_data['vol'].min():.0f} ~ {stock_data['vol'].max():.0f}")

# 计算技术指标
print("\n" + "=" * 60)
print("计算技术指标...")
print("=" * 60)

def calculate_kdj(df, n=9, m1=3, m2=3):
    low_n = df["low"].rolling(window=n, min_periods=n).min()
    high_n = df["high"].rolling(window=n, min_periods=n).max()
    rsv = (df["close"] - low_n) / (high_n - low_n) * 100
    rsv = rsv.fillna(50)
    df["j"] = 3 * rsv.ewm(alpha=1/m1, adjust=False).mean() - 2 * rsv.ewm(alpha=1/m2, adjust=False).mean()
    return df

def calculate_rsi(df, n=6):
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = (-delta).where(delta < 0, 0)
    avg_gain = gain.rolling(window=n, min_periods=n).mean()
    avg_loss = loss.rolling(window=n, min_periods=n).mean()
    df["rsi6"] = 100 - (100 / (1 + avg_gain / avg_loss.replace(0, np.inf)))
    return df

def calculate_vol_ratio(df):
    df["vol_ma5"] = df["vol"].rolling(window=5, min_periods=5).mean()
    df["vol_ratio"] = df["vol"] / df["vol_ma5"]
    return df

# 预处理所有股票
stock_data = {}
for ts_code, group in daily_df.groupby("ts_code"):
    group = group.sort_values("trade_date").copy()
    group = calculate_kdj(group)
    group = calculate_rsi(group)
    group = calculate_vol_ratio(group)
    stock_data[ts_code] = group

print(f"预处理完成: {len(stock_data)} 只股票")

# 统计指标分布
print("\n" + "=" * 60)
print("统计指标分布...")
print("=" * 60)

all_j = []
all_rsi = []
all_vol_ratio = []

for ts_code, df in stock_data.items():
    all_j.extend(df["j"].dropna().tolist())
    all_rsi.extend(df["rsi6"].dropna().tolist())
    all_vol_ratio.extend(df["vol_ratio"].dropna().tolist())

all_j = np.array(all_j)
all_rsi = np.array(all_rsi)
all_vol_ratio = np.array(all_vol_ratio)

print(f"\nJ值分布:")
print(f"  最小值: {all_j.min():.2f}")
print(f"  最大值: {all_j.max():.2f}")
print(f"  均值: {all_j.mean():.2f}")
print(f"  中位数: {np.median(all_j):.2f}")
print(f"  <0的比例: {(all_j < 0).mean()*100:.2f}%")
print(f"  <20的比例: {(all_j < 20).mean()*100:.2f}%")
print(f"  <50的比例: {(all_j < 50).mean()*100:.2f}%")

print(f"\nRSI6分布:")
print(f"  最小值: {all_rsi.min():.2f}")
print(f"  最大值: {all_rsi.max():.2f}")
print(f"  均值: {all_rsi.mean():.2f}")
print(f"  中位数: {np.median(all_rsi):.2f}")
print(f"  <10的比例: {(all_rsi < 10).mean()*100:.2f}%")
print(f"  <20的比例: {(all_rsi < 20).mean()*100:.2f}%")
print(f"  <30的比例: {(all_rsi < 30).mean()*100:.2f}%")

print(f"\n成交量比率分布:")
print(f"  最小值: {all_vol_ratio.min():.2f}")
print(f"  最大值: {all_vol_ratio.max():.2f}")
print(f"  均值: {all_vol_ratio.mean():.2f}")
print(f"  中位数: {np.median(all_vol_ratio):.2f}")
print(f"  >0.8的比例: {(all_vol_ratio > 0.8).mean()*100:.2f}%")
print(f"  >1.0的比例: {(all_vol_ratio > 1.0).mean()*100:.2f}%")
print(f"  >1.2的比例: {(all_vol_ratio > 1.2).mean()*100:.2f}%")

# 检查特定日期的信号
print("\n" + "=" * 60)
print("检查特定日期的信号...")
print("=" * 60)

# 检查中间日期
mid_date = trade_dates[len(trade_dates)//2]
print(f"\n检查日期: {mid_date}")

j_count = 0
rsi_count = 0
vol_count = 0
all_count = 0

for ts_code, df in stock_data.items():
    row = df[df["trade_date"] == mid_date]
    if row.empty:
        continue

    all_count += 1
    row = row.iloc[0]

    if row["j"] < 0:
        j_count += 1
    if row["rsi6"] < 20:
        rsi_count += 1
    if row["vol_ratio"] > 1.0:
        vol_count += 1

print(f"当日有效股票数: {all_count}")
print(f"J<0的股票数: {j_count} ({j_count/all_count*100:.2f}%)")
print(f"RSI<20的股票数: {rsi_count} ({rsi_count/all_count*100:.2f}%)")
print(f"VOL>1.0的股票数: {vol_count} ({vol_count/all_count*100:.2f}%)")

# 找一些满足部分条件的股票
print("\n" + "=" * 60)
print("查找满足部分条件的股票示例...")
print("=" * 60)

for ts_code, df in list(stock_data.items())[:100]:
    row = df[df["trade_date"] == mid_date]
    if row.empty:
        continue

    row = row.iloc[0]

    # 打印前10只股票的指标值
    if len(sample_stocks) < 10:
        print(f"{ts_code}: J={row['j']:.2f}, RSI={row['rsi6']:.2f}, VOL_RATIO={row['vol_ratio']:.2f}")
        sample_stocks = list(sample_stocks) + [ts_code]

# 检查是否有NaN
print("\n" + "=" * 60)
print("检查NaN值...")
print("=" * 60)

j_nan = np.isnan(all_j).sum()
rsi_nan = np.isnan(all_rsi).sum()
vol_nan = np.isnan(all_vol_ratio).sum()

print(f"J值NaN数量: {j_nan} ({j_nan/len(all_j)*100:.2f}%)")
print(f"RSI NaN数量: {rsi_nan} ({rsi_nan/len(all_rsi)*100:.2f}%)")
print(f"VOL_RATIO NaN数量: {vol_nan} ({vol_nan/len(all_vol_ratio)*100:.2f}%)")
