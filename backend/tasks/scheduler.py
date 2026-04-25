from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from app.core.logging import logger
from tasks.jobs.trading_calendar import is_trading_day

scheduler = BackgroundScheduler()


def check_and_run_incr_jobs():
    """检查是否为交易日，如果是则运行增量任务"""
    today = datetime.now()
    if is_trading_day(today):
        logger.info(f"今天是交易日，执行增量任务")
        from tasks.incr_jobs import run_incr_jobs
        run_incr_jobs()
    else:
        logger.info(f"今天不是交易日，跳过增量任务")


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

    # 每天 10:00 执行复权因子同步
    scheduler.add_job(
        lambda: __import__('tasks.adj_factor_job', fromlist=['run_adj_factor_job']).run_adj_factor_job(),
        CronTrigger(hour=10, minute=0),
        id='adj_factor_job',
        name='复权因子同步',
        replace_existing=True
    )

    scheduler.start()
    logger.info("定时任务调度器已启动")
    logger.info("已注册任务:")
    logger.info("  - 初始化任务: 每天 03:00")
    logger.info("  - 增量任务: 交易日 17:00, 19:00")
    logger.info("  - 复权因子同步: 每天 10:00")


def stop_scheduler():
    """停止调度器"""
    scheduler.shutdown()
    logger.info("定时任务调度器已停止")
