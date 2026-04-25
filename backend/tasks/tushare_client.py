"""Tushare 客户端模块"""
import tushare as ts
from app.core.config import get_settings

_settings = get_settings()

# 初始化 Tushare token
ts.set_token(_settings.TUSHARE_TOKEN)

# 创建 pro API 实例
pro = ts.pro_api()


def get_pro_api():
    """获取 Tushare pro API 实例"""
    return pro
