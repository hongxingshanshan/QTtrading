-- =============================================
-- QTtrading 数据库初始化脚本
-- 创建时间: 2026-04-24
-- =============================================

-- 1. 股票基本信息表
CREATE TABLE IF NOT EXISTS stock_basic_info (
    ts_code VARCHAR(20) PRIMARY KEY COMMENT '股票代码',
    symbol VARCHAR(10) COMMENT '股票代码（不含交易所）',
    name VARCHAR(50) COMMENT '股票名称',
    area VARCHAR(20) COMMENT '地域',
    industry VARCHAR(50) COMMENT '所属行业',
    cnspell VARCHAR(20) COMMENT '拼音缩写',
    market VARCHAR(10) COMMENT '市场类型',
    list_date DATE COMMENT '上市日期',
    act_name VARCHAR(100) COMMENT '实控人名称',
    act_ent_type VARCHAR(50) COMMENT '实控人企业性质',
    fullname VARCHAR(100) COMMENT '股票全称',
    enname VARCHAR(100) COMMENT '英文全称',
    exchange VARCHAR(20) COMMENT '交易所代码',
    curr_type VARCHAR(10) COMMENT '交易货币',
    list_status VARCHAR(2) COMMENT '上市状态 L上市 D退市 P暂停上市',
    delist_date DATE COMMENT '退市日期',
    is_hs VARCHAR(2) COMMENT '是否沪深港通标的 N否 H沪股通 S深股通',
    INDEX idx_name (name),
    INDEX idx_industry (industry),
    INDEX idx_list_date (list_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票基本信息表';

-- 2. 游资信息表
CREATE TABLE IF NOT EXISTS hot_money_info (
    name VARCHAR(50) PRIMARY KEY COMMENT '游资名称',
    `desc` TEXT COMMENT '游资描述',
    orgs TEXT COMMENT '常用营业部'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='游资信息表';

-- 3. 每日游资交易明细表
CREATE TABLE IF NOT EXISTS daily_hot_money_trading (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trade_date DATE COMMENT '交易日期',
    ts_code VARCHAR(20) COMMENT '股票代码',
    ts_name VARCHAR(50) COMMENT '股票名称',
    buy_amount DECIMAL(20,2) COMMENT '买入金额（万元）',
    sell_amount DECIMAL(20,2) COMMENT '卖出金额（万元）',
    net_amount DECIMAL(20,2) COMMENT '净买入金额（万元）',
    hm_name VARCHAR(50) COMMENT '游资名称',
    hm_orgs TEXT COMMENT '游资营业部',
    tag VARCHAR(50) COMMENT '标签',
    UNIQUE KEY uk_trade_date_ts_code (trade_date, ts_code, hm_name),
    INDEX idx_trade_date (trade_date),
    INDEX idx_ts_code (ts_code),
    INDEX idx_hm_name (hm_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='每日游资交易明细表';

-- 4. 每日股票行情数据表
CREATE TABLE IF NOT EXISTS daily_data (
    ts_code VARCHAR(20) COMMENT '股票代码',
    trade_date DATE COMMENT '交易日期',
    open DECIMAL(10,3) COMMENT '开盘价',
    high DECIMAL(10,3) COMMENT '最高价',
    low DECIMAL(10,3) COMMENT '最低价',
    close DECIMAL(10,3) COMMENT '收盘价',
    pre_close DECIMAL(10,3) COMMENT '昨收价',
    price_change DECIMAL(10,3) COMMENT '涨跌额',
    pct_chg DECIMAL(10,3) COMMENT '涨跌幅（%）',
    vol DECIMAL(20,2) COMMENT '成交量（手）',
    amount DECIMAL(20,2) COMMENT '成交额（千元）',
    PRIMARY KEY (ts_code, trade_date),
    INDEX idx_trade_date (trade_date),
    INDEX idx_ts_code (ts_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='每日股票行情数据表';

-- 5. 每日涨跌停数据表
CREATE TABLE IF NOT EXISTS daily_limit_data (
    trade_date DATE COMMENT '交易日期',
    ts_code VARCHAR(20) COMMENT '股票代码',
    industry VARCHAR(50) COMMENT '所属行业',
    name VARCHAR(50) COMMENT '股票名称',
    close DECIMAL(10,3) COMMENT '收盘价',
    pct_chg DECIMAL(10,3) COMMENT '涨跌幅（%）',
    amount DECIMAL(20,2) COMMENT '总成交额（万元）',
    limit_amount DECIMAL(20,2) COMMENT '涨停/跌停金额（万元）',
    float_mv DECIMAL(20,2) COMMENT '流通市值（万元）',
    total_mv DECIMAL(20,2) COMMENT '总市值（万元）',
    turnover_ratio DECIMAL(10,3) COMMENT '换手率（%）',
    fd_amount DECIMAL(20,2) COMMENT '封单金额（万元）',
    first_time TIME COMMENT '首次涨停时间',
    last_time TIME COMMENT '最后涨停时间',
    open_times INT COMMENT '打开次数',
    up_stat VARCHAR(20) COMMENT '涨停统计',
    limit_times INT COMMENT '涨停次数',
    limit_status VARCHAR(2) COMMENT '涨跌停状态 U涨停 D跌停',
    PRIMARY KEY (trade_date, ts_code),
    INDEX idx_trade_date (trade_date),
    INDEX idx_ts_code (ts_code),
    INDEX idx_limit_status (limit_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='每日涨跌停数据表';

-- 6. 每日板块涨跌停统计表
CREATE TABLE IF NOT EXISTS daily_sector_limit_data (
    sector_code VARCHAR(20) COMMENT '板块代码',
    sector_name VARCHAR(50) COMMENT '板块名称',
    sector_type VARCHAR(10) COMMENT '板块类型',
    trade_date DATE COMMENT '交易日期',
    up_limit_count INT COMMENT '涨停股票数量',
    down_limit_count INT COMMENT '跌停股票数量',
    PRIMARY KEY (sector_code, trade_date),
    INDEX idx_trade_date (trade_date),
    INDEX idx_sector_name (sector_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='每日板块涨跌停统计表';

-- 7. 同花顺指数表
CREATE TABLE IF NOT EXISTS ths_index (
    ts_code VARCHAR(20) PRIMARY KEY COMMENT '指数代码',
    name VARCHAR(50) COMMENT '指数名称',
    count INT COMMENT '成分股数量',
    exchange VARCHAR(20) COMMENT '交易所',
    list_date DATE COMMENT '发布日期',
    type VARCHAR(10) COMMENT '类型',
    INDEX idx_name (name),
    INDEX idx_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='同花顺指数表';

-- 8. 同花顺指数成分股表
CREATE TABLE IF NOT EXISTS ths_member (
    ts_code VARCHAR(20) COMMENT '指数代码',
    con_code VARCHAR(20) COMMENT '成分股代码',
    con_name VARCHAR(50) COMMENT '成分股名称',
    weight DECIMAL(10,3) COMMENT '权重',
    in_date DATE COMMENT '纳入日期',
    out_date DATE COMMENT '剔除日期',
    is_new VARCHAR(2) COMMENT '是否最新 Y是 N否',
    PRIMARY KEY (ts_code, con_code),
    INDEX idx_ts_code (ts_code),
    INDEX idx_con_code (con_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='同花顺指数成分股表';

-- 9. 每日最强概念板块表
CREATE TABLE IF NOT EXISTS daily_limit_cpt_list (
    ts_code VARCHAR(20) COMMENT '概念板块代码',
    name VARCHAR(50) COMMENT '概念板块名称',
    trade_date DATE COMMENT '交易日期',
    days INT COMMENT '连续涨停天数',
    up_stat VARCHAR(20) COMMENT '涨停统计',
    cons_nums INT COMMENT '涨停股票数量',
    up_nums INT COMMENT '上涨股票数量',
    pct_chg DECIMAL(10,3) COMMENT '涨跌幅（%）',
    `rank` INT COMMENT '排名',
    PRIMARY KEY (ts_code, trade_date),
    INDEX idx_trade_date (trade_date),
    INDEX idx_rank (`rank`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='每日最强概念板块表';

-- 10. 龙虎榜每日交易明细表
CREATE TABLE IF NOT EXISTS top_trade_data (
    trade_date DATE COMMENT '交易日期',
    ts_code VARCHAR(20) COMMENT '股票代码',
    name VARCHAR(50) COMMENT '股票名称',
    close DECIMAL(10,3) COMMENT '收盘价',
    pct_change DECIMAL(10,3) COMMENT '涨跌幅（%）',
    turnover_rate DECIMAL(10,3) COMMENT '换手率（%）',
    amount DECIMAL(20,2) COMMENT '总成交额（万元）',
    l_sell DECIMAL(20,2) COMMENT '龙虎榜卖出金额（万元）',
    l_buy DECIMAL(20,2) COMMENT '龙虎榜买入金额（万元）',
    l_amount DECIMAL(20,2) COMMENT '龙虎榜总金额（万元）',
    net_amount DECIMAL(20,2) COMMENT '龙虎榜净买入金额（万元）',
    net_rate DECIMAL(10,3) COMMENT '净买入占比（%）',
    amount_rate DECIMAL(10,3) COMMENT '龙虎榜成交额占比（%）',
    float_values DECIMAL(20,2) COMMENT '当日流通市值（万元）',
    reason VARCHAR(100) COMMENT '上榜原因',
    PRIMARY KEY (trade_date, ts_code),
    INDEX idx_trade_date (trade_date),
    INDEX idx_ts_code (ts_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='龙虎榜每日交易明细表';

-- 11. 龙虎榜机构交易明细表
CREATE TABLE IF NOT EXISTS top_inst_trade_data (
    trade_date DATE COMMENT '交易日期',
    ts_code VARCHAR(20) COMMENT '股票代码',
    exalter VARCHAR(50) COMMENT '营业部名称',
    side VARCHAR(10) COMMENT '买卖方向 B买 S卖',
    buy DECIMAL(20,2) COMMENT '买入金额（万元）',
    buy_rate DECIMAL(10,3) COMMENT '买入占比（%）',
    sell DECIMAL(20,2) COMMENT '卖出金额（万元）',
    sell_rate DECIMAL(10,3) COMMENT '卖出占比（%）',
    net_buy DECIMAL(20,2) COMMENT '净买入金额（万元）',
    reason VARCHAR(100) COMMENT '上榜原因',
    PRIMARY KEY (trade_date, ts_code, exalter),
    INDEX idx_trade_date (trade_date),
    INDEX idx_ts_code (ts_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='龙虎榜机构交易明细表';

-- 12. 复权因子表
CREATE TABLE IF NOT EXISTS adj_factor (
    ts_code VARCHAR(20) COMMENT '股票代码',
    trade_date DATE COMMENT '交易日期',
    adj_factor DECIMAL(20,6) COMMENT '复权因子',
    PRIMARY KEY (ts_code, trade_date),
    INDEX idx_trade_date (trade_date),
    INDEX idx_ts_code (ts_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='复权因子表';

-- =============================================
-- 数据库初始化完成
-- =============================================