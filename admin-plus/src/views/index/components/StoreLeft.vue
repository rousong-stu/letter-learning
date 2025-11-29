<script lang="ts" setup>
    import { onMounted, ref } from 'vue'

    const systemStats = ref({
        cpu: 0,
        memory: 0,
        disk: 0,
        network: 0,
    })

    const quickActions = ref([
        {
            title: '系统监控',
            icon: 'dashboard-line',
            color: '#52c41a',
            action: 'monitor',
        },
        {
            title: '数据备份',
            icon: 'cloud-line',
            color: '#1890ff',
            action: 'backup',
        },
        {
            title: '日志查看',
            icon: 'file-list-line',
            color: '#fa8c16',
            action: 'logs',
        },
        {
            title: '性能分析',
            icon: 'speed-line',
            color: '#eb2f96',
            action: 'performance',
        },
    ])

    const handleAction = (action: string) => {
        // 这里可以添加具体的功能实现
        console.log('执行操作:', action)
    }

    const updateStats = () => {
        // 模拟系统状态数据
        systemStats.value = {
            cpu: Math.floor(Math.random() * 30) + 20,
            memory: Math.floor(Math.random() * 40) + 30,
            disk: Math.floor(Math.random() * 20) + 60,
            network: Math.floor(Math.random() * 50) + 10,
        }
    }

    onMounted(() => {
        updateStats()
        // 每5秒更新一次状态
        setInterval(updateStats, 5000)
    })
</script>

<template>
    <vab-card class="store-left" shadow="never">
        <template #header>
            <vab-icon icon="dashboard-line" />
            系统概览
        </template>

        <!-- 系统状态 -->
        <div class="system-status">
            <h4>系统状态</h4>
            <el-row :gutter="16">
                <el-col :span="12">
                    <div class="status-item">
                        <div class="status-label">CPU使用率</div>
                        <el-progress
                            :color="
                                systemStats.cpu > 80 ? '#f56c6c' : '#67c23a'
                            "
                            :percentage="systemStats.cpu"
                            :stroke-width="8"
                        />
                    </div>
                </el-col>
                <el-col :span="12">
                    <div class="status-item">
                        <div class="status-label">内存使用率</div>
                        <el-progress
                            :color="
                                systemStats.memory > 80 ? '#f56c6c' : '#67c23a'
                            "
                            :percentage="systemStats.memory"
                            :stroke-width="8"
                        />
                    </div>
                </el-col>
            </el-row>
            <el-row :gutter="16" style="margin-top: 16px">
                <el-col :span="12">
                    <div class="status-item">
                        <div class="status-label">磁盘使用率</div>
                        <el-progress
                            :color="
                                systemStats.disk > 80 ? '#f56c6c' : '#67c23a'
                            "
                            :percentage="systemStats.disk"
                            :stroke-width="8"
                        />
                    </div>
                </el-col>
                <el-col :span="12">
                    <div class="status-item">
                        <div class="status-label">网络流量</div>
                        <el-progress
                            :color="
                                systemStats.network > 80 ? '#f56c6c' : '#67c23a'
                            "
                            :percentage="systemStats.network"
                            :stroke-width="8"
                        />
                    </div>
                </el-col>
            </el-row>
        </div>

        <!-- 快速操作 -->
        <div class="quick-actions">
            <h4>快速操作</h4>
            <el-row :gutter="12">
                <el-col
                    v-for="(action, index) in quickActions"
                    :key="index"
                    :span="12"
                    style="margin-bottom: 12px"
                >
                    <div
                        class="action-item"
                        :style="{ borderLeftColor: action.color }"
                        @click="handleAction(action.action)"
                    >
                        <vab-icon
                            :icon="action.icon"
                            :style="{ color: action.color }"
                        />
                        <span>{{ action.title }}</span>
                    </div>
                </el-col>
            </el-row>
        </div>
    </vab-card>
</template>

<style lang="scss" scoped>
    .store-left {
        .system-status {
            margin-bottom: 24px;

            h4 {
                margin: 0 0 16px 0;
                font-size: 16px;
                font-weight: 600;
                color: #333;
            }

            .status-item {
                .status-label {
                    margin-bottom: 8px;
                    font-size: 14px;
                    color: #666;
                }
            }
        }

        .quick-actions {
            h4 {
                margin: 0 0 16px 0;
                font-size: 16px;
                font-weight: 600;
                color: #333;
            }

            .action-item {
                display: flex;
                align-items: center;
                padding: 12px 16px;
                cursor: pointer;
                background: #f8f9fa;
                border-left: 4px solid;
                border-radius: 6px;
                transition: all 0.3s ease;

                &:hover {
                    background: #e9ecef;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                    transform: translateY(-2px);
                }

                i {
                    margin-right: 8px;
                    font-size: 18px;
                }

                span {
                    font-size: 14px;
                    color: #333;
                }
            }
        }
    }
</style>
