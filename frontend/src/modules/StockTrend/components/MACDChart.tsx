import ReactECharts from 'echarts-for-react'
import type { ECharts } from 'echarts'
import { formatDate } from '@/shared/utils/format'
import type { StockTrendKlineItem } from '@/shared/types/common'

interface MACDChartProps {
  kline: StockTrendKlineItem[]
  onChartReady?: (instance: ECharts | null) => void
}

function calculateMACD(kline: StockTrendKlineItem[]) {
  const closes = kline.map((item) => item.close || 0)

  const ema12 = calculateEMA(closes, 12)
  const ema26 = calculateEMA(closes, 26)

  const dif: (number | null)[] = []
  for (let i = 0; i < closes.length; i++) {
    if (ema12[i] === null || ema26[i] === null) {
      dif.push(null)
    } else {
      dif.push(Number((ema12[i]! - ema26[i]!).toFixed(4)))
    }
  }

  const dea = calculateEMA(dif.filter((v): v is number => v !== null), 9)

  const deaFull: (number | null)[] = []
  let deaIndex = 0
  for (let i = 0; i < dif.length; i++) {
    if (dif[i] === null) {
      deaFull.push(null)
    } else {
      deaFull.push(dea[deaIndex] ?? null)
      deaIndex++
    }
  }

  const macd: (number | null)[] = []
  for (let i = 0; i < dif.length; i++) {
    if (dif[i] === null || deaFull[i] === null) {
      macd.push(null)
    } else {
      macd.push(Number(((dif[i]! - deaFull[i]!) * 2).toFixed(4)))
    }
  }

  return {
    dif: dif.map((v) => v ?? 0),
    dea: deaFull.map((v) => v ?? 0),
    macd: macd.map((v) => v ?? 0),
  }
}

function calculateEMA(data: number[], period: number): (number | null)[] {
  const result: (number | null)[] = []
  const multiplier = 2 / (period + 1)

  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(null)
    } else if (i === period - 1) {
      const sum = data.slice(0, period).reduce((a, b) => a + b, 0)
      result.push(sum / period)
    } else {
      const prevEma = result[i - 1]!
      result.push((data[i] - prevEma) * multiplier + prevEma)
    }
  }

  return result
}

function MACDChart({ kline, onChartReady }: MACDChartProps) {
  const { dif, dea, macd } = calculateMACD(kline)
  const dates = kline.map((item) => formatDate(item.trade_date) || '')

  const macdBarData = macd.map((value) => ({
    value,
    itemStyle: {
      color: value >= 0 ? '#ef5350' : '#26a69a',
    },
  }))

  const option = {
    animation: false,
    legend: {
      data: ['DIF', 'DEA', 'MACD'],
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
        name: 'DIF',
        type: 'line',
        data: dif,
        lineStyle: { width: 1 },
        itemStyle: { color: '#f5a623' },
        symbol: 'none',
      },
      {
        name: 'DEA',
        type: 'line',
        data: dea,
        lineStyle: { width: 1 },
        itemStyle: { color: '#4a90d9' },
        symbol: 'none',
      },
      {
        name: 'MACD',
        type: 'bar',
        data: macdBarData,
        barWidth: '40%',
        itemStyle: { color: '#9013fe' },
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

export default MACDChart