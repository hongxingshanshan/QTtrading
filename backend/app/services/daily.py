from typing import List
from sqlalchemy.orm import Session
from app.repositories.daily import DailyDataRepository
from app.schemas.daily import DailyDataItem


class DailyDataService:
    def __init__(self, db: Session):
        self.repository = DailyDataRepository(db)

    def get_daily_data(self, ts_code: str) -> List[DailyDataItem]:
        """获取日线数据"""
        items = self.repository.get_by_ts_code(ts_code)
        return [DailyDataItem.model_validate(item) for item in items]
