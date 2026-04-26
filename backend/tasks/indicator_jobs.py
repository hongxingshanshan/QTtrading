"""
技术指标计算定时任务
在日线数据更新后计算技术指标
"""
from loguru import logger
from datetime import datetime
from strategy.indicator_calc import run_incremental_calculation, run_indicator_calculation
from app.core.logging import setup_logging

# 初始化日志配置
setup_logging()


def run_indicator_incremental_job():
    """运行增量指标计算（每天执行）"""
    logger.info("开始执行增量指标计算...")

    try:
        result = run_incremental_calculation(days=30, max_workers=8)
        logger.info(f"增量指标计算完成: 成功={result['success']}, 错误={result['error']}, 耗时={result['elapsed_seconds']:.1f}秒")
    except Exception as e:
        logger.error(f"增量指标计算失败: {e}")


def run_indicator_full_job():
    """运行全量指标计算（每周执行）"""
    logger.info("开始执行全量指标计算...")

    try:
        result = run_indicator_calculation(max_workers=8)
        logger.info(f"全量指标计算完成: 成功={result['success']}, 错误={result['error']}, 总记录={result['total_records']}, 耗时={result['elapsed_seconds']:.1f}秒")
    except Exception as e:
        logger.error(f"全量指标计算失败: {e}")
