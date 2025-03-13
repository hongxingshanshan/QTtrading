<template>
  <div id="app">
    <header>
      <h1>量化数据</h1>
    </header>
    <div class="container">
      <aside>
        <router-link to="/">首页</router-link>
        <router-link to="/daily-hm-trade-data">龙虎榜</router-link>
        <router-link to="/daily-limit-data">打板数据</router-link>
        <router-link to="/daily-sector-limit-data">板块行情</router-link>
        <router-link to="/stock-basic-info">股票</router-link>
        <router-link to="/hot-money-info">游资介绍</router-link>
      </aside>
      <main>
        <router-view />
      </main>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>
<style src="./assets/css/App.css"></style>