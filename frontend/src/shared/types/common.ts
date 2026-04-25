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

// 股票走势图相关类型
export interface StockTrendBasic {
  ts_code?: string
  name?: string
  industry?: string
}

export interface StockTrendLatest {
  close?: number
  pct_chg?: number
  vol?: number
  amount?: number
  open?: number
  high?: number
  low?: number
  pre_close?: number
  price_change?: number
}

export interface StockTrendKlineItem {
  trade_date?: string
  open?: number
  high?: number
  low?: number
  close?: number
  pre_close?: number // 前收盘价
  vol?: number
  amount?: number
  pct_chg?: number
}

export interface StockTrendMA {
  ma5: (number | null)[]
  ma10: (number | null)[]
  ma20: (number | null)[]
  ma30: (number | null)[]
  ma60: (number | null)[]
  ma90: (number | null)[]
  ma125: (number | null)[]
  ma250: (number | null)[]
}

export interface StockTrendResponse {
  basic: StockTrendBasic
  latest: StockTrendLatest
  kline: StockTrendKlineItem[]
  ma: StockTrendMA
}
