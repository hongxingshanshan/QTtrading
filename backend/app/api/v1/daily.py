from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_database
from app.services.daily import DailyDataService

router = APIRouter()


@router.get("/get_daily_data")
def get_daily_data(
    ts_code: str = "",
    db: Session = Depends(get_database),
):
    """获取日线数据"""
    service = DailyDataService(db)
    data = service.get_daily_data(ts_code)
    return {"data": data}
