<script lang="ts" setup>
    import { useSettingsStore } from '@/store/modules/settings'
    import { translate } from '@/i18n'
    import { getList } from '@/api/notice'

    const $baseMessage: any = inject('$baseMessage')

    const settingsStore = useSettingsStore()
    const { theme } = storeToRefs(settingsStore)

    const activeName = ref('notice')
    const notices: any = ref([])
    const badge = ref(undefined)

    const fetchData = async () => {
        const {
            data: { list, total },
        } = await getList()
        notices.value = list
        badge.value = total === 0 ? undefined : total
    }

    nextTick(() => {
        if (theme.value.showNotice) fetchData()
    })

    const handleClick = () => {
        fetchData()
    }

    const handleClearNotice = () => {
        badge.value = undefined
        notices.value = []
        $baseMessage('清空消息成功', 'success', 'vab-hey-message-success')
    }

    const formatTime = (time: string) => {
        const date = new Date(time)
        const now = new Date()
        const diff = now.getTime() - date.getTime()
        const minutes = Math.floor(diff / 60000)
        const hours = Math.floor(diff / 3600000)
        const days = Math.floor(diff / 86400000)

        if (minutes < 1) return '刚刚'
        if (minutes < 60) return `${minutes}分钟前`
        if (hours < 24) return `${hours}小时前`
        if (days < 7) return `${days}天前`
        return date.toLocaleDateString()
    }
</script>

<template>
    <el-badge
        v-if="theme.showNotice"
        class="notice-badge"
        type="danger"
        :value="badge"
    >
        <el-popover
            placement="bottom-end"
            popper-class="notice-popover"
            :show-arrow="false"
            :width="380"
        >
            <template #reference>
                <div class="notice-trigger">
                    <vab-icon icon="notification-line" />
                </div>
            </template>

            <div class="notice-container">
                <div class="notice-header">
                    <h3>{{ translate('消息中心') }}</h3>
                    <el-button
                        class="clear-btn"
                        size="small"
                        text
                        type="primary"
                        @click="handleClearNotice"
                    >
                        <vab-icon icon="delete-bin-line" />
                        {{ translate('清空') }}
                    </el-button>
                </div>

                <el-tabs
                    v-model="activeName"
                    class="notice-tabs"
                    @tab-click="handleClick"
                >
                    <el-tab-pane :label="translate('通知')" name="notice">
                        <div class="notice-list">
                            <el-scrollbar height="320px">
                                <div
                                    v-if="notices.length === 0"
                                    class="empty-state"
                                >
                                    <vab-icon
                                        class="empty-icon"
                                        icon="notification-off-line"
                                    />
                                    <p>{{ translate('暂无通知') }}</p>
                                </div>
                                <div v-else class="notice-items">
                                    <div
                                        v-for="(item, index) in notices"
                                        :key="index"
                                        class="notice-item"
                                    >
                                        <div class="notice-avatar">
                                            <el-avatar
                                                :size="40"
                                                :src="item.image"
                                            />
                                            <div
                                                v-if="!item.read"
                                                class="notice-status"
                                            ></div>
                                        </div>
                                        <div class="notice-content">
                                            <div
                                                class="notice-text"
                                                v-html="item.notice"
                                            ></div>
                                            <div class="notice-time">
                                                {{
                                                    formatTime(
                                                        item.time || new Date()
                                                    )
                                                }}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </el-scrollbar>
                        </div>
                    </el-tab-pane>
                    <el-tab-pane :label="translate('邮件')" name="email">
                        <div class="notice-list">
                            <el-scrollbar height="320px">
                                <div
                                    v-if="notices.length === 0"
                                    class="empty-state"
                                >
                                    <vab-icon
                                        class="empty-icon"
                                        icon="mail-line"
                                    />
                                    <p>{{ translate('暂无邮件') }}</p>
                                </div>
                                <div v-else class="notice-items">
                                    <div
                                        v-for="(item, index) in notices"
                                        :key="index"
                                        class="notice-item"
                                    >
                                        <div class="notice-avatar">
                                            <el-avatar
                                                :size="40"
                                                :src="item.image"
                                            />
                                            <div
                                                v-if="!item.read"
                                                class="notice-status"
                                            ></div>
                                        </div>
                                        <div class="notice-content">
                                            <div class="notice-text">
                                                {{ item.email }}
                                            </div>
                                            <div class="notice-time">
                                                {{
                                                    formatTime(
                                                        item.time || new Date()
                                                    )
                                                }}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </el-scrollbar>
                        </div>
                    </el-tab-pane>
                </el-tabs>
            </div>
        </el-popover>
    </el-badge>
</template>

<style lang="scss" scoped>
    .notice-badge {
        :deep(.el-badge__content) {
            background: linear-gradient(135deg, #ff6b6b, #ee5a52);
        }
    }

    .notice-trigger {
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
    }

    .notice-container {
        .notice-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 20px 12px;
            border-bottom: 1px solid var(--el-border-color-lighter);

            h3 {
                margin: 0;
                font-size: 16px;
                font-weight: 600;
                color: var(--el-text-color-primary);
            }

            .clear-btn {
                padding: 4px 8px;
                font-size: 12px;
                border-radius: 3px;

                &:hover {
                    color: var(--el-color-danger);
                    background: var(--el-color-danger-light-9);
                }
            }
        }

        .notice-tabs {
            :deep(.el-tabs__header) {
                padding: 0 20px;
                margin: 0;

                .el-tabs__nav-wrap {
                    &::after {
                        display: none;
                    }
                }

                .el-tabs__item {
                    padding: 12px 16px;
                    font-size: 14px;
                    transition: all 0.3s ease;

                    &.is-active {
                        font-weight: 500;
                        color: var(--el-color-primary);
                    }

                    &:hover {
                        color: var(--el-color-primary);
                    }
                }

                .el-tabs__active-bar {
                    min-width: 28px;
                }
            }

            :deep(.el-tabs__content) {
                padding: 0;
            }
        }

        .notice-list {
            .empty-state {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 200px;
                color: var(--el-text-color-placeholder);

                .empty-icon {
                    margin-bottom: 12px;
                    font-size: 48px;
                    opacity: 0.6;
                }

                p {
                    margin: 0;
                    font-size: 14px;
                }
            }

            .notice-items {
                padding: 8px 0;

                .notice-item {
                    display: flex;
                    align-items: flex-start;
                    padding: 12px 20px;
                    margin: 0 8px;
                    cursor: pointer;
                    border-radius: 8px;
                    transition: all 0.3s ease;

                    &:hover {
                        background: var(--el-fill-color-light);
                    }

                    .notice-avatar {
                        position: relative;
                        flex-shrink: 0;
                        margin-right: 12px;

                        .notice-status {
                            position: absolute;
                            top: -2px;
                            right: -2px;
                            width: 8px;
                            height: 8px;
                            background: var(--el-color-danger);
                            border: 2px solid #fff;
                            border-radius: 50%;
                        }
                    }

                    .notice-content {
                        flex: 1;
                        min-width: 0;

                        .notice-text {
                            margin-bottom: 4px;
                            font-size: 14px;
                            line-height: 1.5;
                            color: var(--el-text-color-primary);
                            word-break: break-all;
                        }

                        .notice-time {
                            font-size: 12px;
                            color: var(--el-text-color-placeholder);
                        }
                    }
                }
            }
        }
    }
</style>

<style lang="scss">
    .notice-popover {
        padding: 0 !important;
        border: 1px solid var(--el-border-color-lighter) !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12) !important;

        .el-popover__title {
            display: none;
        }
    }
</style>
