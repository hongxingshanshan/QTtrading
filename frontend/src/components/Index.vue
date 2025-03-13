<template>
  <div class="page-container">
    <header>
      <h1>欢迎来到量化数据</h1>
    </header>
    <div class="content">
      <p>为您提供最新的股票市场数据和量化分析工具</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Index'
}
</script>

<style scoped>
/* 让 Index.vue 占满父容器 main */
.page-container {
  display: flex;
  flex-direction: column;
  flex: 1; /* 让它填充 main */
  box-sizing: border-box;
  overflow: auto;
}

.content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 20px;
}
</style>
