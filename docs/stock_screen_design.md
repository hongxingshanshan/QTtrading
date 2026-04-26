# 选股功能设计方案

## 一、功能概述

支持多条件组合选股，包括技术指标、行业、基本面、涨跌停、概念板块等维度。

### 输入示例
```
日期: 20260424
条件: RSI < 15 AND KDJ_J < -10 AND MACD金叉 AND 量比 > 1 AND 行业=医药 AND PE < 20
```

### 输出示例
```
符合条件的股票列表，包含股票代码、名称、各指标值、匹配条件等
```

---

## 二、条件类型定义

### 1. 技术指标条件（已实现）

| 指标 | 字段名 | 条件类型 | 示例 |
|------|--------|----------|------|
| KDJ | k_value, d_value, j_value | 数值比较 | `j_value < -10` |
| RSI | rsi6, rsi12, rsi24 | 数值比较 | `rsi6 < 15` |
| MACD | macd_dif, macd_dea, macd_hist | 金叉/死叉/数值 | `macd金叉` |
| 布林带 | boll_upper, boll_lower, boll_position | 位置判断 | `boll_position < 0.2` |
| 均线 | ma5, ma10, ma20... | 多头/空头排列 | `ma5 > ma10 > ma20` |
| CCI | cci | 数值比较 | `cci < -100` |
| WR | wr10, wr14 | 数值比较 | `wr10 > 80` |
| 量比 | vol_ratio, vol_ratio_10 | 数值比较 | `vol_ratio > 1` |
| 涨跌幅 | pct_change, pct_change_5d... | 数值比较 | `pct_change_5d < -0.1` |
| 连续涨跌 | consecutive_up, consecutive_down | 数值比较 | `consecutive_down >= 3` |
| 回撤/反弹 | drawdown_20d, rebound_20d | 数值比较 | `drawdown_20d < -0.2` |
| 换手率 | turnover_rate, turnover_rate_ma5 | 数值比较 | `turnover_rate > 5` |
| ATR | atr14 | 数值比较 | `atr14 > 1` |
| VR | vr | 数值比较 | `vr < 50` |

### 2. 行业条件（已实现）

| 条件 | 字段名 | 示例 |
|------|--------|------|
| 行业 | industry | `行业 = 医药` |
| 地域 | area | `地域 = 北京` |
| 市场类型 | market | `市场 = 创业板` |

### 3. 涨跌停条件（已实现）

| 条件 | 字段名 | 说明 | 示例 |
|------|--------|------|------|
| 涨跌停状态 | limit_status | U=涨停, D=跌停 | `{"type": "limit_status", "status": "up"}` |
| 涨停次数 | limit_times | 历史涨停次数 | `limit_times > 3` |
| 打开次数 | open_times | 涨停打开次数 | `open_times == 0` (一字板) |
| 封单金额 | fd_amount | 封单金额(万) | `fd_amount > 10000` |
| 连板 | up_stat | 连板统计 | `{"type": "limit_up", "days": 2}` (2连板) |

### 4. 每日基本面条件（已实现 - daily_basic）

| 条件 | 字段名 | 说明 | 示例 |
|------|--------|------|------|
| 市盈率 | pe, pe_ttm | PE估值 | `pe_ttm < 20` |
| 市净率 | pb | PB估值 | `pb < 2` |
| 市销率 | ps, ps_ttm | PS估值 | `ps_ttm < 3` |
| 股息率 | dv_ratio, dv_ttm | 分红收益 | `dv_ttm > 3` |
| 总市值 | total_mv | 总市值(万元) | `total_mv < 1000000` (100亿以下) |
| 流通市值 | circ_mv | 流通市值(万元) | `circ_mv < 500000` (50亿以下) |
| 换手率 | turnover_rate | 日换手率 | `turnover_rate > 5` |
| 量比 | volume_ratio | 量比 | `volume_ratio > 1.5` |

### 5. 财务指标条件（已实现 - fina_indicator）

| 条件 | 字段名 | 说明 | 示例 |
|------|--------|------|------|
| **每股指标** | | | |
| 每股收益 | eps | 基本每股收益 | `eps > 0.5` |
| 每股净资产 | bps | 每股净资产 | `bps > 5` |
| 每股现金流 | ocfps | 经营现金流/股 | `ocfps > 0` |
| **盈利能力** | | | |
| 净资产收益率 | roe | ROE | `roe > 0.1` (10%以上) |
| 加权ROE | roe_waa | 加权平均ROE | `roe_waa > 0.15` |
| 扣非ROE | roe_dt | 扣非后ROE | `roe_dt > 0.1` |
| 总资产报酬率 | roa | ROA | `roa > 0.05` |
| 销售净利率 | netprofit_margin | 净利率 | `netprofit_margin > 0.1` |
| 销售毛利率 | grossprofit_margin | 毛利率 | `grossprofit_margin > 0.3` |
| **营运能力** | | | |
| 存货周转天数 | invturn_days | 存货周转 | `invturn_days < 60` |
| 应收账款周转天数 | arturn_days | 应收周转 | `arturn_days < 30` |
| 总资产周转率 | assets_turn | 资产周转 | `assets_turn > 0.5` |
| **偿债能力** | | | |
| 流动比率 | current_ratio | 流动比率 | `current_ratio > 1.5` |
| 速动比率 | quick_ratio | 速动比率 | `quick_ratio > 1` |
| 资产负债率 | debt_to_assets | 负债率 | `debt_to_assets < 0.6` |
| 已获利息倍数 | ebit_to_interest | 利息保障 | `ebit_to_interest > 3` |
| **成长能力** | | | |
| 营收增长 | or_yoy | 营收同比 | `or_yoy > 20` |
| 净利润增长 | netprofit_yoy | 利润同比 | `netprofit_yoy > 20` |
| 扣非净利润增长 | dt_netprofit_yoy | 扣非同比 | `dt_netprofit_yoy > 15` |
| ROE增长 | roe_yoy | ROE同比 | `roe_yoy > 0` |
| **现金流量** | | | |
| 企业自由现金流 | fcff | FCFF | `fcff > 0` |
| 股权自由现金流 | fcfe | FCFE | `fcfe > 0` |

### 6. 概念板块条件（待实现）

| 条件 | 说明 | 数据源 |
|------|------|--------|
| 概念板块 | 所属概念 | Tushare concept |
| 同花顺概念 | THS概念 | Tushare ths_index |
| 板块涨跌 | 板块当日涨跌 | 已有 daily_sector_limit_data |

---

## 三、数据结构设计

### 1. 选股条件请求格式

```json
{
  "trade_date": "20260424",
  "conditions": [
    {
      "type": "indicator",
      "field": "rsi6",
      "operator": "<",
      "value": 15
    },
    {
      "type": "indicator",
      "field": "j_value",
      "operator": "<",
      "value": -10
    },
    {
      "type": "macd_cross",
      "cross_type": "golden"
    },
    {
      "type": "basic",
      "field": "pe_ttm",
      "operator": "<",
      "value": 20
    },
    {
      "type": "fina",
      "field": "roe",
      "operator": ">",
      "value": 0.1
    },
    {
      "type": "limit_status",
      "status": "up"
    },
    {
      "type": "industry",
      "field": "industry",
      "operator": "in",
      "value": ["医药生物", "化学制药"]
    }
  ],
  "logic": "AND",
  "limit": 100
}
```

### 2. 选股结果响应格式

```json
{
  "success": true,
  "data": {
    "total": 25,
    "trade_date": "20260424",
    "stocks": [
      {
        "ts_code": "000001.SZ",
        "name": "平安银行",
        "industry": "银行",
        "close": 10.5,
        "pct_change": 0.02,
        "indicators": {
          "rsi6": 12.5,
          "j_value": -15.3,
          "macd_hist": 0.05,
          "vol_ratio": 1.2
        }
      }
    ]
  }
}
```

---

## 四、API接口

### 1. 执行选股

```
POST /api/stock_screen
```

### 2. 使用模板选股

```
POST /api/stock_screen/template/{template_id}?trade_date=20260424
```

### 3. 获取可用字段

```
GET /api/stock_screen/fields
```

### 4. 获取策略模板列表

```
GET /api/stock_screen/templates
```

---

## 五、预设策略模板

| 模板ID | 名称 | 描述 | 条件 |
|--------|------|------|------|
| oversold_bounce | 超跌反弹 | RSI超卖+KDJ低位+量能放大 | rsi6<20, j_value<0, vol_ratio>1.5 |
| golden_cross | 金叉买入 | MACD金叉+量能配合 | macd金叉, vol_ratio>1 |
| breakout | 突破策略 | 布林带上轨突破+量能放大 | boll_position>0.8, vol_ratio>2 |
| bottom_fishing | 抄底策略 | 连续下跌+RSI超卖+WR超卖 | 连续下跌3天, rsi6<25, wr10>80 |
| strong_momentum | 强势动量 | 均线多头+放量上涨+MACD强势 | 均线多头, vol_ratio>1.5, macd_hist>0 |
| limit_up_pool | 涨停板 | 当日涨停股票 | limit_status=up |
| low_valuation | 低估值 | 低PE+低PB+高ROE | pe_ttm<20, pb<2, roe>10% |
| high_growth | 高成长 | 营收增长+利润增长+高ROE | or_yoy>20%, netprofit_yoy>20%, roe>15% |
| small_cap | 小市值 | 流通市值小于50亿 | circ_mv<500000万 |

---

## 六、数据模型

### 1. 已有数据表

| 表名 | 说明 | 来源 |
|------|------|------|
| daily_indicator | 技术指标 | 本地计算 |
| daily_data | 日线行情 | Tushare daily |
| stock_basic_info | 股票基本信息 | Tushare stock_basic |
| daily_limit_data | 涨跌停数据 | Tushare limit_list |

### 2. 新增数据表

| 表名 | 说明 | 来源 |
|------|------|------|
| daily_basic | 每日基本面指标 | Tushare daily_basic |
| fina_indicator | 财务指标 | Tushare fina_indicator |

---

## 七、使用示例

### 1. 技术指标选股

```bash
curl -X POST "http://localhost:8000/api/stock_screen" \
  -H "Content-Type: application/json" \
  -d '{
    "trade_date": "20260424",
    "conditions": [
      {"type": "indicator", "field": "rsi6", "operator": "<", "value": 20},
      {"type": "indicator", "field": "j_value", "operator": "<", "value": 0},
      {"type": "macd_cross", "cross_type": "golden"}
    ],
    "logic": "AND"
  }'
```

### 2. 低估值选股

```bash
curl -X POST "http://localhost:8000/api/stock_screen" \
  -H "Content-Type: application/json" \
  -d '{
    "trade_date": "20260424",
    "conditions": [
      {"type": "basic", "field": "pe_ttm", "operator": "<", "value": 15},
      {"type": "basic", "field": "pb", "operator": "<", "value": 1.5},
      {"type": "fina", "field": "roe", "operator": ">", "value": 0.1}
    ],
    "logic": "AND"
  }'
```

### 3. 涨停板选股

```bash
curl -X POST "http://localhost:8000/api/stock_screen" \
  -H "Content-Type: application/json" \
  -d '{
    "trade_date": "20260424",
    "conditions": [
      {"type": "limit_status", "status": "up"},
      {"type": "limit", "field": "open_times", "operator": "==", "value": 0}
    ],
    "logic": "AND"
  }'
```

### 4. 使用模板选股

```bash
curl -X POST "http://localhost:8000/api/stock_screen/template/low_valuation?trade_date=20260424"
```

---

## 八、实现状态

| 功能 | 状态 | 说明 |
|------|------|------|
| 技术指标条件 | ✅ 已实现 | 支持所有预计算指标 |
| 行业/地域条件 | ✅ 已实现 | 支持行业、地域、市场筛选 |
| 涨跌停条件 | ✅ 已实现 | 支持涨跌停状态、连板等 |
| 每日基本面条件 | ✅ 已实现 | PE/PB/市值等 |
| 财务指标条件 | ✅ 已实现 | ROE/毛利率/增长率等 |
| 概念板块条件 | ⏳ 待实现 | 需接入概念数据 |
| 预设策略模板 | ✅ 已实现 | 9个内置模板 |
| 策略保存/加载 | ⏳ 待实现 | 用户自定义策略 |
| 历史回测验证 | ⏳ 待实现 | 验证策略有效性 |

---

## 九、数据采集任务

需要新增以下数据采集任务：

### 1. daily_basic 采集

```python
# tasks/basic_jobs.py
def fetch_daily_basic(trade_date: str):
    """采集每日基本面数据"""
    pro = ts.pro_api()
    df = pro.daily_basic(trade_date=trade_date)
    # 存入 daily_basic 表
```

### 2. fina_indicator 采集

```python
# tasks/fina_jobs.py
def fetch_fina_indicator(period: str):
    """采集财务指标数据"""
    pro = ts.pro_api()
    df = pro.fina_indicator(period=period)
    # 存入 fina_indicator 表
```

---

## 十、注意事项

1. **财务数据时效性**: 财务指标按季度更新，选股时使用最近一期财报数据
2. **数据完整性**: 部分股票可能缺少某些指标，查询时使用 LEFT JOIN
3. **性能优化**: 多表关联查询时注意索引优化
4. **概念板块**: 暂未实现，后续需要接入 Tushare concept 接口
