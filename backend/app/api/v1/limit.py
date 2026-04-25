from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_database
from app.services.limit import DailyLimitService

router = APIRouter()


@router.get("/get_daily_limit_data")
def get_daily_limit_data(
    db: Session = Depends(get_database),
):
    """获取涨跌停数据"""
    service = DailyLimitService(db)
    data = service.get_limit_data()
    return {"data": data}
