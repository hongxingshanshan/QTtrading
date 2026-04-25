import Vue from 'vue'
import Router from 'vue-router'
import Index from '../components/Index.vue'
import StockBasicInfo from '../components/StockBasicInfo.vue'
import SectorData from '../components/SectorData.vue'
import HotMoneyInfo from '../components/HotMoneyInfo.vue'
import StockTrend from '../components/StockTrend.vue'
import DailyLimitData from '../components/DailyLimitData.vue'
import DailyHmTradeData from '../components/DailyHmTradeData.vue'
import DailySectorLimitData from '../components/DailySectorLimitData.vue'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Index',
      component: Index
    },
    {
      path: '/stock-basic-info',
      name: 'StockBasicInfo',
      component: StockBasicInfo
    },
    {
      path: '/sector-data',
      name: 'SectorData',
      component: SectorData
    },
    {
      path: '/hot-money-info',
      name: 'HotMoneyInfo',
      component: HotMoneyInfo
    },
    {
      path: '/stock-trend/:tsCode',
      name: 'StockTrend',
      component: StockTrend,
      props: true
    },
    {
      path: '/daily-limit-data',
      name: 'DailyLimitData',
      component: DailyLimitData
    },
    {
      path: '/daily-hm-trade-data',
      name: 'DailyHmTradeData',
      component: DailyHmTradeData,
      props: true
    },
    {
      path: '/daily-sector-limit-data',
      name: 'DailySectorLimitData',
      component: DailySectorLimitData  
    }
  ]
})