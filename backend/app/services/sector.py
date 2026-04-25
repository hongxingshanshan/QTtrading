from typing import List
from sqlalchemy.orm import Session
from app.repositories.sector import DailySectorLimitRepository, ThsIndexRepository
from app.schemas.sector import DailySectorLimitItem, ThsIndexItem


class DailySectorLimitService:
    def __init__(self, db: Session):
        self.repository = DailySectorLimitRepository(db)

    def get_sector_data(
        self,
        sector_code: str = "",
        sector_name: str = "",
        sector_type: str = "",
        start_date: str = "",
        end_date: str = "",
    ) -> List[DailySectorLimitItem]:
        """获取板块数据"""
        items = self.repository.get_with_filter(
            sector_code=sector_code,
            sector_name=sector_name,
            sector_type=sector_type,
            start_date=start_date,
            end_date=end_date,
        )
        return [DailySectorLimitItem.model_validate(item) for item in items]


class ThsIndexService:
    def __init__(self, db: Session):
        self.repository = ThsIndexRepository(db)

    def get_all_index(self) -> List[ThsIndexItem]:
        """获取所有同花顺指数"""
        items = self.repository.get_all()
        return [ThsIndexItem.model_validate(item) for item in items]
