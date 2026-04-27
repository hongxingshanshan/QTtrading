import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Card,
  Button,
  Space,
  Select,
  Radio,
  InputNumber,
  Table,
  message,
  Row,
  Col,
  Statistic
} from 'antd'
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons'
import ConditionBuilder from './components/ConditionBuilder'
import TemplateSelector from './components/TemplateSelector'
import { stockScreenApi } from '@/shared/api/stockScreen'
import type { ScreenCondition, ScreenStock } from './types'
import StockLink from '@/shared/components/StockLink'

function StockScreen() {
  const [tradeDate, setTradeDate] = useState<string>('')
  const [conditions, setConditions] = useState<ScreenCondition[]>([])
  const [logic, setLogic] = useState<'AND' | 'OR'>('AND')
  const [limit, setLimit] = useState(100)
  const [availableDates, setAvailableDates] = useState<string[]>([])

  // 加载可用日期
  useEffect(() => {
    loadDates()
  }, [])

  const loadDates = async () => {
    try {
      const res = await stockScreenApi.getAvailableDates(30)
      if (res.success && res.data.length > 0) {
        setAvailableDates(res.data)
        setTradeDate(res.data[0])
      }
    } catch (error) {
      console.error('加载日期失败:', error)
    }
  }

  // 执行选股
  const { data, isLoading, refetch, isFetching } = useQuery({
    queryKey: ['stock-screen', tradeDate, conditions, logic, limit],
    queryFn: async () => {
      if (!tradeDate || conditions.length === 0) return null
      const res = await stockScreenApi.screen({
        trade_date: tradeDate,
        conditions,
        logic,
        limit,
        offset: 0,
        order_by: 'pct_change',
        order_desc: true
      })
      return res.success ? res.data : null
    },
    enabled: false // 手动触发
  })

  const handleSearch = () => {
    if (!tradeDate) {
      message.warning('请选择交易日期')
      return
    }
    if (conditions.length === 0) {
      message.warning('请添加至少一个筛选条件')
      return
    }
    refetch()
  }

  const handleTemplateSelect = (templateConditions: ScreenCondition[]) => {
    setConditions(templateConditions)
  }

  const handleReset = () => {
    setConditions([])
    setLogic('AND')
    setLimit(100)
  }

  // 格式化日期显示
  const formatDateLabel = (date: string) => {
    if (!date || date.length !== 8) return date
    return `${date.slice(0, 4)}-${date.slice(4, 6)}-${date.slice(6, 8)}`
  }

  // 表格列定义
  const columns = [
    {
      title: '代码',
      dataIndex: 'ts_code',
      key: 'ts_code',
      width: 120,
      render: (code: string) => <StockLink code={code}>{code}</StockLink>
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      width: 100,
      render: (name: string, record: ScreenStock) =>
        <StockLink code={record.ts_code}>{name}</StockLink>
    },
    {
      title: '行业',
      dataIndex: 'industry',
      key: 'industry',
      width: 80
    },
    {
      title: '地域',
      dataIndex: 'area',
      key: 'area',
      width: 70
    },
    {
      title: '收盘价',
      dataIndex: 'close',
      key: 'close',
      width: 80,
      render: (v: number) => v?.toFixed(2)
    },
    {
      title: '涨跌幅',
      dataIndex: 'pct_change',
      key: 'pct_change',
      width: 80,
      render: (v: number) => (
        <span style={{ color: v > 0 ? '#f5222d' : v < 0 ? '#52c41a' : '#666' }}>
          {v?.toFixed(2)}%
        </span>
      )
    },
    {
      title: 'RSI6',
      key: 'rsi6',
      width: 70,
      render: (_: unknown, record: ScreenStock) => record.indicators?.rsi6?.toFixed(1)
    },
    {
      title: 'J值',
      key: 'j_value',
      width: 70,
      render: (_: unknown, record: ScreenStock) => record.indicators?.j_value?.toFixed(1)
    },
    {
      title: 'MACD',
      key: 'macd_hist',
      width: 70,
      render: (_: unknown, record: ScreenStock) => {
        const v = record.indicators?.macd_hist
        if (v === undefined || v === null) return '-'
        return (
          <span style={{ color: v > 0 ? '#f5222d' : '#52c41a' }}>
            {v.toFixed(3)}
          </span>
        )
      }
    },
    {
      title: '量比',
      key: 'vol_ratio',
      width: 70,
      render: (_: unknown, record: ScreenStock) => record.indicators?.vol_ratio?.toFixed(2)
    }
  ]

  return (
    <div className="space-y-4">
      {/* 操作栏 */}
      <Card size="small">
        <Row gutter={16} align="middle">
          <Col>
            <Space>
              <span>交易日期:</span>
              <Select
                style={{ width: 150 }}
                value={tradeDate}
                onChange={setTradeDate}
                options={availableDates.map(d => ({
                  value: d,
                  label: formatDateLabel(d)
                }))}
              />
            </Space>
          </Col>
          <Col>
            <Space>
              <span>逻辑组合:</span>
              <Radio.Group value={logic} onChange={(e) => setLogic(e.target.value)}>
                <Radio.Button value="AND">且(AND)</Radio.Button>
                <Radio.Button value="OR">或(OR)</Radio.Button>
              </Radio.Group>
            </Space>
          </Col>
          <Col>
            <Space>
              <span>返回数量:</span>
              <InputNumber
                min={10}
                max={1000}
                value={limit}
                onChange={(v) => setLimit(v || 100)}
              />
            </Space>
          </Col>
          <Col flex={1} className="text-right">
            <Space>
              <Button
                type="primary"
                icon={<SearchOutlined />}
                onClick={handleSearch}
                loading={isFetching}
              >
                开始选股
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={handleReset}
              >
                重置
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 策略模板 */}
      <TemplateSelector onSelect={handleTemplateSelect} />

      {/* 条件构建器 */}
      <ConditionBuilder conditions={conditions} onChange={setConditions} />

      {/* 结果统计 */}
      {data && (
        <Card size="small">
          <Row gutter={24}>
            <Col span={6}>
              <Statistic title="交易日期" value={formatDateLabel(data.trade_date)} />
            </Col>
            <Col span={6}>
              <Statistic title="筛选条件数" value={conditions.length} />
            </Col>
            <Col span={6}>
              <Statistic title="符合条件股票数" value={data.total} suffix="只" />
            </Col>
            <Col span={6}>
              <Statistic title="实际返回" value={data.stocks.length} suffix="只" />
            </Col>
          </Row>
        </Card>
      )}

      {/* 结果表格 */}
      <Card title="选股结果">
        <Table
          columns={columns}
          dataSource={data?.stocks || []}
          loading={isLoading || isFetching}
          rowKey="ts_code"
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`
          }}
          scroll={{ x: 970 }}
        />
      </Card>
    </div>
  )
}

export default StockScreen
