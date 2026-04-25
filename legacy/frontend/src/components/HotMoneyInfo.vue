<template>
  <div class="container">
    <div class="search-container">
      <div class="search-field">
        <label>游资名称:</label>
        <input v-model="searchParams.name" placeholder="游资名称" />
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
            <th>名称</th>
            <th>描述</th>
            <th>机构</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(data, index) in hotMoneyData" :key="index">
            <td>{{ data.name }}</td>
            <td>
              <span class="ellipsis" :title="data.desc">{{ truncateText(data.desc, 100) }}</span>
            </td>
            <td>
              <span class="ellipsis" :title="data.orgs">{{ truncateText(data.orgs, 100) }}</span>
            </td>
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
      <button class="btn" @click="goToFirstPage">返回第一页</button>
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  data() {
    return {
      hotMoneyData: [],
      searchParams: {
        name: ''
      },
      currentPage: 1,
      pageSize: 15,
      totalPages: 1,
      totalItems: 0,
      jumpPage: 1
    }
  },
  methods: {
    async fetchData() {
      const params = {
        name: this.searchParams.name,
        page: this.currentPage,
        pageSize: this.pageSize
      }
      const response = await api.getHotMoneyData(params)
      this.hotMoneyData = response.data
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
        name: ''
      }
      this.currentPage = 1
      this.fetchData()
    },
    truncateText(text, length) {
      return text.length > length ? text.substring(0, length) + '...' : text
    }
  },
  async created() {
    await this.fetchData()
  }
}
</script>

<style src="../assets/css/HotMoneyInfo.css" scoped />