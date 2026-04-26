"""
数据库迁移脚本 - 创建技术指标表
运行方式: python backend/scripts/create_indicator_table.py
"""
import sys
import os

# 设置工作目录为 backend 目录
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

# 加载环境变量
from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

from loguru import logger
from sqlalchemy import text
from app.core.database import engine
from app.models.base import Base
from app.models.indicator import DailyIndicator


def create_indicator_table():
    """创建技术指标表"""
    logger.info("开始创建技术指标表...")

    # 创建表
    Base.metadata.create_all(bind=engine, tables=[DailyIndicator.__table__])

    logger.info("技术指标表创建完成")

    # 创建索引
    with engine.connect() as conn:
        # 创建日期索引
        try:
            conn.execute(text("CREATE INDEX idx_indicator_trade_date ON daily_indicator(trade_date)"))
            conn.commit()
            logger.info("创建日期索引完成")
        except Exception as e:
            if "Duplicate" in str(e):
                logger.info("日期索引已存在")
            else:
                logger.warning(f"创建日期索引失败: {e}")

    logger.info("索引创建完成")


def drop_indicator_table():
    """删除技术指标表（谨慎使用）"""
    logger.warning("即将删除技术指标表...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS daily_indicator"))
        conn.commit()
    logger.info("技术指标表已删除")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='技术指标表管理')
    parser.add_argument('--drop', action='store_true', help='删除表（谨慎使用）')

    args = parser.parse_args()

    if args.drop:
        drop_indicator_table()
    else:
        create_indicator_table()
