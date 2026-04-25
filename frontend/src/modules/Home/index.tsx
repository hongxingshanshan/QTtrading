import { Card, Row, Col, Statistic } from 'antd'
import { StockOutlined, RiseOutlined, TeamOutlined, BarChartOutlined } from '@ant-design/icons'

function Home() {
  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Statistic
              title="龙虎榜"
              value={0}
              prefix={<TeamOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="涨跌停"
              value={0}
              prefix={<RiseOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="板块行情"
              value={0}
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="股票数量"
              value={0}
              prefix={<StockOutlined />}
            />
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Home
