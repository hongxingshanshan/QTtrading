from typing import List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.sector import DailySectorLimitData, ThsIndex


class DailySectorLimitRepository(BaseRepository[DailySectorLimitData]):
    def __init__(self, db: Session):
        super().__init__(db, DailySectorLimitData)

    def get_with_filter(
        self,
        sector_code: str = "",
        sector_name: str = "",
        sector_type: str = "",
        start_date: str = "",
        end_date: str = "",
    ) -> List[DailySectorLimitData]:
        """带过滤条件的查询"""
        query = self.db.query(self.model)

        if sector_code:
            query = query.filter(self.model.sector_code == sector_code)
        if sector_name:
            query = query.filter(self.model.sector_name.like(f"%{sector_name}%"))
        if sector_type:
            query = query.filter(self.model.sector_type == sector_type)
        if start_date:
            query = query.filter(self.model.trade_date >= start_date)
        if end_date:
            query = query.filter(self.model.trade_date <= end_date)

        return query.all()


class ThsIndexRepository(BaseRepository[ThsIndex]):
    def __init__(self, db: Session):
        super().__init__(db, ThsIndex)
