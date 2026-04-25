import { Layout } from 'antd'
import { Outlet } from 'react-router-dom'
import Header from './Header'
import Sidebar from './Sidebar'

const { Content, Sider } = Layout

function LayoutComponent() {
  return (
    <Layout className="min-h-screen">
      <Header />
      <Layout>
        <Sider width={200} className="bg-white">
          <Sidebar />
        </Sider>
        <Content className="p-6 bg-gray-50">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}

export default LayoutComponent
