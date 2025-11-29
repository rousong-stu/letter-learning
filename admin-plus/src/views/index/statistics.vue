<template>
    <div class="statistics-container">
        <el-row class="stat-cards-row" :gutter="20">
            <el-col
                v-for="(item, index) in statCards"
                :key="index"
                :lg="6"
                :md="12"
                :sm="24"
                :xl="6"
                :xs="24"
            >
                <div class="stat-card">
                    <div
                        class="stat-card-icon-wrapper"
                        :style="{ backgroundColor: item.color }"
                    >
                        <i class="stat-card-icon" :class="item.icon"></i>
                    </div>
                    <div class="stat-card-content">
                        <div class="stat-card-value">{{ item.value }}</div>
                        <div class="stat-card-title">{{ item.title }}</div>
                        <div class="stat-card-footer">
                            <span
                                :class="
                                    item.change > 0 ? 'increase' : 'decrease'
                                "
                            >
                                <i
                                    :class="
                                        item.change > 0
                                            ? 'el-icon-top'
                                            : 'el-icon-bottom'
                                    "
                                ></i>
                                {{ Math.abs(item.change) }}%
                            </span>
                            <span class="compare-text">较昨日</span>
                        </div>
                    </div>
                </div>
            </el-col>
            <el-col :lg="8" :md="24" :sm="24" :xl="8" :xs="24">
                <el-card class="chart-card" shadow="never">
                    <template #header>
                        <div class="card-header">
                            <span>用户类型分布</span>
                        </div>
                    </template>
                    <div class="chart-container">
                        <vab-chart
                            ref="pieChartRef"
                            :option="pieChartOption"
                            :style="{ height: '350px', width: '100%' }"
                            theme="vab-echarts-theme"
                        />
                    </div>
                </el-card>
            </el-col>
            <el-col :lg="8" :md="24" :sm="24" :xl="8" :xs="24">
                <el-card shadow="never">
                    <template #header>
                        <div class="card-header">
                            <span>系统状态</span>
                        </div>
                    </template>
                    <div class="system-status">
                        <div
                            v-for="(item, index) in systemStatus"
                            :key="index"
                            class="status-item"
                        >
                            <div class="status-label">{{ item.label }}</div>
                            <div class="status-value">{{ item.value }}</div>
                            <el-progress
                                :percentage="item.percentage"
                                :stroke-width="10"
                            />
                        </div>
                    </div>
                </el-card>
            </el-col>
            <el-col :lg="8" :md="24" :sm="24" :xl="8" :xs="24">
                <el-card class="chart-card" shadow="never">
                    <template #header>
                        <div class="card-header">
                            <span>销售数据</span>
                        </div>
                    </template>
                    <div class="chart-container">
                        <vab-chart
                            ref="barChartRef"
                            :option="barChartOption"
                            :style="{ height: '350px', width: '100%' }"
                            theme="vab-echarts-theme"
                        />
                    </div>
                </el-card>
            </el-col>
            <el-col :lg="12" :md="24" :sm="24" :xl="12" :xs="24">
                <el-card shadow="never">
                    <template #header>
                        <div class="card-header">
                            <span>最新订单</span>
                        </div>
                    </template>
                    <el-table
                        :data="recentOrders"
                        style="width: 100%; height: 305px"
                    >
                        <el-table-column label="订单号" prop="id" width="100" />
                        <el-table-column label="用户" prop="user" width="120" />
                        <el-table-column label="金额" prop="amount" width="100">
                            <template #default="scope">
                                ¥{{ scope.row.amount }}
                            </template>
                        </el-table-column>
                        <el-table-column label="状态" prop="status" width="100">
                            <template #default="scope">
                                <el-tag
                                    :type="getOrderStatusType(scope.row.status)"
                                >
                                    {{ scope.row.status }}
                                </el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column label="日期" prop="date" />
                    </el-table>
                </el-card>
            </el-col>
            <el-col :lg="12" :md="24" :sm="24" :xl="12" :xs="24">
                <el-card class="chart-card" shadow="never">
                    <template #header>
                        <div class="card-header">
                            <span>数据趋势分析</span>
                            <div class="chart-actions">
                                <el-radio-group
                                    v-model="timeRange"
                                    size="small"
                                    @change="loadChartData"
                                >
                                    <el-radio-button label="day">
                                        今日
                                    </el-radio-button>
                                    <el-radio-button label="week">
                                        本周
                                    </el-radio-button>
                                    <el-radio-button label="month">
                                        本月
                                    </el-radio-button>
                                    <el-radio-button label="year">
                                        本年
                                    </el-radio-button>
                                </el-radio-group>
                            </div>
                        </div>
                    </template>
                    <div class="chart-container">
                        <vab-chart
                            ref="lineChartRef"
                            :option="lineChartOption"
                            :style="{ height: '350px', width: '100%' }"
                            theme="vab-echarts-theme"
                        />
                    </div>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script lang="ts" setup>
    import VabChart from '@/plugins/VabChart/index.vue'
    import { nextTick, onMounted, reactive, ref } from 'vue'

    defineOptions({
        name: 'Statistics',
    })

    // 图表引用
    const lineChartRef = ref(null)
    const pieChartRef = ref(null)
    const barChartRef = ref(null)

    // 数据概览卡片
    const statCards = ref([
        {
            title: '总用户数',
            value: '12,345',
            icon: 'ri-user-line',
            change: 2.5,
            color: '#1890ff',
        },
        {
            title: '订单总数',
            value: '5,678',
            icon: 'ri-shopping-bag-line',
            change: -1.2,
            color: '#13ce66',
        },
        {
            title: '总收入',
            value: '¥238,760',
            icon: 'ri-money-dollar-circle-line',
            change: 5.7,
            color: '#ffba00',
        },
        {
            title: '访问量',
            value: '89,654',
            icon: 'ri-eye-line',
            change: 3.2,
            color: '#ff6700',
        },
    ])

    // 时间范围选择
    const timeRange = ref('week')

    // 最近订单数据
    const recentOrders = ref([
        {
            id: 'ORD001',
            user: '张三',
            amount: 299.0,
            status: '已完成',
            date: '2023-06-15 14:30',
        },
        {
            id: 'ORD002',
            user: '李四',
            amount: 599.0,
            status: '处理中',
            date: '2023-06-15 13:45',
        },
        {
            id: 'ORD003',
            user: '王五',
            amount: 199.0,
            status: '已取消',
            date: '2023-06-15 12:15',
        },
        {
            id: 'ORD004',
            user: '赵六',
            amount: 899.0,
            status: '待发货',
            date: '2023-06-15 11:20',
        },
        {
            id: 'ORD005',
            user: '钱七',
            amount: 399.0,
            status: '已完成',
            date: '2023-06-15 10:10',
        },
    ])

    // 系统状态数据
    const systemStatus = ref([
        { label: 'CPU使用率', value: '45%', percentage: 45, status: '' },
        { label: '内存使用率', value: '68%', percentage: 68, status: '' },
        { label: '磁盘使用率', value: '32%', percentage: 32, status: '' },
        { label: '网络使用率', value: '12%', percentage: 12, status: '' },
    ])

    // 获取订单状态标签类型
    const getOrderStatusType = (status) => {
        const statusMap = {
            已完成: 'success',
            处理中: 'primary',
            待发货: 'warning',
            已取消: 'danger',
        }
        return statusMap[status] || 'info'
    }

    // 折线图配置
    const lineChartOption = reactive({
        tooltip: {
            trigger: 'axis',
        },
        legend: {
            data: ['用户数', '订单数', '收入'],
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
        },
        yAxis: {
            type: 'value',
        },
        series: [
            {
                name: '用户数',
                type: 'line',
                stack: '总量',
                data: [120, 132, 101, 134, 90, 230, 210],
                smooth: true,
            },
            {
                name: '订单数',
                type: 'line',
                stack: '总量',
                data: [220, 182, 191, 234, 290, 330, 310],
                smooth: true,
            },
            {
                name: '收入',
                type: 'line',
                stack: '总量',
                data: [150, 232, 201, 154, 190, 330, 410],
                smooth: true,
            },
        ],
    })

    // 饼图配置
    const pieChartOption = reactive({
        tooltip: {
            trigger: 'item',
        },
        legend: {
            orient: 'vertical',
            left: 'left',
        },
        series: [
            {
                name: '用户类型',
                type: 'pie',
                radius: '50%',
                data: [
                    { value: 1048, name: '普通用户' },
                    { value: 735, name: 'VIP用户' },
                    { value: 580, name: 'SVIP用户' },
                    { value: 484, name: '企业用户' },
                ],
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)',
                    },
                },
            },
        ],
    })

    // 柱状图配置
    const barChartOption = reactive({
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow',
            },
        },
        legend: {
            data: ['销售额', '利润'],
        },
        // grid: {
        //     left: '3%',
        //     right: '4%',
        //     bottom: '3%',
        //     containLabel: true,
        // },
        xAxis: [
            {
                type: 'category',
                data: ['一月', '二月', '三月', '四月', '五月', '六月'],
            },
        ],
        yAxis: [
            {
                type: 'value',
            },
        ],
        series: [
            {
                name: '销售额',
                type: 'bar',
                barGap: 0,
                data: [220, 312, 201, 334, 390, 330],
                itemStyle: {
                    borderRadius: [4, 4, 0, 0],
                },
            },
            {
                name: '利润',
                type: 'bar',
                data: [120, 132, 101, 134, 90, 230],
                itemStyle: {
                    borderRadius: [4, 4, 0, 0],
                },
            },
        ],
    })

    // 加载图表数据（模拟）
    const loadChartData = () => {
        // 这里可以调用API获取实际数据
        console.log('加载图表数据，时间范围：', timeRange.value)
    }

    // 窗口大小改变时重绘图表
    const handleResize = () => {
        nextTick(() => {
            if (lineChartRef.value) {
                lineChartRef.value.resize()
            }
            if (pieChartRef.value) {
                pieChartRef.value.resize()
            }
            if (barChartRef.value) {
                barChartRef.value.resize()
            }
        })
    }

    onMounted(() => {
        loadChartData()
        window.addEventListener('resize', handleResize)
    })

    // 组件卸载时移除事件监听
    // 注意：在Vue 3的组合式API中，需要在适当的时机移除事件监听器
</script>

<style lang="scss" scoped>
    .statistics-container {
        padding: 0 !important;
        background: $base-color-background !important;

        .stat-card {
            --el-card-border-color: var(--el-border-color-light);
            --el-card-border-radius: 4px;
            --el-card-padding: 20px;
            --el-card-bg-color: var(--el-fill-color-blank);
            display: flex;
            height: 130px;
            padding: 20px;
            background: #fff;
            background-color: var(--el-card-bg-color);
            border: 1px solid var(--el-card-border-color);
            transition: all 0.3s ease;

            // &:hover {
            //     box-shadow: var(--el-box-shadow-light);
            // }

            .stat-card-icon-wrapper {
                display: flex;
                align-items: center;
                justify-content: center;
                width: 60px;
                height: 60px;
                margin-right: 15px;
                border-radius: 12px;

                .stat-card-icon {
                    font-size: 28px;
                    color: #fff;
                }
            }

            .stat-card-content {
                display: flex;
                flex: 1;
                flex-direction: column;

                .stat-card-value {
                    margin-bottom: 5px;
                    font-size: 24px;
                    font-weight: bold;
                    color: #333;
                }

                .stat-card-title {
                    margin-bottom: 10px;
                    font-size: 14px;
                    color: #666;
                }

                .stat-card-footer {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-top: auto;

                    .increase {
                        font-weight: bold;
                        color: #67c23a;

                        i {
                            margin-right: 3px;
                        }
                    }

                    .decrease {
                        font-weight: bold;
                        color: #f56c6c;

                        i {
                            margin-right: 3px;
                        }
                    }

                    .compare-text {
                        font-size: 12px;
                        color: #999;
                    }
                }
            }
            margin-bottom: #{$base-margin};
        }

        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .chart-card {
            .chart-container {
                width: 100%;
                min-height: 300px;
            }

            :deep(.el-card__header) {
                border-bottom: 1px solid #eee;
            }
        }

        .system-status {
            .status-item {
                margin-bottom: 30px;

                &:last-child {
                    margin-bottom: 0;
                }

                .status-label {
                    margin-bottom: 5px;
                    font-weight: bold;
                }

                .status-value {
                    margin-bottom: 8px;
                    font-size: 14px;
                    color: #666;
                }
            }
        }

        :deep() {
            .el-card {
                height: 450px;
            }
        }
    }
</style>
