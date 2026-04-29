# QTtrading 项目

这是一个量化交易网站项目，包含 Vue 前端和 Flask Python 后端。

## 项目结构

```
QTtrading/
├── frontend/              # Vue 2 前端应用
│   ├── src/               # 源代码
│   └── package.json       # 前端依赖
├── backend/               # Flask Python 后端
│   ├── app.py             # Flask 主应用入口
│   ├── DataBase.py        # 数据库连接
│   ├── query/             # 数据查询模块
│   ├── service/           # 业务服务模块
│   ├── strategy/          # 策略模块
│   ├── task/              # 定时任务模块
│   └── tushare/           # Tushare 数据接口
├── requirements.txt       # Python 依赖
└── trading_records.xlsx   # 交易记录数据
```

## 技术栈

### 前端 (frontend/)
- Vue 2.6.12
- Vue Router 3.6.5
- Vue CLI 4.5.13
- ECharts 5.6.0（图表库）
- TailwindCSS 4.0.9（样式）
- Axios 0.21.1（HTTP 请求）

### 后端 (backend/)
- Flask（Web 框架）
- Tushare（金融数据接口）
- MySQL Connector Python（数据库连接）

## API 接口

后端提供以下 API 接口：

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/get_hotmoney_data` | GET | 龙虎榜数据查询 |
| `/api/get_daily_hotmoney_trade_data` | GET | 龙虎榜交易明细 |
| `/api/get_stock_basic_info` | GET | 股票基本信息 |
| `/api/get_daily_data` | GET | 日线数据查询 |
| `/api/get_daily_limit_data` | GET | 涨跌停数据 |
| `/api/get_daily_sector_limit_data` | GET | 板块涨跌停数据 |
| `/api/get_all_ths_index` | GET | 同花顺指数数据 |

## 常用命令

### 前端
```bash
cd frontend
npm install        # 安装依赖
npm run serve      # 开发服务器 (localhost:8080)
npm run build      # 生产构建
```

### 后端
```bash
pip install -r requirements.txt   # 安装 Python 依赖
python backend/app.py              # 启动 Flask 服务 (localhost:8001)
```

## 开发注意事项

- 前端使用 Vue 2，注意与 Vue 3 的语法差异
- 使用 TailwindCSS 进行样式开发
- 图表使用 ECharts 实现
- 后端包含定时任务，启动时会自动运行
- 数据来源于 Tushare 金融数据接口