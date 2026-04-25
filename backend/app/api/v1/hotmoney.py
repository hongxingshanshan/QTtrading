from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_database
from app.services.hotmoney import HotMoneyService, DailyHotMoneyTradeService

router = APIRouter()


@router.get("/get_hotmoney_data")
def get_hotmoney_data(
    name: str = "",
    page: int = 1,
    pageSize: int = 10,
    db: Session = Depends(get_database),
):
    """获取游资列表"""
    service = HotMoneyService(db)
    data, total = service.get_hotmoney_list(
        name=name,
        page=page,
        page_size=pageSize,
    )
    return {"data": data, "total": total}


@router.get("/get_daily_hotmoney_trade_data")
def get_daily_hotmoney_trade_data(
    hmName: str = "",
    tradeDate: str = "",
    tsName: str = "",
    tsCode: str = "",
    page: int = 1,
    pageSize: int = 10,
    db: Session = Depends(get_database),
):
    """获取龙虎榜交易数据"""
    service = DailyHotMoneyTradeService(db)
    data, total = service.get_trade_list(
        hm_name=hmName,
        trade_date=tradeDate,
        ts_name=tsName,
        ts_code=tsCode,
        page=page,
        page_size=pageSize,
    )
    return {"data": data, "total": total}
