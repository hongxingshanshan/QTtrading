# QTtrading 项目

量化交易数据查询与策略分析平台，提供龙虎榜、股票信息、涨跌停、板块行情等数据查询功能，以及智能选股、策略回测、因子分析等量化分析工具。

## 技术栈

### 后端
| 技术 | 版本 | 用途 |
|------|------|------|
| FastAPI | 0.110.0 | 高性能 Web 框架 |
| SQLAlchemy | 2.0.25 | ORM 框架 |
| Pydantic | 2.6.1 | 数据校验 |
| Pandas | 2.2.0 | 数据分析 |
| NumPy | 1.26.4 | 数值计算 |
| Tushare | 1.4.3 | 金融数据源 |
| APScheduler | 3.10.4 | 定时任务调度 |
| Loguru | 0.7.2 | 日志系统 |

### 前端
| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.2.0 | UI 框架 |
| TypeScript | 5.3.3 | 类型安全 |
| Vite | 5.1.0 | 构建工具 |
| Ant Design | 5.14.0 | UI 组件库 |
| ECharts | 5.5.0 | 图表可视化 |
| TanStack Query | 5.20.0 | 数据请求/缓存 |
| TailwindCSS | 3.4.1 | 样式框架 |
| Zustand | 4.5.0 | 状态管理 |

## 项目结构

```
QTtrading/
├── backend/                          # 后端服务
│   ├── app/                          # 应用核心
│   │   ├── api/                      # API 接口层
│   │   │   ├── deps.py               # 依赖注入
│   │   │   └── v1/                   # V1 版本 API
│   │   │       ├── router.py         # 路由汇总
│   │   │       ├── stock.py          # 股票 API
│   │   │       ├── hotmoney.py       # 游资 API
│   │   │       ├── daily.py          # 日线 API
│   │   │       ├── limit.py          # 涨跌停 API
│   │   │       ├── sector.py         # 板块 API
│   │   │       ├── trend.py          # 走势图 API
│   │   │       └── stock_screen.py   # 智能选股 API
│   │   ├── core/                     # 核心配置
│   │   │   ├── config.py             # 配置管理
│   │   │   ├── database.py           # 数据库连接
│   │   │   ├── exceptions.py         # 异常处理
│   │   │   └── logging.py            # 日志配置
│   │   ├── models/                   # 数据模型 (ORM)
│   │   ├── repositories/             # 数据仓库层
│   │   ├── schemas/                  # Pydantic 模型
│   │   ├── services/                 # 业务服务层
│   │   └── main.py                   # 应用入口
│   ├── strategy/                     # 策略分析模块
│   │   ├── indicator_calc.py         # 技术指标计算
│   │   ├── signal_engine.py          # 信号引擎
│   │   ├── backtest_engine.py        # 回测引擎
│   │   ├── factor_analysis.py        # 因子分析
│   │   ├── stock_screener.py         # 选股引擎
│   │   └── strategy_optimizer.py     # 策略优化器
│   ├── tasks/                        # 定时任务
│   │   ├── scheduler.py              # 调度器
│   │   ├── init_jobs.py              # 初始化任务
│   │   ├── incr_jobs.py              # 增量任务
│   │   ├── basic_jobs.py             # 基本面数据任务
│   │   ├── fina_jobs.py              # 财务指标任务
│   │   ├── indicator_jobs.py         # 指标计算任务
│   │   └── kline_jobs.py             # K线数据任务
│   ├── scripts/                      # 数据库脚本
│   ├── logs/                         # 日志目录
│   ├── .env                          # 环境变量
│   └── requirements.txt              # Python 依赖
│
├── frontend/                         # 前端应用
│   ├── src/
│   │   ├── modules/                  # 功能模块
│   │   │   ├── Home/                 # 首页
│   │   │   ├── Stock/                # 股票列表
│   │   │   ├── StockTrend/           # 股票走势图
│   │   │   ├── StockScreen/          # 智能选股
│   │   │   ├── HotMoney/             # 龙虎榜
│   │   │   ├── HotMoneyInfo/         # 游资信息
│   │   │   ├── DailyLimit/           # 涨跌停数据
│   │   │   └── SectorLimit/          # 板块行情
│   │   ├── shared/                   # 共享资源
│   │   │   ├── api/                  # API 客户端
│   │   │   ├── components/           # 公共组件
│   │   │   ├── hooks/                # 自定义 Hooks
│   │   │   ├── types/                # 类型定义
│   │   │   └── utils/                # 工具函数
│   │   ├── router.tsx                # 路由配置
│   │   └── App.tsx                   # 应用入口
│   ├── package.json                  # 前端依赖
│   └── vite.config.ts                # Vite 配置
│
├── start-backend.bat                 # 后端启动脚本
├── start-frontend.bat                # 前端启动脚本
└── README.md
```

## 快速启动

### 环境准备

1. **Python 环境**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Node.js 环境**
   ```bash
   cd frontend
   npm install
   ```

3. **数据库配置**
   创建 `backend/.env` 文件：
   ```env
   APP_NAME=QTtrading
   APP_ENV=development
   DEBUG=true

   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_NAME=quant_trading

   TUSHARE_TOKEN=your_tushare_token

   LOG_LEVEL=INFO
   LOG_FILE=logs/app.log
   ```

### 启动服务

**Windows 用户：**
- 双击 `start-backend.bat` 启动后端服务
- 双击 `start-frontend.bat` 启动前端服务

**手动启动：**
```bash
# 后端
cd backend
python -m uvicorn app.main:app --reload --port 8000

# 前端
cd frontend
npm run dev
```

### 访问地址
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

## API 接口

### 股票相关
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/get_stock_basic_info` | 获取股票基本信息列表 |
| GET | `/api/trend/{ts_code}` | 获取股票走势图数据 |

### 龙虎榜相关
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/get_hotmoney_data` | 获取游资列表 |
| GET | `/api/get_daily_hotmoney_trade_data` | 获取龙虎榜交易数据 |

### 涨跌停相关
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/get_daily_limit_data` | 获取涨跌停数据 |

### 板块相关
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/get_daily_sector_limit_data` | 获取板块涨跌停数据 |
| GET | `/api/get_all_ths_index` | 获取同花顺指数列表 |

### 日线数据
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/get_daily_data` | 获取日线数据 |

### 智能选股
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/stock_screen` | 执行多条件选股 |
| GET | `/api/stock_screen/templates` | 获取策略模板列表 |
| GET | `/api/stock_screen/templates/{id}` | 获取单个策略模板 |
| POST | `/api/stock_screen/template/{id}` | 使用模板选股 |
| GET | `/api/stock_screen/dates` | 获取可用交易日期 |
| GET | `/api/stock_screen/fields` | 获取可用字段列表 |

## 功能模块

| 路由路径 | 模块名 | 功能描述 |
|----------|--------|----------|
| `/` | Home | 首页仪表盘，显示统计数据 |
| `/screen` | StockScreen | **智能选股**，多条件组合筛选 |
| `/hotmoney` | HotMoney | 龙虎榜游资列表 |
| `/hotmoney/info` | HotMoneyInfo | 游资详细介绍 |
| `/limit` | DailyLimit | 涨跌停数据统计 |
| `/sector` | SectorLimit | 板块涨跌停行情 |
| `/stock` | Stock | 股票基本信息列表 |
| `/stock/trend/:code` | StockTrend | 股票K线走势图（含技术指标） |

### 股票走势图组件
- `TrendChart` - K线主图（含均线 MA5/10/20/60）
- `MACDChart` - MACD 指标图（DIF/DEA/HIST）
- `KDJChart` - KDJ 指标图（K/D/J）
- `RSIChart` - RSI 指标图（RSI6/12/24）
- `BOLLChart` - 布林带图（上轨/中轨/下轨）
- `ToolBar` - 周期/复权/指标切换工具栏

## 数据模型

### 核心数据表

| 表名 | 说明 | 主键 |
|------|------|------|
| `stock_basic_info` | 股票基本信息 | ts_code |
| `daily_data` | 日线行情数据 | (ts_code, trade_date) |
| `daily_indicator` | 技术指标预计算表 | (ts_code, trade_date) |
| `daily_basic` | 每日基本面(PE/PB/市值) | (ts_code, trade_date) |
| `fina_indicator` | 财务指标(ROE/毛利率) | (ts_code, end_date) |
| `daily_limit_data` | 涨跌停数据 | (trade_date, ts_code) |
| `daily_sector_limit_data` | 板块涨跌停数据 | (sector_code, trade_date) |
| `daily_hot_money_trading` | 龙虎榜交易数据 | id (自增) |
| `hot_money_info` | 游资信息 | name |
| `ths_index` | 同花顺指数 | ts_code |
| `weekly_data` | 周K线数据 | (ts_code, trade_date) |
| `monthly_data` | 月K线数据 | (ts_code, trade_date) |
| `adj_factor` | 复权因子 | (ts_code, trade_date) |

### 技术指标表字段 (daily_indicator)

**趋势类**：MA5/10/20/30/60/120/250, MA偏离度, MA排列状态

**动量类**：KDJ(K,D,J), RSI(6,12,24), MACD(DIF,DEA,HIST)

**波动类**：BOLL(上轨,中轨,下轨,宽度,位置), ATR14, CCI

**成交量类**：OBV, VR, 量比, 成交量均线

**价格形态**：连续涨跌天数, 回撤, 反弹, 振幅, 累计涨跌幅

## 定时任务

| 任务名 | 执行时间 | 功能描述 |
|--------|----------|----------|
| init_job | 每天 03:00 | 导入静态数据（股票信息、游资、同花顺指数） |
| incr_job_17 | 交易日 17:00 | 增量数据采集（日线、涨跌停、游资交易） |
| incr_job_19 | 交易日 19:00 | 增量数据采集（冗余执行） |
| basic_incr_job | 每天 18:00 | 增量基本面数据采集（PE/PB/市值） |
| indicator_incr_job | 每天 20:00 | 增量技术指标计算 |
| indicator_full_job | 每周日 06:00 | 全量技术指标计算 |
| fina_incr_job | 每季度首月15日 02:00 | 财务指标采集（ROE/毛利率等） |
| basic_full_job | 每月1号 03:30 | 全量基本面数据补充 |
| weekly_kline_job | 每周日 04:00 | 周K线数据导入 |
| monthly_kline_job | 每月1号 05:00 | 月K线数据导入 |

## 策略分析模块

### 模块文件

| 文件名 | 功能描述 |
|--------|----------|
| `indicator_calc.py` | 技术指标预计算（50+个指标） |
| `signal_engine.py` | 信号引擎，定义20+种内置信号策略 |
| `backtest_engine.py` | 回测引擎，支持完整的策略回测 |
| `factor_analysis.py` | 因子有效性分析（IC/ICIR计算） |
| `stock_screener.py` | 多条件选股引擎，支持9种预设模板 |
| `strategy_optimizer.py` | 策略参数优化器 |

### 内置信号策略

| 策略名 | 类型 | 条件 |
|--------|------|------|
| kdj_oversold | 超跌 | J值 < 0 |
| kdj_deep_oversold | 超跌 | J值 < -10 |
| rsi_oversold | 超跌 | RSI6 < 20 |
| cci_oversold | 超跌 | CCI < -100 |
| wr_oversold | 超跌 | WR14 > 80 |
| kdj_rsi_oversold | 组合 | J<0 且 RSI6<20 |
| kdj_rsi_volume | 组合 | J<-10 且 RSI6<15 且 量比>1 |
| macd_golden_cross | 趋势 | MACD底部金叉 |
| boll_lower | 超跌 | 跌破布林下轨 |
| ma_bullish | 趋势 | 均线多头排列 |
| consecutive_down_rebound | 超跌 | 连续下跌3天+且回撤>10% |
| oversold_resonance | 组合 | KDJ+RSI+CCI三指标超跌共振 |
| oversold_reversal | 组合 | 超跌+MACD金叉+放量 |

### 选股策略模板

| 模板ID | 名称 | 描述 |
|--------|------|------|
| oversold_bounce | 超跌反弹 | RSI超卖+KDJ低位+量能放大 |
| golden_cross | 金叉买入 | MACD金叉+均线多头+量能配合 |
| breakout | 突破策略 | 布林带上轨突破+量能放大 |
| bottom_fishing | 抄底策略 | 连续下跌+RSI超卖+WR超卖 |
| strong_momentum | 强势动量 | 均线多头+放量上涨+MACD强势 |
| limit_up_pool | 涨停板 | 当日涨停股票 |
| low_valuation | 低估值 | 低PE+低PB+高ROE |
| high_growth | 高成长 | 营收增长+利润增长+高ROE |
| small_cap | 小市值 | 流通市值小于50亿 |

## 开发说明

### 架构设计
- 后端采用分层架构：API → Service → Repository → Model
- 前端采用模块化结构，每个页面独立模块
- 使用 Pydantic Settings 管理配置，避免硬编码
- 使用 TanStack Query 进行数据请求和缓存

### 代码规范
- 日志使用 Loguru，支持文件轮转和压缩
- 数据库使用 SQLAlchemy 2.0 异步 ORM
- API 使用 FastAPI 依赖注入模式
- 前端使用 TypeScript 严格模式

### 策略回测
```python
from strategy.backtest_engine import BacktestEngine, BacktestConfig
from strategy.signal_engine import SignalStrategy, SignalType, FactorCondition

# 创建策略
strategy = SignalStrategy(
    name='custom_strategy',
    signal_type=SignalType.CUSTOM,
    conditions=[
        FactorCondition('j_value', '<', -10),
        FactorCondition('macd_hist', '>', 0),
        FactorCondition('vol_ratio', '>', 1.0),
    ],
    combine_mode='and'
)

# 配置回测
config = BacktestConfig(
    initial_capital=1000000,
    max_positions=5,
    position_size=0.15,
    max_hold_days=10,
    stop_loss_pct=-0.05,
    take_profit_pct=0.08,
)

# 运行回测
engine = BacktestEngine(config)
engine.signal_engine.register_strategy(strategy)
performance = engine.run_backtest(db, '20240101', '20260424', strategy_names=['custom_strategy'])
```

## License

MIT
