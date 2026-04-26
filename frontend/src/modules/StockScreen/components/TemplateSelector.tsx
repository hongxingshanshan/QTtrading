import { useEffect, useState } from 'react'
import { Card, Row, Col, Tag, message } from 'antd'
import { ThunderboltOutlined } from '@ant-design/icons'
import type { ScreenTemplate, ScreenCondition } from '../types'
import { stockScreenApi } from '@/shared/api/stockScreen'

interface TemplateSelectorProps {
  onSelect: (conditions: ScreenCondition[]) => void
}

function TemplateSelector({ onSelect }: TemplateSelectorProps) {
  const [templates, setTemplates] = useState<ScreenTemplate[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    setLoading(true)
    try {
      const res = await stockScreenApi.getTemplates()
      if (res.success) {
        setTemplates(res.data)
      }
    } catch (error) {
      console.error('加载模板失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSelect = (template: ScreenTemplate) => {
    onSelect(template.conditions)
    message.success(`已应用模板: ${template.name}`)
  }

  const getTemplateColor = (id: string): string => {
    const colorMap: Record<string, string> = {
      'oversold_bounce': 'blue',
      'golden_cross': 'gold',
      'breakout': 'purple',
      'bottom_fishing': 'green',
      'strong_momentum': 'red',
      'limit_up_pool': 'orange',
      'low_valuation': 'cyan',
      'high_growth': 'magenta',
      'small_cap': 'geekblue',
    }
    return colorMap[id] || 'default'
  }

  return (
    <Card title="策略模板" loading={loading}>
      <Row gutter={[12, 12]}>
        {templates.map((template) => (
          <Col key={template.id} xs={24} sm={12} md={8}>
            <Card
              hoverable
              size="small"
              className="cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => handleSelect(template)}
            >
              <div className="flex items-center gap-2 mb-2">
                <ThunderboltOutlined style={{ color: '#1890ff' }} />
                <span className="font-medium">{template.name}</span>
                <Tag color={getTemplateColor(template.id)} className="ml-auto">
                  {template.conditions.length}条件
                </Tag>
              </div>
              <div className="text-gray-500 text-sm">
                {template.description}
              </div>
            </Card>
          </Col>
        ))}
      </Row>
    </Card>
  )
}

export default TemplateSelector
