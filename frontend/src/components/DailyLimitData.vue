<template>
  <div class="container">
    <div ref="chart" class="chart-container"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import api from '../services/api';

export default {
  data() {
    return {
      dailyLimitData: [],
      chart: null
    };
  },
  async created() {
    await this.fetchDailyLimitData();
    this.drawChart();
  },
  methods: {
    async fetchDailyLimitData() {
      const response = await api.getDailyLimitData();
      this.dailyLimitData = response.data;
    },
    formatDate(inputDate) {
    const date = new Date(inputDate);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
    },
    formatDateWeek(inputDate) {
    const date = new Date(inputDate);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const value = `${year}-${month}-${day}`;
    const days = ['日', '一', '二', '三', '四', '五', '六'];
    return value + ' 周' + days[date.getDay()];
    },
    drawChart() {
      const dates = this.dailyLimitData.map(item => this.formatDateWeek(item.trade_date));
      const totalUps = this.dailyLimitData.map(item => parseInt(item.up_count));
      const upMain = this.dailyLimitData.map(item => parseInt(item.up_main));
      const upChuang = this.dailyLimitData.map(item => parseInt(item.up_chuang));
      const upKeChuang = this.dailyLimitData.map(item => parseInt(item.up_kechuang));
      const upBeiJiao = this.dailyLimitData.map(item => parseInt(item.up_beijiao));
      const highestConsecutiveLimits = this.dailyLimitData.map(item => parseInt(item.highest_consecutive_limit));
      const downCounts = this.dailyLimitData.map(item => parseInt(item.down_count));
      const downMain = this.dailyLimitData.map(item => parseInt(item.down_main));
      const downChuang = this.dailyLimitData.map(item => parseInt(item.down_chuang));
      const downKeChuang = this.dailyLimitData.map(item => parseInt(item.down_kechuang));
      const downBeiJiao = this.dailyLimitData.map(item => parseInt(item.down_beijiao));
      const zCounts = this.dailyLimitData.map(item => parseInt(item.z_count));

      // 计算最近半年的数据范围
      const sixMonthsAgo = new Date();
      sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
      const sixMonthsAgoStr = sixMonthsAgo.toISOString().split('T')[0].replace(/-/g, '');
      const startIndex = dates.findIndex(date => date >= sixMonthsAgoStr);
      const startPercent = (startIndex / dates.length) * 100;
      const endPercent = 100;

      const option = {
        title: {
          text: '每日涨跌停和炸板数据',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['涨停数量', '主板涨停数量', '创业板涨停数量', '科创板涨停数量', '北交所涨停数量', '连板高度', '跌停数量', '主板跌停数量', '创业板跌停数量', '科创板跌停数量', '北交所涨停数量', '炸板数量'],
          top: 30
        },
        xAxis: {
          type: 'category',
          data: dates,
          boundaryGap: false,
          axisLabel: {
            formatter: (value) => {
              return `${value}`;
            }
          }
        },
        yAxis: {
          type: 'value'
        },
        grid: {
          bottom: 150 
        },
        dataZoom: [
          {
            type: 'inside',
            start: startPercent,
            end: endPercent
          },
          {
            type: 'slider',
            start: startPercent,
            end: endPercent,
            height: 60, // 设置滑动轴的高度
            handleSize: '120%', // 设置滑动轴手柄的大小
            bottom: 30 // 确保滑动轴上移
          }
        ],
        series: [
          {
            name: '涨停数量',
            type: 'line',
            data: totalUps,
            smooth: true
          },
          {
            name: '主板涨停数量',
            type: 'line',
            data: upMain,
            smooth: true
          },
          {
            name: '创业板涨停数量',
            type: 'line',
            data: upChuang,
            smooth: true
          },
          {
            name: '科创板涨停数量',
            type: 'line',
            data: upKeChuang,
            smooth: true
          },
          {
            name: '北交所涨停数量',
            type: 'line',
            data: upBeiJiao,
            smooth: true
          },
          {
            name: '连板高度',
            type: 'line',
            data: highestConsecutiveLimits,
            smooth: true
          },
          {
            name: '跌停数量',
            type: 'line',
            data: downCounts,
            smooth: true
          },
          {
            name: '主板跌停数量',
            type: 'line',
            data: downMain,
            smooth: true
          },
          {
            name: '创业板跌停数量',
            type: 'line',
            data: downChuang,
            smooth: true
          },
          {
            name: '科创板跌停数量',
            type: 'line',
            data: downKeChuang,
            smooth: true
          },
          {
            name: '北交所涨停数量',
            type: 'line',
            data: downBeiJiao,
            smooth: true
          },
          {
            name: '炸板数量',
            type: 'line',
            data: zCounts,
            smooth: true
          }
        ]
      };

      this.chart = echarts.init(this.$refs.chart);
      this.chart.setOption(option);
    },
    goHome() {
      this.$router.push('/');
    }
  }
};
</script>

<style scoped>
.container {
  font-family: 'Arial', sans-serif;
  background-color: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h2 {
  color: #333;
  text-align: center;
  margin-bottom: 20px;
}

.home-button {
  display: block;
  margin: 0 auto 20px;
  padding: 10px 20px;
  font-size: 16px;
  color: #fff;
  background-color: #007bff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.home-button:hover {
  background-color: #0056b3;
}

.chart-container {
  width: 100%;
  height: 100%;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>