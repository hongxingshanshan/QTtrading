"""
数据库迁移脚本 - 创建财务指标表
运行方式: python backend/scripts/create_fina_table.py
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
from app.models.fina_indicator import FinaIndicator


def create_fina_table():
    """创建财务指标表"""
    logger.info("开始创建财务指标表...")

    # 创建表
    Base.metadata.create_all(bind=engine, tables=[FinaIndicator.__table__])

    logger.info("财务指标表创建完成")

    # 创建索引
    with engine.connect() as conn:
        indexes = [
            ("idx_fina_end_date", "end_date"),
            ("idx_fina_ts_code", "ts_code"),
            ("idx_fina_ann_date", "ann_date"),
            ("idx_fina_roe", "roe"),
            ("idx_fina_grossprofit", "grossprofit_margin"),
        ]

        for idx_name, idx_col in indexes:
            try:
                conn.execute(text(f"CREATE INDEX {idx_name} ON fina_indicator({idx_col})"))
                conn.commit()
                logger.info(f"创建索引 {idx_name} 完成")
            except Exception as e:
                if "Duplicate" in str(e):
                    logger.info(f"索引 {idx_name} 已存在")
                else:
                    logger.warning(f"创建索引 {idx_name} 失败: {e}")

    logger.info("索引创建完成")


def drop_fina_table():
    """删除财务指标表（谨慎使用）"""
    logger.warning("即将删除财务指标表...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS fina_indicator"))
        conn.commit()
    logger.info("财务指标表已删除")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='财务指标表管理')
    parser.add_argument('--drop', action='store_true', help='删除表（谨慎使用）')

    args = parser.parse_args()

    if args.drop:
        drop_fina_table()
    else:
        create_fina_table()
