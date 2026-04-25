import axios from 'axios'

const api = {
  async getSectorData() {
    const response = await axios.get('/api/sector_data')
    return response.data
  },
  
  async getHotMoneyData(params) {
    try {
      const response = await axios.get('/api/get_hotmoney_data', { params })
      return response.data
    } catch (error) {
      console.error('Error fetching hot money data:', error)
      return { data: [], total: 0 }
    }
  },
  
  async getDailyHotMoneyTradeData(params) {
    try {
      const response = await axios.get('/api/get_daily_hotmoney_trade_data', { params })
      return response.data
    } catch (error) {
      console.error('Error fetching daily hot money trade data:', error)
      return { data: [], total: 0 }
    }
  },

  async getStockBasicInfo(params) {
    try {
      const response = await axios.get('/api/get_stock_basic_info', { params })
      return response.data
    } catch (error) {
      console.error('Error fetching stock basic info:', error)
      return { data: [], total: 0 }
    }
  },

  async getDailyData(params) {
    try {
      const response = await axios.get('/api/get_daily_data', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching daily data:', error);
      return { data: [] };
    }
  },

  async getDailyLimitData() {
    try {
      const response = await axios.get('/api/get_daily_limit_data');
      return response.data;
    } catch (error) {
      console.error('Error fetching daily limit data:', error);
      return { data: [] };
    }
  },
  async getDailySectorLimitData() {
    try {
      const response = await axios.get('/api/get_daily_sector_limit_data');
      return response.data;
    } catch (error) {
      console.error('Error fetching daily sector limit data:', error);
      return { data: [] };
    } 
  },
  async get_all_ths_index(){
    try {
      const response = await axios.get('/api/get_all_ths_index');
      return response.data;
    } catch (error) {
      console.error('Error fetching all ths index:', error);
      return { data: [] };
    }
  }
}

export default api