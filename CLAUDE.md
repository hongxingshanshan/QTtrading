# QTtrading 项目

量化交易数据查询与策略分析平台，提供龙虎榜、股票信息、涨跌停、板块行情等数据查询功能，以及智能选股、策略回测、因子分析等量化分析工具。

## 技术栈

### 前端 (frontend/)
| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.2.0 | UI 框架 |
| TypeScript | 5.3.3 | 类型安全 |
| Vite | 5.1.0 | 构建工具 |
| React Router | 6.22.0 | 路由管理 |
| Ant Design | 5.14.0 | UI 组件库 |
| ECharts | 5.5.0 | 图表可视化 |
| TanStack Query | 5.20.0 | 数据请求/缓存 |
| Zustand | 4.5.0 | 状态管理 |
| TailwindCSS | 3.4.1 | 样式框架 |
| Axios | 1.6.7 | HTTP 请求 |

### 后端 (backend/)
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

## 项目结构

```
QTtrading/
├── backend/                          # 后端服务
│   ├── app/                          # 应用核心
│   │   ├── api/                      # API 接口层
│   │   │   └── v1/                   # V1 版本 API
│   │   ├── core/                     # 核心配置
│   │   ├── models/                   # 数据模型 (ORM)
│   │   ├── repositories/             # 数据仓库层
│   │   ├── schemas/                  # Pydantic 模型
│   │   ├── services/                 # 业务服务层
│   │   └── main.py                   # 应用入口
│   ├── strategy/                     # 策略分析模块
│   ├── tasks/                        # 定时任务
│   ├── scripts/                      # 数据库脚本
│   └── logs/                         # 日志目录
│
├── frontend/                         # 前端应用
│   ├── src/
│   │   ├── modules/                  # 功能模块
│   │   │   ├── Home/                 # 首页
│   │   │   ├── Stock/                # 股票列表
│   │   │   ├── StockTrend/           # 股票走势图
│   │   │   ├── StockScreen/          # 智能选股
│   │   │   ├── HotMoney/             # 龙虎榜
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
│   └── package.json                  # 前端依赖
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
python -m uvicorn app.main:app --reload --port 8001

# 前端
cd frontend
npm run dev
```

### 访问地址
- 前端: http://localhost:3001
- 后端 API: http://localhost:8001
- API 文档: http://localhost:8001/docs

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

### 智能选股
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/stock_screen` | 执行多条件选股 |
| GET | `/api/stock_screen/templates` | 获取策略模板列表 |
| GET | `/api/stock_screen/templates/{id}` | 获取单个策略模板 |
| POST | `/api/stock_screen/template/{id}` | 使用模板选股 |

## 功能模块

| 路由路径 | 模块名 | 功能描述 |
|----------|--------|----------|
| `/` | Home | 首页仪表盘 |
| `/screen` | StockScreen | 智能选股，多条件组合筛选 |
| `/hotmoney` | HotMoney | 龙虎榜游资列表 |
| `/limit` | DailyLimit | 涨跌停数据统计 |
| `/sector` | SectorLimit | 板块涨跌停行情 |
| `/stock` | Stock | 股票基本信息列表 |
| `/stock/trend/:code` | StockTrend | 股票K线走势图（含技术指标） |

## 开发注意事项

- 前端使用 React 18 + TypeScript，严格模式
- 使用 TanStack Query 进行数据请求和缓存
- 后端采用分层架构：API → Service → Repository → Model
- 后端使用 FastAPI 依赖注入模式
- 日志使用 Loguru，支持文件轮转和压缩
