import client from './client'
import type { PagedResponse, StockBasicInfo, DailyData, StockTrendResponse } from '@/shared/types/common'

export const stockApi = {
  getStockList: (params: {
    symbol?: string
    name?: string
    industry?: string
    startDate?: string
    endDate?: string
    page?: number
    pageSize?: number
  }) => client.get<any, PagedResponse<StockBasicInfo>>('/get_stock_basic_info', { params }),

  getDailyData: (params: { ts_code: string }) =>
    client.get<any, { data: DailyData[] }>('/get_daily_data', { params }),

  getTrendData: (
    ts_code: string,
    params?: {
      start_date?: string
      end_date?: string
      period?: 'daily' | 'weekly' | 'monthly'
      adj_type?: 'qfq' | 'hfq' | 'none'
    }
  ) => client.get<any, StockTrendResponse>(`/trend/${ts_code}`, { params }),
}
