<template>
  <div class="container">
    <h1>个股基本信息</h1>
    <div class="search-container">
      <div class="search-field">
        <label>股票代码:</label>
        <input v-model="searchParams.symbol" placeholder="股票代码" />
      </div>
      <div class="search-field">
        <label>股票名称:</label>
        <input v-model="searchParams.name" placeholder="股票名称" />
      </div>
      <div class="search-field">
        <label>行业:</label>
        <input v-model="searchParams.industry" placeholder="行业" />
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
            <th>TS代码</th>
            <th>股票代码</th>
            <th>股票名称</th>
            <th>地域</th>
            <th>所属行业</th>
            <th>拼音缩写</th>
            <th>市场类型</th>
            <th>上市日期</th>
            <th>实控人名称</th>
            <th>实控人企业性质</th>
            <th>股票全称</th>
            <th>英文全称</th>
            <th>交易所代码</th>
            <th>交易货币</th>
            <th>上市状态</th>
            <th>退市日期</th>
            <th>是否沪深港通标的</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(stock, index) in stockBasicInfo" :key="stock.ts_code">
            <td @click="goToStockTrend(stock.ts_code, stock.name)" class="clickable">{{ stock.ts_code }}</td>
            <td @click="goToStockTrend(stock.ts_code, stock.name)" class="clickable">{{ stock.symbol }}</td>
            <td @click="goToStockTrend(stock.ts_code, stock.name)" class="clickable">{{ stock.name }}</td>
            <td>{{ stock.area }}</td>
            <td>{{ stock.industry }}</td>
            <td>{{ stock.cnspell }}</td>
            <td>{{ stock.market }}</td>
            <td>{{ formatDate(stock.list_date) }}</td>
            <td>{{ stock.act_name }}</td>
            <td>{{ stock.act_ent_type }}</td>
            <td>{{ stock.fullname }}</td>
            <td>{{ stock.enname }}</td>
            <td>{{ stock.exchange }}</td>
            <td>{{ stock.curr_type }}</td>
            <td>{{ stock.list_status }}</td>
            <td>{{ formatDate(stock.delist_date) }}</td>
            <td>{{ stock.is_hs }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="pagination-container">
      <button class="btn" @click="prevPage" :disabled="currentPage === 1">上一页</button>
      <span>第 {{ currentPage }} 页，共 {{ totalPages }} 页</span>
      <button class="btn" @click="nextPage" :disabled="currentPage === totalPages">下一页</button>
      <label>跳转到:</label>
      <input type="number" v-model.number="jumpPage" min="1" :max="totalPages" />
      <button class="btn" @click="goToPage">跳页</button>
      <button class="btn" @click="goToFirstPage">返回第一页</button>
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  data() {
    return {
      stockBasicInfo: [],
      searchParams: {
        symbol: '',
        name: '',
        industry: '',
        startDate: '',
        endDate: ''
      },
      currentPage: 1,
      pageSize: 10,
      totalPages: 1,
      totalItems: 0,
      jumpPage: 1
    }
  },
  methods: {
    async fetchData() {
      const params = {
        symbol: this.searchParams.symbol,
        name: this.searchParams.name,
        industry: this.searchParams.industry,
        startDate: this.searchParams.startDate,
        endDate: this.searchParams.endDate,
        page: this.currentPage,
        pageSize: this.pageSize
      }
      const response = await api.getStockBasicInfo(params)
      this.stockBasicInfo = response.data
      this.totalItems = response.total
      this.totalPages = Math.ceil(this.totalItems / this.pageSize)
    },
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--
        this.fetchData()
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
        this.fetchData()
      }
    },
    goToPage() {
      if (this.jumpPage >= 1 && this.jumpPage <= this.totalPages) {
        this.currentPage = this.jumpPage
        this.fetchData()
      }
    },
    goToFirstPage() {
      this.currentPage = 1
      this.fetchData()
    },
    resetSearch() {
      this.searchParams = {
        symbol: '',
        name: '',
        industry: '',
        startDate: '',
        endDate: ''
      }
      this.currentPage = 1
      this.fetchData()
    },
    goToIndex() {
      this.$router.push('/')
    },
    goToStockTrend(tsCode, stockName) {
      this.$router.push({ name: 'StockTrend', params: { tsCode }, query: { stockName } });
    },
    formatDate(date) {
      if (!date) return ''
      const options = { year: 'numeric', month: '2-digit', day: '2-digit' }
      return new Date(date).toLocaleDateString('zh-CN', options)
    }
  },
  async created() {
    await this.fetchData()
  },
}
</script>

<style src="../assets/css/StockBasicInfo.css" scoped/>