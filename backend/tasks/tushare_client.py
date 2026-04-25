"""Tushare API 客户端"""
import tushare as ts
from loguru import logger
from app.core.config import get_settings

_settings = get_settings()

# 初始化 Tushare token
try:
    ts.set_token(_settings.TUSHARE_TOKEN)
    pro = ts.pro_api()
    logger.info("Tushare API 初始化成功")
except Exception as e:
    logger.error(f"Tushare API 初始化失败: {e}")
    pro = None


def get_pro_api():
    """获取 Tushare pro API 实例"""
    if pro is None:
        raise RuntimeError("Tushare API 未初始化，请检查 TUSHARE_TOKEN 配置")
    return pro


def check_api_available() -> bool:
    """检查 Tushare API 是否可用"""
    try:
        api = get_pro_api()
        df = api.trade_cal(exchange='SSE', start_date='20240101', end_date='20240101')
        return not df.empty
    except Exception as e:
        logger.error(f"Tushare API 检查失败: {e}")
        return False
