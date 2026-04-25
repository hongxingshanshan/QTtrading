from typing import List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.hotmoney import HotMoneyInfo, DailyHotMoneyTradeData


class HotMoneyRepository(BaseRepository[HotMoneyInfo]):
    def __init__(self, db: Session):
        super().__init__(db, HotMoneyInfo)

    def get_paginated_with_filter(
        self,
        name: str = "",
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[List[HotMoneyInfo], int]:
        """带过滤条件的分页查询"""
        query = self.db.query(self.model)

        if name:
            query = query.filter(self.model.name.like(f"%{name}%"))

        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total


class DailyHotMoneyTradeRepository(BaseRepository[DailyHotMoneyTradeData]):
    def __init__(self, db: Session):
        super().__init__(db, DailyHotMoneyTradeData)

    def get_paginated_with_filter(
        self,
        hm_name: str = "",
        trade_date: str = "",
        ts_name: str = "",
        ts_code: str = "",
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[List[DailyHotMoneyTradeData], int]:
        """带过滤条件的分页查询"""
        query = self.db.query(self.model)

        if hm_name:
            query = query.filter(self.model.hm_name.like(f"%{hm_name}%"))
        if trade_date:
            query = query.filter(self.model.trade_date == trade_date)
        if ts_name:
            query = query.filter(self.model.ts_name.like(f"%{ts_name}%"))
        if ts_code:
            query = query.filter(self.model.ts_code.like(f"%{ts_code}%"))

        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total
