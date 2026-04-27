import { useQuery } from '@tanstack/react-query'
import { Table, Card } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { limitApi } from '@/shared/api/limit'
import { renderDate } from '@/shared/utils/format'
import StockLink from '@/shared/components/StockLink'
import type { DailyLimitData } from '@/shared/types/common'

function DailyLimit() {
  const { data, isLoading } = useQuery({
    queryKey: ['daily-limit'],
    queryFn: () => limitApi.getDailyLimitData(),
  })

  const columns: ColumnsType<DailyLimitData> = [
    { title: '交易日期', dataIndex: 'trade_date', key: 'trade_date', width: 120, render: renderDate },
    {
      title: '股票代码',
      dataIndex: 'ts_code',
      key: 'ts_code',
      width: 120,
      render: (code: string) => <StockLink code={code}>{code}</StockLink>,
    },
    {
      title: '股票名称',
      dataIndex: 'name',
      key: 'name',
      width: 120,
      render: (name: string, record) => <StockLink code={record.ts_code}>{name}</StockLink>,
    },
    {
      title: '收盘价',
      dataIndex: 'close',
      key: 'close',
      width: 100,
      render: (v) => v?.toFixed(2),
    },
    {
      title: '涨跌幅',
      dataIndex: 'pct_chg',
      key: 'pct_chg',
      width: 100,
      render: (v) => (
        <span style={{ color: v > 0 ? '#f5222d' : '#52c41a' }}>
          {v?.toFixed(2)}%
        </span>
      ),
    },
    {
      title: '涨停价',
      dataIndex: 'limit_price',
      key: 'limit_price',
      width: 100,
      render: (v) => v?.toFixed(2),
    },
  ]

  return (
    <Card title="涨跌停数据">
      <Table
        columns={columns}
        dataSource={data?.data || []}
        loading={isLoading}
        rowKey={(record) => `${record.trade_date}-${record.ts_code}`}
        pagination={{ pageSize: 20 }}
      />
    </Card>
  )
}

export default DailyLimit
