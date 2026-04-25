<template>
    <div class="container">
        <div class="query-container">
            <label>板块类型:</label>
            <select v-model="sectorType" @change="filterSectors" class="custom-select">
                <option v-for="type in sectorTypes" :key="type.value" :value="type.value">{{ type.label }}</option>
            </select>
            <label>板块名称:</label>
            <v-select v-model="sectorCode" :options="filteredSectors" label="name" :reduce="sector => sector.ts_code"
                placeholder="选择板块" :filterable="true" :searchable="true" class="custom-select"></v-select>
            <label>开始时间:</label>
            <input type="date" v-model="startDate" class="custom-input">
            <label>结束时间:</label>
            <input type="date" v-model="endDate" class="custom-input">
            <button @click="fetchData" class="custom-button">查询</button>
        </div>
        <div class="chart-container" ref="chart"></div>
    </div>
</template>

<script>
import axios from 'axios';
import * as echarts from 'echarts';
import vSelect from 'vue-select';
import 'vue-select/dist/vue-select.css';

export default {
    components: { vSelect },
    data() {
        return {
            chart: null,
            dailySectorLimitData: [],
            sectorTypes: [],
            sectors: [],
            filteredSectors: [],
            sectorType: '',
            sectorCode: '',
            startDate: '',
            endDate: ''
        };
    },
    async created() {
        await this.getSectorData();
        this.setDefaultDates();
        await this.fetchData();
        this.drawChart();
    },
    methods: {
        async getSectorData() {
            const response = await axios.get('/api/get_all_ths_index');
            this.sectors = response.data;

            // 映射板块类型到显示名称
            const typeMapping = {
                'N': '概念指数',
                'I': '行业指数',
                'R': '地域指数',
                'S': '同花顺特色指数',
                'ST': '同花顺风格指数',
                'TH': '同花顺主题指数',
                'BB': '同花顺宽基指数'
            };

            this.sectorTypes = [...new Set(this.sectors.map(sector => sector.type))]
                .map(type => ({ value: type, label: typeMapping[type] || type }));

            this.sectorType = this.sectorTypes[0].value; // 设置默认板块类型
            this.filterSectors();
        },
        filterSectors() {
            this.filteredSectors = this.sectors.filter(sector => sector.type === this.sectorType);
            if (this.filteredSectors.length > 0) {
                this.sectorCode = this.filteredSectors[0].ts_code; // 设置默认板块名称
            }
        },
        setDefaultDates() {
            const today = new Date();
            const sixMonthsAgo = new Date();
            sixMonthsAgo.setMonth(today.getMonth() - 6);
            this.startDate = sixMonthsAgo.toISOString().split('T')[0];
            this.endDate = today.toISOString().split('T')[0];
        },
        async fetchData() {
            const response = await axios.get('/api/get_daily_sector_limit_data', {
                params: {
                    sector_code: this.sectorCode,
                    start_date: this.startDate.replace(/-/g, ''),
                    end_date: this.endDate.replace(/-/g, '')
                }
            });
            this.dailySectorLimitData = response.data;
            this.drawChart();
        },
        drawChart() {
            // 按板块分组数据
            const groupedData = this.dailySectorLimitData.reduce((acc, item) => {
                if (!acc[item.sector_name]) {
                    acc[item.sector_name] = {
                        dates: [],
                        upLimitCounts: [],
                        downLimitCounts: []
                    };
                }
                acc[item.sector_name].dates.push(item.trade_date);
                acc[item.sector_name].upLimitCounts.push(item.up_limit_count);
                acc[item.sector_name].downLimitCounts.push(item.down_limit_count);
                return acc;
            }, {});

            const sectorNames = Object.keys(groupedData);

            const series = [];
            sectorNames.forEach(sectorName => {
                series.push({
                    name: `${sectorName} 涨停数量`,
                    type: 'line',
                    data: groupedData[sectorName].upLimitCounts,
                    smooth: true
                });
                series.push({
                    name: `${sectorName} 跌停数量`,
                    type: 'line',
                    data: groupedData[sectorName].downLimitCounts,
                    smooth: true
                });
            });

            const option = {
                title: {
                    text: '每日板块涨跌停趋势',
                    left: 'center'
                },
                tooltip: {
                    trigger: 'axis'
                },
                legend: {
                    data: series.map(s => s.name),
                    top: 30
                },
                xAxis: {
                    type: 'category',
                    data: groupedData[sectorNames[0]].dates,
                    boundaryGap: false,
                    axisLabel: {
                        formatter: (value) => {
                            const date = new Date(value.slice(0, 4) + '-' + value.slice(4, 6) + '-' + value.slice(6, 8));
                            const day = date.getDay();
                            const days = ['日', '一', '二', '三', '四', '五', '六'];
                            return `${value.slice(0, 4)}-${value.slice(4, 6)}-${value.slice(6, 8)} 周${days[day]}`;
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
                        start: 0,
                        end: 100
                    },
                    {
                        type: 'slider',
                        start: 0,
                        end: 100,
                        height: 40,
                        handleSize: '120%',
                        bottom: 30
                    }
                ],
                series: series
            };

            if (!this.chart) {
                this.chart = echarts.init(this.$refs.chart);
            }
            this.chart.setOption(option);
        }
    }
};
</script>

<style scoped>
.container {
    display: flex;
    flex-direction: column;
    padding: 20px;
    background-color: #f5f5f5;
}

.query-container {
    margin-bottom: 20px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    color:black;
}

.chart-container {
    flex-grow: 1;
    height: 100%;
}

/* 添加样式以确保 v-select 在下拉时保持正确的大小和形状 */
.v-select {
    width: 200px;
    /* 根据需要调整宽度 */
}

.v-select .dropdown-toggle {
    width: 100%;
}

.v-select .dropdown-menu {
    width: 100%;
}

/* 美化查询框 */
.custom-select, .custom-input, .custom-button {
    margin: 5px;
    padding: 7px;
    border-radius: 5px;
    border: 1px solid #ccc;
    font-size: 14px;
    width: 200px; /* 统一宽度 */
}

.custom-select {
    background-color: #f9f9f9;
}

.custom-input {
    background-color: #fff;
}

.custom-button {
    background-color: #007bff;
    color: #fff;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.custom-button:hover {
    background-color: #0056b3;
}
</style>