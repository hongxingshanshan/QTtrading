"""
财务指标数据采集任务
数据来源: Tushare fina_indicator 接口
包含: ROE/毛利率/负债率/成长性等
"""
import pandas as pd
from datetime import datetime
from loguru import logger
from sqlalchemy import text
from app.core.database import SessionLocal
from .tushare_client import get_pro_api


# 需要采集的字段列表
FINA_FIELDS = [
    'ts_code', 'ann_date', 'end_date',
    # 每股指标
    'eps', 'dt_eps', 'bps', 'ocfps', 'cfps', 'revenue_ps',
    'capital_rese_ps', 'surplus_rese_ps', 'undist_profit_ps', 'retainedps',
    # 盈利能力
    'roe', 'roe_waa', 'roe_dt', 'roa', 'roic',
    'netprofit_margin', 'grossprofit_margin', 'ebit', 'ebitda',
    # 营运能力
    'invturn_days', 'arturn_days', 'inv_turn', 'ar_turn', 'assets_turn', 'turn_days',
    # 偿债能力
    'current_ratio', 'quick_ratio', 'cash_ratio',
    'debt_to_assets', 'debt_to_eqt', 'ebit_to_interest',
    # 成长能力
    'or_yoy', 'tr_yoy', 'netprofit_yoy', 'dt_netprofit_yoy',
    'basic_eps_yoy', 'roe_yoy', 'equity_yoy', 'assets_yoy',
    # 现金流量
    'fcff', 'fcfe', 'ocf_to_or', 'ocf_to_opincome',
    # 其他
    'profit_dedt', 'gross_margin', 'working_capital', 'tangible_asset',
    'invest_capital', 'retained_earnings', 'rd_exp',
    # 单季度指标
    'q_eps', 'q_netprofit_margin', 'q_gsprofit_margin', 'q_roe',
    'q_gr_yoy', 'q_sales_yoy', 'q_profit_yoy', 'q_netprofit_yoy'
]


def get_recent_periods(count: int = 8) -> list:
    """
    获取最近的报告期列表

    报告期规则：
    - 0331: 一季报
    - 0630: 中报
    - 0930: 三季报
    - 1231: 年报
    """
    now = datetime.now()
    year = now.year
    month = now.month

    periods = []
    all_periods = ['1231', '0930', '0630', '0331']

    # 确定当前应该有的最新报告期
    if month >= 5:
        periods.append(f"{year-1}1231")
    if month >= 9:
        periods.append(f"{year}0630")
    if month >= 11:
        periods.append(f"{year}0930")

    # 补充历史报告期
    current_year = year
    while len(periods) < count:
        for p in all_periods:
            if len(periods) >= count:
                break
            period_str = f"{current_year}{p}"
            if period_str not in periods:
                periods.append(period_str)
        current_year -= 1

    return periods[:count]


def import_fina_indicator(periods: list = None, ts_code: str = None):
    """
    导入财务指标数据

    Args:
        periods: 报告期列表，如 ['20231231', '20230930']
        ts_code: 股票代码，为None时导入全部股票
    """
    logger.info(f"开始导入财务指标数据: periods={periods}, ts_code={ts_code}")

    try:
        pro = get_pro_api()
        db = SessionLocal()

        try:
            imported_count = 0
            error_count = 0

            if periods is None:
                # 获取最近8个报告期
                periods = get_recent_periods(8)

            for period in periods:
                logger.info(f"正在处理报告期: {period}")

                try:
                    # 调用 Tushare fina_indicator 接口
                    if ts_code:
                        df = pro.fina_indicator(ts_code=ts_code, period=period)
                    else:
                        df = pro.fina_indicator(period=period)

                    if df.empty:
                        logger.debug(f"报告期 {period} 无数据")
                        continue

                    # 只保留需要的字段
                    available_fields = [f for f in FINA_FIELDS if f in df.columns]
                    df = df[available_fields]

                    # 处理 NaN 值
                    df = df.where(pd.notna(df), None)
                    data = df.to_dict(orient='records')

                    # 批量插入
                    for record in data:
                        # 构建 SQL
                        columns = list(record.keys())
                        placeholders = [f':{col}' for col in columns]
                        update_cols = [col for col in columns if col not in ['ts_code', 'end_date']]
                        update_set = ', '.join([f'{col}=VALUES({col})' for col in update_cols])

                        sql = f"""
                            INSERT INTO fina_indicator ({', '.join(columns)})
                            VALUES ({', '.join(placeholders)})
                            ON DUPLICATE KEY UPDATE {update_set}
                        """
                        db.execute(text(sql), record)

                    db.commit()
                    imported_count += len(data)
                    logger.info(f"报告期 {period} 导入完成: {len(data)} 条")

                except Exception as e:
                    error_count += 1
                    logger.warning(f"导入报告期 {period} 失败: {e}")

            logger.info(f"财务指标数据导入完成: 成功={imported_count}, 失败={error_count}")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"导入财务指标数据出错: {e}")


def run_fina_incremental_job():
    """
    运行增量财务指标采集（每季度执行）
    只采集最近2个报告期的数据
    """
    logger.info("开始执行增量财务指标采集")

    periods = get_recent_periods(2)
    import_fina_indicator(periods=periods)

    logger.info("增量财务指标采集完成")


def run_fina_full_job():
    """
    运行全量财务指标采集
    采集最近8个报告期的数据
    """
    logger.info("开始执行全量财务指标采集")

    periods = get_recent_periods(8)
    import_fina_indicator(periods=periods)

    logger.info("全量财务指标采集完成")
