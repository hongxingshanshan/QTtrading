from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_database
from app.services.trend import StockTrendService
from app.schemas.trend import StockTrendResponse

router = APIRouter()


@router.get("/trend/{ts_code}", response_model=StockTrendResponse)
def get_stock_trend(
    ts_code: str,
    start_date: str = Query(default="", description="开始日期 YYYYMMDD"),
    end_date: str = Query(default="", description="结束日期 YYYYMMDD"),
    period: str = Query(default="daily", description="周期: daily/weekly/monthly"),
    adj_type: str = Query(default="qfq", description="复权类型: qfq前复权/hfq后复权/none不复权"),
    db: Session = Depends(get_database),
):
    """获取股票走势图数据

    包括基本信息、最新行情、K线数据、均线数据

    Args:
        ts_code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        period: 周期 (daily日K/weekly周K/monthly月K)
        adj_type: 复权类型 (qfq前复权/hfq后复权/none不复权)
    """
    service = StockTrendService(db)
    return service.get_trend_data(ts_code, start_date, end_date, period, adj_type)