# 股票走势图设计方案

## 一、页面布局

```
┌──────────────────────────────────────────────────────────────────────┐
│ 【顶部信息栏】                                                        │
│ ┌────────────────────────────────────────────────────────────────┐  │
│ │ 平安银行(000001.SZ)  11.25  +0.15(+1.35%)                      │  │
│ │ 今开:11.10  最高:11.30  最低:11.05  昨收:11.10                  │  │
│ │ 成交量:52.3万手  成交额:5.86亿  换手率:0.27%                    │  │
│ └────────────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────┤
│ 【工具栏】                                                            │
│ ┌────────────────────────────────────────────────────────────────┐  │
│ │ 周期: [日K] [周K] [月K]  |  复权: [前复权] [后复权] [不复权]    │  │
│ │ 指标: [MACD] [KDJ] [BOLL] [RSI]  |  均线: MA5 MA10 MA20 MA60   │  │
│ └────────────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────┤
│ 【主图区域 - K线图 + 均线】                                           │
│                                                                      │
│   价格 ▲                                                             │
│        │    ┌───┐                                                    │
│   11.30│    │   │   ╱╲    ┌───┐                                      │
│        │  ┌─┤   ├──╱  ╲───┤   ├───═                                  │
│   11.10│  │ │   │          │   │   │  ─── MA5                        │
│        │  │ └───┘          └───┘   │  ─── MA10                       │
│   10.90│  │                      ┌─┘  ─── MA20                       │
│        │  └──────────────────────┘                                    │
│        └─────────────────────────────────────────────────────▶ 日期   │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│ 【副图区域1 - 成交量】                                                │
│   成交量▲                                                            │
│        │  ▓▓  ▓▓    ▓▓                                               │
│        │  ▓▓▓▓▓▓▓▓  ▓▓▓▓  ▓▓                                         │
│        │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                                          │
│        └─────────────────────────────────────────────────────▶        │
│              (红色上涨/绿色下跌)                                       │
├──────────────────────────────────────────────────────────────────────┤
│ 【副图区域2 - MACD指标】                                               │
│   MACD ▲                                                             │
│        │      ┌──┐                                                   │
│      0 │──────┤  ├──┐────────────────────── DIF                      │
│        │         └──┘                    DEA                        │
│        │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  MACD柱                      │
│        └─────────────────────────────────────────────────────▶        │
└──────────────────────────────────────────────────────────────────────┘
```

## 二、功能模块

### 1. 顶部信息栏
| 信息项 | 数据来源 | 说明 |
|--------|----------|------|
| 股票名称/代码 | stock_basic_info | 基本信息查询 |
| 当前价 | daily_data.close | 最新收盘价 |
| 涨跌额 | daily_data.price_change | 涨跌金额 |
| 涨跌幅 | daily_data.pct_chg | 涨跌百分比 |
| 今开 | daily_data.open | 当日开盘价 |
| 最高 | daily_data.high | 当日最高价 |
| 最低 | daily_data.low | 当日最低价 |
| 昨收 | daily_data.pre_close | 上一交易日收盘价 |
| 成交量 | daily_data.vol | 成交量（手） |
| 成交额 | daily_data.amount | 成交额（千元） |

### 2. 工具栏功能

**周期切换：**
- 日K线（默认）
- 周K线（后端聚合）
- 月K线（后端聚合）

**复权设置：**
- 前复权（默认）- 以当前价格为基准
- 后复权 - 以上市价格为基准
- 不复权 - 原始价格

**均线系统：**
- MA5（5日均线）
- MA10（10日均线）
- MA20（20日均线）
- MA60（60日均线）
- 支持自定义显示/隐藏

**技术指标：**
- MACD（默认显示）
- KDJ
- BOLL（布林带）
- RSI
- VOL（成交量）

### 3. 主图区域（K线图）

**K线绘制规则：**
- 红色/空心：收盘价 > 开盘价（上涨）
- 绿色/实心：收盘价 < 开盘价（下跌）
- 上影线：最高价
- 下影线：最低价
- 实体：开盘价到收盘价

**均线计算：**
```typescript
// MA5 = 最近5日收盘价之和 / 5
const calculateMA = (data: number[], period: number) => {
  return data.map((_, index) => {
    if (index < period - 1) return null
    const sum = data.slice(index - period + 1, index + 1).reduce((a, b) => a + b, 0)
    return (sum / period).toFixed(2)
  })
}
```

### 4. 副图区域

**成交量柱状图：**
- 根据涨跌显示不同颜色
- 涨：红色
- 跌：绿色

**MACD指标：**
- DIF线：快线（12日EMA - 26日EMA）
- DEA线：慢线（DIF的9日EMA）
- MACD柱：(DIF - DEA) × 2

## 三、数据接口设计

### 1. 获取股票日线数据
```
GET /api/stock/trend/:ts_code?start_date=20230101&end_date=20231231
```

响应：
```json
{
  "code": 0,
  "data": {
    "basic": {
      "ts_code": "000001.SZ",
      "name": "平安银行",
      "industry": "银行"
    },
    "latest": {
      "close": 11.25,
      "pct_chg": 1.35,
      "vol": 523000,
      "amount": 586000
    },
    "kline": [
      {
        "trade_date": "20231201",
        "open": 11.10,
        "high": 11.30,
        "low": 11.05,
        "close": 11.25,
        "vol": 523000,
        "amount": 586000,
        "pct_chg": 1.35
      }
    ],
    "ma": {
      "ma5": [11.20, 11.22, ...],
      "ma10": [11.15, 11.18, ...],
      "ma20": [11.10, 11.12, ...],
      "ma60": [10.95, 10.97, ...]
    }
  }
}
```

### 2. 获取复权数据
```
GET /api/stock/adj/:ts_code?start_date=20230101&end_date=20231231&type=qfq
```

## 四、前端组件结构

```
src/modules/StockTrend/
├── index.tsx                    # 页面入口
├── components/
│   ├── StockHeader.tsx          # 顶部信息栏
│   ├── ToolBar.tsx              # 工具栏
│   ├── KLineChart.tsx           # K线图主图
│   ├── VolumeChart.tsx          # 成交量副图
│   ├── MACDChart.tsx            # MACD指标副图
│   └── ChartContainer.tsx       # 图表容器
├── hooks/
│   ├── useStockData.ts          # 数据获取
│   └── useIndicator.ts          # 指标计算
└── utils/
    ├── ma.ts                    # 均线计算
    ├── macd.ts                  # MACD计算
    └── kdj.ts                   # KDJ计算
```

## 五、技术实现要点

### 1. ECharts K线图配置
```typescript
const klineOption = {
  animation: false,
  legend: { data: ['K线', 'MA5', 'MA10', 'MA20', 'MA60'] },
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross' }
  },
  axisPointer: {
    link: [{ xAxisIndex: 'all' }]
  },
  dataZoom: [
    { type: 'inside', xAxisIndex: [0, 1], start: 50, end: 100 },
    { show: true, xAxisIndex: [0, 1], type: 'slider', bottom: 10 }
  ],
  xAxis: [
    { type: 'category', data: dates, gridIndex: 0 },
    { type: 'category', data: dates, gridIndex: 1 }
  ],
  yAxis: [
    { scale: true, gridIndex: 0 },
    { scale: true, gridIndex: 1 }
  ],
  grid: [
    { left: '10%', right: '8%', height: '60%' },
    { left: '10%', right: '8%', top: '70%', height: '20%' }
  ],
  series: [
    {
      name: 'K线',
      type: 'candlestick',
      data: klineData,
      itemStyle: {
        color: '#ef5350',      // 阳线填充色
        color0: '#26a69a',     // 阴线填充色
        borderColor: '#ef5350', // 阳线边框
        borderColor0: '#26a69a' // 阴线边框
      }
    },
    { name: 'MA5', type: 'line', data: ma5, smooth: true, lineStyle: { width: 1 } },
    { name: 'MA10', type: 'line', data: ma10, smooth: true, lineStyle: { width: 1 } },
    { name: 'MA20', type: 'line', data: ma20, smooth: true, lineStyle: { width: 1 } },
    { name: 'MA60', type: 'line', data: ma60, smooth: true, lineStyle: { width: 1 } },
    {
      name: '成交量',
      type: 'bar',
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: volumeData
    }
  ]
}
```

### 2. 复权计算
```typescript
// 前复权：以最新价格为基准
const qfq = (kline: KlineData[], adjFactors: AdjFactor[]) => {
  const latestAdj = adjFactors[adjFactors.length - 1].adj_factor
  return kline.map((item, index) => {
    const adj = adjFactors[index]?.adj_factor || 1
    const ratio = latestAdj / adj
    return {
      ...item,
      open: item.open * ratio,
      high: item.high * ratio,
      low: item.low * ratio,
      close: item.close * ratio
    }
  })
}
```

## 六、交互设计

1. **鼠标悬停**：显示十字光标，展示当前K线的详细数据
2. **滚轮缩放**：调整显示的时间范围
3. **拖拽平移**：查看历史数据
4. **点击均线**：显示/隐藏对应均线
5. **双击**：重置视图

## 七、性能优化

1. 数据分页加载，初始加载最近250个交易日
2. 滚动到边缘时自动加载更多历史数据
3. 使用 ECharts 的 `large` 模式处理大数据量
4. 缓存已加载的数据，避免重复请求
