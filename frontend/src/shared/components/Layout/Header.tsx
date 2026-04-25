import { Layout, Typography } from 'antd'

const { Header: AntHeader } = Layout

function Header() {
  return (
    <AntHeader className="bg-white px-6 flex items-center border-b">
      <Typography.Title level={4} className="m-0">
        量化数据
      </Typography.Title>
    </AntHeader>
  )
}

export default Header
