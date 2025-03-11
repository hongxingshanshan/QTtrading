<template>
  <div class="container">
    <div ref="chart" class="chart-container"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import api from '../services/api';

export default {
  props: ['tsCode'],
  data() {
    return {
      chart: null,
      dailyData: [],
      stockName: this.$route.query.stockName || ''
    };
  },
  async mounted() {
    this.chart = echarts.init(this.$refs.chart);
    await this.fetchDailyData();
    this.drawChart();
  },
  methods: {
    async fetchDailyData() {
      const response = await api.getDailyData({ ts_code: this.tsCode });
      this.dailyData = response.data;
    },
    drawChart() {
      const now = new Date();
      const sixMonthsAgo = new Date();
      sixMonthsAgo.setMonth(now.getMonth() - 6);

      const dates = this.dailyData.map(item => this.formatDate(item.trade_date));
      const prices = this.dailyData.map(item => item.close);

      // 计算最近半年的数据范围
      const startIndex = dates.findIndex(date => new Date(date) >= sixMonthsAgo);
      const endIndex = dates.length - 1;

      const option = {
        title: {
          text: this.stockName + ' (' + this.tsCode + ') 价格走势',
          left: 'center'
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisLabel: {
            formatter: (value) => {
              const date = new Date(value);
              const day = date.getDay();
              const days = ['日', '一', '二', '三', '四', '五', '六'];
              return `${value} 周${days[day]}`;
            }
          }
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          data: prices,
          type: 'line'
        }],
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            const data = params[0].dataIndex;
            const item = this.dailyData[data];
            const date = new Date(item.trade_date);
            const day = date.getDay();
            const days = ['日', '一', '二', '三', '四', '五', '六'];
            const formattedDate = `${this.formatDate(item.trade_date)} 周${days[day]}`;
            return `
              日期: ${formattedDate}<br/>
              开盘价: ${item.open}<br/>
              最高价: ${item.high}<br/>
              最低价: ${item.low}<br/>
              收盘价: ${item.close}<br/>
              前收盘价: ${item.pre_close}<br/>
              涨跌额: ${item.price_change}<br/>
              涨跌幅: ${item.pct_chg}%<br/>
              成交量: ${this.formatVolume(item.vol)}<br/>
              成交额: ${this.formatAmount(item.amount)}
            `;
          }
        },
        grid: {
          bottom: 150 
        },
        dataZoom: [
          {
            type: 'slider',
            startValue: dates[startIndex],
            endValue: dates[endIndex],
            height: 60, // 设置滑动轴的高度
            handleSize: '120%', // 设置滑动轴手柄的大小
            bottom: 30 // 确保滑动轴上移
          },
          {
            type: 'inside',
            startValue: dates[startIndex],
            endValue: dates[endIndex]
          }
        ]
      };

      this.chart.setOption(option);
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      const year = date.getFullYear();
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const day = date.getDate().toString().padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    formatAmount(amount) {
      amount = amount * 1000;
      if (amount >= 100000000) {
        return (amount / 100000000).toFixed(2) + '亿';
      } else if (amount >= 10000) {
        return (amount / 10000).toFixed(2) + '万';
      } else {
        return amount + '元';
      }
    },
    formatVolume(volume) {
      return (volume / 10000).toFixed(2) + '万';
    }
  }
}
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  height: 100%;
  padding: 20px;
  box-sizing: border-box;
}

.chart-container {
  width: 100%;
  height: 100%;
}
</style>