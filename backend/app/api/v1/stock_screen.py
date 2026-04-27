"""
选股API接口
支持技术指标、行业、基本面、涨跌停等多条件组合选股
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field

from app.core.database import get_db
from strategy.stock_screener import StockScreener, get_all_templates, get_template_by_id

router = APIRouter(prefix="/stock_screen", tags=["选股"])


# ============== 请求/响应模型 ==============

class ConditionModel(BaseModel):
    """选股条件模型"""
    type: str = Field(
        default="indicator",
        description="条件类型: indicator/industry/basic/fina/limit/limit_status/macd_cross/ma_alignment/boll_position/consecutive/limit_up"
    )
    field: Optional[str] = Field(None, description="字段名")
    operator: Optional[str] = Field(None, description="操作符: >/>=/</<=/==/!=/in/not_in/between")
    op: Optional[str] = Field(None, description="操作符(简写): >/>=/</<=/==/!=/in/not_in/between")
    value: Optional[float | List[float] | List[str]] = Field(None, description="比较值")
    # 特殊条件参数
    cross_type: Optional[str] = Field(None, description="金叉死叉类型: golden/death")
    alignment: Optional[str] = Field(None, description="均线排列: bullish/bearish")
    direction: Optional[str] = Field(None, description="方向: up/down")
    days: Optional[int] = Field(None, description="天数")
    status: Optional[str] = Field(None, description="涨跌停状态: up/down/none")

    def model_dump(self, *args, **kwargs):
        """重写 model_dump，合并 op 和 operator 字段"""
        data = super().model_dump(*args, **kwargs)
        # 如果 op 字段有值但 operator 没有，则使用 op 的值
        if data.get('op') and not data.get('operator'):
            data['operator'] = data['op']
        # 删除 op 字段，避免混淆
        data.pop('op', None)
        return data


class ScreenRequest(BaseModel):
    """选股请求"""
    trade_date: str = Field(..., description="交易日期 YYYYMMDD", example="20260424")
    conditions: List[ConditionModel] = Field(..., description="条件列表")
    logic: str = Field(default="AND", description="逻辑组合: AND/OR")
    limit: int = Field(default=100, ge=1, le=1000, description="返回数量")
    offset: int = Field(default=0, ge=0, description="偏移量")
    order_by: str = Field(default="pct_change", description="排序字段")
    order_desc: bool = Field(default=True, description="是否降序")


class StockResult(BaseModel):
    """股票结果"""
    ts_code: str
    name: str
    industry: Optional[str]
    area: Optional[str]
    close: Optional[float]
    pct_change: Optional[float]
    indicators: dict


class ScreenResponse(BaseModel):
    """选股响应"""
    success: bool
    data: dict


class TemplateResponse(BaseModel):
    """策略模板响应"""
    success: bool
    data: List[dict]


# ============== API接口 ==============

@router.post("", response_model=ScreenResponse, summary="执行选股")
async def screen_stocks(
    request: ScreenRequest,
    db: Session = Depends(get_db)
):
    """
    执行选股

    ## 支持的条件类型

    | 类型 | 说明 | 示例 |
    |------|------|------|
    | indicator | 技术指标 | `{"type": "indicator", "field": "rsi6", "operator": "<", "value": 20}` |
    | industry | 行业/地域 | `{"type": "industry", "field": "industry", "operator": "in", "value": ["医药", "电子"]}` |
    | basic | 每日基本面(PE/PB/市值) | `{"type": "basic", "field": "pe_ttm", "operator": "<", "value": 20}` |
    | fina | 财务指标(ROE/毛利率) | `{"type": "fina", "field": "roe", "operator": ">", "value": 0.1}` |
    | limit | 涨跌停数据 | `{"type": "limit", "field": "limit_times", "operator": ">", "value": 1}` |
    | limit_status | 涨跌停状态 | `{"type": "limit_status", "status": "up"}` |
    | macd_cross | MACD金叉/死叉 | `{"type": "macd_cross", "cross_type": "golden"}` |
    | ma_alignment | 均线排列 | `{"type": "ma_alignment", "alignment": "bullish"}` |
    | boll_position | 布林带位置 | `{"type": "boll_position", "value": 0.2}` |
    | consecutive | 连续涨跌 | `{"type": "consecutive", "direction": "down", "days": 3}` |
    | limit_up | 连板条件 | `{"type": "limit_up", "days": 2}` |

    ## 示例请求

    ```json
    {
        "trade_date": "20260424",
        "conditions": [
            {"type": "indicator", "field": "rsi6", "operator": "<", "value": 15},
            {"type": "indicator", "field": "j_value", "operator": "<", "value": -10},
            {"type": "macd_cross", "cross_type": "golden"},
            {"type": "indicator", "field": "vol_ratio", "operator": ">", "value": 1}
        ],
        "logic": "AND",
        "limit": 50
    }
    ```

    ## 低估值选股示例

    ```json
    {
        "trade_date": "20260424",
        "conditions": [
            {"type": "basic", "field": "pe_ttm", "operator": "<", "value": 15},
            {"type": "basic", "field": "pb", "operator": "<", "value": 1.5},
            {"type": "fina", "field": "roe", "operator": ">", "value": 0.1}
        ],
        "logic": "AND"
    }
    ```

    ## 涨停板选股示例

    ```json
    {
        "trade_date": "20260424",
        "conditions": [
            {"type": "limit_status", "status": "up"},
            {"type": "limit", "field": "open_times", "operator": "==", "value": 0}
        ],
        "logic": "AND"
    }
    ```
    """
    try:
        screener = StockScreener(db)

        # 转换条件格式
        conditions = [cond.model_dump(exclude_none=True) for cond in request.conditions]

        result = screener.screen(
            trade_date=request.trade_date,
            conditions=conditions,
            logic=request.logic,
            limit=request.limit,
            offset=request.offset,
            order_by=request.order_by,
            order_desc=request.order_desc
        )

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"选股失败: {str(e)}")


@router.get("/templates", response_model=TemplateResponse, summary="获取策略模板")
async def get_templates():
    """
    获取预设的选股策略模板

    返回内置的策略模板列表，包括:
    - 超跌反弹: RSI超卖+KDJ低位+量能放大
    - 金叉买入: MACD金叉+均线多头+量能配合
    - 突破策略: 布林带上轨突破+量能放大
    - 抄底策略: 连续下跌+RSI超卖+WR超卖
    - 强势动量: 均线多头+放量上涨+MACD强势
    - 涨停板: 当日涨停股票
    - 低估值: 低PE+低PB+高ROE
    - 高成长: 营收增长+利润增长+高ROE
    - 小市值: 流通市值小于50亿
    """
    templates = get_all_templates()
    return {
        "success": True,
        "data": templates
    }


@router.get("/templates/{template_id}", summary="获取单个策略模板")
async def get_template(template_id: str):
    """根据ID获取策略模板详情"""
    template = get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return {
        "success": True,
        "data": template
    }


@router.post("/template/{template_id}", response_model=ScreenResponse, summary="使用模板选股")
async def screen_by_template(
    template_id: str,
    trade_date: str = Query(..., description="交易日期 YYYYMMDD"),
    limit: int = Query(default=100, description="返回数量"),
    db: Session = Depends(get_db)
):
    """
    使用预设模板执行选股

    直接使用模板ID进行选股，无需构建条件

    ## 可用模板ID

    - oversold_bounce: 超跌反弹
    - golden_cross: 金叉买入
    - breakout: 突破策略
    - bottom_fishing: 抄底策略
    - strong_momentum: 强势动量
    - limit_up_pool: 涨停板
    - low_valuation: 低估值
    - high_growth: 高成长
    - small_cap: 小市值
    """
    template = get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    try:
        screener = StockScreener(db)
        result = screener.screen(
            trade_date=trade_date,
            conditions=template['conditions'],
            logic="AND",
            limit=limit
        )

        return {
            "success": True,
            "data": {
                **result,
                "template_name": template['name']
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"选股失败: {str(e)}")


@router.get("/dates", summary="获取可用交易日期")
async def get_available_dates(
    limit: int = Query(default=30, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取有指标数据的交易日期列表"""
    try:
        screener = StockScreener(db)
        dates = screener.get_available_dates(limit)
        return {
            "success": True,
            "data": dates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/fields", summary="获取可用字段")
async def get_available_fields():
    """
    获取可用于选股的字段列表

    返回所有可用的字段类型和字段名
    """
    from strategy.stock_screener import StockScreener

    return {
        "success": True,
        "data": {
            "indicator_fields": StockScreener.INDICATOR_FIELDS,
            "stock_fields": StockScreener.STOCK_FIELDS,
            "basic_fields": StockScreener.BASIC_FIELDS,
            "fina_fields": StockScreener.FINA_FIELDS,
            "limit_fields": StockScreener.LIMIT_FIELDS,
            "operators": {
                "numeric": [">", ">=", "<", "<=", "==", "!=", "between"],
                "list": ["in", "not_in"],
                "string": ["==", "!="]
            },
            "special_conditions": [
                {"type": "macd_cross", "params": ["cross_type: golden/death"], "desc": "MACD金叉/死叉"},
                {"type": "ma_alignment", "params": ["alignment: bullish/bearish"], "desc": "均线多头/空头排列"},
                {"type": "boll_position", "params": ["value: 0-1"], "desc": "布林带位置"},
                {"type": "consecutive", "params": ["direction: up/down", "days: int"], "desc": "连续涨跌"},
                {"type": "limit_status", "params": ["status: up/down/none"], "desc": "涨跌停状态"},
                {"type": "limit_up", "params": ["days: int"], "desc": "连板条件"}
            ]
        }
    }


@router.get("/industries", summary="获取行业列表")
async def get_industries(db: Session = Depends(get_db)):
    """获取所有行业列表"""
    try:
        from sqlalchemy import text
        result = db.execute(text("""
            SELECT DISTINCT industry FROM stock_basic_info
            WHERE industry IS NOT NULL AND industry != ''
            ORDER BY industry
        """))
        industries = [row[0] for row in result.fetchall()]
        return {
            "success": True,
            "data": industries
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/areas", summary="获取地域列表")
async def get_areas(db: Session = Depends(get_db)):
    """获取所有地域列表"""
    try:
        from sqlalchemy import text
        result = db.execute(text("""
            SELECT DISTINCT area FROM stock_basic_info
            WHERE area IS NOT NULL AND area != ''
            ORDER BY area
        """))
        areas = [row[0] for row in result.fetchall()]
        return {
            "success": True,
            "data": areas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
