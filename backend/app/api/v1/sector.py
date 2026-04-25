from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_database
from app.services.sector import DailySectorLimitService, ThsIndexService

router = APIRouter()


@router.get("/get_daily_sector_limit_data")
def get_daily_sector_limit_data(
    sector_code: str = "",
    sector_name: str = "",
    sector_type: str = "",
    start_date: str = "",
    end_date: str = "",
    db: Session = Depends(get_database),
):
    """获取板块涨跌停数据"""
    service = DailySectorLimitService(db)
    data = service.get_sector_data(
        sector_code=sector_code,
        sector_name=sector_name,
        sector_type=sector_type,
        start_date=start_date,
        end_date=end_date,
    )
    return {"data": data}


@router.get("/get_all_ths_index")
def get_all_ths_index(
    db: Session = Depends(get_database),
):
    """获取同花顺指数"""
    service = ThsIndexService(db)
    data = service.get_all_index()
    return {"data": data}
