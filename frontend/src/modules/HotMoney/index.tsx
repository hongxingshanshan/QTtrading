import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Input, Button, Table, Space, DatePicker } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { hotmoneyApi } from '@/shared/api/hotmoney'
import { usePagination } from '@/shared/hooks/usePagination'
import { formatAmount } from '@/shared/utils/format'
import PaginationTable from '@/shared/components/PaginationTable'
import type { DailyHotMoneyTradeItem } from './types'

const { RangePicker } = DatePicker

function HotMoney() {
  const [hmName, setHmName] = useState('')
  const [tsName, setTsName] = useState('')
  const [tsCode, setTsCode] = useState('')
  const [tradeDate, setTradeDate] = useState('')
  const { page, pageSize, onChange, reset: resetPagination } = usePagination()

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['hotmoney-trade', hmName, tsName, tsCode, tradeDate, page, pageSize],
    queryFn: () =>
      hotmoneyApi.getDailyHotMoneyTrade({
        hmName,
        tsName,
        tsCode,
        tradeDate,
        page,
        pageSize,
      }),
  })

  const columns: ColumnsType<DailyHotMoneyTradeItem> = [
    { title: '交易日期', dataIndex: 'trade_date', key: 'trade_date', width: 120 },
    { title: '股票代码', dataIndex: 'ts_code', key: 'ts_code', width: 120 },
    { title: '股票名称', dataIndex: 'ts_name', key: 'ts_name', width: 120 },
    { title: '游资名称', dataIndex: 'hm_name', key: 'hm_name', width: 150 },
    {
      title: '买入金额',
      dataIndex: 'buy_amount',
      key: 'buy_amount',
      width: 120,
      render: formatAmount,
    },
    {
      title: '卖出金额',
      dataIndex: 'sell_amount',
      key: 'sell_amount',
      width: 120,
      render: formatAmount,
    },
    {
      title: '净买入',
      dataIndex: 'net_amount',
      key: 'net_amount',
      width: 120,
      render: formatAmount,
    },
  ]

  const handleSearch = () => {
    resetPagination()
    refetch()
  }

  const handleReset = () => {
    setHmName('')
    setTsName('')
    setTsCode('')
    setTradeDate('')
    resetPagination()
  }

  return (
    <div>
      <Space className="mb-4" wrap>
        <Input
          placeholder="游资名称"
          value={hmName}
          onChange={(e) => setHmName(e.target.value)}
          style={{ width: 150 }}
        />
        <Input
          placeholder="股票代码"
          value={tsCode}
          onChange={(e) => setTsCode(e.target.value)}
          style={{ width: 150 }}
        />
        <Input
          placeholder="股票名称"
          value={tsName}
          onChange={(e) => setTsName(e.target.value)}
          style={{ width: 150 }}
        />
        <Input
          placeholder="交易日期"
          value={tradeDate}
          onChange={(e) => setTradeDate(e.target.value)}
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
        rowKey={(record) => `${record.trade_date}-${record.ts_code}-${record.hm_name}`}
        total={data?.total || 0}
        current={page}
        pageSize={pageSize}
        onChange={onChange}
      />
    </div>
  )
}

export default HotMoney