
from backend.tushare import token
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import ta  # 技术指标库

# 初始化 Tushare 接口
ts = token.get_tushare()
pro = ts.pro_api()

# 获取股票列表
def get_stock_list():
    df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    return df

# 获取历史行情数据
def get_price_data(ts_code, start_date='20220101', end_date='20250401'):
    df = ts.pro_bar(ts_code=ts_code, adj='qfq', start_date=start_date, end_date=end_date)
    df.sort_values('trade_date', inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

# 计算因子
def calculate_factors(df):
    df['return'] = df['close'].pct_change()
    df['volatility_20'] = df['return'].rolling(window=20).std()
    df['momentum_10'] = df['close'].pct_change(periods=10)
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['ma_ratio'] = df['ma5'] / df['ma20']
    df['volume_change'] = df['vol'].pct_change()

    # 使用 ta 库添加更多指标
    df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
    df['macd'] = ta.trend.MACD(close=df['close']).macd()

    # 保留有用列
    factor_cols = ['volatility_20', 'momentum_10', 'ma_ratio', 'volume_change', 'rsi', 'macd']
    df = df[['ts_code', 'trade_date'] + factor_cols].dropna()
    return df

# 多股票数据合并处理
def build_factor_dataset(stock_list, start_date='20220101', end_date='20250401'):
    all_data = []
    for ts_code in stock_list:
        try:
            price_data = get_price_data(ts_code, start_date, end_date)
            if price_data is not None and not price_data.empty:
                factors = calculate_factors(price_data)
                all_data.append(factors)
        except Exception as e:
            print(f"Error with {ts_code}: {e}")
    full_df = pd.concat(all_data, axis=0)
    return full_df

# 因子标准化处理
def standardize_factors(df):
    factor_cols = df.columns.difference(['ts_code', 'trade_date'])
    scaler = StandardScaler()
    df[factor_cols] = scaler.fit_transform(df[factor_cols])
    return df

if __name__ == '__main__':
    stock_df = get_stock_list()  # 示例只取50个股票测试
    ts_code_list = stock_df['ts_code'].tolist()

    factor_data = build_factor_dataset(ts_code_list)
    standardized_data = standardize_factors(factor_data)

    print(standardized_data.head())
    standardized_data.to_csv('factor_dataset.csv', index=False)
