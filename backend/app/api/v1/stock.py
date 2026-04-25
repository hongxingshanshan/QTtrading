from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_database
from app.services.stock import StockService

router = APIRouter()


@router.get("/get_stock_basic_info")
def get_stock_basic_info(
    symbol: str = "",
    name: str = "",
    industry: str = "",
    startDate: str = "",
    endDate: str = "",
    page: int = 1,
    pageSize: int = 10,
    db: Session = Depends(get_database),
):
    """获取股票基本信息"""
    service = StockService(db)
    data, total = service.get_stock_list(
        symbol=symbol,
        name=name,
        industry=industry,
        start_date=startDate,
        end_date=endDate,
        page=page,
        page_size=pageSize,
    )
    return {"data": data, "total": total}
