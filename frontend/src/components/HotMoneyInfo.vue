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

<style scoped>
.container {
  max-width: 80%;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.search-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-bottom: 20px;
  background-color: #f9f9f9;
  padding: 10px;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-field {
  display: flex;
  flex-direction: column;
  margin-bottom: 10px;
}

.search-field label {
  margin-bottom: 5px;
}

.search-buttons {
  display: flex;
  align-items: flex-end;
}

.table-container {
  flex: 1;
  overflow-y: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

th, td {
  border: 1px solid #ddd;
  padding: 8px;
}

th {
  background-color: #f2f2f2;
  text-align: left;
}

.ellipsis {
  display: inline-block;
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pagination-container {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f9f9f9;
  padding: 10px;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: sticky;
  bottom: 0;
  z-index: 1;
}

.pagination-container button {
  margin: 0 5px;
}

.pagination-container input {
  width: 50px;
  margin: 0 5px;
}

.btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 14px;
  margin: 4px 2px;
  cursor: pointer;
  border-radius: 5px;
  transition: background-color 0.3s;
}

.btn:hover {
  background-color: #0056b3;
}

.btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>