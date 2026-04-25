from typing import Generator
from sqlalchemy.orm import Session
from app.core.database import get_db


def get_database() -> Generator[Session, None, None]:
    """获取数据库会话依赖"""
    yield from get_db()
