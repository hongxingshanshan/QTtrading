import client from './client'

export const dailyApi = {
  getDailyData: (ts_code: string) =>
    client.get('/get_daily_data', { params: { ts_code } }),
}
