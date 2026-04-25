from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.repositories.base import BaseRepository
from app.models.stock import StockBasicInfo


class StockRepository(BaseRepository[StockBasicInfo]):
    def __init__(self, db: Session):
        super().__init__(db, StockBasicInfo)

    def get_by_ts_code(self, ts_code: str) -> Optional[StockBasicInfo]:
        """根据股票代码查询"""
        return self.db.query(self.model).filter(self.model.ts_code == ts_code).first()

    def get_paginated_with_filter(
        self,
        symbol: str = "",
        name: str = "",
        industry: str = "",
        start_date: str = "",
        end_date: str = "",
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[List[StockBasicInfo], int]:
        """带过滤条件的分页查询"""
        query = self.db.query(self.model)

        if symbol:
            query = query.filter(self.model.ts_code.like(f"%{symbol}%"))
        if name:
            query = query.filter(self.model.name.like(f"%{name}%"))
        if industry:
            query = query.filter(self.model.industry == industry)
        if start_date:
            query = query.filter(self.model.list_date >= start_date)
        if end_date:
            query = query.filter(self.model.list_date <= end_date)

        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total


# 别名，保持兼容
StockBasicInfoRepository = StockRepository
