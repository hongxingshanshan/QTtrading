import client from './client'
import type { PagedResponse, DailySectorLimitData, ThsIndex } from '@/shared/types/common'

export const sectorApi = {
  getDailySectorLimitData: (params?: {
    sector_code?: string
    sector_name?: string
    sector_type?: string
    start_date?: string
    end_date?: string
  }) => client.get<any, PagedResponse<DailySectorLimitData>>('/get_daily_sector_limit_data', { params }),

  getAllThsIndex: () => client.get<any, PagedResponse<ThsIndex>>('/get_all_ths_index'),
}
