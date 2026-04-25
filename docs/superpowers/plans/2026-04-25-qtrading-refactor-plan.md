# QTtrading 重构实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 Flask + Vue 2 项目完全重写为 FastAPI + React + TypeScript 架构

**Architecture:** 后端采用分层架构（API → Service → Repository → Model），前端按页面模块划分，全面 TypeScript 类型安全

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, React, TypeScript, Vite, Ant Design, ECharts, TailwindCSS

---

## 阶段一：后端基础架构搭建

### Task 1: 创建后端目录结构和配置文件

**Files:**
- Create: `backend/app/__init__.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/config.py`
- Create: `backend/.env.example`
- Create: `backend/requirements.txt`

- [ ] **Step 1: 创建后端目录结构**

```bash
mkdir -p backend/app/api/v1
mkdir -p backend/app/services
mkdir -p backend/app/repositories
mkdir -p backend/app/models
mkdir -p backend/app/schemas
mkdir -p backend/app/core
mkdir -p backend/tasks/jobs
mkdir -p backend/logs
```

- [ ] **Step 2: 创建 requirements.txt**

```txt
# Web 框架
fastapi==0.110.0
uvicorn[standard]==0.27.1

# 数据库
sqlalchemy==2.0.25
mysql-connector-python==8.3.0

# 数据校验
pydantic==2.6.1
pydantic-settings==2.2.1

# 数据处理
pandas==2.2.0
numpy==1.26.4

# 金融数据
tushare==1.4.3

# 定时任务
apscheduler==3.10.4
chinese-calendar==2.0.0

# 日志
loguru==0.7.2

# 进度条
tqdm==4.66.2

# 环境变量
python-dotenv==1.0.1
```

- [ ] **Step 3: 创建 .env.example**

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
TUSHARE_TOKEN=your_tushare_token

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

- [ ] **Step 4: 创建配置管理模块**

```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "QTtrading"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # 数据库配置
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "quant_trading"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Tushare 配置
    TUSHARE_TOKEN: str = ""

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+mysqlconnector://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 5: 创建 __init__.py 文件**

```python
# backend/app/__init__.py
from app.core.config import get_settings

__all__ = ["get_settings"]
```

```python
# backend/app/core/__init__.py
from app.core.config import get_settings, Settings

__all__ = ["get_settings", "Settings"]
```

- [ ] **Step 6: 提交代码**

```bash
git add backend/
git commit -m "feat(backend): 初始化后端项目结构和配置管理"
```

---

### Task 2: 创建日志系统

**Files:**
- Create: `backend/app/core/logging.py`

- [ ] **Step 1: 创建日志配置模块**

```python
# backend/app/core/logging.py
import sys
from loguru import logger
from app.core.config import get_settings


def setup_logging():
    """配置日志系统"""
    settings = get_settings()
    logger.remove()

    # 控制台输出
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )

    # 文件输出
    logger.add(
        settings.LOG_FILE,
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8"
    )

    # 错误日志单独文件
    logger.add(
        "logs/error.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8"
    )


__all__ = ["logger", "setup_logging"]
```

- [ ] **Step 2: 提交代码**

```bash
git add backend/app/core/logging.py
git commit -m "feat(backend): 添加日志系统配置"
```

---

### Task 3: 创建数据库连接和异常处理

**Files:**
- Create: `backend/app/core/database.py`
- Create: `backend/app/core/exceptions.py`

- [ ] **Step 1: 创建数据库连接模块**

```python
# backend/app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Session:
    """依赖注入：获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """上下文管理器：用于非请求场景"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
```

- [ ] **Step 2: 创建异常处理模块**

```python
# backend/app/core/exceptions.py
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """应用异常基类"""
    def __init__(self, code: int, message: str, data: dict = None):
        self.code = code
        self.message = message
        self.data = data


class NotFoundException(AppException):
    """资源不存在"""
    def __init__(self, message: str = "资源不存在"):
        super().__init__(code=404, message=message)


class DatabaseException(AppException):
    """数据库异常"""
    def __init__(self, message: str = "数据库操作失败"):
        super().__init__(code=500, message=message)


def register_exception_handlers(app):
    """注册全局异常处理器"""
    @app.exception_handler(AppException)
    async def app_exception_handler(request, exc: AppException):
        return JSONResponse(
            status_code=exc.code,
            content={
                "code": exc.code,
                "message": exc.message,
                "data": exc.data
            }
        )
```

- [ ] **Step 3: 提交代码**

```bash
git add backend/app/core/database.py backend/app/core/exceptions.py
git commit -m "feat(backend): 添加数据库连接池和异常处理"
```

---

### Task 4: 创建 ORM 模型

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/base.py`
- Create: `backend/app/models/stock.py`
- Create: `backend/app/models/hotmoney.py`
- Create: `backend/app/models/daily.py`
- Create: `backend/app/models/limit.py`
- Create: `backend/app/models/sector.py`

- [ ] **Step 1: 创建基础模型**

```python
# backend/app/models/base.py
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

- [ ] **Step 2: 创建股票模型**

```python
# backend/app/models/stock.py
from sqlalchemy import Column, String, Date
from app.models.base import Base


class StockBasicInfo(Base):
    __tablename__ = "stock_basic_info"

    ts_code = Column(String(20), primary_key=True, comment="股票代码")
    symbol = Column(String(10), comment="股票代码简写")
    name = Column(String(50), comment="股票名称")
    area = Column(String(20), comment="地域")
    industry = Column(String(50), comment="行业")
    market = Column(String(10), comment="市场类型")
    list_date = Column(Date, comment="上市日期")
```

- [ ] **Step 3: 创建游资模型**

```python
# backend/app/models/hotmoney.py
from sqlalchemy import Column, String, Integer, Text
from app.models.base import Base


class HotMoneyInfo(Base):
    __tablename__ = "hot_money_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), comment="游资名称")
    desc = Column(Text, comment="描述")
    orgs = Column(Text, comment="关联机构")


class DailyHotMoneyTradeData(Base):
    __tablename__ = "daily_hotmoney_trade_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_date = Column(String(10), comment="交易日期")
    ts_code = Column(String(20), comment="股票代码")
    ts_name = Column(String(50), comment="股票名称")
    hm_name = Column(String(100), comment="游资名称")
    buy_amount = Column(String(50), comment="买入金额")
    sell_amount = Column(String(50), comment="卖出金额")
    net_amount = Column(String(50), comment="净买入")
```

- [ ] **Step 4: 创建日线数据模型**

```python
# backend/app/models/daily.py
from sqlalchemy import Column, String, Float, BigInteger
from app.models.base import Base


class DailyData(Base):
    __tablename__ = "daily_data"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), comment="股票代码")
    trade_date = Column(String(10), comment="交易日期")
    open = Column(Float, comment="开盘价")
    high = Column(Float, comment="最高价")
    low = Column(Float, comment="最低价")
    close = Column(Float, comment="收盘价")
    pre_close = Column(Float, comment="昨收价")
    price_change = Column(Float, comment="涨跌额")
    pct_chg = Column(Float, comment="涨跌幅")
    vol = Column(BigInteger, comment="成交量")
    amount = Column(Float, comment="成交额")
```

- [ ] **Step 5: 创建涨跌停模型**

```python
# backend/app/models/limit.py
from sqlalchemy import Column, String, Float, BigInteger
from app.models.base import Base


class DailyLimitData(Base):
    __tablename__ = "daily_limit_data"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    trade_date = Column(String(10), comment="交易日期")
    ts_code = Column(String(20), comment="股票代码")
    name = Column(String(50), comment="股票名称")
    close = Column(Float, comment="收盘价")
    pct_chg = Column(Float, comment="涨跌幅")
    limit_price = Column(Float, comment="涨停价")
```

- [ ] **Step 6: 创建板块模型**

```python
# backend/app/models/sector.py
from sqlalchemy import Column, String, Float, BigInteger
from app.models.base import Base


class DailySectorLimitData(Base):
    __tablename__ = "daily_sector_limit_data"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    trade_date = Column(String(10), comment="交易日期")
    sector_code = Column(String(20), comment="板块代码")
    sector_name = Column(String(50), comment="板块名称")
    sector_type = Column(String(20), comment="板块类型")
    pct_chg = Column(Float, comment="涨跌幅")
    up_count = Column(Integer, comment="上涨家数")
    down_count = Column(Integer, comment="下跌家数")


class ThsIndex(Base):
    __tablename__ = "ths_index"

    ts_code = Column(String(20), primary_key=True, comment="指数代码")
    name = Column(String(50), comment="指数名称")
```

- [ ] **Step 7: 创建模型导出**

```python
# backend/app/models/__init__.py
from app.models.base import Base
from app.models.stock import StockBasicInfo
from app.models.hotmoney import HotMoneyInfo, DailyHotMoneyTradeData
from app.models.daily import DailyData
from app.models.limit import DailyLimitData
from app.models.sector import DailySectorLimitData, ThsIndex

__all__ = [
    "Base",
    "StockBasicInfo",
    "HotMoneyInfo",
    "DailyHotMoneyTradeData",
    "DailyData",
    "DailyLimitData",
    "DailySectorLimitData",
    "ThsIndex",
]
```

- [ ] **Step 8: 提交代码**

```bash
git add backend/app/models/
git commit -m "feat(backend): 添加 SQLAlchemy ORM 模型"
```

---

### Task 5: 创建 Pydantic Schemas

**Files:**
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/common.py`
- Create: `backend/app/schemas/stock.py`
- Create: `backend/app/schemas/hotmoney.py`
- Create: `backend/app/schemas/daily.py`
- Create: `backend/app/schemas/limit.py`
- Create: `backend/app/schemas/sector.py`

- [ ] **Step 1: 创建通用 Schema**

```python
# backend/app/schemas/common.py
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List

T = TypeVar("T")


class PagedResponse(BaseModel, Generic[T]):
    """分页响应格式"""
    data: List[T]
    total: int
```

- [ ] **Step 2: 创建股票 Schema**

```python
# backend/app/schemas/stock.py
from pydantic import BaseModel
from typing import Optional
from datetime import date


class StockBasicInfoItem(BaseModel):
    ts_code: str
    symbol: Optional[str] = None
    name: Optional[str] = None
    area: Optional[str] = None
    industry: Optional[str] = None
    market: Optional[str] = None
    list_date: Optional[str] = None

    class Config:
        from_attributes = True


class StockQuery(BaseModel):
    symbol: Optional[str] = ""
    name: Optional[str] = ""
    industry: Optional[str] = ""
    startDate: Optional[str] = ""
    endDate: Optional[str] = ""
    page: int = 1
    pageSize: int = 10
```

- [ ] **Step 3: 创建游资 Schema**

```python
# backend/app/schemas/hotmoney.py
from pydantic import BaseModel
from typing import Optional


class HotMoneyInfoItem(BaseModel):
    name: Optional[str] = None
    desc: Optional[str] = None
    orgs: Optional[str] = None

    class Config:
        from_attributes = True


class HotMoneyQuery(BaseModel):
    name: Optional[str] = ""
    page: int = 1
    pageSize: int = 10


class DailyHotMoneyTradeItem(BaseModel):
    trade_date: Optional[str] = None
    ts_code: Optional[str] = None
    ts_name: Optional[str] = None
    hm_name: Optional[str] = None
    buy_amount: Optional[str] = None
    sell_amount: Optional[str] = None
    net_amount: Optional[str] = None

    class Config:
        from_attributes = True


class DailyHotMoneyTradeQuery(BaseModel):
    hmName: Optional[str] = ""
    tradeDate: Optional[str] = ""
    tsName: Optional[str] = ""
    tsCode: Optional[str] = ""
    page: int = 1
    pageSize: int = 10
```

- [ ] **Step 4: 创建日线数据 Schema**

```python
# backend/app/schemas/daily.py
from pydantic import BaseModel
from typing import Optional


class DailyDataItem(BaseModel):
    trade_date: Optional[str] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    pre_close: Optional[float] = None
    price_change: Optional[float] = None
    pct_chg: Optional[float] = None
    vol: Optional[int] = None
    amount: Optional[float] = None

    class Config:
        from_attributes = True
```

- [ ] **Step 5: 创建涨跌停 Schema**

```python
# backend/app/schemas/limit.py
from pydantic import BaseModel
from typing import Optional


class DailyLimitItem(BaseModel):
    trade_date: Optional[str] = None
    ts_code: Optional[str] = None
    name: Optional[str] = None
    close: Optional[float] = None
    pct_chg: Optional[float] = None
    limit_price: Optional[float] = None

    class Config:
        from_attributes = True
```

- [ ] **Step 6: 创建板块 Schema**

```python
# backend/app/schemas/sector.py
from pydantic import BaseModel
from typing import Optional


class DailySectorLimitItem(BaseModel):
    trade_date: Optional[str] = None
    sector_code: Optional[str] = None
    sector_name: Optional[str] = None
    sector_type: Optional[str] = None
    pct_chg: Optional[float] = None

    class Config:
        from_attributes = True


class SectorLimitQuery(BaseModel):
    sector_code: Optional[str] = ""
    sector_name: Optional[str] = ""
    sector_type: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""


class ThsIndexItem(BaseModel):
    ts_code: Optional[str] = None
    name: Optional[str] = None

    class Config:
        from_attributes = True
```

- [ ] **Step 7: 创建 Schema 导出**

```python
# backend/app/schemas/__init__.py
from app.schemas.common import PagedResponse
from app.schemas.stock import StockBasicInfoItem, StockQuery
from app.schemas.hotmoney import HotMoneyInfoItem, HotMoneyQuery, DailyHotMoneyTradeItem, DailyHotMoneyTradeQuery
from app.schemas.daily import DailyDataItem
from app.schemas.limit import DailyLimitItem
from app.schemas.sector import DailySectorLimitItem, SectorLimitQuery, ThsIndexItem

__all__ = [
    "PagedResponse",
    "StockBasicInfoItem",
    "StockQuery",
    "HotMoneyInfoItem",
    "HotMoneyQuery",
    "DailyHotMoneyTradeItem",
    "DailyHotMoneyTradeQuery",
    "DailyDataItem",
    "DailyLimitItem",
    "DailySectorLimitItem",
    "SectorLimitQuery",
    "ThsIndexItem",
]
```

- [ ] **Step 8: 提交代码**

```bash
git add backend/app/schemas/
git commit -m "feat(backend): 添加 Pydantic Schema 模型"
```

---

### Task 6: 创建 Repository 层

**Files:**
- Create: `backend/app/repositories/__init__.py`
- Create: `backend/app/repositories/base.py`
- Create: `backend/app/repositories/stock.py`
- Create: `backend/app/repositories/hotmoney.py`
- Create: `backend/app/repositories/daily.py`
- Create: `backend/app/repositories/limit.py`
- Create: `backend/app/repositories/sector.py`

- [ ] **Step 1: 创建基础 Repository**

```python
# backend/app/repositories/base.py
from typing import Generic, TypeVar, Optional, List, Any
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, db: Session, model: type[ModelType]):
        self.db = db
        self.model = model

    def get_by_id(self, id: Any) -> Optional[ModelType]:
        """根据主键查询"""
        return self.db.query(self.model).get(id)

    def get_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[List[ModelType], int]:
        """分页查询"""
        query = self.db.query(self.model)
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def get_all(self) -> List[ModelType]:
        """查询全部"""
        return self.db.query(self.model).all()

    def create(self, obj_in: dict) -> ModelType:
        """创建单条记录"""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def create_batch(self, objs_in: List[dict]) -> List[ModelType]:
        """批量创建"""
        db_objs = [self.model(**obj) for obj in objs_in]
        self.db.add_all(db_objs)
        self.db.commit()
        for obj in db_objs:
            self.db.refresh(obj)
        return db_objs

    def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        """更新记录"""
        for key, value in obj_in.items():
            setattr(db_obj, key, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: Any) -> bool:
        """删除记录"""
        db_obj = self.get_by_id(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False
```

- [ ] **Step 2: 创建股票 Repository**

```python
# backend/app/repositories/stock.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.repositories.base import BaseRepository
from app.models.stock import StockBasicInfo


class StockRepository(BaseRepository[StockBasicInfo]):
    def __init__(self, db: Session):
        super().__init__(db, StockBasicInfo)

    def get_paginated_with_filter(
        self,
        symbol: str = "",
        name: str = "",
        industry: str = "",
        start_date: str = "",
        end_date: str = "",
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[List[StockBasicInfo], int]:
        """带过滤条件的分页查询"""
        query = self.db.query(self.model)

        if symbol:
            query = query.filter(self.model.ts_code.like(f"%{symbol}%"))
        if name:
            query = query.filter(self.model.name.like(f"%{name}%"))
        if industry:
            query = query.filter(self.model.industry == industry)
        if start_date:
            query = query.filter(self.model.list_date >= start_date)
        if end_date:
            query = query.filter(self.model.list_date <= end_date)

        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total
```

- [ ] **Step 3: 创建游资 Repository**

```python
# backend/app/repositories/hotmoney.py
from typing import List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.hotmoney import HotMoneyInfo, DailyHotMoneyTradeData


class HotMoneyRepository(BaseRepository[HotMoneyInfo]):
    def __init__(self, db: Session):
        super().__init__(db, HotMoneyInfo)

    def get_paginated_with_filter(
        self,
        name: str = "",
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[List[HotMoneyInfo], int]:
        """带过滤条件的分页查询"""
        query = self.db.query(self.model)

        if name:
            query = query.filter(self.model.name.like(f"%{name}%"))

        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total


class DailyHotMoneyTradeRepository(BaseRepository[DailyHotMoneyTradeData]):
    def __init__(self, db: Session):
        super().__init__(db, DailyHotMoneyTradeData)

    def get_paginated_with_filter(
        self,
        hm_name: str = "",
        trade_date: str = "",
        ts_name: str = "",
        ts_code: str = "",
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[List[DailyHotMoneyTradeData], int]:
        """带过滤条件的分页查询"""
        query = self.db.query(self.model)

        if hm_name:
            query = query.filter(self.model.hm_name.like(f"%{hm_name}%"))
        if trade_date:
            query = query.filter(self.model.trade_date == trade_date)
        if ts_name:
            query = query.filter(self.model.ts_name.like(f"%{ts_name}%"))
        if ts_code:
            query = query.filter(self.model.ts_code.like(f"%{ts_code}%"))

        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total
```

- [ ] **Step 4: 创建日线数据 Repository**

```python
# backend/app/repositories/daily.py
from typing import List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.daily import DailyData


class DailyDataRepository(BaseRepository[DailyData]):
    def __init__(self, db: Session):
        super().__init__(db, DailyData)

    def get_by_ts_code(self, ts_code: str) -> List[DailyData]:
        """根据股票代码查询日线数据"""
        return self.db.query(self.model).filter(
            self.model.ts_code == ts_code
        ).order_by(self.model.trade_date.asc()).all()
```

- [ ] **Step 5: 创建涨跌停 Repository**

```python
# backend/app/repositories/limit.py
from typing import List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.limit import DailyLimitData


class DailyLimitRepository(BaseRepository[DailyLimitData]):
    def __init__(self, db: Session):
        super().__init__(db, DailyLimitData)

    def get_all_ordered(self) -> List[DailyLimitData]:
        """查询全部并按日期排序"""
        return self.db.query(self.model).order_by(
            self.model.trade_date.desc()
        ).all()
```

- [ ] **Step 6: 创建板块 Repository**

```python
# backend/app/repositories/sector.py
from typing import List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.sector import DailySectorLimitData, ThsIndex


class DailySectorLimitRepository(BaseRepository[DailySectorLimitData]):
    def __init__(self, db: Session):
        super().__init__(db, DailySectorLimitData)

    def get_with_filter(
        self,
        sector_code: str = "",
        sector_name: str = "",
        sector_type: str = "",
        start_date: str = "",
        end_date: str = "",
    ) -> List[DailySectorLimitData]:
        """带过滤条件的查询"""
        query = self.db.query(self.model)

        if sector_code:
            query = query.filter(self.model.sector_code == sector_code)
        if sector_name:
            query = query.filter(self.model.sector_name.like(f"%{sector_name}%"))
        if sector_type:
            query = query.filter(self.model.sector_type == sector_type)
        if start_date:
            query = query.filter(self.model.trade_date >= start_date)
        if end_date:
            query = query.filter(self.model.trade_date <= end_date)

        return query.all()


class ThsIndexRepository(BaseRepository[ThsIndex]):
    def __init__(self, db: Session):
        super().__init__(db, ThsIndex)
```

- [ ] **Step 7: 创建 Repository 导出**

```python
# backend/app/repositories/__init__.py
from app.repositories.base import BaseRepository
from app.repositories.stock import StockRepository
from app.repositories.hotmoney import HotMoneyRepository, DailyHotMoneyTradeRepository
from app.repositories.daily import DailyDataRepository
from app.repositories.limit import DailyLimitRepository
from app.repositories.sector import DailySectorLimitRepository, ThsIndexRepository

__all__ = [
    "BaseRepository",
    "StockRepository",
    "HotMoneyRepository",
    "DailyHotMoneyTradeRepository",
    "DailyDataRepository",
    "DailyLimitRepository",
    "DailySectorLimitRepository",
    "ThsIndexRepository",
]
```

- [ ] **Step 8: 提交代码**

```bash
git add backend/app/repositories/
git commit -m "feat(backend): 添加 Repository 数据访问层"
```

---

### Task 7: 创建 Service 层

**Files:**
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/stock.py`
- Create: `backend/app/services/hotmoney.py`
- Create: `backend/app/services/daily.py`
- Create: `backend/app/services/limit.py`
- Create: `backend/app/services/sector.py`

- [ ] **Step 1: 创建股票 Service**

```python
# backend/app/services/stock.py
from typing import List
from sqlalchemy.orm import Session
from app.repositories.stock import StockRepository
from app.schemas.stock import StockBasicInfoItem


class StockService:
    def __init__(self, db: Session):
        self.repository = StockRepository(db)

    def get_stock_list(
        self,
        symbol: str = "",
        name: str = "",
        industry: str = "",
        start_date: str = "",
        end_date: str = "",
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[List[StockBasicInfoItem], int]:
        """获取股票列表"""
        items, total = self.repository.get_paginated_with_filter(
            symbol=symbol,
            name=name,
            industry=industry,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
        )
        return [StockBasicInfoItem.model_validate(item) for item in items], total
```

- [ ] **Step 2: 创建游资 Service**

```python
# backend/app/services/hotmoney.py
from typing import List
from sqlalchemy.orm import Session
from app.repositories.hotmoney import HotMoneyRepository, DailyHotMoneyTradeRepository
from app.schemas.hotmoney import HotMoneyInfoItem, DailyHotMoneyTradeItem


class HotMoneyService:
    def __init__(self, db: Session):
        self.repository = HotMoneyRepository(db)

    def get_hotmoney_list(
        self,
        name: str = "",
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[List[HotMoneyInfoItem], int]:
        """获取游资列表"""
        items, total = self.repository.get_paginated_with_filter(
            name=name,
            page=page,
            page_size=page_size,
        )
        return [HotMoneyInfoItem.model_validate(item) for item in items], total


class DailyHotMoneyTradeService:
    def __init__(self, db: Session):
        self.repository = DailyHotMoneyTradeRepository(db)

    def get_trade_list(
        self,
        hm_name: str = "",
        trade_date: str = "",
        ts_name: str = "",
        ts_code: str = "",
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[List[DailyHotMoneyTradeItem], int]:
        """获取龙虎榜交易列表"""
        items, total = self.repository.get_paginated_with_filter(
            hm_name=hm_name,
            trade_date=trade_date,
            ts_name=ts_name,
            ts_code=ts_code,
            page=page,
            page_size=page_size,
        )
        return [DailyHotMoneyTradeItem.model_validate(item) for item in items], total
```

- [ ] **Step 3: 创建日线数据 Service**

```python
# backend/app/services/daily.py
from typing import List
from sqlalchemy.orm import Session
from app.repositories.daily import DailyDataRepository
from app.schemas.daily import DailyDataItem


class DailyDataService:
    def __init__(self, db: Session):
        self.repository = DailyDataRepository(db)

    def get_daily_data(self, ts_code: str) -> List[DailyDataItem]:
        """获取日线数据"""
        items = self.repository.get_by_ts_code(ts_code)
        return [DailyDataItem.model_validate(item) for item in items]
```

- [ ] **Step 4: 创建涨跌停 Service**

```python
# backend/app/services/limit.py
from typing import List
from sqlalchemy.orm import Session
from app.repositories.limit import DailyLimitRepository
from app.schemas.limit import DailyLimitItem


class DailyLimitService:
    def __init__(self, db: Session):
        self.repository = DailyLimitRepository(db)

    def get_limit_data(self) -> List[DailyLimitItem]:
        """获取涨跌停数据"""
        items = self.repository.get_all_ordered()
        return [DailyLimitItem.model_validate(item) for item in items]
```

- [ ] **Step 5: 创建板块 Service**

```python
# backend/app/services/sector.py
from typing import List
from sqlalchemy.orm import Session
from app.repositories.sector import DailySectorLimitRepository, ThsIndexRepository
from app.schemas.sector import DailySectorLimitItem, ThsIndexItem


class DailySectorLimitService:
    def __init__(self, db: Session):
        self.repository = DailySectorLimitRepository(db)

    def get_sector_data(
        self,
        sector_code: str = "",
        sector_name: str = "",
        sector_type: str = "",
        start_date: str = "",
        end_date: str = "",
    ) -> List[DailySectorLimitItem]:
        """获取板块数据"""
        items = self.repository.get_with_filter(
            sector_code=sector_code,
            sector_name=sector_name,
            sector_type=sector_type,
            start_date=start_date,
            end_date=end_date,
        )
        return [DailySectorLimitItem.model_validate(item) for item in items]


class ThsIndexService:
    def __init__(self, db: Session):
        self.repository = ThsIndexRepository(db)

    def get_all_index(self) -> List[ThsIndexItem]:
        """获取所有同花顺指数"""
        items = self.repository.get_all()
        return [ThsIndexItem.model_validate(item) for item in items]
```

- [ ] **Step 6: 创建 Service 导出**

```python
# backend/app/services/__init__.py
from app.services.stock import StockService
from app.services.hotmoney import HotMoneyService, DailyHotMoneyTradeService
from app.services.daily import DailyDataService
from app.services.limit import DailyLimitService
from app.services.sector import DailySectorLimitService, ThsIndexService

__all__ = [
    "StockService",
    "HotMoneyService",
    "DailyHotMoneyTradeService",
    "DailyDataService",
    "DailyLimitService",
    "DailySectorLimitService",
    "ThsIndexService",
]
```

- [ ] **Step 7: 提交代码**

```bash
git add backend/app/services/
git commit -m "feat(backend): 添加 Service 业务逻辑层"
```

---

### Task 8: 创建 API 路由层

**Files:**
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/deps.py`
- Create: `backend/app/api/v1/__init__.py`
- Create: `backend/app/api/v1/router.py`
- Create: `backend/app/api/v1/hotmoney.py`
- Create: `backend/app/api/v1/stock.py`
- Create: `backend/app/api/v1/daily.py`
- Create: `backend/app/api/v1/limit.py`
- Create: `backend/app/api/v1/sector.py`

- [ ] **Step 1: 创建依赖注入**

```python
# backend/app/api/deps.py
from typing import Generator
from sqlalchemy.orm import Session
from app.core.database import get_db


def get_database() -> Generator[Session, None, None]:
    """获取数据库会话依赖"""
    yield from get_db()
```

- [ ] **Step 2: 创建游资路由**

```python
# backend/app/api/v1/hotmoney.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_database
from app.services.hotmoney import HotMoneyService, DailyHotMoneyTradeService

router = APIRouter()


@router.get("/get_hotmoney_data")
def get_hotmoney_data(
    name: str = "",
    page: int = 1,
    pageSize: int = 10,
    db: Session = Depends(get_database),
):
    """获取游资列表"""
    service = HotMoneyService(db)
    data, total = service.get_hotmoney_list(
        name=name,
        page=page,
        page_size=pageSize,
    )
    return {"data": data, "total": total}


@router.get("/get_daily_hotmoney_trade_data")
def get_daily_hotmoney_trade_data(
    hmName: str = "",
    tradeDate: str = "",
    tsName: str = "",
    tsCode: str = "",
    page: int = 1,
    pageSize: int = 10,
    db: Session = Depends(get_database),
):
    """获取龙虎榜交易数据"""
    service = DailyHotMoneyTradeService(db)
    data, total = service.get_trade_list(
        hm_name=hmName,
        trade_date=tradeDate,
        ts_name=tsName,
        ts_code=tsCode,
        page=page,
        page_size=pageSize,
    )
    return {"data": data, "total": total}
```

- [ ] **Step 3: 创建股票路由**

```python
# backend/app/api/v1/stock.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_database
from app.services.stock import StockService

router = APIRouter()


@router.get("/get_stock_basic_info")
def get_stock_basic_info(
    symbol: str = "",
    name: str = "",
    industry: str = "",
    startDate: str = "",
    endDate: str = "",
    page: int = 1,
    pageSize: int = 10,
    db: Session = Depends(get_database),
):
    """获取股票基本信息"""
    service = StockService(db)
    data, total = service.get_stock_list(
        symbol=symbol,
        name=name,
        industry=industry,
        start_date=startDate,
        end_date=endDate,
        page=page,
        page_size=pageSize,
    )
    return {"data": data, "total": total}
```

- [ ] **Step 4: 创建日线数据路由**

```python
# backend/app/api/v1/daily.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_database
from app.services.daily import DailyDataService

router = APIRouter()


@router.get("/get_daily_data")
def get_daily_data(
    ts_code: str = "",
    db: Session = Depends(get_database),
):
    """获取日线数据"""
    service = DailyDataService(db)
    data = service.get_daily_data(ts_code)
    return {"data": data}
```

- [ ] **Step 5: 创建涨跌停路由**

```python
# backend/app/api/v1/limit.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_database
from app.services.limit import DailyLimitService

router = APIRouter()


@router.get("/get_daily_limit_data")
def get_daily_limit_data(
    db: Session = Depends(get_database),
):
    """获取涨跌停数据"""
    service = DailyLimitService(db)
    data = service.get_limit_data()
    return {"data": data}
```

- [ ] **Step 6: 创建板块路由**

```python
# backend/app/api/v1/sector.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_database
from app.services.sector import DailySectorLimitService, ThsIndexService

router = APIRouter()


@router.get("/get_daily_sector_limit_data")
def get_daily_sector_limit_data(
    sector_code: str = "",
    sector_name: str = "",
    sector_type: str = "",
    start_date: str = "",
    end_date: str = "",
    db: Session = Depends(get_database),
):
    """获取板块涨跌停数据"""
    service = DailySectorLimitService(db)
    data = service.get_sector_data(
        sector_code=sector_code,
        sector_name=sector_name,
        sector_type=sector_type,
        start_date=start_date,
        end_date=end_date,
    )
    return {"data": data}


@router.get("/get_all_ths_index")
def get_all_ths_index(
    db: Session = Depends(get_database),
):
    """获取同花顺指数"""
    service = ThsIndexService(db)
    data = service.get_all_index()
    return {"data": data}
```

- [ ] **Step 7: 创建路由汇总**

```python
# backend/app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1 import hotmoney, stock, daily, limit, sector

api_router = APIRouter()

api_router.include_router(hotmoney.router)
api_router.include_router(stock.router)
api_router.include_router(daily.router)
api_router.include_router(limit.router)
api_router.include_router(sector.router)
```

- [ ] **Step 8: 创建 API 导出**

```python
# backend/app/api/__init__.py
from app.api.v1.router import api_router

__all__ = ["api_router"]
```

```python
# backend/app/api/v1/__init__.py
from app.api.v1.router import api_router

__all__ = ["api_router"]
```

- [ ] **Step 9: 提交代码**

```bash
git add backend/app/api/
git commit -m "feat(backend): 添加 API 路由层"
```

---

### Task 9: 创建 FastAPI 主应用

**Files:**
- Create: `backend/app/main.py`

- [ ] **Step 1: 创建主应用入口**

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.logging import setup_logging, logger
from app.core.exceptions import register_exception_handlers
from app.api import api_router

settings = get_settings()
setup_logging()


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
    )

    # 注册异常处理器
    register_exception_handlers(app)

    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(api_router, prefix="/api")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    logger.info(f"启动 {settings.APP_NAME} 服务")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
```

- [ ] **Step 2: 提交代码**

```bash
git add backend/app/main.py
git commit -m "feat(backend): 添加 FastAPI 主应用入口"
```

---

### Task 10: 创建定时任务模块

**Files:**
- Create: `backend/tasks/__init__.py`
- Create: `backend/tasks/scheduler.py`
- Create: `backend/tasks/jobs/__init__.py`
- Create: `backend/tasks/jobs/trading_calendar.py`

- [ ] **Step 1: 创建交易日历模块**

```python
# backend/tasks/jobs/trading_calendar.py
import chinese_calendar as calendar
from datetime import datetime


def is_trading_day(date: datetime = None) -> bool:
    """判断是否为交易日"""
    if date is None:
        date = datetime.now()
    return calendar.is_workday(date) and not calendar.is_holiday(date)
```

- [ ] **Step 2: 创建调度器**

```python
# backend/tasks/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.core.logging import logger

scheduler = BackgroundScheduler()


def start_scheduler():
    """启动调度器"""
    from tasks.jobs.trading_calendar import is_trading_day

    # 这里后续添加具体的任务
    # scheduler.add_job(...)

    scheduler.start()
    logger.info("定时任务调度器已启动")


def stop_scheduler():
    """停止调度器"""
    scheduler.shutdown()
    logger.info("定时任务调度器已停止")
```

- [ ] **Step 3: 创建任务导出**

```python
# backend/tasks/__init__.py
from tasks.scheduler import start_scheduler, stop_scheduler

__all__ = ["start_scheduler", "stop_scheduler"]
```

```python
# backend/tasks/jobs/__init__.py
from tasks.jobs.trading_calendar import is_trading_day

__all__ = ["is_trading_day"]
```

- [ ] **Step 4: 提交代码**

```bash
git add backend/tasks/
git commit -m "feat(backend): 添加定时任务调度器"
```

---

## 阶段二：前端基础架构搭建

### Task 11: 创建前端项目结构

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Create: `frontend/index.html`

- [ ] **Step 1: 创建前端目录结构**

```bash
mkdir -p frontend/src/modules/Home
mkdir -p frontend/src/modules/HotMoney
mkdir -p frontend/src/modules/HotMoneyInfo
mkdir -p frontend/src/modules/Stock
mkdir -p frontend/src/modules/StockTrend
mkdir -p frontend/src/modules/DailyLimit
mkdir -p frontend/src/modules/SectorLimit
mkdir -p frontend/src/shared/components/Layout
mkdir -p frontend/src/shared/components/PaginationTable
mkdir -p frontend/src/shared/hooks
mkdir -p frontend/src/shared/api
mkdir -p frontend/src/shared/types
mkdir -p frontend/src/shared/utils
mkdir -p frontend/src/stores
mkdir -p frontend/public
```

- [ ] **Step 2: 创建 package.json**

```json
{
  "name": "qtrading",
  "version": "2.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.22.0",
    "antd": "^5.14.0",
    "@ant-design/icons": "^5.1.0",
    "@tanstack/react-query": "^5.20.0",
    "echarts": "^5.5.0",
    "echarts-for-react": "^3.0.2",
    "axios": "^1.6.7",
    "zustand": "^4.5.0",
    "dayjs": "^1.11.10"
  },
  "devDependencies": {
    "@types/react": "^18.2.55",
    "@types/react-dom": "^18.2.19",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.1.0",
    "tailwindcss": "^3.4.1",
    "postcss": "^8.4.35",
    "autoprefixer": "^10.4.17"
  }
}
```

- [ ] **Step 3: 创建 tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 4: 创建 tsconfig.node.json**

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 5: 创建 vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

- [ ] **Step 6: 创建 tailwind.config.js**

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

- [ ] **Step 7: 创建 postcss.config.js**

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

- [ ] **Step 8: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>量化数据</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 9: 提交代码**

```bash
git add frontend/
git commit -m "feat(frontend): 初始化前端项目结构"
```

---

### Task 12: 创建前端基础文件

**Files:**
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/router.tsx`
- Create: `frontend/src/index.css`

- [ ] **Step 1: 创建 main.tsx**

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import './index.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
)
```

- [ ] **Step 2: 创建 index.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

- [ ] **Step 3: 创建 router.tsx**

```tsx
import { createBrowserRouter } from 'react-router-dom'
import Layout from '@/shared/components/Layout'

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <div>首页</div>,
      },
      {
        path: 'hotmoney',
        element: <div>龙虎榜</div>,
      },
      {
        path: 'hotmoney/info',
        element: <div>游资介绍</div>,
      },
      {
        path: 'stock',
        element: <div>股票信息</div>,
      },
      {
        path: 'stock/trend/:code',
        element: <div>股票走势</div>,
      },
      {
        path: 'limit',
        element: <div>涨跌停</div>,
      },
      {
        path: 'sector',
        element: <div>板块行情</div>,
      },
    ],
  },
])

export default router
```

- [ ] **Step 4: 创建 App.tsx**

```tsx
import { RouterProvider } from 'react-router-dom'
import router from './router'

function App() {
  return <RouterProvider router={router} />
}

export default App
```

- [ ] **Step 5: 提交代码**

```bash
git add frontend/src/main.tsx frontend/src/App.tsx frontend/src/router.tsx frontend/src/index.css
git commit -m "feat(frontend): 添加前端入口文件和路由配置"
```

---

### Task 13: 创建共享组件

**Files:**
- Create: `frontend/src/shared/components/Layout/index.tsx`
- Create: `frontend/src/shared/components/Layout/Header.tsx`
- Create: `frontend/src/shared/components/Layout/Sidebar.tsx`
- Create: `frontend/src/shared/components/PaginationTable/index.tsx`

- [ ] **Step 1: 创建 Header 组件**

```tsx
import { Layout, Typography } from 'antd'

const { Header: AntHeader } = Layout

function Header() {
  return (
    <AntHeader className="bg-white px-6 flex items-center border-b">
      <Typography.Title level={4} className="m-0">
        量化数据
      </Typography.Title>
    </AntHeader>
  )
}

export default Header
```

- [ ] **Step 2: 创建 Sidebar 组件**

```tsx
import { Menu } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  HomeOutlined,
  StockOutlined,
  RiseOutlined,
  BarChartOutlined,
  TeamOutlined,
} from '@ant-design/icons'

const menuItems = [
  {
    key: '/',
    icon: <HomeOutlined />,
    label: '首页',
  },
  {
    key: '/hotmoney',
    icon: <TeamOutlined />,
    label: '龙虎榜',
  },
  {
    key: '/limit',
    icon: <RiseOutlined />,
    label: '打板数据',
  },
  {
    key: '/sector',
    icon: <BarChartOutlined />,
    label: '板块行情',
  },
  {
    key: '/stock',
    icon: <StockOutlined />,
    label: '股票',
  },
  {
    key: '/hotmoney/info',
    icon: <TeamOutlined />,
    label: '游资介绍',
  },
]

function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <Menu
      mode="inline"
      selectedKeys={[location.pathname]}
      items={menuItems}
      onClick={({ key }) => navigate(key)}
      className="h-full border-r"
    />
  )
}

export default Sidebar
```

- [ ] **Step 3: 创建 Layout 组件**

```tsx
import { Layout } from 'antd'
import { Outlet } from 'react-router-dom'
import Header from './Header'
import Sidebar from './Sidebar'

const { Content, Sider } = Layout

function LayoutComponent() {
  return (
    <Layout className="min-h-screen">
      <Header />
      <Layout>
        <Sider width={200} className="bg-white">
          <Sidebar />
        </Sider>
        <Content className="p-6 bg-gray-50">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}

export default LayoutComponent
```

- [ ] **Step 4: 创建 PaginationTable 组件**

```tsx
import { Table, Pagination } from 'antd'
import type { TableProps, PaginationProps } from 'antd'

interface PaginationTableProps<T> extends TableProps<T> {
  total: number
  current: number
  pageSize: number
  onChange: (page: number, pageSize: number) => void
}

function PaginationTable<T extends object>({
  total,
  current,
  pageSize,
  onChange,
  ...tableProps
}: PaginationTableProps<T>) {
  return (
    <div>
      <Table {...tableProps} pagination={false} />
      <div className="mt-4 flex justify-end">
        <Pagination
          current={current}
          pageSize={pageSize}
          total={total}
          onChange={onChange}
          showSizeChanger
          showTotal={(total) => `共 ${total} 条`}
        />
      </div>
    </div>
  )
}

export default PaginationTable
```

- [ ] **Step 5: 提交代码**

```bash
git add frontend/src/shared/components/
git commit -m "feat(frontend): 添加布局和分页表格组件"
```

---

### Task 14: 创建 API 请求模块

**Files:**
- Create: `frontend/src/shared/api/client.ts`
- Create: `frontend/src/shared/api/hotmoney.ts`
- Create: `frontend/src/shared/api/stock.ts`
- Create: `frontend/src/shared/api/daily.ts`
- Create: `frontend/src/shared/api/limit.ts`
- Create: `frontend/src/shared/api/sector.ts`

- [ ] **Step 1: 创建 Axios 客户端**

```typescript
import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

client.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default client
```

- [ ] **Step 2: 创建游资 API**

```typescript
import client from './client'

export const hotmoneyApi = {
  getHotMoneyList: (params: {
    name?: string
    page?: number
    pageSize?: number
  }) => client.get('/get_hotmoney_data', { params }),

  getDailyHotMoneyTrade: (params: {
    hmName?: string
    tradeDate?: string
    tsName?: string
    tsCode?: string
    page?: number
    pageSize?: number
  }) => client.get('/get_daily_hotmoney_trade_data', { params }),
}
```

- [ ] **Step 3: 创建股票 API**

```typescript
import client from './client'

export const stockApi = {
  getStockList: (params: {
    symbol?: string
    name?: string
    industry?: string
    startDate?: string
    endDate?: string
    page?: number
    pageSize?: number
  }) => client.get('/get_stock_basic_info', { params }),

  getDailyData: (params: { ts_code: string }) =>
    client.get('/get_daily_data', { params }),
}
```

- [ ] **Step 4: 创建日线数据 API**

```typescript
import client from './client'

export const dailyApi = {
  getDailyData: (ts_code: string) =>
    client.get('/get_daily_data', { params: { ts_code } }),
}
```

- [ ] **Step 5: 创建涨跌停 API**

```typescript
import client from './client'

export const limitApi = {
  getDailyLimitData: () => client.get('/get_daily_limit_data'),
}
```

- [ ] **Step 6: 创建板块 API**

```typescript
import client from './client'

export const sectorApi = {
  getDailySectorLimitData: (params?: {
    sector_code?: string
    sector_name?: string
    sector_type?: string
    start_date?: string
    end_date?: string
  }) => client.get('/get_daily_sector_limit_data', { params }),

  getAllThsIndex: () => client.get('/get_all_ths_index'),
}
```

- [ ] **Step 7: 提交代码**

```bash
git add frontend/src/shared/api/
git commit -m "feat(frontend): 添加 API 请求模块"
```

---

### Task 15: 创建公共类型和工具

**Files:**
- Create: `frontend/src/shared/types/common.ts`
- Create: `frontend/src/shared/utils/format.ts`
- Create: `frontend/src/shared/hooks/usePagination.ts`

- [ ] **Step 1: 创建公共类型**

```typescript
export interface PagedResponse<T> {
  data: T[]
  total: number
}

export interface HotMoneyInfo {
  name: string
  desc?: string
  orgs?: string
}

export interface DailyHotMoneyTrade {
  trade_date?: string
  ts_code?: string
  ts_name?: string
  hm_name?: string
  buy_amount?: string
  sell_amount?: string
  net_amount?: string
}

export interface StockBasicInfo {
  ts_code: string
  symbol?: string
  name?: string
  area?: string
  industry?: string
  market?: string
  list_date?: string
}

export interface DailyData {
  trade_date?: string
  open?: number
  high?: number
  low?: number
  close?: number
  pre_close?: number
  price_change?: number
  pct_chg?: number
  vol?: number
  amount?: number
}

export interface DailyLimitData {
  trade_date?: string
  ts_code?: string
  name?: string
  close?: number
  pct_chg?: number
  limit_price?: number
}

export interface DailySectorLimitData {
  trade_date?: string
  sector_code?: string
  sector_name?: string
  sector_type?: string
  pct_chg?: number
}

export interface ThsIndex {
  ts_code?: string
  name?: string
}
```

- [ ] **Step 2: 创建格式化工具**

```typescript
import dayjs from 'dayjs'

export const formatDate = (date: string | undefined, format = 'YYYY-MM-DD') => {
  if (!date) return '-'
  return dayjs(date).format(format)
}

export const formatNumber = (num: number | undefined | null) => {
  if (num === undefined || num === null) return '-'
  return num.toLocaleString()
}

export const formatPercent = (num: number | undefined | null) => {
  if (num === undefined || num === null) return '-'
  return `${num.toFixed(2)}%`
}

export const formatAmount = (amount: string | undefined) => {
  if (!amount) return '-'
  const num = parseFloat(amount)
  if (isNaN(num)) return amount
  if (num >= 100000000) {
    return `${(num / 100000000).toFixed(2)}亿`
  }
  if (num >= 10000) {
    return `${(num / 10000).toFixed(2)}万`
  }
  return num.toLocaleString()
}
```

- [ ] **Step 3: 创建分页 Hook**

```typescript
import { useState, useCallback } from 'react'

interface UsePaginationProps {
  defaultPage?: number
  defaultPageSize?: number
}

interface UsePaginationReturn {
  page: number
  pageSize: number
  onChange: (page: number, pageSize: number) => void
  reset: () => void
}

export const usePagination = (
  props: UsePaginationProps = {}
): UsePaginationReturn => {
  const { defaultPage = 1, defaultPageSize = 10 } = props
  const [page, setPage] = useState(defaultPage)
  const [pageSize, setPageSize] = useState(defaultPageSize)

  const onChange = useCallback((newPage: number, newPageSize: number) => {
    setPage(newPage)
    setPageSize(newPageSize)
  }, [])

  const reset = useCallback(() => {
    setPage(defaultPage)
    setPageSize(defaultPageSize)
  }, [defaultPage, defaultPageSize])

  return { page, pageSize, onChange, reset }
}
```

- [ ] **Step 4: 提交代码**

```bash
git add frontend/src/shared/types/ frontend/src/shared/utils/ frontend/src/shared/hooks/
git commit -m "feat(frontend): 添加公共类型、工具函数和 Hooks"
```

---

## 阶段三：前端页面开发

### Task 16: 创建首页模块

**Files:**
- Create: `frontend/src/modules/Home/index.tsx`

- [ ] **Step 1: 创建首页组件**

```tsx
import { Card, Row, Col, Statistic } from 'antd'
import { StockOutlined, RiseOutlined, TeamOutlined, BarChartOutlined } from '@ant-design/icons'

function Home() {
  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Statistic
              title="龙虎榜"
              value={0}
              prefix={<TeamOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="涨跌停"
              value={0}
              prefix={<RiseOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="板块行情"
              value={0}
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="股票数量"
              value={0}
              prefix={<StockOutlined />}
            />
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Home
```

- [ ] **Step 2: 更新路由**

```tsx
import Home from '@/modules/Home'

// 在 children 中更新首页路由
{
  index: true,
  element: <Home />,
},
```

- [ ] **Step 3: 提交代码**

```bash
git add frontend/src/modules/Home/
git commit -m "feat(frontend): 添加首页模块"
```

---

### Task 17: 创建游资介绍模块

**Files:**
- Create: `frontend/src/modules/HotMoneyInfo/index.tsx`
- Create: `frontend/src/modules/HotMoneyInfo/types.ts`

- [ ] **Step 1: 创建类型定义**

```typescript
export interface HotMoneyInfoItem {
  name: string
  desc?: string
  orgs?: string
}
```

- [ ] **Step 2: 创建游资介绍页面**

```tsx
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Input, Button, Table, Space } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { hotmoneyApi } from '@/shared/api/hotmoney'
import { usePagination } from '@/shared/hooks/usePagination'
import PaginationTable from '@/shared/components/PaginationTable'
import type { HotMoneyInfoItem } from './types'

function HotMoneyInfo() {
  const [name, setName] = useState('')
  const { page, pageSize, onChange, reset: resetPagination } = usePagination()

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['hotmoney-info', name, page, pageSize],
    queryFn: () => hotmoneyApi.getHotMoneyList({ name, page, pageSize }),
  })

  const columns: ColumnsType<HotMoneyInfoItem> = [
    { title: '名称', dataIndex: 'name', key: 'name', width: 150 },
    {
      title: '描述',
      dataIndex: 'desc',
      key: 'desc',
      ellipsis: true,
      render: (text) => text?.slice(0, 100) + (text?.length > 100 ? '...' : ''),
    },
    {
      title: '机构',
      dataIndex: 'orgs',
      key: 'orgs',
      ellipsis: true,
      render: (text) => text?.slice(0, 100) + (text?.length > 100 ? '...' : ''),
    },
  ]

  const handleSearch = () => {
    resetPagination()
    refetch()
  }

  const handleReset = () => {
    setName('')
    resetPagination()
  }

  return (
    <div>
      <Space className="mb-4">
        <Input
          placeholder="游资名称"
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={{ width: 200 }}
        />
        <Button type="primary" onClick={handleSearch}>
          查询
        </Button>
        <Button onClick={handleReset}>重置</Button>
      </Space>

      <PaginationTable
        columns={columns}
        dataSource={data?.data || []}
        loading={isLoading}
        rowKey="name"
        total={data?.total || 0}
        current={page}
        pageSize={pageSize}
        onChange={onChange}
      />
    </div>
  )
}

export default HotMoneyInfo
```

- [ ] **Step 3: 更新路由**

```tsx
import HotMoneyInfo from '@/modules/HotMoneyInfo'

// 更新路由
{
  path: 'hotmoney/info',
  element: <HotMoneyInfo />,
},
```

- [ ] **Step 4: 提交代码**

```bash
git add frontend/src/modules/HotMoneyInfo/
git commit -m "feat(frontend): 添加游资介绍模块"
```

---

### Task 18: 创建龙虎榜交易模块

**Files:**
- Create: `frontend/src/modules/HotMoney/index.tsx`
- Create: `frontend/src/modules/HotMoney/types.ts`

- [ ] **Step 1: 创建类型定义**

```typescript
export interface DailyHotMoneyTradeItem {
  trade_date?: string
  ts_code?: string
  ts_name?: string
  hm_name?: string
  buy_amount?: string
  sell_amount?: string
  net_amount?: string
}
```

- [ ] **Step 2: 创建龙虎榜交易页面**

```tsx
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Input, Button, Table, Space, DatePicker } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { hotmoneyApi } from '@/shared/api/hotmoney'
import { usePagination } from '@/shared/hooks/usePagination'
import { formatAmount } from '@/shared/utils/format'
import PaginationTable from '@/shared/components/PaginationTable'
import type { DailyHotMoneyTradeItem } from './types'

const { RangePicker } = DatePicker

function HotMoney() {
  const [hmName, setHmName] = useState('')
  const [tsName, setTsName] = useState('')
  const [tsCode, setTsCode] = useState('')
  const [tradeDate, setTradeDate] = useState('')
  const { page, pageSize, onChange, reset: resetPagination } = usePagination()

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['hotmoney-trade', hmName, tsName, tsCode, tradeDate, page, pageSize],
    queryFn: () =>
      hotmoneyApi.getDailyHotMoneyTrade({
        hmName,
        tsName,
        tsCode,
        tradeDate,
        page,
        pageSize,
      }),
  })

  const columns: ColumnsType<DailyHotMoneyTradeItem> = [
    { title: '交易日期', dataIndex: 'trade_date', key: 'trade_date', width: 120 },
    { title: '股票代码', dataIndex: 'ts_code', key: 'ts_code', width: 120 },
    { title: '股票名称', dataIndex: 'ts_name', key: 'ts_name', width: 120 },
    { title: '游资名称', dataIndex: 'hm_name', key: 'hm_name', width: 150 },
    {
      title: '买入金额',
      dataIndex: 'buy_amount',
      key: 'buy_amount',
      width: 120,
      render: formatAmount,
    },
    {
      title: '卖出金额',
      dataIndex: 'sell_amount',
      key: 'sell_amount',
      width: 120,
      render: formatAmount,
    },
    {
      title: '净买入',
      dataIndex: 'net_amount',
      key: 'net_amount',
      width: 120,
      render: formatAmount,
    },
  ]

  const handleSearch = () => {
    resetPagination()
    refetch()
  }

  const handleReset = () => {
    setHmName('')
    setTsName('')
    setTsCode('')
    setTradeDate('')
    resetPagination()
  }

  return (
    <div>
      <Space className="mb-4" wrap>
        <Input
          placeholder="游资名称"
          value={hmName}
          onChange={(e) => setHmName(e.target.value)}
          style={{ width: 150 }}
        />
        <Input
          placeholder="股票代码"
          value={tsCode}
          onChange={(e) => setTsCode(e.target.value)}
          style={{ width: 150 }}
        />
        <Input
          placeholder="股票名称"
          value={tsName}
          onChange={(e) => setTsName(e.target.value)}
          style={{ width: 150 }}
        />
        <Input
          placeholder="交易日期"
          value={tradeDate}
          onChange={(e) => setTradeDate(e.target.value)}
          style={{ width: 150 }}
        />
        <Button type="primary" onClick={handleSearch}>
          查询
        </Button>
        <Button onClick={handleReset}>重置</Button>
      </Space>

      <PaginationTable
        columns={columns}
        dataSource={data?.data || []}
        loading={isLoading}
        rowKey={(record) => `${record.trade_date}-${record.ts_code}-${record.hm_name}`}
        total={data?.total || 0}
        current={page}
        pageSize={pageSize}
        onChange={onChange}
      />
    </div>
  )
}

export default HotMoney
```

- [ ] **Step 3: 更新路由并提交**

```bash
git add frontend/src/modules/HotMoney/
git commit -m "feat(frontend): 添加龙虎榜交易模块"
```

---

### Task 19: 创建股票信息模块

**Files:**
- Create: `frontend/src/modules/Stock/index.tsx`
- Create: `frontend/src/modules/Stock/types.ts`

- [ ] **Step 1: 创建股票信息页面**

```tsx
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Input, Button, Table, Space, Select } from 'antd'
import { useNavigate } from 'react-router-dom'
import type { ColumnsType } from 'antd/es/table'
import { stockApi } from '@/shared/api/stock'
import { usePagination } from '@/shared/hooks/usePagination'
import PaginationTable from '@/shared/components/PaginationTable'
import type { StockBasicInfo } from '@/shared/types/common'

function Stock() {
  const navigate = useNavigate()
  const [symbol, setSymbol] = useState('')
  const [name, setName] = useState('')
  const [industry, setIndustry] = useState('')
  const { page, pageSize, onChange, reset: resetPagination } = usePagination()

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['stock-list', symbol, name, industry, page, pageSize],
    queryFn: () =>
      stockApi.getStockList({
        symbol,
        name,
        industry,
        page,
        pageSize,
      }),
  })

  const columns: ColumnsType<StockBasicInfo> = [
    { title: '股票代码', dataIndex: 'ts_code', key: 'ts_code', width: 120 },
    { title: '股票名称', dataIndex: 'name', key: 'name', width: 120 },
    { title: '行业', dataIndex: 'industry', key: 'industry', width: 100 },
    { title: '上市日期', dataIndex: 'list_date', key: 'list_date', width: 120 },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_, record) => (
        <Button type="link" onClick={() => navigate(`/stock/trend/${record.ts_code}`)}>
          走势
        </Button>
      ),
    },
  ]

  const handleSearch = () => {
    resetPagination()
    refetch()
  }

  const handleReset = () => {
    setSymbol('')
    setName('')
    setIndustry('')
    resetPagination()
  }

  return (
    <div>
      <Space className="mb-4" wrap>
        <Input
          placeholder="股票代码"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          style={{ width: 150 }}
        />
        <Input
          placeholder="股票名称"
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={{ width: 150 }}
        />
        <Input
          placeholder="行业"
          value={industry}
          onChange={(e) => setIndustry(e.target.value)}
          style={{ width: 150 }}
        />
        <Button type="primary" onClick={handleSearch}>
          查询
        </Button>
        <Button onClick={handleReset}>重置</Button>
      </Space>

      <PaginationTable
        columns={columns}
        dataSource={data?.data || []}
        loading={isLoading}
        rowKey="ts_code"
        total={data?.total || 0}
        current={page}
        pageSize={pageSize}
        onChange={onChange}
      />
    </div>
  )
}

export default Stock
```

- [ ] **Step 2: 提交代码**

```bash
git add frontend/src/modules/Stock/
git commit -m "feat(frontend): 添加股票信息模块"
```

---

### Task 20: 创建股票走势模块

**Files:**
- Create: `frontend/src/modules/StockTrend/index.tsx`
- Create: `frontend/src/modules/StockTrend/components/TrendChart.tsx`

- [ ] **Step 1: 创建走势图组件**

```tsx
import ReactECharts from 'echarts-for-react'
import type { DailyData } from '@/shared/types/common'

interface TrendChartProps {
  data: DailyData[]
}

function TrendChart({ data }: TrendChartProps) {
  const option = {
    title: { text: '股票走势' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['收盘价', '成交量'] },
    xAxis: {
      type: 'category',
      data: data.map((item) => item.trade_date),
    },
    yAxis: [
      { type: 'value', name: '价格' },
      { type: 'value', name: '成交量' },
    ],
    series: [
      {
        name: '收盘价',
        type: 'line',
        data: data.map((item) => item.close),
      },
      {
        name: '成交量',
        type: 'bar',
        yAxisIndex: 1,
        data: data.map((item) => item.vol),
      },
    ],
  }

  return <ReactECharts option={option} style={{ height: 400 }} />
}

export default TrendChart
```

- [ ] **Step 2: 创建股票走势页面**

```tsx
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Card, Spin } from 'antd'
import { stockApi } from '@/shared/api/stock'
import TrendChart from './components/TrendChart'

function StockTrend() {
  const { code } = useParams<{ code: string }>()

  const { data, isLoading } = useQuery({
    queryKey: ['stock-trend', code],
    queryFn: () => stockApi.getDailyData({ ts_code: code || '' }),
    enabled: !!code,
  })

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spin size="large" />
      </div>
    )
  }

  return (
    <Card title={`股票走势 - ${code}`}>
      <TrendChart data={data?.data || []} />
    </Card>
  )
}

export default StockTrend
```

- [ ] **Step 3: 提交代码**

```bash
git add frontend/src/modules/StockTrend/
git commit -m "feat(frontend): 添加股票走势模块"
```

---

### Task 21: 创建涨跌停模块

**Files:**
- Create: `frontend/src/modules/DailyLimit/index.tsx`

- [ ] **Step 1: 创建涨跌停页面**

```tsx
import { useQuery } from '@tanstack/react-query'
import { Table, Card } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { limitApi } from '@/shared/api/limit'
import type { DailyLimitData } from '@/shared/types/common'

function DailyLimit() {
  const { data, isLoading } = useQuery({
    queryKey: ['daily-limit'],
    queryFn: () => limitApi.getDailyLimitData(),
  })

  const columns: ColumnsType<DailyLimitData> = [
    { title: '交易日期', dataIndex: 'trade_date', key: 'trade_date', width: 120 },
    { title: '股票代码', dataIndex: 'ts_code', key: 'ts_code', width: 120 },
    { title: '股票名称', dataIndex: 'name', key: 'name', width: 120 },
    {
      title: '收盘价',
      dataIndex: 'close',
      key: 'close',
      width: 100,
      render: (v) => v?.toFixed(2),
    },
    {
      title: '涨跌幅',
      dataIndex: 'pct_chg',
      key: 'pct_chg',
      width: 100,
      render: (v) => (
        <span style={{ color: v > 0 ? '#f5222d' : '#52c41a' }}>
          {v?.toFixed(2)}%
        </span>
      ),
    },
    {
      title: '涨停价',
      dataIndex: 'limit_price',
      key: 'limit_price',
      width: 100,
      render: (v) => v?.toFixed(2),
    },
  ]

  return (
    <Card title="涨跌停数据">
      <Table
        columns={columns}
        dataSource={data?.data || []}
        loading={isLoading}
        rowKey={(record) => `${record.trade_date}-${record.ts_code}`}
        pagination={{ pageSize: 20 }}
      />
    </Card>
  )
}

export default DailyLimit
```

- [ ] **Step 2: 提交代码**

```bash
git add frontend/src/modules/DailyLimit/
git commit -m "feat(frontend): 添加涨跌停模块"
```

---

### Task 22: 创建板块行情模块

**Files:**
- Create: `frontend/src/modules/SectorLimit/index.tsx`

- [ ] **Step 1: 创建板块行情页面**

```tsx
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Input, Button, Table, Space, Card } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { sectorApi } from '@/shared/api/sector'
import type { DailySectorLimitData } from '@/shared/types/common'

function SectorLimit() {
  const [sectorName, setSectorName] = useState('')
  const [sectorType, setSectorType] = useState('')

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['sector-limit', sectorName, sectorType],
    queryFn: () =>
      sectorApi.getDailySectorLimitData({
        sector_name: sectorName,
        sector_type: sectorType,
      }),
  })

  const columns: ColumnsType<DailySectorLimitData> = [
    { title: '交易日期', dataIndex: 'trade_date', key: 'trade_date', width: 120 },
    { title: '板块代码', dataIndex: 'sector_code', key: 'sector_code', width: 120 },
    { title: '板块名称', dataIndex: 'sector_name', key: 'sector_name', width: 150 },
    { title: '板块类型', dataIndex: 'sector_type', key: 'sector_type', width: 100 },
    {
      title: '涨跌幅',
      dataIndex: 'pct_chg',
      key: 'pct_chg',
      width: 100,
      render: (v) => (
        <span style={{ color: v > 0 ? '#f5222d' : '#52c41a' }}>
          {v?.toFixed(2)}%
        </span>
      ),
    },
  ]

  const handleSearch = () => {
    refetch()
  }

  const handleReset = () => {
    setSectorName('')
    setSectorType('')
  }

  return (
    <Card title="板块行情">
      <Space className="mb-4">
        <Input
          placeholder="板块名称"
          value={sectorName}
          onChange={(e) => setSectorName(e.target.value)}
          style={{ width: 150 }}
        />
        <Input
          placeholder="板块类型"
          value={sectorType}
          onChange={(e) => setSectorType(e.target.value)}
          style={{ width: 150 }}
        />
        <Button type="primary" onClick={handleSearch}>
          查询
        </Button>
        <Button onClick={handleReset}>重置</Button>
      </Space>

      <Table
        columns={columns}
        dataSource={data?.data || []}
        loading={isLoading}
        rowKey={(record) => `${record.trade_date}-${record.sector_code}`}
        pagination={{ pageSize: 20 }}
      />
    </Card>
  )
}

export default SectorLimit
```

- [ ] **Step 2: 提交代码**

```bash
git add frontend/src/modules/SectorLimit/
git commit -m "feat(frontend): 添加板块行情模块"
```

---

### Task 23: 更新完整路由配置

**Files:**
- Modify: `frontend/src/router.tsx`

- [ ] **Step 1: 更新路由配置**

```tsx
import { createBrowserRouter } from 'react-router-dom'
import Layout from '@/shared/components/Layout'
import Home from '@/modules/Home'
import HotMoney from '@/modules/HotMoney'
import HotMoneyInfo from '@/modules/HotMoneyInfo'
import Stock from '@/modules/Stock'
import StockTrend from '@/modules/StockTrend'
import DailyLimit from '@/modules/DailyLimit'
import SectorLimit from '@/modules/SectorLimit'

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <Home />,
      },
      {
        path: 'hotmoney',
        element: <HotMoney />,
      },
      {
        path: 'hotmoney/info',
        element: <HotMoneyInfo />,
      },
      {
        path: 'stock',
        element: <Stock />,
      },
      {
        path: 'stock/trend/:code',
        element: <StockTrend />,
      },
      {
        path: 'limit',
        element: <DailyLimit />,
      },
      {
        path: 'sector',
        element: <SectorLimit />,
      },
    ],
  },
])

export default router
```

- [ ] **Step 2: 提交代码**

```bash
git add frontend/src/router.tsx
git commit -m "feat(frontend): 更新完整路由配置"
```

---

## 阶段四：清理和最终配置

### Task 24: 更新 .gitignore

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: 更新 .gitignore**

```
# Python
__pycache__/
*.py[cod]
*$py.class
.env
*.egg-info/
.eggs/

# Node
node_modules/
dist/
.vite/

# Logs
logs/
*.log

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

- [ ] **Step 2: 提交代码**

```bash
git add .gitignore
git commit -m "chore: 更新 .gitignore 配置"
```

---

### Task 25: 创建启动脚本和文档

**Files:**
- Create: `start-backend.bat`
- Create: `start-frontend.bat`
- Modify: `readme.md`

- [ ] **Step 1: 创建后端启动脚本**

```bat
@echo off
cd backend
call venv\Scripts\activate 2>nul || echo "Please create venv first"
python -m app.main
```

- [ ] **Step 2: 创建前端启动脚本**

```bat
@echo off
cd frontend
npm run dev
```

- [ ] **Step 3: 更新 README**

```markdown
# QTtrading 量化交易数据平台

## 技术栈

### 后端
- FastAPI
- SQLAlchemy 2.0
- Pydantic v2
- MySQL

### 前端
- React 18
- TypeScript
- Vite
- Ant Design
- ECharts
- TailwindCSS

## 快速开始

### 后端

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 配置数据库连接
python -m app.main
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 项目结构

详见 docs/superpowers/specs/2026-04-25-qtrading-refactor-design.md
```

- [ ] **Step 4: 提交代码**

```bash
git add start-backend.bat start-frontend.bat readme.md
git commit -m "docs: 添加启动脚本和更新 README"
```

---

### Task 26: 最终提交

- [ ] **Step 1: 检查所有文件**

```bash
git status
```

- [ ] **Step 2: 最终提交**

```bash
git add .
git commit -m "feat: 完成项目重构 - FastAPI + React + TypeScript 架构"
```

---

## 实施完成

项目重构完成，包含：

**后端：**
- FastAPI 应用框架
- SQLAlchemy ORM 模型
- 分层架构（API → Service → Repository → Model）
- 配置管理、日志系统、异常处理
- 定时任务调度器

**前端：**
- React 18 + TypeScript
- Vite 构建工具
- Ant Design UI 组件库
- ECharts 图表库
- 模块化页面结构
- TanStack Query 数据请求管理
