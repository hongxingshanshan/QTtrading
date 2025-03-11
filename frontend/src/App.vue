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

<style>
html, body {
  height: 100%;
  margin: 0;
  overflow: hidden; /* 确保整体页面不会出现右侧滚动轴 */
}

#app {
  display: flex;
  flex-direction: column;
  height: 100%;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

header {
  background-color: #42b983;
  padding: 20px;
  color: white;
}

.container {
  display: flex;
  flex: 1;
  height: 100%;
}

aside {
  width: 200px;
  background-color: #f4f4f4;
  padding: 20px;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
}

aside a {
  display: block;
  margin-bottom: 10px;
  color: #333;
  text-decoration: none;
}

aside a:hover {
  color: #42b983;
}

main {
  flex: 1;
  overflow: hidden; /* 确保内容区域不会出现滚动轴 */
  display: flex;
  flex-direction: column;
  padding: 20px;
}
</style>