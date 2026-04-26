from fastapi import APIRouter
from app.api.v1 import hotmoney, stock, daily, limit, sector, trend, stock_screen

api_router = APIRouter()

api_router.include_router(hotmoney.router)
api_router.include_router(stock.router)
api_router.include_router(daily.router)
api_router.include_router(limit.router)
api_router.include_router(sector.router)
api_router.include_router(trend.router)
api_router.include_router(stock_screen.router)
