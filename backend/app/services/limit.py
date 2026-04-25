from typing import List
from sqlalchemy.orm import Session
from app.repositories.limit import DailyLimitRepository
from app.schemas.limit import DailyLimitItem


class DailyLimitService:
    def __init__(self, db: Session):
        self.repository = DailyLimitRepository(db)

    def get_limit_data(self) -> List[DailyLimitItem]:
        """获取涨跌停数据"""
        items = self.repository.get_all_ordered()
        return [DailyLimitItem.model_validate(item) for item in items]
