import { createBrowserRouter } from 'react-router-dom'
import Layout from '@/shared/components/Layout'

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <div>首页</div>,
      },
      {
        path: 'hotmoney',
        element: <div>龙虎榜</div>,
      },
      {
        path: 'hotmoney/info',
        element: <div>游资介绍</div>,
      },
      {
        path: 'stock',
        element: <div>股票信息</div>,
      },
      {
        path: 'stock/trend/:code',
        element: <div>股票走势</div>,
      },
      {
        path: 'limit',
        element: <div>涨跌停</div>,
      },
      {
        path: 'sector',
        element: <div>板块行情</div>,
      },
    ],
  },
])

export default router
