import ReactECharts from 'echarts-for-react'
import type { ECharts } from 'echarts'
import { formatDate } from '@/shared/utils/format'
import type { StockTrendKlineItem } from '@/shared/types/common'

interface BOLLChartProps {
  kline: StockTrendKlineItem[]
  onChartReady?: (instance: ECharts | null) => void
}

function calculateBOLL(kline: StockTrendKlineItem[], n: number = 20, k: number = 2) {
  const closes = kline.map((item) => item.close || 0)

  const mid: (number | null)[] = []
  const upper: (number | null)[] = []
  const lower: (number | null)[] = []

  for (let i = 0; i < kline.length; i++) {
    if (i < n - 1) {
      mid.push(null)
      upper.push(null)
      lower.push(null)
      continue
    }

    const sum = closes.slice(i - n + 1, i + 1).reduce((a, b) => a + b, 0)
    const ma = sum / n
    mid.push(Number(ma.toFixed(2)))

    const squaredDiffs = closes.slice(i - n + 1, i + 1).map((c) => Math.pow(c - ma, 2))
    const variance = squaredDiffs.reduce((a, b) => a + b, 0) / n
    const stdDev = Math.sqrt(variance)

    upper.push(Number((ma + k * stdDev).toFixed(2)))
    lower.push(Number((ma - k * stdDev).toFixed(2)))
  }

  return { mid, upper, lower }
}

function BOLLChart({ kline, onChartReady }: BOLLChartProps) {
  const { mid, upper, lower } = calculateBOLL(kline)
  const dates = kline.map((item) => formatDate(item.trade_date) || '')
  const closes = kline.map((item) => item.close)

  const option = {
    animation: false,
    legend: {
      data: ['BOLL上轨', 'BOLL中轨', 'BOLL下轨', '收盘价'],
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
        name: 'BOLL上轨',
        type: 'line',
        data: upper,
        lineStyle: { width: 1 },
        itemStyle: { color: '#ef5350' },
        symbol: 'none',
      },
      {
        name: 'BOLL中轨',
        type: 'line',
        data: mid,
        lineStyle: { width: 1 },
        itemStyle: { color: '#4a90d9' },
        symbol: 'none',
      },
      {
        name: 'BOLL下轨',
        type: 'line',
        data: lower,
        lineStyle: { width: 1 },
        itemStyle: { color: '#26a69a' },
        symbol: 'none',
      },
      {
        name: '收盘价',
        type: 'line',
        data: closes,
        lineStyle: { width: 1 },
        itemStyle: { color: '#999' },
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

export default BOLLChart