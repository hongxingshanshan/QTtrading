from typing import List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.daily import DailyData


class DailyDataRepository(BaseRepository[DailyData]):
    def __init__(self, db: Session):
        super().__init__(db, DailyData)

    def get_by_ts_code(self, ts_code: str) -> List[DailyData]:
        """根据股票代码查询日线数据"""
        return self.db.query(self.model).filter(
            self.model.ts_code == ts_code
        ).order_by(self.model.trade_date.asc()).all()
