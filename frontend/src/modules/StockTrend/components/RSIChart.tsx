import ReactECharts from 'echarts-for-react'
import type { ECharts } from 'echarts'
import { formatDate } from '@/shared/utils/format'
import type { StockTrendKlineItem } from '@/shared/types/common'

interface RSIChartProps {
  kline: StockTrendKlineItem[]
  onChartReady?: (instance: ECharts | null) => void
}

function calculateRSI(kline: StockTrendKlineItem[], periods: number[] = [6, 12, 24]) {
  const closes = kline.map((item) => item.close || 0)

  const rsiData: { [key: string]: (number | null)[] } = {}

  periods.forEach((n) => {
    const rsi: (number | null)[] = []

    for (let i = 0; i < kline.length; i++) {
      if (i < n) {
        rsi.push(null)
        continue
      }

      let upSum = 0
      let downSum = 0

      for (let j = i - n + 1; j <= i; j++) {
        const change = closes[j] - closes[j - 1]
        if (change > 0) {
          upSum += change
        } else {
          downSum += Math.abs(change)
        }
      }

      const avgUp = upSum / n
      const avgDown = downSum / n

      if (avgDown === 0) {
        rsi.push(100)
      } else {
        const rs = avgUp / avgDown
        rsi.push(Number((100 - 100 / (1 + rs)).toFixed(2)))
      }
    }

    rsiData[`rsi${n}`] = rsi
  })

  return rsiData
}

function RSIChart({ kline, onChartReady }: RSIChartProps) {
  const rsiData = calculateRSI(kline)
  const dates = kline.map((item) => formatDate(item.trade_date) || '')

  const option = {
    animation: false,
    legend: {
      data: ['RSI6', 'RSI12', 'RSI24'],
      top: 5,
      left: 'center',
      itemWidth: 15,
      itemHeight: 10,
      textStyle: { fontSize: 12 },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#ccc',
      borderWidth: 1,
      textStyle: { color: '#333' },
    },
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: 0,
        startValue: dates.length > 130 ? dates.length - 130 : 0,
        endValue: dates.length - 1,
      },
      {
        type: 'slider',
        show: false,
        xAxisIndex: 0,
        startValue: dates.length > 130 ? dates.length - 130 : 0,
        endValue: dates.length - 1,
      },
    ],
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { color: '#666' },
    },
    yAxis: {
      scale: true,
      min: 0,
      max: 100,
      splitLine: {
        lineStyle: { color: '#e0e0e0', type: 'dashed' },
      },
      axisLabel: { color: '#666' },
    },
    grid: {
      left: '10%',
      right: '8%',
      top: '18%',
      bottom: '15%',
    },
    series: [
      {
        name: 'RSI6',
        type: 'line',
        data: rsiData.rsi6,
        lineStyle: { width: 1 },
        itemStyle: { color: '#f5a623' },
        symbol: 'none',
      },
      {
        name: 'RSI12',
        type: 'line',
        data: rsiData.rsi12,
        lineStyle: { width: 1 },
        itemStyle: { color: '#4a90d9' },
        symbol: 'none',
      },
      {
        name: 'RSI24',
        type: 'line',
        data: rsiData.rsi24,
        lineStyle: { width: 1 },
        itemStyle: { color: '#9013fe' },
        symbol: 'none',
      },
    ],
  }

  return (
    <div className="mt-2">
      <ReactECharts
        option={option}
        style={{ height: 180 }}
        opts={{ renderer: 'canvas' }}
        onChartReady={(instance) => onChartReady?.(instance)}
      />
    </div>
  )
}

export default RSIChart