from typing import List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.limit import DailyLimitData


class DailyLimitRepository(BaseRepository[DailyLimitData]):
    def __init__(self, db: Session):
        super().__init__(db, DailyLimitData)

    def get_all_ordered(self) -> List[DailyLimitData]:
        """查询全部并按日期排序"""
        return self.db.query(self.model).order_by(
            self.model.trade_date.desc()
        ).all()
