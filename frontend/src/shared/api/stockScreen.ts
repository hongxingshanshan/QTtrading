import client from './client'
import type { ScreenRequest, ScreenResponse, ScreenTemplate, AvailableFields } from '@/modules/StockScreen/types'

export const stockScreenApi = {
  // 执行选股
  screen: (params: ScreenRequest) =>
    client.post<any, ScreenResponse>('/stock_screen', params),

  // 获取策略模板列表
  getTemplates: () =>
    client.get<any, { success: boolean; data: ScreenTemplate[] }>('/stock_screen/templates'),

  // 获取单个模板
  getTemplate: (templateId: string) =>
    client.get<any, { success: boolean; data: ScreenTemplate }>(`/stock_screen/templates/${templateId}`),

  // 使用模板选股
  screenByTemplate: (templateId: string, tradeDate: string, limit: number = 100) =>
    client.post<any, ScreenResponse>(`/stock_screen/template/${templateId}`, null, {
      params: { trade_date: tradeDate, limit }
    }),

  // 获取可用交易日期
  getAvailableDates: (limit: number = 30) =>
    client.get<any, { success: boolean; data: string[] }>('/stock_screen/dates', {
      params: { limit }
    }),

  // 获取可用字段
  getAvailableFields: () =>
    client.get<any, { success: boolean; data: AvailableFields }>('/stock_screen/fields'),
}
