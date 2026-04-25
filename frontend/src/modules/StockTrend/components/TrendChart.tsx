import ReactECharts from 'echarts-for-react'
import type { ECharts } from 'echarts'
import type { EChartsOption } from 'echarts'
import type { StockTrendResponse } from '@/shared/types/common'

interface TrendChartProps {
  data: StockTrendResponse | null
  visibleMas?: string[]
  onChartReady?: (instance: ECharts | null) => void
}

function TrendChart({ data, visibleMas = ['ma5', 'ma10', 'ma20', 'ma30', 'ma60', 'ma90', 'ma125', 'ma250'], onChartReady }: TrendChartProps) {
  if (!data || !data.kline.length) {
    return <div className="text-center text-gray-400 py-20">暂无数据</div>
  }

  const { kline, ma, latest } = data
  const dates = kline.map((item) => item.trade_date || '')

  // K线数据 [open, close, low, high]
  const klineData = kline.map((item) => [
    item.open,
    item.close,
    item.low,
    item.high,
  ])

  // 成交量数据
  const volumeData = kline.map((item, index) => ({
    value: item.vol,
    itemStyle: {
      color: item.close && item.open && item.close >= item.open ? '#ef5350' : '#26a69a',
    },
  }))

  // 根据可见性过滤均线
  const legendData = ['K线']
  if (visibleMas.includes('ma5')) legendData.push('MA5')
  if (visibleMas.includes('ma10')) legendData.push('MA10')
  if (visibleMas.includes('ma20')) legendData.push('MA20')
  if (visibleMas.includes('ma30')) legendData.push('MA30')
  if (visibleMas.includes('ma60')) legendData.push('MA60')
  if (visibleMas.includes('ma90')) legendData.push('MA90')
  if (visibleMas.includes('ma125')) legendData.push('MA125')
  if (visibleMas.includes('ma250')) legendData.push('MA250')

  const option = {
    animation: false,
    legend: {
      data: legendData,
      top: 10,
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        link: [{ xAxisIndex: 'all' }],
      },
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#ccc',
      borderWidth: 1,
      textStyle: {
        color: '#333',
      },
      confine: true,
      formatter: function (params: any) {
        const dataIndex = params[0].dataIndex
        const item = kline[dataIndex]
        const lastItem = kline[kline.length - 1]

        // 计算至今涨跌幅（以悬停日前收盘价为基准，与同花顺一致）
        const preClose = item.pre_close || 0
        const lastClose = lastItem.close || 0
        const toNowPctChg = preClose > 0 ? ((lastClose - preClose) / preClose) * 100 : 0

        // 根据涨跌确定颜色
        const getColor = (value: number) => {
          if (value > 0) return '#ef5350' // 红色 - 涨
          if (value < 0) return '#26a69a' // 绿色 - 跌
          return '#999999' // 灰色 - 持平
        }

        const toNowColor = getColor(toNowPctChg)
        const pctChgColor = getColor(item.pct_chg || 0)

        const maValues = [
          visibleMas.includes('ma5') && ma.ma5[dataIndex] ? `MA5: ${ma.ma5[dataIndex]}` : '',
          visibleMas.includes('ma10') && ma.ma10[dataIndex] ? `MA10: ${ma.ma10[dataIndex]}` : '',
          visibleMas.includes('ma20') && ma.ma20[dataIndex] ? `MA20: ${ma.ma20[dataIndex]}` : '',
          visibleMas.includes('ma30') && ma.ma30[dataIndex] ? `MA30: ${ma.ma30[dataIndex]}` : '',
          visibleMas.includes('ma60') && ma.ma60[dataIndex] ? `MA60: ${ma.ma60[dataIndex]}` : '',
          visibleMas.includes('ma90') && ma.ma90[dataIndex] ? `MA90: ${ma.ma90[dataIndex]}` : '',
          visibleMas.includes('ma125') && ma.ma125[dataIndex] ? `MA125: ${ma.ma125[dataIndex]}` : '',
          visibleMas.includes('ma250') && ma.ma250[dataIndex] ? `MA250: ${ma.ma250[dataIndex]}` : '',
        ].filter(Boolean)

        return `
          <div style="padding: 8px;">
            <div style="font-weight: bold; margin-bottom: 8px;">${item.trade_date}</div>
            <div>开盘: ${item.open?.toFixed(2)}</div>
            <div>收盘: <span style="color: ${pctChgColor}">${item.close?.toFixed(2)}</span></div>
            <div>最高: ${item.high?.toFixed(2)}</div>
            <div>最低: ${item.low?.toFixed(2)}</div>
            <div>涨跌幅: <span style="color: ${pctChgColor}">${item.pct_chg?.toFixed(2)}%</span></div>
            <div>成交量: ${item.vol ? (item.vol / 10000).toFixed(2) + '万手' : '-'}</div>
            <div style="margin-top: 8px; border-top: 1px solid #eee; padding-top: 8px;">
              <div style="font-weight: bold;">
                ${item.trade_date} 至今涨幅 <span style="color: ${toNowColor}">${toNowPctChg >= 0 ? '+' : ''}${toNowPctChg.toFixed(2)}%</span>
              </div>
            </div>
            ${maValues.length > 0 ? `
            <div style="margin-top: 8px; border-top: 1px solid #eee; padding-top: 8px;">
              ${maValues.join('<br/>')}
            </div>
            ` : ''}
          </div>
        `
      },
    },
    axisPointer: {
      link: [{ xAxisIndex: 'all' }],
      label: {
        backgroundColor: '#777',
      },
    },
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 70,
        end: 100,
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        bottom: 10,
        start: 70,
        end: 100,
      },
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        gridIndex: 0,
        axisLabel: { show: false },
        axisTick: { show: false },
        axisPointer: {
          show: true,
          label: {
            show: true,
          },
        },
      },
      {
        type: 'category',
        data: dates,
        gridIndex: 1,
        axisLabel: { color: '#666' },
        axisPointer: {
          show: true,
          label: {
            show: true,
          },
        },
      },
    ],
    yAxis: [
      {
        scale: true,
        gridIndex: 0,
        splitLine: {
          lineStyle: {
            color: '#e0e0e0',
            type: 'dashed',
          },
        },
        axisLabel: { color: '#666' },
      },
      {
        scale: true,
        gridIndex: 1,
        splitLine: { show: false },
        axisLabel: { color: '#666' },
      },
    ],
    grid: [
      {
        left: '10%',
        right: '8%',
        top: '10%',
        height: '55%',
      },
      {
        left: '10%',
        right: '8%',
        top: '72%',
        height: '18%',
      },
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: klineData,
        itemStyle: {
          color: '#ef5350',       // 阳线填充色（上涨）
          color0: '#26a69a',      // 阴线填充色（下跌）
          borderColor: '#ef5350', // 阳线边框
          borderColor0: '#26a69a', // 阴线边框
        },
      },
      ...(visibleMas.includes('ma5') ? [{
        name: 'MA5',
        type: 'line' as const,
        data: ma.ma5,
        smooth: true,
        lineStyle: { width: 1 },
        itemStyle: { color: '#f5a623' },
        symbol: 'none',
      }] : []),
      ...(visibleMas.includes('ma10') ? [{
        name: 'MA10',
        type: 'line' as const,
        data: ma.ma10,
        smooth: true,
        lineStyle: { width: 1 },
        itemStyle: { color: '#7ed321' },
        symbol: 'none',
      }] : []),
      ...(visibleMas.includes('ma20') ? [{
        name: 'MA20',
        type: 'line' as const,
        data: ma.ma20,
        smooth: true,
        lineStyle: { width: 1 },
        itemStyle: { color: '#4a90d9' },
        symbol: 'none',
      }] : []),
      ...(visibleMas.includes('ma30') ? [{
        name: 'MA30',
        type: 'line' as const,
        data: ma.ma30,
        smooth: true,
        lineStyle: { width: 1 },
        itemStyle: { color: '#e8b04b' },
        symbol: 'none',
      }] : []),
      ...(visibleMas.includes('ma60') ? [{
        name: 'MA60',
        type: 'line' as const,
        data: ma.ma60,
        smooth: true,
        lineStyle: { width: 1 },
        itemStyle: { color: '#9013fe' },
        symbol: 'none',
      }] : []),
      ...(visibleMas.includes('ma90') ? [{
        name: 'MA90',
        type: 'line' as const,
        data: ma.ma90,
        smooth: true,
        lineStyle: { width: 1 },
        itemStyle: { color: '#ff6b6b' },
        symbol: 'none',
      }] : []),
      ...(visibleMas.includes('ma125') ? [{
        name: 'MA125',
        type: 'line' as const,
        data: ma.ma125,
        smooth: true,
        lineStyle: { width: 1 },
        itemStyle: { color: '#4ecdc4' },
        symbol: 'none',
      }] : []),
      ...(visibleMas.includes('ma250') ? [{
        name: 'MA250',
        type: 'line' as const,
        data: ma.ma250,
        smooth: true,
        lineStyle: { width: 1 },
        itemStyle: { color: '#45b7d1' },
        symbol: 'none',
      }] : []),
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumeData,
        barWidth: '60%',
      },
    ],
  }

  return (
    <div className="w-full">
      {/* 顶部信息栏 */}
      <div className="bg-gray-50 p-4 rounded-t-lg border-b">
        <div className="flex items-center gap-4 mb-2">
          <span className="text-xl font-bold">{data.basic.name}</span>
          <span className="text-gray-500">{data.basic.ts_code}</span>
          <span className="text-gray-500">{data.basic.industry}</span>
        </div>
        <div className="flex items-center gap-6">
          <span className={`text-2xl font-bold ${latest.pct_chg && latest.pct_chg >= 0 ? 'text-red-500' : 'text-green-500'}`}>
            {latest.close?.toFixed(2)}
          </span>
          <span className={latest.pct_chg && latest.pct_chg >= 0 ? 'text-red-500' : 'text-green-500'}>
            {latest.price_change && latest.price_change >= 0 ? '+' : ''}{latest.price_change?.toFixed(2)}
            ({latest.pct_chg && latest.pct_chg >= 0 ? '+' : ''}{latest.pct_chg?.toFixed(2)}%)
          </span>
        </div>
        <div className="flex gap-6 mt-2 text-sm text-gray-600">
          <span>今开: {latest.open?.toFixed(2)}</span>
          <span>最高: {latest.high?.toFixed(2)}</span>
          <span>最低: {latest.low?.toFixed(2)}</span>
          <span>昨收: {latest.pre_close?.toFixed(2)}</span>
          <span>成交量: {latest.vol ? (latest.vol / 10000).toFixed(2) + '万手' : '-'}</span>
          <span>成交额: {latest.amount ? (latest.amount / 10000).toFixed(2) + '万' : '-'}</span>
        </div>
      </div>
      {/* 图表区域 */}
      <ReactECharts
        option={option}
        style={{ height: 500 }}
        opts={{ renderer: 'canvas' }}
        notMerge={true}
        lazyUpdate={true}
        onChartReady={(instance) => onChartReady?.(instance)}
      />
    </div>
  )
}

export default TrendChart
