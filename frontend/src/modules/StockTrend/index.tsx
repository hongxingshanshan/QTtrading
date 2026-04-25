import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Card, Spin } from 'antd'
import { stockApi } from '@/shared/api/stock'
import TrendChart from './components/TrendChart'

function StockTrend() {
  const { code } = useParams<{ code: string }>()

  const { data, isLoading } = useQuery({
    queryKey: ['stock-trend', code],
    queryFn: () => stockApi.getDailyData({ ts_code: code || '' }),
    enabled: !!code,
  })

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spin size="large" />
      </div>
    )
  }

  return (
    <Card title={`股票走势 - ${code}`}>
      <TrendChart data={data?.data || []} />
    </Card>
  )
}

export default StockTrend
