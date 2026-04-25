# QTtrading 项目

量化交易数据查询平台，提供龙虎榜、股票信息、涨跌停、板块行情等数据查询功能。

## 技术栈

### 后端
- **FastAPI** - 高性能 Python Web 框架
- **SQLAlchemy 2.0** - ORM 框架
- **Pydantic v2** - 数据校验
- **Loguru** - 日志系统
- **APScheduler** - 定时任务
- **Tushare** - 金融数据接口

### 前端
- **React 18** - UI 框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Ant Design 5** - UI 组件库
- **ECharts** - 图表库
- **TanStack Query** - 数据请求
- **TailwindCSS** - 样式框架

## 项目结构

```
QTtrading/
├── backend/                    # 后端应用
│   ├── app/
│   │   ├── api/               # API 路由层
│   │   ├── services/          # 业务逻辑层
│   │   ├── repositories/      # 数据访问层
│   │   ├── models/            # ORM 模型
│   │   ├── schemas/           # Pydantic 模型
│   │   └── core/              # 核心配置
│   ├── tasks/                 # 定时任务
│   ├── logs/                  # 日志目录
│   ├── .env                   # 环境变量
│   └── requirements.txt       # Python 依赖
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── modules/           # 业务模块
│   │   ├── shared/            # 共享资源
│   │   │   ├── api/           # API 请求
│   │   │   ├── components/    # 公共组件
│   │   │   ├── hooks/         # 公共 Hooks
│   │   │   ├── types/         # 类型定义
│   │   │   └── utils/         # 工具函数
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── router.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── start-backend.bat           # 后端启动脚本
├── start-frontend.bat          # 前端启动脚本
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
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_NAME=quant_trading
   TUSHARE_TOKEN=your_token
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
- 前端: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

## API 接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/get_hotmoney_data` | GET | 游资信息查询 |
| `/api/get_daily_hotmoney_trade_data` | GET | 龙虎榜交易明细 |
| `/api/get_stock_basic_info` | GET | 股票基本信息 |
| `/api/get_daily_data` | GET | 日线数据查询 |
| `/api/get_daily_limit_data` | GET | 涨跌停数据 |
| `/api/get_daily_sector_limit_data` | GET | 板块涨跌停数据 |
| `/api/get_all_ths_index` | GET | 同花顺指数数据 |

## 功能模块

- **首页** - 数据统计概览
- **龙虎榜交易** - 查询游资交易明细
- **游资介绍** - 查询游资基本信息
- **股票信息** - 查询股票基本信息
- **股票走势** - 查看股票 K 线走势图
- **涨跌停** - 查询每日涨跌停股票
- **板块行情** - 查询板块涨跌数据

## 定时任务

| 任务 | 执行时间 | 说明 |
|------|---------|------|
| 初始化任务 | 每天 03:00 | 游资信息、股票基本信息、同花顺指数 |
| 增量任务 | 交易日 17:00, 19:00 | 涨跌停、龙虎榜、日线数据 |
| 复权因子 | 每天 10:00 | 复权因子同步 |

## 开发说明

- 后端采用分层架构：API → Service → Repository → Model
- 前端采用模块化结构，每个页面独立模块
- 使用 Pydantic Settings 管理配置，避免硬编码
- 使用 TanStack Query 进行数据请求和缓存
- 日志使用 Loguru，支持文件轮转和压缩

## License

MIT