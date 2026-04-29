from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.logging import setup_logging, logger
from app.core.exceptions import register_exception_handlers
from app.api import api_router

settings = get_settings()
setup_logging()


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
    )

    # 注册异常处理器
    register_exception_handlers(app)

    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(api_router, prefix="/api")

    # 启动事件：启动定时任务调度器
    @app.on_event("startup")
    async def startup_event():
        from tasks.scheduler import start_scheduler
        start_scheduler()

    # 关闭事件：停止定时任务调度器
    @app.on_event("shutdown")
    async def shutdown_event():
        from tasks.scheduler import stop_scheduler
        stop_scheduler()

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    logger.info(f"启动 {settings.APP_NAME} 服务")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG,
    )
