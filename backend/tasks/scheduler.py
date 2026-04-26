"""定时任务调度器"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from loguru import logger
from .trading_calendar import is_trading_day

scheduler = BackgroundScheduler()


def check_and_run_incr_jobs():
    """检查是否为交易日，如果是则运行增量任务"""
    today = datetime.now()
    if is_trading_day(today):
        logger.info("今天是交易日，执行增量任务")
        from .incr_jobs import run_incr_jobs
        run_incr_jobs()
    else:
        logger.info("今天不是交易日，跳过增量任务")


def start_scheduler():
    """启动调度器"""
    # 每天凌晨3点执行初始化任务
    scheduler.add_job(
        lambda: __import__('tasks.init_jobs', fromlist=['run_init_jobs']).run_init_jobs(),
        CronTrigger(hour=3, minute=0),
        id='init_job',
        name='初始化任务',
        replace_existing=True
    )

    # 交易日 17:00 执行增量任务
    scheduler.add_job(
        check_and_run_incr_jobs,
        CronTrigger(hour=17, minute=0),
        id='incr_job_17',
        name='增量任务-17点',
        replace_existing=True
    )

    # 交易日 19:00 执行增量任务
    scheduler.add_job(
        check_and_run_incr_jobs,
        CronTrigger(hour=19, minute=0),
        id='incr_job_19',
        name='增量任务-19点',
        replace_existing=True
    )

    # 每周日凌晨4点执行周K线导入
    scheduler.add_job(
        lambda: __import__('tasks.kline_jobs', fromlist=['import_weekly_data']).import_weekly_data(),
        CronTrigger(day_of_week='sun', hour=4, minute=0),
        id='weekly_kline_job',
        name='周K线导入',
        replace_existing=True
    )

    # 每月1号凌晨5点执行月K线导入
    scheduler.add_job(
        lambda: __import__('tasks.kline_jobs', fromlist=['import_monthly_data']).import_monthly_data(),
        CronTrigger(day=1, hour=5, minute=0),
        id='monthly_kline_job',
        name='月K线导入',
        replace_existing=True
    )

    # 交易日 20:00 执行增量指标计算（在日线数据更新后）
    scheduler.add_job(
        lambda: __import__('tasks.indicator_jobs', fromlist=['run_indicator_incremental_job']).run_indicator_incremental_job(),
        CronTrigger(hour=20, minute=0),
        id='indicator_incr_job',
        name='增量指标计算',
        replace_existing=True
    )

    # 每周日凌晨6点执行全量指标计算
    scheduler.add_job(
        lambda: __import__('tasks.indicator_jobs', fromlist=['run_indicator_full_job']).run_indicator_full_job(),
        CronTrigger(day_of_week='sun', hour=6, minute=0),
        id='indicator_full_job',
        name='全量指标计算',
        replace_existing=True
    )

    scheduler.start()
    logger.info("定时任务调度器已启动")
    logger.info("已注册任务:")
    logger.info("  - 初始化任务: 每天 03:00")
    logger.info("  - 增量任务: 交易日 17:00, 19:00")
    logger.info("  - 周K线导入: 每周日 04:00")
    logger.info("  - 月K线导入: 每月1号 05:00")
    logger.info("  - 增量指标计算: 每天 20:00")
    logger.info("  - 全量指标计算: 每周日 06:00")


def stop_scheduler():
    """停止调度器"""
    scheduler.shutdown()
    logger.info("定时任务调度器已停止")
