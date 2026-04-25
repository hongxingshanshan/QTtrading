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
