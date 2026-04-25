import { createBrowserRouter } from 'react-router-dom'
import Layout from '@/shared/components/Layout'
import Home from '@/modules/Home'
import HotMoney from '@/modules/HotMoney'
import HotMoneyInfo from '@/modules/HotMoneyInfo'
import Stock from '@/modules/Stock'
import StockTrend from '@/modules/StockTrend'
import DailyLimit from '@/modules/DailyLimit'
import SectorLimit from '@/modules/SectorLimit'

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <Home />,
      },
      {
        path: 'hotmoney',
        element: <HotMoney />,
      },
      {
        path: 'hotmoney/info',
        element: <HotMoneyInfo />,
      },
      {
        path: 'stock',
        element: <Stock />,
      },
      {
        path: 'stock/trend/:code',
        element: <StockTrend />,
      },
      {
        path: 'limit',
        element: <DailyLimit />,
      },
      {
        path: 'sector',
        element: <SectorLimit />,
      },
    ],
  },
])

export default router
