<template>
  <div class="container">
    <h1>龙虎榜</h1>
    <div class="search-container">
      <div class="search-field">
        <label>游资名称:</label>
        <input v-model="searchParams.hmName" placeholder="游资名称" />
      </div>
      <div class="search-field">
        <label>交易日期:</label>
        <input v-model="searchParams.tradeDate" placeholder="交易日期（YYYYMMDD）" />
      </div>
      <div class="search-field">
        <label>股票名称:</label>
        <input v-model="searchParams.tsName" placeholder="股票名称" />
      </div>
      <div class="search-field">
        <label>股票代码:</label>
        <input v-model="searchParams.tsCode" placeholder="股票代码" />
      </div>
      <div class="search-buttons">
        <button class="btn" @click="fetchData">查询</button>
        <button class="btn" @click="resetSearch">重置</button>
      </div>
    </div>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>交易日期</th>
            <th>股票代码</th>
            <th>股票名称</th>
            <th>买入金额（元）</th>
            <th>卖出金额（元）</th>
            <th>净买卖（元）</th>
            <th>游资名称</th>
            <th>关联机构</th>
            <th>标签</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(trade, index) in dailyHotMoneyTrades" :key="index">
            <td>{{ formatDate(trade.trade_date) }}</td>
            <td>{{ trade.ts_code }}</td>
            <td>{{ trade.ts_name }}</td>
            <td :class="{ 'text-red': trade.buy_amount > 0 }">{{ formatAmount(trade.buy_amount) }}</td>
            <td :class="{ 'text-green': trade.sell_amount > 0 }">{{ formatAmount(trade.sell_amount) }}</td>
            <td :class="{ 'text-red': trade.net_amount > 0, 'text-green': trade.net_amount < 0 }">{{
              formatAmount(trade.net_amount) }}</td>
            <td>{{ trade.hm_name }}</td>
            <td>{{ trade.hm_orgs }}</td>
            <td>{{ trade.tag }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="pagination-container">
      <button class="btn" @click="prevPage">上一页</button>
      <span>第 {{ currentPage }} 页，共 {{ totalPages }} 页</span>
      <button class="btn" @click="nextPage">下一页</button>
      <label>跳转到:</label>
      <input type="number" v-model.number="jumpPage" min="1" :max="totalPages" />
      <button class="btn" @click="goToPage">跳页</button>
      <button class="btn" @click="firstPage">返回第一页</button>
    </div>

  </div>
</template>

<script>
import { format } from 'echarts';
import api from '../services/api';

export default {
  data() {
    return {
      searchParams: {
        hmName: '',
        tradeDate: '',
        tsName: '',
        tsCode: ''
      },
      dailyHotMoneyTrades: [],
      currentPage: 1,
      pageSize: 10,
      totalPages: 1,
      totalItems: 0,
      jumpPage: 1
    };
  },
  methods: {
    async fetchData() {
      const params = {
        hmName: this.searchParams.hmName,
        tradeDate: this.searchParams.tradeDate,
        tsName: this.searchParams.tsName,
        tsCode: this.searchParams.tsCode,
        page: this.currentPage,
        page_size: this.pageSize
      };
      const response = await api.getDailyHotMoneyTradeData(params);
      this.dailyHotMoneyTrades = response.data;
      this.totalItems = response.total;
      this.totalPages = Math.ceil(this.totalItems / this.pageSize);
    },
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
        this.fetchData();
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
        this.fetchData();
      }
    },
    goToPage() {
      if (this.jumpPage >= 1 && this.jumpPage <= this.totalPages) {
        this.currentPage = this.jumpPage;
        this.fetchData();
      }
    },
    resetSearch() {
      this.searchParams = {
        hmName: '',
        tradeDate: '',
        tsName: '',
        tsCode: ''
      };
      this.currentPage = 1;
      this.fetchData();
    },
    formatAmount(amount) {
      amount = amount * 1
      if (amount >= 100000000 || amount <= -100000000) {
        return (amount / 100000000).toFixed(3) + '亿';
      } else if (amount >= 10000 || amount <= -10000) {
        return (amount / 10000).toFixed(3) + '万';
      } else {
        return amount.toFixed(2) + '元';
      }
    },
    formatDate(trade_date) {
      const date = new Date(trade_date);
      return date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + date.getDate();
    },
    firstPage() {
    if (this.currentPage !== 1) {
        this.currentPage = 1;
        this.fetchData();
    }
}

  },
  async created() {
    await this.fetchData();
  }
};
</script>

<style src="../assets/css/DailyHmTradeData.css" scoped></style>