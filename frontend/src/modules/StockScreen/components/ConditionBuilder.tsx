import { useState, useEffect } from 'react'
import { Card, Select, InputNumber, Button, Space, Tag, Row, Col, Radio, Input } from 'antd'
import { DeleteOutlined, PlusOutlined } from '@ant-design/icons'
import type { ScreenCondition, ConditionType, OperatorType, AvailableFields } from '../types'
import { stockScreenApi } from '@/shared/api/stockScreen'

interface ConditionBuilderProps {
  conditions: ScreenCondition[]
  onChange: (conditions: ScreenCondition[]) => void
}

// 条件类型选项
const CONDITION_TYPE_OPTIONS: { value: ConditionType; label: string }[] = [
  { value: 'indicator', label: '技术指标' },
  { value: 'basic', label: '估值指标(PE/PB)' },
  { value: 'fina', label: '财务指标(ROE/毛利率)' },
  { value: 'industry', label: '行业/地域' },
  { value: 'limit', label: '涨跌停数据' },
  { value: 'limit_status', label: '涨跌停状态' },
  { value: 'macd_cross', label: 'MACD金叉/死叉' },
  { value: 'ma_alignment', label: '均线排列' },
  { value: 'boll_position', label: '布林带位置' },
  { value: 'consecutive', label: '连续涨跌' },
  { value: 'limit_up', label: '连板条件' },
]

function ConditionBuilder({ conditions, onChange }: ConditionBuilderProps) {
  const [fields, setFields] = useState<AvailableFields | null>(null)

  useEffect(() => {
    loadFields()
  }, [])

  const loadFields = async () => {
    try {
      const res = await stockScreenApi.getAvailableFields()
      if (res.success) {
        setFields(res.data)
      }
    } catch (error) {
      console.error('加载字段失败:', error)
    }
  }

  const addCondition = () => {
    onChange([...conditions, { type: 'indicator', field: 'rsi6', operator: '<', value: 20 }])
  }

  const removeCondition = (index: number) => {
    onChange(conditions.filter((_, i) => i !== index))
  }

  const updateCondition = (index: number, updates: Partial<ScreenCondition>) => {
    const newConditions = [...conditions]
    newConditions[index] = { ...newConditions[index], ...updates }
    onChange(newConditions)
  }

  const getFieldOptions = (condition: ScreenCondition) => {
    switch (condition.type) {
      case 'indicator':
        return Object.entries(fields?.indicator_fields || {}).map(([key, label]) => ({
          value: key,
          label: `${label} (${key})`
        }))
      case 'basic':
        return Object.entries(fields?.basic_fields || {}).map(([key, label]) => ({
          value: key,
          label: `${label} (${key})`
        }))
      case 'fina':
        return Object.entries(fields?.fina_fields || {}).map(([key, label]) => ({
          value: key,
          label: `${label} (${key})`
        }))
      case 'limit':
        return Object.entries(fields?.limit_fields || {}).map(([key, label]) => ({
          value: key,
          label: `${label} (${key})`
        }))
      case 'industry':
        return [
          { value: 'industry', label: '行业' },
          { value: 'area', label: '地域' },
        ]
      default:
        return []
    }
  }

  const getOperatorOptions = (): { value: OperatorType; label: string }[] => {
    return fields?.operators.numeric.map(o => ({ value: o as OperatorType, label: o })) || []
  }

  const renderConditionEditor = (condition: ScreenCondition, index: number) => {
    // 特殊条件渲染
    if (condition.type === 'macd_cross') {
      return (
        <Radio.Group
          value={condition.cross_type || 'golden'}
          onChange={(e) => updateCondition(index, { cross_type: e.target.value })}
        >
          <Radio value="golden">金叉</Radio>
          <Radio value="death">死叉</Radio>
        </Radio.Group>
      )
    }

    if (condition.type === 'ma_alignment') {
      return (
        <Radio.Group
          value={condition.alignment || 'bullish'}
          onChange={(e) => updateCondition(index, { alignment: e.target.value })}
        >
          <Radio value="bullish">多头排列</Radio>
          <Radio value="bearish">空头排列</Radio>
        </Radio.Group>
      )
    }

    if (condition.type === 'limit_status') {
      return (
        <Radio.Group
          value={condition.status || 'up'}
          onChange={(e) => updateCondition(index, { status: e.target.value })}
        >
          <Radio value="up">涨停</Radio>
          <Radio value="down">跌停</Radio>
          <Radio value="none">非涨跌停</Radio>
        </Radio.Group>
      )
    }

    if (condition.type === 'consecutive') {
      return (
        <Space>
          <Radio.Group
            value={condition.direction || 'down'}
            onChange={(e) => updateCondition(index, { direction: e.target.value })}
          >
            <Radio value="up">连续上涨</Radio>
            <Radio value="down">连续下跌</Radio>
          </Radio.Group>
          <Space.Compact>
            <span style={{ padding: '0 11px', lineHeight: '32px', background: '#fafafa', border: '1px solid #d9d9d9', borderRadius: '6px 0 0 6px' }}>天数</span>
            <InputNumber
              min={1}
              max={20}
              value={condition.days || 3}
              onChange={(v) => updateCondition(index, { days: v || 3 })}
              style={{ borderRadius: '0 6px 6px 0' }}
            />
          </Space.Compact>
        </Space>
      )
    }

    if (condition.type === 'limit_up') {
      return (
        <Space.Compact>
          <span style={{ padding: '0 11px', lineHeight: '32px', background: '#fafafa', border: '1px solid #d9d9d9', borderRadius: '6px 0 0 6px' }}>连板数</span>
          <InputNumber
            min={1}
            max={10}
            value={condition.days || 1}
            onChange={(v) => updateCondition(index, { days: v || 1 })}
            style={{ borderRadius: '0 6px 6px 0' }}
          />
        </Space.Compact>
      )
    }

    if (condition.type === 'boll_position') {
      return (
        <Space.Compact>
          <span style={{ padding: '0 11px', lineHeight: '32px', background: '#fafafa', border: '1px solid #d9d9d9', borderRadius: '6px 0 0 6px' }}>位置阈值</span>
          <InputNumber
            min={0}
            max={1}
            step={0.1}
            value={(condition.value as number) || 0.2}
            onChange={(v) => updateCondition(index, { value: v })}
            style={{ borderRadius: '0 6px 6px 0' }}
          />
        </Space.Compact>
      )
    }

    // 标准条件渲染（字段+操作符+值）
    const needsField = ['indicator', 'basic', 'fina', 'limit', 'industry'].includes(condition.type)
    const needsOperator = ['indicator', 'basic', 'fina', 'limit'].includes(condition.type)
    const needsValue = ['indicator', 'basic', 'fina', 'limit'].includes(condition.type)

    return (
      <Row gutter={8} align="middle">
        {needsField && (
          <Col>
            <Select
              style={{ width: 180 }}
              value={condition.field}
              onChange={(v) => updateCondition(index, { field: v })}
              options={getFieldOptions(condition)}
              showSearch
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
            />
          </Col>
        )}
        {needsOperator && (
          <Col>
            <Select
              style={{ width: 80 }}
              value={condition.operator}
              onChange={(v) => updateCondition(index, { operator: v })}
              options={getOperatorOptions()}
            />
          </Col>
        )}
        {needsValue && (
          <Col>
            {condition.operator === 'between' ? (
              <Space>
                <InputNumber
                  value={(condition.value as number[])?.[0]}
                  onChange={(v) => updateCondition(index, { value: [v, (condition.value as number[])?.[1]] })}
                />
                <span>~</span>
                <InputNumber
                  value={(condition.value as number[])?.[1]}
                  onChange={(v) => updateCondition(index, { value: [(condition.value as number[])?.[0], v] })}
                />
              </Space>
            ) : condition.operator === 'in' || condition.operator === 'not_in' ? (
              <Input
                style={{ width: 200 }}
                placeholder="多个值用逗号分隔"
                value={(condition.value as string[])?.join(',')}
                onChange={(e) => updateCondition(index, { value: e.target.value.split(',').map(s => s.trim()) })}
              />
            ) : (
              <InputNumber
                style={{ width: 120 }}
                value={condition.value as number}
                onChange={(v) => updateCondition(index, { value: v })}
              />
            )}
          </Col>
        )}
      </Row>
    )
  }

  return (
    <Card
      title="筛选条件"
      extra={
        <Button type="dashed" icon={<PlusOutlined />} onClick={addCondition}>
          添加条件
        </Button>
      }
    >
      {conditions.length === 0 ? (
        <div className="text-gray-400 text-center py-4">
          请添加筛选条件
        </div>
      ) : (
        <Space direction="vertical" className="w-full">
          {conditions.map((condition, index) => (
            <div key={index} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
              <Select
                style={{ width: 150 }}
                value={condition.type}
                onChange={(v) => {
                  // 切换类型时重置字段为该类型的默认值
                  const defaults: Record<ConditionType, Partial<ScreenCondition>> = {
                    indicator: { field: 'rsi6', operator: '<', value: 20 },
                    basic: { field: 'pe_ttm', operator: '<', value: 20 },
                    fina: { field: 'roe', operator: '>', value: 0.1 },
                    industry: { field: 'industry', operator: 'in', value: [] },
                    limit: { field: 'limit_times', operator: '>', value: 1 },
                    limit_status: { status: 'up' },
                    macd_cross: { cross_type: 'golden' },
                    ma_alignment: { alignment: 'bullish' },
                    boll_position: { value: 0.2 },
                    consecutive: { direction: 'down', days: 3 },
                    limit_up: { days: 1 },
                  }
                  updateCondition(index, { type: v, ...defaults[v] })
                }}
                options={CONDITION_TYPE_OPTIONS}
              />
              {renderConditionEditor(condition, index)}
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
                onClick={() => removeCondition(index)}
              />
            </div>
          ))}
        </Space>
      )}
    </Card>
  )
}

export default ConditionBuilder
