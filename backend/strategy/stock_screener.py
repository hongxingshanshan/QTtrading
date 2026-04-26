"""
选股引擎 - 多条件组合选股
支持技术指标、行业、基本面、涨跌停等条件筛选
"""
from typing import List, Dict, Any, Optional
from sqlalchemy import and_, or_, text
from sqlalchemy.orm import Session
from loguru import logger

from app.models.indicator import DailyIndicator
from app.models.stock import StockBasicInfo
from app.models.daily import DailyData
from app.models.limit import DailyLimitData
from app.models.daily_basic import DailyBasic
from app.models.fina_indicator import FinaIndicator
from app.core.logging import setup_logging

setup_logging()


class StockScreener:
    """选股引擎"""

    # 支持的指标字段映射
    INDICATOR_FIELDS = {
        # KDJ
        'k_value': 'K值',
        'd_value': 'D值',
        'j_value': 'J值',
        # RSI
        'rsi6': 'RSI6',
        'rsi12': 'RSI12',
        'rsi24': 'RSI24',
        # MACD
        'macd_dif': 'MACD_DIF',
        'macd_dea': 'MACD_DEA',
        'macd_hist': 'MACD柱',
        # 布林带
        'boll_upper': '布林上轨',
        'boll_mid': '布林中轨',
        'boll_lower': '布林下轨',
        'boll_width': '布林宽度',
        'boll_position': '布林位置',
        # 均线
        'ma5': 'MA5',
        'ma10': 'MA10',
        'ma20': 'MA20',
        'ma30': 'MA30',
        'ma60': 'MA60',
        'ma120': 'MA120',
        'ma250': 'MA250',
        'ma_alignment': '均线排列',
        # 其他指标
        'cci': 'CCI',
        'wr10': 'WR10',
        'wr14': 'WR14',
        'obv': 'OBV',
        'obv_ma5': 'OBV_MA5',
        'obv_ma10': 'OBV_MA10',
        # 成交量
        'vol_ma5': '成交量MA5',
        'vol_ma10': '成交量MA10',
        'vol_ma20': '成交量MA20',
        'vol_ratio': '量比',
        'vol_ratio_10': '量比10',
        # 价格形态
        'consecutive_down': '连续下跌',
        'consecutive_up': '连续上涨',
        'drawdown_20d': '20日回撤',
        'drawdown_60d': '60日回撤',
        'rebound_20d': '20日反弹',
        'rebound_60d': '60日反弹',
        'amplitude': '振幅',
        'pct_change': '涨跌幅',
        'pct_change_5d': '5日涨跌',
        'pct_change_10d': '10日涨跌',
        'pct_change_20d': '20日涨跌',
        # 换手率
        'turnover_rate': '换手率',
        'turnover_rate_ma5': '5日换手',
        # ATR
        'atr14': 'ATR14',
        # DMA
        'dma_dif': 'DMA_DIF',
        'dma_ama': 'DMA_AMA',
        # VR
        'vr': 'VR',
    }

    # 股票基本信息字段
    STOCK_FIELDS = {
        'industry': '行业',
        'area': '地域',
        'market': '市场',
        'list_status': '上市状态',
    }

    # 涨跌停相关字段
    LIMIT_FIELDS = {
        'limit_status': '涨跌停状态',
        'limit_times': '涨停次数',
        'open_times': '打开次数',
        'fd_amount': '封单金额',
        'up_stat': '涨停统计',
    }

    # 每日基本面字段 (daily_basic)
    BASIC_FIELDS = {
        'pe': '市盈率',
        'pe_ttm': '市盈率TTM',
        'pb': '市净率',
        'ps': '市销率',
        'ps_ttm': '市销率TTM',
        'dv_ratio': '股息率',
        'dv_ttm': '股息率TTM',
        'total_mv': '总市值(万)',
        'circ_mv': '流通市值(万)',
        'total_share': '总股本(万)',
        'float_share': '流通股本(万)',
        'turnover_rate': '换手率',
        'turnover_rate_f': '自由流通换手率',
        'volume_ratio': '量比',
    }

    # 财务指标字段 (fina_indicator)
    FINA_FIELDS = {
        # 每股指标
        'eps': '每股收益',
        'bps': '每股净资产',
        'ocfps': '每股经营现金流',
        'cfps': '每股现金流',
        'revenue_ps': '每股营收',
        # 盈利能力
        'roe': '净资产收益率',
        'roe_waa': '加权平均ROE',
        'roe_dt': '扣非ROE',
        'roa': '总资产报酬率',
        'roic': '投入资本回报率',
        'netprofit_margin': '销售净利率',
        'grossprofit_margin': '销售毛利率',
        'ebit': '息税前利润',
        'ebitda': '息税折旧摊销前利润',
        # 营运能力
        'invturn_days': '存货周转天数',
        'arturn_days': '应收账款周转天数',
        'assets_turn': '总资产周转率',
        'turn_days': '营业周期',
        # 偿债能力
        'current_ratio': '流动比率',
        'quick_ratio': '速动比率',
        'cash_ratio': '保守速动比率',
        'debt_to_assets': '资产负债率',
        'debt_to_eqt': '产权比率',
        'ebit_to_interest': '已获利息倍数',
        # 成长能力
        'or_yoy': '营收同比增长',
        'tr_yoy': '总营收同比增长',
        'netprofit_yoy': '净利润同比增长',
        'dt_netprofit_yoy': '扣非净利润同比增长',
        'basic_eps_yoy': '每股收益同比增长',
        'roe_yoy': 'ROE同比增长',
        'equity_yoy': '净资产同比增长',
        # 现金流量
        'fcff': '企业自由现金流',
        'fcfe': '股权自由现金流',
        'ocf_to_or': '经营现金流/营收',
        # 其他
        'profit_dedt': '扣非净利润',
        'rd_exp': '研发费用',
    }

    def __init__(self, db: Session):
        self.db = db

    def screen(
        self,
        trade_date: str,
        conditions: List[Dict[str, Any]],
        logic: str = "AND",
        limit: int = 100,
        offset: int = 0,
        order_by: str = "pct_change",
        order_desc: bool = True
    ) -> Dict[str, Any]:
        """
        执行选股

        Args:
            trade_date: 交易日期 YYYYMMDD
            conditions: 条件列表
            logic: AND/OR 逻辑组合
            limit: 返回数量限制
            offset: 偏移量（分页）
            order_by: 排序字段
            order_desc: 是否降序

        Returns:
            {
                'total': 总数,
                'trade_date': 日期,
                'stocks': 股票列表
            }
        """
        try:
            # 检测需要关联哪些表
            need_limit = any(c.get('type') in ['limit', 'limit_status'] for c in conditions)
            need_basic = any(c.get('type') == 'basic' for c in conditions)
            need_fina = any(c.get('type') == 'fina' for c in conditions)

            # 构建基础查询
            query = self._build_base_query(trade_date, need_limit, need_basic, need_fina)

            # 构建条件
            where_conditions = []
            for cond in conditions:
                cond_expr = self._evaluate_condition(cond, trade_date)
                if cond_expr is not None:
                    where_conditions.append(cond_expr)

            if not where_conditions:
                return {'total': 0, 'trade_date': trade_date, 'stocks': []}

            # 应用逻辑组合
            if logic.upper() == "AND":
                query = query.where(and_(*where_conditions))
            else:
                query = query.where(or_(*where_conditions))

            # 统计总数 - 使用 subquery 方式
            from sqlalchemy import func
            count_subquery = query.subquery()
            total = self.db.query(func.count()).select_from(count_subquery).scalar()

            # 排序
            order_field = self._get_order_field(order_by)
            if order_desc:
                query = query.order_by(order_field.desc())
            else:
                query = query.order_by(order_field.asc())

            # 分页
            query = query.limit(limit).offset(offset)

            # 执行查询
            result = self.db.execute(query)
            stocks = self._format_result(result)

            return {
                'total': total,
                'trade_date': trade_date,
                'stocks': stocks
            }

        except Exception as e:
            logger.error(f"选股失败: {e}")
            raise

    def _build_base_query(self, trade_date: str, need_limit: bool = False,
                          need_basic: bool = False, need_fina: bool = False):
        """构建基础查询（关联指标表和股票信息表）"""
        query = self.db.query(
            DailyIndicator.ts_code,
            StockBasicInfo.name,
            StockBasicInfo.industry,
            StockBasicInfo.area,
            DailyData.close,
            DailyData.pct_chg,
            DailyIndicator
        ).join(
            StockBasicInfo,
            DailyIndicator.ts_code == StockBasicInfo.ts_code
        ).join(
            DailyData,
            and_(
                DailyIndicator.ts_code == DailyData.ts_code,
                DailyIndicator.trade_date == DailyData.trade_date
            )
        ).filter(
            DailyIndicator.trade_date == trade_date,
            StockBasicInfo.list_status == 'L'  # 只选上市股票
        )

        # 关联涨跌停表
        if need_limit:
            query = query.outerjoin(
                DailyLimitData,
                and_(
                    DailyIndicator.ts_code == DailyLimitData.ts_code,
                    DailyIndicator.trade_date == DailyLimitData.trade_date
                )
            )

        # 关联每日基本面表
        if need_basic:
            query = query.outerjoin(
                DailyBasic,
                and_(
                    DailyIndicator.ts_code == DailyBasic.ts_code,
                    DailyIndicator.trade_date == DailyBasic.trade_date
                )
            )

        # 关联财务指标表 (取最近一期财报)
        if need_fina:
            # 获取最近报告期
            recent_period = self._get_recent_period(trade_date)
            query = query.outerjoin(
                FinaIndicator,
                and_(
                    DailyIndicator.ts_code == FinaIndicator.ts_code,
                    FinaIndicator.end_date == recent_period
                )
            )

        return query

    def _get_recent_period(self, trade_date: str) -> str:
        """根据交易日期获取最近的财报期"""
        year = int(trade_date[:4])
        month = int(trade_date[4:6])

        # 确定最近财报期
        if month <= 3:
            # 1-3月，看去年三季报
            return f"{year-1}0930"
        elif month <= 6:
            # 4-6月，看去年年报
            return f"{year-1}1231"
        elif month <= 9:
            # 7-9月，看今年一季报
            return f"{year}0331"
        else:
            # 10-12月，看今年中报
            return f"{year}0630"

    def _evaluate_condition(self, condition: Dict[str, Any], trade_date: str):
        """
        评估单个条件，返回SQLAlchemy查询条件

        Args:
            condition: {
                "type": "indicator" | "industry" | "basic" | "fina" | "limit" |
                        "macd_cross" | "ma_alignment" | "limit_status",
                "field": "rsi6",
                "operator": "<" | ">" | "==" | "in" | "between",
                "value": 15 或 [10, 20]
            }
        """
        cond_type = condition.get('type', 'indicator')
        field = condition.get('field')
        operator = condition.get('operator')
        value = condition.get('value')

        # 技术指标条件
        if cond_type == 'indicator':
            return self._build_indicator_condition(field, operator, value)

        # 行业/地域条件
        elif cond_type == 'industry':
            return self._build_stock_condition(field, operator, value)

        # 每日基本面条件 (PE/PB/市值等)
        elif cond_type == 'basic':
            return self._build_basic_condition(field, operator, value)

        # 财务指标条件 (ROE/毛利率等)
        elif cond_type == 'fina':
            return self._build_fina_condition(field, operator, value)

        # 涨跌停条件
        elif cond_type == 'limit':
            return self._build_limit_condition(field, operator, value)

        # 涨跌停状态 (涨停/跌停/非涨跌停)
        elif cond_type == 'limit_status':
            return self._build_limit_status_condition(condition.get('status', 'up'))

        # MACD金叉/死叉
        elif cond_type == 'macd_cross':
            return self._build_macd_cross_condition(condition.get('cross_type', 'golden'))

        # 均线排列
        elif cond_type == 'ma_alignment':
            return self._build_ma_alignment_condition(condition.get('alignment', 'bullish'))

        # 布林带位置
        elif cond_type == 'boll_position':
            return self._build_boll_position_condition(value)

        # 连续涨跌
        elif cond_type == 'consecutive':
            return self._build_consecutive_condition(
                condition.get('direction', 'down'),
                condition.get('days', 3)
            )

        # 涨停板条件 (连板等)
        elif cond_type == 'limit_up':
            return self._build_limit_up_condition(condition.get('days', 1))

        return None

    def _build_indicator_condition(self, field: str, operator: str, value: Any):
        """构建指标条件"""
        if field not in self.INDICATOR_FIELDS:
            logger.warning(f"未知指标字段: {field}")
            return None

        column = getattr(DailyIndicator, field)
        return self._apply_operator(column, operator, value)

    def _build_stock_condition(self, field: str, operator: str, value: Any):
        """构建股票信息条件"""
        if field not in self.STOCK_FIELDS:
            logger.warning(f"未知股票字段: {field}")
            return None

        column = getattr(StockBasicInfo, field)
        return self._apply_operator(column, operator, value)

    def _build_basic_condition(self, field: str, operator: str, value: Any):
        """构建每日基本面条件 (PE/PB/市值等)"""
        if field not in self.BASIC_FIELDS:
            logger.warning(f"未知基本面字段: {field}")
            return None

        column = getattr(DailyBasic, field)
        return self._apply_operator(column, operator, value)

    def _build_fina_condition(self, field: str, operator: str, value: Any):
        """构建财务指标条件 (ROE/毛利率等)"""
        if field not in self.FINA_FIELDS:
            logger.warning(f"未知财务字段: {field}")
            return None

        column = getattr(FinaIndicator, field)
        return self._apply_operator(column, operator, value)

    def _build_limit_condition(self, field: str, operator: str, value: Any):
        """构建涨跌停条件"""
        if field not in self.LIMIT_FIELDS:
            logger.warning(f"未知涨跌停字段: {field}")
            return None

        column = getattr(DailyLimitData, field)
        return self._apply_operator(column, operator, value)

    def _build_limit_status_condition(self, status: str):
        """
        构建涨跌停状态条件
        status: 'up'=涨停, 'down'=跌停, 'none'=非涨跌停
        """
        if status == 'up':
            return DailyLimitData.limit_status == 'U'
        elif status == 'down':
            return DailyLimitData.limit_status == 'D'
        else:
            # 非涨跌停
            return or_(
                DailyLimitData.limit_status == None,
                DailyLimitData.limit_status == ''
            )

    def _build_limit_up_condition(self, days: int):
        """
        构建连板条件
        days: 连续涨停天数
        """
        # up_stat 格式如 "2/3" 表示2连板，总共3次涨停
        return DailyLimitData.up_stat.like(f"{days}/%")

    def _apply_operator(self, column, operator: str, value: Any):
        """应用操作符"""
        if operator == '>':
            return column > value
        elif operator == '>=':
            return column >= value
        elif operator == '<':
            return column < value
        elif operator == '<=':
            return column <= value
        elif operator == '==':
            return column == value
        elif operator == '!=':
            return column != value
        elif operator == 'in':
            return column.in_(value)
        elif operator == 'not_in':
            return ~column.in_(value)
        elif operator == 'between':
            return column.between(value[0], value[1])
        return None

    def _build_macd_cross_condition(self, cross_type: str):
        """构建MACD金叉/死叉条件"""
        if cross_type == 'golden':
            return and_(
                DailyIndicator.macd_dif > DailyIndicator.macd_dea,
                DailyIndicator.macd_hist > 0
            )
        else:
            return and_(
                DailyIndicator.macd_dif < DailyIndicator.macd_dea,
                DailyIndicator.macd_hist < 0
            )

    def _build_ma_alignment_condition(self, alignment: str):
        """构建均线排列条件"""
        if alignment == 'bullish':
            return and_(
                DailyIndicator.ma5 > DailyIndicator.ma10,
                DailyIndicator.ma10 > DailyIndicator.ma20,
                DailyIndicator.ma20 > DailyIndicator.ma60
            )
        else:
            return and_(
                DailyIndicator.ma5 < DailyIndicator.ma10,
                DailyIndicator.ma10 < DailyIndicator.ma20,
                DailyIndicator.ma20 < DailyIndicator.ma60
            )

    def _build_boll_position_condition(self, position: float):
        """构建布林带位置条件"""
        return DailyIndicator.boll_position < position

    def _build_consecutive_condition(self, direction: str, days: int):
        """构建连续涨跌条件"""
        if direction == 'down':
            return DailyIndicator.consecutive_down >= days
        else:
            return DailyIndicator.consecutive_up >= days

    def _get_order_field(self, order_by: str):
        """获取排序字段"""
        if order_by in self.INDICATOR_FIELDS:
            return getattr(DailyIndicator, order_by)
        elif order_by in self.BASIC_FIELDS:
            return getattr(DailyBasic, order_by)
        elif order_by == 'pct_change':
            return DailyData.pct_chg
        elif order_by == 'close':
            return DailyData.close
        return DailyIndicator.ts_code

    def _format_result(self, result) -> List[Dict]:
        """格式化查询结果"""
        stocks = []
        for row in result:
            indicator = row[-1]  # DailyIndicator 对象
            stocks.append({
                'ts_code': row.ts_code,
                'name': row.name,
                'industry': row.industry,
                'area': row.area,
                'close': float(row.close) if row.close else None,
                'pct_change': float(row.pct_chg) if row.pct_chg else None,
                'indicators': {
                    'rsi6': float(indicator.rsi6) if indicator.rsi6 else None,
                    'j_value': float(indicator.j_value) if indicator.j_value else None,
                    'macd_hist': float(indicator.macd_hist) if indicator.macd_hist else None,
                    'vol_ratio': float(indicator.vol_ratio) if indicator.vol_ratio else None,
                    'k_value': float(indicator.k_value) if indicator.k_value else None,
                    'd_value': float(indicator.d_value) if indicator.d_value else None,
                    'boll_position': float(indicator.boll_position) if indicator.boll_position else None,
                }
            })
        return stocks

    def get_available_dates(self, limit: int = 30) -> List[str]:
        """获取有数据的交易日期列表"""
        dates = self.db.query(DailyIndicator.trade_date).distinct().order_by(
            DailyIndicator.trade_date.desc()
        ).limit(limit).all()
        return [d[0] for d in dates]


# ============== 预设策略模板 ==============

SCREEN_TEMPLATES = [
    {
        "id": "oversold_bounce",
        "name": "超跌反弹",
        "description": "RSI超卖+KDJ低位+量能放大",
        "conditions": [
            {"type": "indicator", "field": "rsi6", "operator": "<", "value": 20},
            {"type": "indicator", "field": "j_value", "operator": "<", "value": 0},
            {"type": "indicator", "field": "vol_ratio", "operator": ">", "value": 1.5},
            {"type": "indicator", "field": "drawdown_20d", "operator": "<", "value": -0.15}
        ]
    },
    {
        "id": "golden_cross",
        "name": "金叉买入",
        "description": "MACD金叉+均线多头+量能配合",
        "conditions": [
            {"type": "macd_cross", "cross_type": "golden"},
            {"type": "indicator", "field": "vol_ratio", "operator": ">", "value": 1},
            {"type": "indicator", "field": "pct_change", "operator": ">", "value": 0}
        ]
    },
    {
        "id": "breakout",
        "name": "突破策略",
        "description": "布林带上轨突破+量能放大",
        "conditions": [
            {"type": "indicator", "field": "boll_position", "operator": ">", "value": 0.8},
            {"type": "indicator", "field": "vol_ratio", "operator": ">", "value": 2},
            {"type": "indicator", "field": "pct_change", "operator": ">", "value": 0.03}
        ]
    },
    {
        "id": "bottom_fishing",
        "name": "抄底策略",
        "description": "连续下跌+RSI超卖+WR超卖",
        "conditions": [
            {"type": "consecutive", "direction": "down", "days": 3},
            {"type": "indicator", "field": "rsi6", "operator": "<", "value": 25},
            {"type": "indicator", "field": "wr10", "operator": ">", "value": 80}
        ]
    },
    {
        "id": "strong_momentum",
        "name": "强势动量",
        "description": "均线多头+放量上涨+MACD强势",
        "conditions": [
            {"type": "ma_alignment", "alignment": "bullish"},
            {"type": "indicator", "field": "vol_ratio", "operator": ">", "value": 1.5},
            {"type": "indicator", "field": "macd_hist", "operator": ">", "value": 0},
            {"type": "indicator", "field": "pct_change", "operator": ">", "value": 0.02}
        ]
    },
    {
        "id": "limit_up_pool",
        "name": "涨停板",
        "description": "当日涨停股票",
        "conditions": [
            {"type": "limit_status", "status": "up"}
        ]
    },
    {
        "id": "low_valuation",
        "name": "低估值",
        "description": "低PE+低PB+高ROE",
        "conditions": [
            {"type": "basic", "field": "pe_ttm", "operator": "<", "value": 20},
            {"type": "basic", "field": "pb", "operator": "<", "value": 2},
            {"type": "fina", "field": "roe", "operator": ">", "value": 0.1}
        ]
    },
    {
        "id": "high_growth",
        "name": "高成长",
        "description": "营收增长+利润增长+高ROE",
        "conditions": [
            {"type": "fina", "field": "or_yoy", "operator": ">", "value": 20},
            {"type": "fina", "field": "netprofit_yoy", "operator": ">", "value": 20},
            {"type": "fina", "field": "roe", "operator": ">", "value": 0.15}
        ]
    },
    {
        "id": "small_cap",
        "name": "小市值",
        "description": "流通市值小于50亿",
        "conditions": [
            {"type": "basic", "field": "circ_mv", "operator": "<", "value": 500000}  # 万元
        ]
    }
]


def get_template_by_id(template_id: str) -> Optional[Dict]:
    """根据ID获取策略模板"""
    for template in SCREEN_TEMPLATES:
        if template['id'] == template_id:
            return template
    return None


def get_all_templates() -> List[Dict]:
    """获取所有策略模板"""
    return SCREEN_TEMPLATES
