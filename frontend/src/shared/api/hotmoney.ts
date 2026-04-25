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
