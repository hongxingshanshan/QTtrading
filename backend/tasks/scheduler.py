from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.core.logging import logger

scheduler = BackgroundScheduler()


def start_scheduler():
    """启动调度器"""
    from tasks.jobs.trading_calendar import is_trading_day

    # 这里后续添加具体的任务
    # scheduler.add_job(...)

    scheduler.start()
    logger.info("定时任务调度器已启动")


def stop_scheduler():
    """停止调度器"""
    scheduler.shutdown()
    logger.info("定时任务调度器已停止")
