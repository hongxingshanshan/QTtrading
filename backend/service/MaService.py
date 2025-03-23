import pandas as pd
from backend.query.DailyData import get_daily_data
from backend.query.AdjFactorData import get_adj_factor_data


def get_qfq_data(ts_code):
    """
    获取某只股票的前复权数据
    :param ts_code: 股票代码
    :param start_date: 开始日期 (格式: YYYYMMDD)
    :param end_date: 结束日期 (格式: YYYYMMDD)
    :return: DataFrame 包含前复权数据
    """
    # 获取每日行情数据
    daily_data = get_daily_data(ts_code)
    if not daily_data:
        print(f"未获取到股票 {ts_code} 的每日行情数据")
        return None

    # 获取复权因子数据
    adj_factor_data = get_adj_factor_data(ts_code)
    if not adj_factor_data:
        print(f"未获取到股票 {ts_code} 的复权因子数据")
        return None

    daily_data_df = pd.DataFrame(daily_data)
    adj_factor_data_df = pd.DataFrame(adj_factor_data)
    # 合并每日行情数据和复权因子数据
    merged_data = pd.merge(daily_data_df, adj_factor_data_df, on='trade_date', how='inner')

    # 计算前复权价格
    merged_data = calc_qfq_prices(merged_data, style='tushare')

    return merged_data

import pandas as pd

def calc_qfq_prices(df: pd.DataFrame, style='tushare'):
    """
    计算前复权价格，支持 tushare / 同花顺 两种方式。

    :param df: 包含至少 ['open', 'high', 'low', 'close', 'adj_factor'] 的 DataFrame（按交易日升序排列）
    :param style: 'tushare' 或 'ths'，选择复权基准方式
    :return: 添加前复权后的列：qfq_open、qfq_high、qfq_low、qfq_close
    """
    if 'adj_factor' not in df.columns:
        raise ValueError("DataFrame 必须包含 'adj_factor' 列")

    # 确保复权因子为浮点数类型
    df['adj_factor'] = df['adj_factor'].astype(float)

    if style == 'tushare':
        anchor = df['adj_factor'].iloc[-1]  # 最新的复权因子作为基准            
        ratio = df['adj_factor'] / anchor
    elif style == 'ths':
        anchor = df['adj_factor'].iloc[0]  # 最早的复权因子作为基准
        ratio = df['adj_factor'] / anchor
    else:
        raise ValueError("style 参数只能是 'tushare' 或 'ths'")

    df['qfq_open'] = df['open'] * ratio
    df['qfq_high'] = df['high'] * ratio
    df['qfq_low'] = df['low'] * ratio
    df['qfq_close'] = df['close'] * ratio
    df['qfq_change'] = df['qfq_close'].diff()
    df['qfq_pct_chg'] = df['qfq_close'].pct_change() * 100


    return df


# 示例调用
if __name__ == "__main__":
    ts_code = '000001.SZ'  # 示例股票代码
    start_date = '20250301'
    end_date = '20250301'

    qfq_data = get_qfq_data(ts_code)
    if qfq_data is not None:
        print(qfq_data)