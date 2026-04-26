from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "QTtrading"
    APP_ENV: str = "development"
    DEBUG: bool = False

    # 数据库配置
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "quant_trading"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Tushare 配置
    TUSHARE_TOKEN: str = ""

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+mysqlconnector://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    class Config:
        # 使用相对于 backend 目录的 .env 文件
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
