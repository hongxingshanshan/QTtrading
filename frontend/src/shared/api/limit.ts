import client from './client'

export const limitApi = {
  getDailyLimitData: () => client.get('/get_daily_limit_data'),
}
