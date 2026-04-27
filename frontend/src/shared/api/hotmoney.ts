import client from './client'
import type { PagedResponse, HotMoneyInfo, DailyHotMoneyTrade } from '@/shared/types/common'

export const hotmoneyApi = {
  getHotMoneyList: (params: {
    name?: string
    page?: number
    pageSize?: number
  }) => client.get<any, PagedResponse<HotMoneyInfo>>('/get_hotmoney_data', { params }),

  getDailyHotMoneyTrade: (params: {
    hmName?: string
    tradeDate?: string
    tsName?: string
    tsCode?: string
    page?: number
    pageSize?: number
  }) => client.get<any, PagedResponse<DailyHotMoneyTrade>>('/get_daily_hotmoney_trade_data', { params }),
}
