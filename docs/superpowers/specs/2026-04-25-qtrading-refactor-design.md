# QTtrading 重构设计文档

## 一、项目概述

### 重构目标

将现有 Flask + Vue 2 项目完全重写为 FastAPI + React + TypeScript 架构，提升代码规范性、安全性、性能和可扩展性。

### 功能范围

保留功能：
- 龙虎榜数据查询
- 股票基本信息
- 日线数据查询
- 涨跌停数据
- 板块行情
- 定时任务（数据同步）

移除功能：
- 策略回测模块

---

## 二、技术栈

### 后端

| 类别 | 技术选型 | 版本 |
|------|---------|------|
| Web 框架 | FastAPI | 0.110.0 |
| ASGI 服务器 | Uvicorn | 0.27.1 |
| ORM | SQLAlchemy | 2.0.25 |
| 数据库驱动 | mysql-connector-python | 8.3.0 |
| 数据校验 | Pydantic | 2.6.1 |
| 配置管理 | pydantic-settings | 2.2.1 |
| 定时任务 | APScheduler | 3.10.4 |
| 日志 | Loguru | 0.7.2 |
| 数据处理 | Pandas | 2.2.0 |
| 金融数据 | Tushare | 1.4.3 |

### 前端

| 类别 | 技术选型 | 版本 |
|------|---------|------|
| 框架 | React | 18.2.0 |
| 语言 | TypeScript | 5.3.3 |
| 构建工具 | Vite | 5.1.0 |
| UI 组件库 | Ant Design | 5.14.0 |
| 图表库 | ECharts | 5.5.0 |
| 样式 | TailwindCSS | 3.4.1 |
| 数据请求 | TanStack Query | 5.20.0 |
| 路由 | React Router | 6.22.0 |
| 状态管理 | Zustand | 4.5.0 |

---

## 三、后端架构设计

### 目录结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # 入口文件
│   │
│   ├── api/                       # API 路由层
│   │   ├── __init__.py
│   │   ├── deps.py                # 依赖注入
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py          # 路由汇总
│   │       ├── hotmoney.py        # 龙虎榜接口
│   │       ├── stock.py           # 股票接口
│   │       ├── daily.py           # 日线数据接口
│   │       ├── limit.py           # 涨跌停接口
│   │       └── sector.py          # 板块接口
│   │
│   ├── services/                  # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── hotmoney.py
│   │   ├── stock.py
│   │   ├── daily.py
│   │   ├── limit.py
│   │   └── sector.py
│   │
│   ├── repositories/              # 数据访问层
│   │   ├── __init__.py
│   │   ├── base.py                # 基础 CRUD
│   │   ├── hotmoney.py
│   │   ├── stock.py
│   │   ├── daily.py
│   │   ├── limit.py
│   │   └── sector.py
│   │
│   ├── models/                    # SQLAlchemy ORM 模型
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── hotmoney.py
│   │   ├── stock.py
│   │   ├── daily.py
│   │   ├── limit.py
│   │   └── sector.py
│   │
│   ├── schemas/                   # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── common.py
│   │   ├── hotmoney.py
│   │   ├── stock.py
│   │   ├── daily.py
│   │   ├── limit.py
│   │   └── sector.py
│   │
│   └── core/                      # 核心配置
│       ├── __init__.py
│       ├── config.py              # 配置管理
│       ├── database.py            # 数据库连接池
│       ├── logging.py             # 日志配置
│       └── exceptions.py          # 自定义异常
│
├── tasks/                         # 定时任务
│   ├── __init__.py
│   ├── scheduler.py
│   └── jobs/
│       ├── __init__.py
│       ├── init_jobs.py
│       ├── incr_jobs.py
│       ├── adj_factor_job.py
│       └── trading_calendar.py
│
├── logs/                          # 日志目录
├── .env
├── .env.example
└── requirements.txt
```

### 分层职责

| 层级 | 职责 |
|------|------|
| API | 接收请求、参数校验、调用 Service、返回响应 |
| Service | 业务逻辑处理、调用 Repository |
| Repository | 数据库 CRUD 操作 |
| Models | ORM 模型定义 |
| Schemas | 请求/响应数据模型 |

---

## 四、前端架构设计

### 目录结构

```
frontend/
├── src/
│   ├── modules/                   # 业务模块
│   │   ├── Home/
│   │   │   ├── index.tsx
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   └── types.ts
│   │   ├── HotMoney/
│   │   ├── HotMoneyInfo/
│   │   ├── Stock/
│   │   ├── StockTrend/
│   │   ├── DailyLimit/
│   │   └── SectorLimit/
│   │
│   ├── shared/                    # 共享资源
│   │   ├── components/
│   │   │   ├── Layout/
│   │   │   └── PaginationTable/
│   │   ├── hooks/
│   │   │   └── usePagination.ts
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── hotmoney.ts
│   │   │   ├── stock.ts
│   │   │   ├── daily.ts
│   │   │   ├── limit.ts
│   │   │   └── sector.ts
│   │   ├── types/
│   │   │   └── common.ts
│   │   └── utils/
│   │       └── format.ts
│   │
│   ├── stores/
│   │   └── index.ts
│   │
│   ├── App.tsx
│   ├── main.tsx
│   └── router.tsx
│
├── public/
├── index.html
├── vite.config.ts
├── tsconfig.json
├── package.json
└── tailwind.config.js
```

### 路由配置

| 路由 | 页面 | 功能 |
|------|------|------|
| `/` | Home | 首页 |
| `/hotmoney` | HotMoney | 龙虎榜交易明细 |
| `/hotmoney/info` | HotMoneyInfo | 游资介绍 |
| `/stock` | Stock | 股票基本信息 |
| `/stock/trend/:code` | StockTrend | 股票走势图 |
| `/limit` | DailyLimit | 涨跌停数据 |
| `/sector` | SectorLimit | 板块行情 |

---

## 五、API 接口设计

### 接口列表

| 接口 | 方法 | 路径 | 描述 |
|------|------|------|------|
| 游资列表 | GET | `/api/get_hotmoney_data` | 分页查询游资信息 |
| 龙虎榜交易 | GET | `/api/get_daily_hotmoney_trade_data` | 分页查询龙虎榜交易明细 |
| 股票列表 | GET | `/api/get_stock_basic_info` | 分页查询股票基本信息 |
| 日线数据 | GET | `/api/get_daily_data` | 查询股票日线行情 |
| 涨跌停 | GET | `/api/get_daily_limit_data` | 查询涨跌停数据 |
| 板块行情 | GET | `/api/get_daily_sector_limit_data` | 查询板块涨跌停 |
| 同花顺指数 | GET | `/api/get_all_ths_index` | 查询同花顺指数 |

### 接口详情

#### 1. 游资列表

```
GET /api/get_hotmoney_data

Query Parameters:
  - name: string (可选)
  - page: int (默认 1)
  - pageSize: int (默认 10)

Response:
{
  "data": [{ "name": "", "desc": "", "orgs": "" }],
  "total": 100
}
```

#### 2. 龙虎榜交易

```
GET /api/get_daily_hotmoney_trade_data

Query Parameters:
  - hmName: string (可选)
  - tradeDate: string (可选)
  - tsName: string (可选)
  - tsCode: string (可选)
  - page: int (默认 1)
  - pageSize: int (默认 10)

Response:
{
  "data": [...],
  "total": 500
}
```

#### 3. 股票列表

```
GET /api/get_stock_basic_info

Query Parameters:
  - symbol: string (可选)
  - name: string (可选)
  - industry: string (可选)
  - startDate: string (可选)
  - endDate: string (可选)
  - page: int (默认 1)
  - pageSize: int (默认 10)

Response:
{
  "data": [{ "ts_code": "", "name": "", "industry": "", "list_date": "" }],
  "total": 5000
}
```

#### 4. 日线数据

```
GET /api/get_daily_data

Query Parameters:
  - ts_code: string

Response:
{
  "data": [{ "trade_date": "", "open": 0, "high": 0, "low": 0, "close": 0, "pre_close": 0, "price_change": 0, "pct_chg": 0, "vol": 0, "amount": 0 }]
}
```

#### 5. 涨跌停数据

```
GET /api/get_daily_limit_data

Response:
{
  "data": [...]
}
```

#### 6. 板块行情

```
GET /api/get_daily_sector_limit_data

Query Parameters:
  - sector_code: string (可选)
  - sector_name: string (可选)
  - sector_type: string (可选)
  - start_date: string (可选)
  - end_date: string (可选)

Response:
{
  "data": [...]
}
```

#### 7. 同花顺指数

```
GET /api/get_all_ths_index

Response:
{
  "data": [...]
}
```

---

## 六、数据库设计

### 数据表（保持现有）

| 表名 | 用途 |
|------|------|
| stock_basic_info | 股票基本信息 |
| daily_data | 日线行情 |
| hot_money_info | 游资信息 |
| daily_hotmoney_trade_data | 龙虎榜交易明细 |
| daily_limit_data | 涨跌停数据 |
| daily_sector_limit_data | 板块涨跌停 |
| ths_index | 同花顺指数 |
| adj_factor | 复权因子 |

### Repository CRUD 操作

```python
class BaseRepository:
    # 查询
    def get_by_id(id) -> Model
    def get_by_field(field, value) -> Model
    def get_paginated(page, page_size, filters) -> (List[Model], int)
    def get_all() -> List[Model]

    # 新增
    def create(obj_in) -> Model
    def create_batch(objs_in) -> List[Model]

    # 修改
    def update(db_obj, obj_in) -> Model
    def update_by_id(id, obj_in) -> Model
    def update_batch(updates) -> int

    # 删除
    def delete(id) -> bool
    def delete_batch(ids) -> int

    # 存在性检查
    def exists(id) -> bool
    def exists_by_field(field, value) -> bool
```

---

## 七、定时任务设计

### 任务列表

| 任务 | 执行时间 | 说明 |
|------|---------|------|
| 初始化任务 | 每天 03:00 | 游资信息、股票基本信息、同花顺指数 |
| 增量任务 | 交易日 17:00, 19:00 | 涨跌停、龙虎榜、日线数据 |
| 复权因子 | 每天 10:00 | 复权因子同步 |

### 调度器

使用 APScheduler + CronTrigger，支持异步执行。

---

## 八、配置与安全

### 环境变量

```bash
# 应用配置
APP_NAME=QTtrading
APP_ENV=development
DEBUG=true

# 数据库配置
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=quant_trading
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Tushare 配置
TUSHARE_TOKEN=your_token

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### 安全措施

| 措施 | 实现 |
|------|------|
| 密码保护 | .env 不提交 git |
| SQL 注入 | SQLAlchemy 参数化查询 |
| 连接池 | 防止连接耗尽 |
| 健康检查 | pool_pre_ping |

---

## 九、日志系统

### 配置

- 控制台输出：开发调试
- 文件输出：全量日志，自动轮转压缩
- 错误日志：单独文件记录

### 日志级别

| 级别 | 用途 |
|------|------|
| DEBUG | 开发调试 |
| INFO | 正常业务 |
| WARNING | 警告信息 |
| ERROR | 错误信息 |

---

## 十、依赖管理

### 后端依赖

```
fastapi==0.110.0
uvicorn[standard]==0.27.1
sqlalchemy==2.0.25
mysql-connector-python==8.3.0
pydantic==2.6.1
pydantic-settings==2.2.1
apscheduler==3.10.4
loguru==0.7.2
pandas==2.2.0
tushare==1.4.3
chinese-calendar==2.0.0
tqdm==4.66.2
python-dotenv==1.0.1
```

### 前端依赖

```
react@18.2.0
react-router-dom@6.22.0
antd@5.14.0
echarts@5.5.0
@tanstack/react-query@5.20.0
zustand@4.5.0
axios@1.6.7
tailwindcss@3.4.1
typescript@5.3.3
vite@5.1.0
```
