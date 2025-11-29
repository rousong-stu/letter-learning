<script lang="ts" setup>
    import { ref } from 'vue'

    const activities = ref([
        {
            id: 1,
            type: 'login',
            title: '用户登录',
            description: '管理员登录系统',
            time: '2分钟前',
            icon: 'user-line',
            color: 'var(--el-color-success)',
        },
        {
            id: 2,
            type: 'update',
            title: '系统更新',
            description: 'Vue3版本升级完成',
            time: '5分钟前',
            icon: 'refresh-line',
            color: 'var(--el-color-primary)',
        },
        {
            id: 3,
            type: 'backup',
            title: '数据备份',
            description: '自动备份任务执行成功',
            time: '10分钟前',
            icon: 'cloud-line',
            color: 'var(--el-color-warning)',
        },
        {
            id: 4,
            type: 'alert',
            title: '系统告警',
            description: 'CPU使用率超过80%',
            time: '15分钟前',
            icon: 'alert-line',
            color: 'var(--el-color-danger)',
        },
        {
            id: 5,
            type: 'user',
            title: '新用户注册',
            description: '用户张三完成注册',
            time: '20分钟前',
            icon: 'user-add-line',
            color: 'var(--el-color-info)',
        },
    ])

    const getStatusText = (type: string) => {
        const textMap: Record<string, string> = {
            login: '登录',
            update: '更新',
            backup: '备份',
            alert: '告警',
            user: '用户',
        }
        return textMap[type] || '其他'
    }
</script>

<template>
    <vab-card class="store-activity" shadow="never">
        <template #header>
            <vab-icon icon="time-line" />
            最近活动
        </template>

        <div class="activity-list">
            <div
                v-for="activity in activities"
                :key="activity.id"
                class="activity-item"
            >
                <div
                    class="activity-icon"
                    :style="{ background: activity.color }"
                >
                    <vab-icon :icon="activity.icon" />
                </div>
                <div class="activity-content">
                    <div class="activity-header">
                        <span class="activity-title">{{ activity.title }}</span>
                        <span class="activity-time">{{ activity.time }}</span>
                    </div>
                    <div class="activity-description">
                        {{ activity.description }}
                    </div>
                    <div
                        class="activity-status"
                        :style="{ color: activity.color }"
                    >
                        {{ getStatusText(activity.type) }}
                    </div>
                </div>
            </div>
        </div>

        <div class="activity-footer">
            <el-button size="small" text type="primary">
                查看全部活动
                <vab-icon icon="arrow-right-line" />
            </el-button>
        </div>
    </vab-card>
</template>

<style lang="scss" scoped>
    .store-activity {
        margin-top: 20px;

        .activity-list {
            .activity-item {
                display: flex;
                align-items: flex-start;
                padding: 12px 0;
                border-bottom: 1px solid #f0f0f0;

                &:last-child {
                    border-bottom: none;
                }

                .activity-icon {
                    display: flex;
                    flex-shrink: 0;
                    align-items: center;
                    justify-content: center;
                    width: 40px;
                    height: 40px;
                    margin-right: 12px;
                    border-radius: 8px;

                    i {
                        font-size: 18px;
                        color: #fff;
                    }
                }

                .activity-content {
                    flex: 1;
                    min-width: 0;

                    .activity-header {
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        margin-bottom: 4px;

                        .activity-title {
                            font-size: 14px;
                            font-weight: 600;
                            color: #333;
                        }

                        .activity-time {
                            font-size: 12px;
                            color: #999;
                        }
                    }

                    .activity-description {
                        margin-bottom: 6px;
                        font-size: 13px;
                        line-height: 1.4;
                        color: #666;
                    }

                    .activity-status {
                        font-size: 11px;
                        font-weight: 500;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                    }
                }
            }
        }

        .activity-footer {
            padding-top: 16px;
            margin-top: 16px;
            text-align: center;
            border-top: 1px solid #f0f0f0;

            .el-button {
                i {
                    margin-left: 4px;
                }
            }
        }
    }
</style>
