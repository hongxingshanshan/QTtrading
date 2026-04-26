"""
因子分析模块
基于 daily_indicator 表进行因子有效性分析
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from sqlalchemy import text
from sqlalchemy.orm import Session
from loguru import logger


class FactorAnalyzer:
    """因子分析器"""

    # 因子分类
    FACTOR_CATEGORIES = {
        'trend': ['ma_alignment', 'ma5_deviation', 'ma10_deviation', 'ma20_deviation',
                  'dma_dif', 'dma_ama', 'boll_position'],
        'momentum': ['k_value', 'd_value', 'j_value', 'rsi6', 'rsi12', 'rsi24',
                     'cci', 'wr10', 'wr14', 'macd_dif', 'macd_dea', 'macd_hist'],
        'volatility': ['boll_width', 'atr14', 'amplitude'],
        'volume': ['vol_ratio', 'vol_ratio_10', 'obv', 'vr'],
        'price_pattern': ['consecutive_down', 'consecutive_up', 'drawdown_20d',
                          'drawdown_60d', 'rebound_20d', 'rebound_60d',
                          'pct_change_5d', 'pct_change_10d', 'pct_change_20d']
    }

    # 所有可用因子
    ALL_FACTORS = [
        # KDJ
        'k_value', 'd_value', 'j_value',
        # RSI
        'rsi6', 'rsi12', 'rsi24',
        # MACD
        'macd_dif', 'macd_dea', 'macd_hist',
        # BOLL
        'boll_upper', 'boll_mid', 'boll_lower', 'boll_width', 'boll_position',
        # MA
        'ma5', 'ma10', 'ma20', 'ma30', 'ma60', 'ma120', 'ma250',
        'ma5_deviation', 'ma10_deviation', 'ma20_deviation', 'ma30_deviation',
        'ma60_deviation', 'ma120_deviation', 'ma250_deviation', 'ma_alignment',
        # CCI & WR
        'cci', 'wr10', 'wr14',
        # OBV
        'obv', 'obv_ma5', 'obv_ma10',
        # 成交量
        'vol_ma5', 'vol_ma10', 'vol_ma20', 'vol_ratio', 'vol_ratio_10',
        # 价格形态
        'consecutive_down', 'consecutive_up', 'drawdown_20d', 'drawdown_60d',
        'rebound_20d', 'rebound_60d', 'amplitude', 'pct_change',
        'pct_change_5d', 'pct_change_10d', 'pct_change_20d',
        # ATR & DMA & VR
        'atr14', 'dma_dif', 'dma_ama', 'vr'
    ]

    def __init__(self, db: Session):
        self.db = db

    def load_indicator_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        ts_codes: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        从数据库加载指标数据

        Args:
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            ts_codes: 股票代码列表，None 表示全部

        Returns:
            DataFrame 包含所有指标数据
        """
        query = "SELECT * FROM daily_indicator WHERE 1=1"
        params = {}

        if start_date:
            query += " AND trade_date >= :start_date"
            params['start_date'] = start_date

        if end_date:
            query += " AND trade_date <= :end_date"
            params['end_date'] = end_date

        if ts_codes:
            placeholders = ', '.join([f":code_{i}" for i in range(len(ts_codes))])
            query += f" AND ts_code IN ({placeholders})"
            for i, code in enumerate(ts_codes):
                params[f'code_{i}'] = code

        query += " ORDER BY ts_code, trade_date"

        df = pd.read_sql(text(query), self.db.bind, params=params)
        logger.info(f"加载指标数据: {len(df)} 条记录, {df['ts_code'].nunique()} 只股票")

        return df

    def load_price_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """加载日线价格数据（用于计算未来收益）"""
        query = """
            SELECT ts_code, trade_date, close, high, low, open, vol, pct_chg
            FROM daily_data
            WHERE 1=1
        """
        params = {}

        if start_date:
            query += " AND trade_date >= :start_date"
            params['start_date'] = start_date

        if end_date:
            query += " AND trade_date <= :end_date"
            params['end_date'] = end_date

        query += " ORDER BY ts_code, trade_date"

        df = pd.read_sql(text(query), self.db.bind, params=params)
        return df

    def calculate_future_returns(
        self,
        price_df: pd.DataFrame,
        periods: List[int] = [1, 3, 5, 10, 20]
    ) -> pd.DataFrame:
        """
        计算未来收益

        Args:
            price_df: 价格数据
            periods: 收益周期列表

        Returns:
            添加了未来收益列的 DataFrame
        """
        df = price_df.copy()

        for period in periods:
            # 未来 N 日收益率
            df[f'forward_ret_{period}d'] = df.groupby('ts_code')['close'].transform(
                lambda x: x.shift(-period) / x - 1
            )
            # 未来 N 日最大收益
            df[f'max_ret_{period}d'] = df.groupby('ts_code')['high'].transform(
                lambda x: x.rolling(-period, min_periods=1).max().shift(-period) / x - 1
            )
            # 未来 N 日最大亏损
            df[f'min_ret_{period}d'] = df.groupby('ts_code')['low'].transform(
                lambda x: x.rolling(-period, min_periods=1).min().shift(-period) / x - 1
            )

        return df

    def calculate_ic(
        self,
        factor_df: pd.DataFrame,
        factor_col: str,
        return_col: str = 'forward_ret_5d',
        method: str = 'spearman'
    ) -> Dict:
        """
        计算单因子的 IC (Information Coefficient)

        Args:
            factor_df: 包含因子和收益的数据
            factor_col: 因子列名
            return_col: 收益列名
            method: 相关系数方法 ('spearman' 或 'pearson')

        Returns:
            IC 统计信息
        """
        # 按日期分组计算 IC
        ic_series = factor_df.groupby('trade_date').apply(
            lambda x: x[[factor_col, return_col]].dropna().corr(method=method).iloc[0, 1]
        )

        return {
            'factor': factor_col,
            'ic_mean': ic_series.mean(),
            'ic_std': ic_series.std(),
            'icir': ic_series.mean() / ic_series.std() if ic_series.std() > 0 else 0,
            'ic_positive_ratio': (ic_series > 0).mean(),
            'ic_abs_mean': ic_series.abs().mean(),
            'sample_count': len(ic_series)
        }

    def analyze_factor_groups(
        self,
        factor_df: pd.DataFrame,
        factor_col: str,
        return_col: str = 'forward_ret_5d',
        n_groups: int = 5
    ) -> pd.DataFrame:
        """
        因子分组收益分析

        Args:
            factor_df: 数据
            factor_col: 因子列名
            return_col: 收益列名
            n_groups: 分组数量

        Returns:
            分组收益统计
        """
        df = factor_df.copy()

        # 按日期分组，每日进行分位数分组
        df['factor_group'] = df.groupby('trade_date')[factor_col].transform(
            lambda x: pd.qcut(x.rank(method='first'), n_groups, labels=False, duplicates='drop')
        )

        results = []
        for group in range(n_groups):
            subset = df[df['factor_group'] == group]
            if len(subset) == 0:
                continue

            results.append({
                'factor': factor_col,
                'group': group + 1,
                'count': len(subset),
                'mean_return': subset[return_col].mean() * 100,
                'median_return': subset[return_col].median() * 100,
                'win_rate': (subset[return_col] > 0).mean() * 100,
                'std_return': subset[return_col].std() * 100,
            })

        return pd.DataFrame(results)

    def analyze_all_factors(
        self,
        start_date: str,
        end_date: str,
        return_periods: List[int] = [1, 3, 5, 10, 20],
        factors: Optional[List[str]] = None
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        分析所有因子的有效性

        Args:
            start_date: 开始日期
            end_date: 结束日期
            return_periods: 收益周期
            factors: 要分析的因子列表，None 表示全部

        Returns:
            (IC汇总表, 分组收益字典)
        """
        if factors is None:
            factors = self.ALL_FACTORS

        # 加载数据
        logger.info("加载指标数据...")
        indicator_df = self.load_indicator_data(start_date, end_date)

        logger.info("加载价格数据...")
        price_df = self.load_price_data(start_date, end_date)

        logger.info("计算未来收益...")
        price_df = self.calculate_future_returns(price_df, return_periods)

        # 合并数据
        logger.info("合并数据...")
        merged_df = indicator_df.merge(
            price_df[['ts_code', 'trade_date'] +
                     [col for col in price_df.columns if col.startswith(('forward_ret', 'max_ret', 'min_ret'))]],
            on=['ts_code', 'trade_date'],
            how='inner'
        )
        logger.info(f"合并后数据: {len(merged_df)} 条记录")

        # 计算各因子 IC
        ic_results = []
        group_results = {}

        total_factors = len(factors)
        for i, factor in enumerate(factors):
            if factor not in merged_df.columns:
                logger.warning(f"因子 {factor} 不存在于数据中，跳过")
                continue

            logger.info(f"分析因子 [{i+1}/{total_factors}]: {factor}")

            # 计算不同周期的 IC
            for period in return_periods:
                return_col = f'forward_ret_{period}d'
                if return_col not in merged_df.columns:
                    continue

                ic_info = self.calculate_ic(merged_df, factor, return_col)
                ic_info['return_period'] = period
                ic_results.append(ic_info)

            # 5日收益分组分析
            if 'forward_ret_5d' in merged_df.columns:
                group_df = self.analyze_factor_groups(merged_df, factor, 'forward_ret_5d')
                group_results[factor] = group_df

        ic_df = pd.DataFrame(ic_results)

        return ic_df, group_results

    def get_top_factors(
        self,
        ic_df: pd.DataFrame,
        return_period: int = 5,
        top_n: int = 10,
        metric: str = 'icir'
    ) -> pd.DataFrame:
        """
        获取表现最好的因子

        Args:
            ic_df: IC 分析结果
            return_period: 收益周期
            top_n: 返回数量
            metric: 排序指标 ('icir', 'ic_mean', 'ic_abs_mean')

        Returns:
            Top N 因子
        """
        subset = ic_df[ic_df['return_period'] == return_period].copy()
        subset = subset.sort_values(metric, ascending=False).head(top_n)
        return subset

    def generate_factor_report(
        self,
        start_date: str,
        end_date: str,
        output_dir: str = 'strategy/reports'
    ) -> Dict:
        """
        生成因子分析报告

        Args:
            start_date: 开始日期
            end_date: 结束日期
            output_dir: 输出目录

        Returns:
            报告摘要
        """
        import os
        os.makedirs(output_dir, exist_ok=True)

        logger.info("=" * 60)
        logger.info("因子有效性分析报告")
        logger.info("=" * 60)
        logger.info(f"分析区间: {start_date} ~ {end_date}")

        # 执行分析
        ic_df, group_results = self.analyze_all_factors(start_date, end_date)

        # 保存结果
        ic_df.to_csv(f'{output_dir}/factor_ic_analysis.csv', index=False, encoding='utf-8-sig')

        # 保存分组收益
        with pd.ExcelWriter(f'{output_dir}/factor_group_analysis.xlsx') as writer:
            for factor, df in group_results.items():
                df.to_excel(writer, sheet_name=factor[:31], index=False)

        # 打印摘要
        print("\n" + "=" * 80)
        print("因子分析摘要 (按 5 日 ICIR 排序)")
        print("=" * 80)

        top_factors = self.get_top_factors(ic_df, return_period=5, top_n=20)
        print("\n【Top 20 因子 - 5日收益 ICIR】")
        for _, row in top_factors.iterrows():
            print(f"  {row['factor']}: IC均值={row['ic_mean']:.4f}, "
                  f"ICIR={row['icir']:.4f}, IC正向比例={row['ic_positive_ratio']:.2%}")

        # 按类别汇总
        print("\n【因子类别 ICIR 汇总】")
        for category, factor_list in self.FACTOR_CATEGORIES.items():
            subset = ic_df[(ic_df['factor'].isin(factor_list)) & (ic_df['return_period'] == 5)]
            if len(subset) > 0:
                avg_icir = subset['icir'].mean()
                avg_ic = subset['ic_mean'].mean()
                print(f"  {category}: 平均IC={avg_ic:.4f}, 平均ICIR={avg_icir:.4f}")

        print(f"\n详细结果已保存到: {output_dir}/")

        return {
            'ic_df': ic_df,
            'group_results': group_results,
            'top_factors': top_factors
        }


def run_factor_analysis(start_date: str = '20240101', end_date: str = '20260424'):
    """运行因子分析"""
    from app.core.database import get_db_context

    with get_db_context() as db:
        analyzer = FactorAnalyzer(db)
        return analyzer.generate_factor_report(start_date, end_date)


if __name__ == "__main__":
    run_factor_analysis()
