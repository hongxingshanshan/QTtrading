import { useState } from 'react'
import { Radio, Checkbox } from 'antd'

interface ToolBarProps {
  onPeriodChange?: (period: string) => void
  onAdjTypeChange?: (adjType: string) => void
  onIndicatorChange?: (indicators: string[]) => void
  onMaChange?: (mas: string[]) => void
}

function ToolBar({ onPeriodChange, onAdjTypeChange, onIndicatorChange, onMaChange }: ToolBarProps) {
  const [period, setPeriod] = useState('daily')
  const [adjType, setAdjType] = useState('qfq')
  const [indicators, setIndicators] = useState<string[]>(['macd', 'kdj', 'rsi', 'boll'])
  const [mas, setMas] = useState<string[]>(['ma5', 'ma10', 'ma20', 'ma30', 'ma60', 'ma90', 'ma125', 'ma250'])

  const handlePeriodChange = (value: string) => {
    setPeriod(value)
    onPeriodChange?.(value)
  }

  const handleAdjTypeChange = (value: string) => {
    setAdjType(value)
    onAdjTypeChange?.(value)
  }

  const handleIndicatorChange = (checkedValues: string[]) => {
    setIndicators(checkedValues)
    onIndicatorChange?.(checkedValues)
  }

  const handleMaChange = (checkedValues: string[]) => {
    setMas(checkedValues)
    onMaChange?.(checkedValues)
  }

  return (
    <div className="bg-white border-b p-3">
      <div className="flex flex-wrap items-center gap-6">
        {/* 周期选择 */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">周期:</span>
          <Radio.Group value={period} onChange={(e) => handlePeriodChange(e.target.value)} size="small">
            <Radio.Button value="daily">日K</Radio.Button>
            <Radio.Button value="weekly">周K</Radio.Button>
            <Radio.Button value="monthly">月K</Radio.Button>
          </Radio.Group>
        </div>

        {/* 复权选择 */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">复权:</span>
          <Radio.Group value={adjType} onChange={(e) => handleAdjTypeChange(e.target.value)} size="small">
            <Radio.Button value="qfq">前复权</Radio.Button>
            <Radio.Button value="hfq">后复权</Radio.Button>
            <Radio.Button value="none">不复权</Radio.Button>
          </Radio.Group>
        </div>

        {/* 技术指标 */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">指标:</span>
          <Checkbox.Group
            value={indicators}
            onChange={(checkedValues) => handleIndicatorChange(checkedValues as string[])}
          >
            <Checkbox value="macd">MACD</Checkbox>
            <Checkbox value="kdj">KDJ</Checkbox>
            <Checkbox value="rsi">RSI</Checkbox>
            <Checkbox value="boll">BOLL</Checkbox>
          </Checkbox.Group>
        </div>
      </div>

      {/* 均线选择 */}
      <div className="flex items-center gap-2 mt-2">
        <span className="text-sm text-gray-500">均线:</span>
        <Checkbox.Group
          value={mas}
          onChange={(checkedValues) => handleMaChange(checkedValues as string[])}
        >
          <Checkbox value="ma5">MA5</Checkbox>
          <Checkbox value="ma10">MA10</Checkbox>
          <Checkbox value="ma20">MA20</Checkbox>
          <Checkbox value="ma30">MA30</Checkbox>
          <Checkbox value="ma60">MA60</Checkbox>
          <Checkbox value="ma90">MA90</Checkbox>
          <Checkbox value="ma125">MA125</Checkbox>
          <Checkbox value="ma250">MA250</Checkbox>
        </Checkbox.Group>
      </div>
    </div>
  )
}

export default ToolBar