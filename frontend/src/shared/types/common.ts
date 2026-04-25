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
