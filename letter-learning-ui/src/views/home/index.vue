<template>
    <div class="index-container">
        <el-row :gutter="20">
            <page-header />
        </el-row>

        <el-row :gutter="20" class="summary-row">
            <el-col
                v-for="item in summaryCards"
                :key="item.title"
                :lg="6"
                :md="12"
                :sm="24"
                :xl="6"
                :xs="24"
            >
                <el-card shadow="never" class="summary-card">
                    <div class="summary-top">
                        <div class="summary-icon" :style="{ background: item.color }">
                            <vab-icon :icon="item.icon" />
                        </div>
                        <div class="summary-title">{{ item.title }}</div>
                    </div>
                    <div class="summary-value">{{ item.value }}</div>
                </el-card>
            </el-col>
        </el-row>

        <el-row :gutter="20">
            <el-col :lg="6" :md="12" :sm="24" :xl="6" :xs="24">
                <access />
            </el-col>
            <el-col :lg="6" :md="12" :sm="24" :xl="6" :xs="24">
                <authorization />
            </el-col>
            <el-col :lg="12" :md="24" :sm="24" :xl="12" :xs="24">
                <version-information />
            </el-col>
        </el-row>
    </div>
</template>

<script>
    import PageHeader from '@/views/index/components/PageHeader.vue'
    import Access from '@/views/index/components/Access.vue'
    import Authorization from '@/views/index/components/Authorization.vue'
    import VersionInformation from '@/views/index/components/VersionInformation.vue'
    import { getDashboardSummary } from '@/api/dashboard'

    export default defineComponent({
        name: 'Home',
        components: {
            PageHeader,
            Access,
            Authorization,
            VersionInformation,
        },
        setup() {
            const summaryCards = ref([
                { title: '总学习单词', value: '0', icon: 'book-2-fill', color: '#3d8cff' },
                { title: '总聊天轮次', value: '0', icon: 'chat-1-fill', color: '#10c469' },
                { title: '总学习文章', value: '0', icon: 'article-fill', color: '#f6c343' },
                { title: '学习达成度', value: '0%', icon: 'check-double-fill', color: '#ff7b1b' },
            ])

            const loadSummary = async () => {
                try {
                    const resp = await getDashboardSummary()
                    const summary = resp.data?.summary || {}
                    summaryCards.value = [
                        {
                            title: '总学习单词',
                            value: String(summary.total_words_learned || 0),
                            icon: 'book-2-fill',
                            color: '#3d8cff',
                        },
                        {
                            title: '总聊天轮次',
                            value: String(summary.total_chat_rounds || 0),
                            icon: 'chat-1-fill',
                            color: '#10c469',
                        },
                        {
                            title: '总学习文章',
                            value: String(summary.total_stories || 0),
                            icon: 'article-fill',
                            color: '#f6c343',
                        },
                        {
                            title: '学习达成度',
                            value: `${summary.completion_rate || 0}%`,
                            icon: 'check-double-fill',
                            color: '#ff7b1b',
                        },
                    ]
                } catch (error) {
                    console.error('加载仪表盘失败', error)
                }
            }

            onMounted(() => {
                loadSummary()
            })

            return { summaryCards }
        },
    })
</script>

<style lang="scss" scoped>
    .index-container {
        padding: 0 !important;
        background: $base-color-background !important;

        :deep() {
            .page-header {
                margin-bottom: 20px;
            }

            .access,
            .authorization,
            .version-information {
                min-height: 268px;
                margin-bottom: 20px;
            }

            .el-card {
                .el-card__header {
                    position: relative;

                    .card-header-tag {
                        position: absolute;
                        top: 15px;
                        right: $base-margin;
                    }

                    > div > span {
                        display: flex;
                        align-items: center;

                        i {
                            margin-right: 3px;
                        }
                    }
                }

                .el-card__body {
                    position: relative;

                    .echarts {
                        width: 100%;
                        height: 127px;
                    }

                    .card-footer-tag {
                        position: absolute;
                        right: $base-margin;
                        bottom: 15px;
                    }
                }
            }

            .bottom {
                padding-top: 20px;
                margin-top: 5px;
                color: #595959;
                text-align: left;
                border-top: 1px solid #{$base-border-color};
            }
        }
    }

    .summary-row {
        margin: 10px 0 20px 0;
    }
    .summary-card {
        display: flex;
        align-items: center;
        border: 1px solid #f0f2f5;
        .el-card__body {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 10px;
            padding: 14px 16px 16px;
        }
    }
    .summary-icon {
        width: 56px;
        height: 56px;
        display: grid;
        place-items: center;
        border-radius: 16px;
        color: #fff;
        font-size: 26px;
    }
    .summary-top {
        display: flex;
        align-items: center;
        gap: 12px;
        width: 100%;
    }
    .summary-body {
        flex: 1;
    }
    .summary-value {
        font-size: 24px;
        font-weight: 700;
        line-height: 1.2;
        padding-left: 4px;
    }
    .summary-title {
        color: #333;
        font-size: 20px;
        font-weight: 800;
    }
</style>
