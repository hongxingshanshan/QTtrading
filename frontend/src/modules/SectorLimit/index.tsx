import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Input, Button, Table, Space, Card } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { sectorApi } from '@/shared/api/sector'
import type { DailySectorLimitData } from '@/shared/types/common'

function SectorLimit() {
  const [sectorName, setSectorName] = useState('')
  const [sectorType, setSectorType] = useState('')

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['sector-limit', sectorName, sectorType],
    queryFn: () =>
      sectorApi.getDailySectorLimitData({
        sector_name: sectorName,
        sector_type: sectorType,
      }),
  })

  const columns: ColumnsType<DailySectorLimitData> = [
    { title: '交易日期', dataIndex: 'trade_date', key: 'trade_date', width: 120 },
    { title: '板块代码', dataIndex: 'sector_code', key: 'sector_code', width: 120 },
    { title: '板块名称', dataIndex: 'sector_name', key: 'sector_name', width: 150 },
    { title: '板块类型', dataIndex: 'sector_type', key: 'sector_type', width: 100 },
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
  ]

  const handleSearch = () => {
    refetch()
  }

  const handleReset = () => {
    setSectorName('')
    setSectorType('')
  }

  return (
    <Card title="板块行情">
      <Space className="mb-4">
        <Input
          placeholder="板块名称"
          value={sectorName}
          onChange={(e) => setSectorName(e.target.value)}
          style={{ width: 150 }}
        />
        <Input
          placeholder="板块类型"
          value={sectorType}
          onChange={(e) => setSectorType(e.target.value)}
          style={{ width: 150 }}
        />
        <Button type="primary" onClick={handleSearch}>
          查询
        </Button>
        <Button onClick={handleReset}>重置</Button>
      </Space>

      <Table
        columns={columns}
        dataSource={data?.data || []}
        loading={isLoading}
        rowKey={(record) => `${record.trade_date}-${record.sector_code}`}
        pagination={{ pageSize: 20 }}
      />
    </Card>
  )
}

export default SectorLimit
