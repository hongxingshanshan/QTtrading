import client from './client'
import type { PagedResponse, DailyLimitData } from '@/shared/types/common'

export const limitApi = {
  getDailyLimitData: () => client.get<any, PagedResponse<DailyLimitData>>('/get_daily_limit_data'),
}
