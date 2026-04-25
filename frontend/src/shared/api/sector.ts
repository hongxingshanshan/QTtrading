import client from './client'

export const sectorApi = {
  getDailySectorLimitData: (params?: {
    sector_code?: string
    sector_name?: string
    sector_type?: string
    start_date?: string
    end_date?: string
  }) => client.get('/get_daily_sector_limit_data', { params }),

  getAllThsIndex: () => client.get('/get_all_ths_index'),
}
