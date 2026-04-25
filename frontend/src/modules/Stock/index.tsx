import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Input, Button, Table, Space, Select } from 'antd'
import { useNavigate } from 'react-router-dom'
import type { ColumnsType } from 'antd/es/table'
import { stockApi } from '@/shared/api/stock'
import { usePagination } from '@/shared/hooks/usePagination'
import PaginationTable from '@/shared/components/PaginationTable'
import type { StockBasicInfo } from '@/shared/types/common'

function Stock() {
  const navigate = useNavigate()
  const [symbol, setSymbol] = useState('')
  const [name, setName] = useState('')
  const [industry, setIndustry] = useState('')
  const { page, pageSize, onChange, reset: resetPagination } = usePagination()

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['stock-list', symbol, name, industry, page, pageSize],
    queryFn: () =>
      stockApi.getStockList({
        symbol,
        name,
        industry,
        page,
        pageSize,
      }),
  })

  const columns: ColumnsType<StockBasicInfo> = [
    { title: '股票代码', dataIndex: 'ts_code', key: 'ts_code', width: 120 },
    { title: '股票名称', dataIndex: 'name', key: 'name', width: 120 },
    { title: '行业', dataIndex: 'industry', key: 'industry', width: 100 },
    { title: '上市日期', dataIndex: 'list_date', key: 'list_date', width: 120 },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_, record) => (
        <Button type="link" onClick={() => navigate(`/stock/trend/${record.ts_code}`)}>
          走势
        </Button>
      ),
    },
  ]

  const handleSearch = () => {
    resetPagination()
    refetch()
  }

  const handleReset = () => {
    setSymbol('')
    setName('')
    setIndustry('')
    resetPagination()
  }

  return (
    <div>
      <Space className="mb-4" wrap>
        <Input
          placeholder="股票代码"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          style={{ width: 150 }}
        />
        <Input
          placeholder="股票名称"
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={{ width: 150 }}
        />
        <Input
          placeholder="行业"
          value={industry}
          onChange={(e) => setIndustry(e.target.value)}
          style={{ width: 150 }}
        />
        <Button type="primary" onClick={handleSearch}>
          查询
        </Button>
        <Button onClick={handleReset}>重置</Button>
      </Space>

      <PaginationTable
        columns={columns}
        dataSource={data?.data || []}
        loading={isLoading}
        rowKey="ts_code"
        total={data?.total || 0}
        current={page}
        pageSize={pageSize}
        onChange={onChange}
      />
    </div>
  )
}

export default Stock