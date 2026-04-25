import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Input, Button, Table, Space } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { hotmoneyApi } from '@/shared/api/hotmoney'
import { usePagination } from '@/shared/hooks/usePagination'
import PaginationTable from '@/shared/components/PaginationTable'
import type { HotMoneyInfoItem } from './types'

function HotMoneyInfo() {
  const [name, setName] = useState('')
  const { page, pageSize, onChange, reset: resetPagination } = usePagination()

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['hotmoney-info', name, page, pageSize],
    queryFn: () => hotmoneyApi.getHotMoneyList({ name, page, pageSize }),
  })

  const columns: ColumnsType<HotMoneyInfoItem> = [
    { title: '名称', dataIndex: 'name', key: 'name', width: 150 },
    {
      title: '描述',
      dataIndex: 'desc',
      key: 'desc',
      ellipsis: true,
      render: (text) => text?.slice(0, 100) + (text?.length > 100 ? '...' : ''),
    },
    {
      title: '机构',
      dataIndex: 'orgs',
      key: 'orgs',
      ellipsis: true,
      render: (text) => text?.slice(0, 100) + (text?.length > 100 ? '...' : ''),
    },
  ]

  const handleSearch = () => {
    resetPagination()
    refetch()
  }

  const handleReset = () => {
    setName('')
    resetPagination()
  }

  return (
    <div>
      <Space className="mb-4">
        <Input
          placeholder="游资名称"
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={{ width: 200 }}
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
        rowKey="name"
        total={data?.total || 0}
        current={page}
        pageSize={pageSize}
        onChange={onChange}
      />
    </div>
  )
}

export default HotMoneyInfo