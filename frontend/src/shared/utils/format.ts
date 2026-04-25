import dayjs from 'dayjs'

export const formatDate = (date: string | undefined, format = 'YYYY-MM-DD') => {
  if (!date) return '-'
  return dayjs(date).format(format)
}

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
  if (num >= 100000000) {
    return `${(num / 100000000).toFixed(2)}亿`
  }
  if (num >= 10000) {
    return `${(num / 10000).toFixed(2)}万`
  }
  return num.toLocaleString()
}
