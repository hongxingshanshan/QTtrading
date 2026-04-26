// 条件类型
export type ConditionType =
  | 'indicator'
  | 'industry'
  | 'basic'
  | 'fina'
  | 'limit'
  | 'limit_status'
  | 'macd_cross'
  | 'ma_alignment'
  | 'boll_position'
  | 'consecutive'
  | 'limit_up'

// 操作符类型
export type OperatorType =
  | '>'
  | '>='
  | '<'
  | '<='
  | '=='
  | '!='
  | 'in'
  | 'not_in'
  | 'between'

// 选股条件
export interface ScreenCondition {
  type: ConditionType
  field?: string
  operator?: OperatorType
  value?: number | number[] | string[]
  // 特殊条件参数
  cross_type?: 'golden' | 'death'
  alignment?: 'bullish' | 'bearish'
  direction?: 'up' | 'down'
  days?: number
  status?: 'up' | 'down' | 'none'
}

// 选股请求
export interface ScreenRequest {
  trade_date: string
  conditions: ScreenCondition[]
  logic: 'AND' | 'OR'
  limit: number
  offset: number
  order_by: string
  order_desc: boolean
}

// 选股结果股票
export interface ScreenStock {
  ts_code: string
  name: string
  industry?: string
  area?: string
  close?: number
  pct_change?: number
  indicators: {
    rsi6?: number
    j_value?: number
    macd_hist?: number
    vol_ratio?: number
    k_value?: number
    d_value?: number
    boll_position?: number
    [key: string]: number | undefined
  }
}

// 选股响应
export interface ScreenResponse {
  success: boolean
  data: {
    total: number
    trade_date: string
    stocks: ScreenStock[]
  }
}

// 策略模板
export interface ScreenTemplate {
  id: string
  name: string
  description: string
  conditions: ScreenCondition[]
}

// 可用字段信息
export interface AvailableFields {
  indicator_fields: Record<string, string>
  stock_fields: Record<string, string>
  basic_fields: Record<string, string>
  fina_fields: Record<string, string>
  limit_fields: Record<string, string>
  operators: {
    numeric: string[]
    list: string[]
    string: string[]
  }
  special_conditions: Array<{
    type: string
    params: string[]
    desc: string
  }>
}
