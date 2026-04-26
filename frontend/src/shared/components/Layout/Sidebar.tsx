import { Menu } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  HomeOutlined,
  StockOutlined,
  RiseOutlined,
  BarChartOutlined,
  TeamOutlined,
  FilterOutlined,
} from '@ant-design/icons'

const menuItems = [
  {
    key: '/',
    icon: <HomeOutlined />,
    label: '首页',
  },
  {
    key: '/screen',
    icon: <FilterOutlined />,
    label: '智能选股',
  },
  {
    key: '/hotmoney',
    icon: <TeamOutlined />,
    label: '龙虎榜',
  },
  {
    key: '/limit',
    icon: <RiseOutlined />,
    label: '打板数据',
  },
  {
    key: '/sector',
    icon: <BarChartOutlined />,
    label: '板块行情',
  },
  {
    key: '/stock',
    icon: <StockOutlined />,
    label: '股票',
  },
  {
    key: '/hotmoney/info',
    icon: <TeamOutlined />,
    label: '游资介绍',
  },
]

function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <Menu
      mode="inline"
      selectedKeys={[location.pathname]}
      items={menuItems}
      onClick={({ key }) => navigate(key)}
      className="h-full border-r"
    />
  )
}

export default Sidebar
