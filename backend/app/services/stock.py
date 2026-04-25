from typing import List
from sqlalchemy.orm import Session
from app.repositories.stock import StockRepository
from app.schemas.stock import StockBasicInfoItem


class StockService:
    def __init__(self, db: Session):
        self.repository = StockRepository(db)

    def get_stock_list(
        self,
        symbol: str = "",
        name: str = "",
        industry: str = "",
        start_date: str = "",
        end_date: str = "",
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[List[StockBasicInfoItem], int]:
        """获取股票列表"""
        items, total = self.repository.get_paginated_with_filter(
            symbol=symbol,
            name=name,
            industry=industry,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
        )
        return [StockBasicInfoItem.model_validate(item) for item in items], total
