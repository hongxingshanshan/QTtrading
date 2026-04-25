from typing import List
from sqlalchemy.orm import Session
from app.repositories.hotmoney import HotMoneyRepository, DailyHotMoneyTradeRepository
from app.schemas.hotmoney import HotMoneyInfoItem, DailyHotMoneyTradeItem


class HotMoneyService:
    def __init__(self, db: Session):
        self.repository = HotMoneyRepository(db)

    def get_hotmoney_list(
        self,
        name: str = "",
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[List[HotMoneyInfoItem], int]:
        """获取游资列表"""
        items, total = self.repository.get_paginated_with_filter(
            name=name,
            page=page,
            page_size=page_size,
        )
        return [HotMoneyInfoItem.model_validate(item) for item in items], total


class DailyHotMoneyTradeService:
    def __init__(self, db: Session):
        self.repository = DailyHotMoneyTradeRepository(db)

    def get_trade_list(
        self,
        hm_name: str = "",
        trade_date: str = "",
        ts_name: str = "",
        ts_code: str = "",
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[List[DailyHotMoneyTradeItem], int]:
        """获取龙虎榜交易列表"""
        items, total = self.repository.get_paginated_with_filter(
            hm_name=hm_name,
            trade_date=trade_date,
            ts_name=ts_name,
            ts_code=ts_code,
            page=page,
            page_size=page_size,
        )
        return [DailyHotMoneyTradeItem.model_validate(item) for item in items], total
