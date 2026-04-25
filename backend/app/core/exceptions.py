from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """应用异常基类"""
    def __init__(self, code: int, message: str, data: dict = None):
        self.code = code
        self.message = message
        self.data = data


class NotFoundException(AppException):
    """资源不存在"""
    def __init__(self, message: str = "资源不存在"):
        super().__init__(code=404, message=message)


class DatabaseException(AppException):
    """数据库异常"""
    def __init__(self, message: str = "数据库操作失败"):
        super().__init__(code=500, message=message)


def register_exception_handlers(app):
    """注册全局异常处理器"""
    @app.exception_handler(AppException)
    async def app_exception_handler(request, exc: AppException):
        return JSONResponse(
            status_code=exc.code,
            content={
                "code": exc.code,
                "message": exc.message,
                "data": exc.data
            }
        )
