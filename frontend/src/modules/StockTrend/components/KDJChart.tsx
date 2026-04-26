import ReactECharts from 'echarts-for-react'
import type { ECharts } from 'echarts'
import { formatDate } from '@/shared/utils/format'
import type { StockTrendKlineItem } from '@/shared/types/common'

interface KDJChartProps {
  kline: StockTrendKlineItem[]
  onChartReady?: (instance: ECharts | null) => void
}

function calculateKDJ(kline: StockTrendKlineItem[], n: number = 9) {
  const closes = kline.map((item) => item.close || 0)
  const highs = kline.map((item) => item.high || 0)
  const lows = kline.map((item) => item.low || 0)

  const k: number[] = []
  const d: number[] = []
  const j: number[] = []

  let prevK = 50
  let prevD = 50

  for (let i = 0; i < kline.length; i++) {
    if (i < n - 1) {
      k.push(50)
      d.push(50)
      j.push(50)
      continue
    }

    const highN = Math.max(...highs.slice(i - n + 1, i + 1))
    const lowN = Math.min(...lows.slice(i - n + 1, i + 1))

    const rsv = highN === lowN ? 50 : ((closes[i] - lowN) / (highN - lowN)) * 100

    const currentK = (2 / 3) * prevK + (1 / 3) * rsv
    prevK = currentK

    const currentD = (2 / 3) * prevD + (1 / 3) * currentK
    prevD = currentD

    const currentJ = 3 * currentK - 2 * currentD

    k.push(Number(currentK.toFixed(2)))
    d.push(Number(currentD.toFixed(2)))
    j.push(Number(currentJ.toFixed(2)))
  }

  return { k, d, j }
}

function KDJChart({ kline, onChartReady }: KDJChartProps) {
  const { k, d, j } = calculateKDJ(kline)
  const dates = kline.map((item) => formatDate(item.trade_date) || '')

  const option = {
    animation: false,
    legend: {
      data: ['K', 'D', 'J'],
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
        start: 70,
        end: 100,
      },
      {
        type: 'slider',
        show: false,
        xAxisIndex: 0,
        start: 70,
        end: 100,
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
        name: 'K',
        type: 'line',
        data: k,
        lineStyle: { width: 1 },
        itemStyle: { color: '#f5a623' },
        symbol: 'none',
      },
      {
        name: 'D',
        type: 'line',
        data: d,
        lineStyle: { width: 1 },
        itemStyle: { color: '#4a90d9' },
        symbol: 'none',
      },
      {
        name: 'J',
        type: 'line',
        data: j,
        lineStyle: { width: 1 },
        itemStyle: { color: '#ef5350' },
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

export default KDJChart