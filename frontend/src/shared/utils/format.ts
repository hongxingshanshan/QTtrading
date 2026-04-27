import dayjs from 'dayjs'
import customParseFormat from 'dayjs/plugin/customParseFormat'

// 启用自定义解析格式插件
dayjs.extend(customParseFormat)

export const formatDate = (date: unknown, formatStr = 'YYYY-MM-DD') => {
  if (!date) return '-'

  // 确保 format 是字符串
  const format = typeof formatStr === 'string' ? formatStr : 'YYYY-MM-DD'

  // 处理 Date 对象
  if (date instanceof Date) {
    return dayjs(date).format(format)
  }

  // 处理数字（时间戳）
  if (typeof date === 'number') {
    return dayjs(date).format(format)
  }

  // 处理字符串
  if (typeof date === 'string') {
    // 支持 YYYYMMDD 格式 (如 20240426)
    if (date.length === 8 && /^\d{8}$/.test(date)) {
      return dayjs(date, 'YYYYMMDD').format(format)
    }
    return dayjs(date).format(format)
  }

  return '-'
}

/**
 * 专门用于 Ant Design Table render 的日期格式化函数
 * 用法: { title: '日期', dataIndex: 'trade_date', render: renderDate }
 */
export const renderDate = (date: unknown) => formatDate(date)

export const formatNumber = (num: number | undefined | null) => {
  if (num === undefined || num === null) return '-'
  return num.toLocaleString()
}

export const formatPercent = (num: number | undefined | null) => {
  if (num === undefined || num === null) return '-'
  return `${num.toFixed(2)}%`
}

export const formatAmount = (amount: string | undefined) => {
  if (!amount) return '-'
  const num = parseFloat(amount)
  if (isNaN(num)) return amount

  const absNum = Math.abs(num)
  const sign = num < 0 ? '-' : ''

  if (absNum >= 100000000) {
    return `${sign}${(absNum / 100000000).toFixed(2)}亿`
  }
  if (absNum >= 10000) {
    return `${sign}${(absNum / 10000).toFixed(2)}万`
  }
  return `${sign}${absNum.toLocaleString()}`
}
