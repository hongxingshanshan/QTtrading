import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Spin, Button } from 'antd'
import { ArrowLeftOutlined } from '@ant-design/icons'
import * as echarts from 'echarts'
import { stockApi } from '@/shared/api/stock'
import TrendChart from './components/TrendChart'
import MACDChart from './components/MACDChart'
import KDJChart from './components/KDJChart'
import BOLLChart from './components/BOLLChart'
import RSIChart from './components/RSIChart'
import ToolBar from './components/ToolBar'
import type { StockTrendResponse } from '@/shared/types/common'

function StockTrend() {
  const { code } = useParams<{ code: string }>()
  const navigate = useNavigate()
  const chartInstancesRef = useRef<echarts.ECharts[]>([])
  const connectedRef = useRef(false)

  const [period, setPeriod] = useState<'daily' | 'weekly' | 'monthly'>('daily')
  const [adjType, setAdjType] = useState<'qfq' | 'hfq' | 'none'>('qfq')
  const [indicators, setIndicators] = useState<string[]>(['macd', 'kdj', 'rsi', 'boll'])
  const [visibleMas, setVisibleMas] = useState<string[]>(['ma5', 'ma10', 'ma20', 'ma30', 'ma60', 'ma90', 'ma125', 'ma250'])

  const { data, isLoading, isFetching, error } = useQuery({
    queryKey: ['stock-trend', code, period, adjType],
    queryFn: async () => {
      const response = await stockApi.getTrendData(code || '', {
        period,
        adj_type: adjType,
      })
      return response as StockTrendResponse
    },
    enabled: !!code,
    staleTime: 60000,
    placeholderData: (previousData) => previousData,
  })

  // 注册图表实例
  const registerChart = useCallback((instance: echarts.ECharts | null) => {
    if (instance && !chartInstancesRef.current.includes(instance)) {
      chartInstancesRef.current.push(instance)
      // 当有新实例注册时，重新连接所有图表
      if (chartInstancesRef.current.length > 1) {
        echarts.connect(chartInstancesRef.current)
        connectedRef.current = true
      }
    }
  }, [])

  // 清理连接
  useEffect(() => {
    return () => {
      if (connectedRef.current) {
        echarts.disconnect('stock-trend-group')
      }
      chartInstancesRef.current = []
    }
  }, [])

  // 首次加载显示全屏 loading
  if (isLoading && !data) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spin size="large" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-64 text-red-500">
        加载失败，请检查股票代码是否正确
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="bg-white border-b px-4 py-2">
        <Button
          type="text"
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/stock')}
        >
          返回股票列表
        </Button>
      </div>
      <ToolBar
        onPeriodChange={(p) => setPeriod(p as 'daily' | 'weekly' | 'monthly')}
        onAdjTypeChange={(a) => setAdjType(a as 'qfq' | 'hfq' | 'none')}
        onIndicatorChange={setIndicators}
        onMaChange={setVisibleMas}
      />
      <div className="p-4">
        <div className="bg-white rounded-lg shadow relative">
          {isFetching && (
            <div className="absolute top-2 right-2 z-10">
              <Spin size="small" />
            </div>
          )}
          <TrendChart data={data || null} visibleMas={visibleMas} onChartReady={registerChart} />
          {data?.kline && indicators.includes('macd') && (
            <MACDChart kline={data.kline} onChartReady={registerChart} />
          )}
          {data?.kline && indicators.includes('kdj') && (
            <KDJChart kline={data.kline} onChartReady={registerChart} />
          )}
          {data?.kline && indicators.includes('rsi') && (
            <RSIChart kline={data.kline} onChartReady={registerChart} />
          )}
          {data?.kline && indicators.includes('boll') && (
            <BOLLChart kline={data.kline} onChartReady={registerChart} />
          )}
        </div>
      </div>
    </div>
  )
}

export default StockTrend