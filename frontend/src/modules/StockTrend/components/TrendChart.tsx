import ReactECharts from 'echarts-for-react'
import type { DailyData } from '@/shared/types/common'

interface TrendChartProps {
  data: DailyData[]
}

function TrendChart({ data }: TrendChartProps) {
  const option = {
    title: { text: '股票走势' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['收盘价', '成交量'] },
    xAxis: {
      type: 'category',
      data: data.map((item) => item.trade_date),
    },
    yAxis: [
      { type: 'value', name: '价格' },
      { type: 'value', name: '成交量' },
    ],
    series: [
      {
        name: '收盘价',
        type: 'line',
        data: data.map((item) => item.close),
      },
      {
        name: '成交量',
        type: 'bar',
        yAxisIndex: 1,
        data: data.map((item) => item.vol),
      },
    ],
  }

  return <ReactECharts option={option} style={{ height: 400 }} />
}

export default TrendChart
