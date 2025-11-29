<template>
    <div class="detail-container">
        <el-page-header
            :content="'【' + route.query.title + '】详情页'"
            @back="goBack"
        />
        <el-alert :closable="false" title="当前详情页允许多开" />
        <el-form inline :model="form" @submit.prevent>
            <el-form-item label="输入框缓存">
                <el-input v-model="form.text" clearable style="width: 200px" />
            </el-form-item>
            <el-form-item label="操作">
                <el-button
                    :icon="Refresh"
                    type="primary"
                    @click="handleRefreshMainPage"
                >
                    刷新综合表格页面
                </el-button>
            </el-form-item>
        </el-form>

        <el-descriptions border :column="2" title="详情">
            <el-descriptions-item>
                <template #label>标题</template>
                {{ route.query.title }}
            </el-descriptions-item>
            <el-descriptions-item>
                <template #label>作者</template>
                {{ route.query.author }}
            </el-descriptions-item>
            <el-descriptions-item>
                <template #label>时间</template>
                {{ route.query.datetime }}
            </el-descriptions-item>
            <el-descriptions-item>
                <template #label>评级</template>
                <el-rate v-model="rate" disabled />
            </el-descriptions-item>
            <el-descriptions-item>
                <template #label>备注</template>
                {{ route.query.description }}
            </el-descriptions-item>
        </el-descriptions>
    </div>
</template>

<script lang="ts" setup>
    import { Refresh } from '@element-plus/icons-vue'
    import { useTabsStore } from '@/store/modules/tabs'
    import { handleActivePath } from '@/utils/routes'

    defineOptions({
        name: 'Detail',
    })

    const route: any = useRoute()
    const $pub = inject<any>('$pub')
    const tabsStore = useTabsStore()
    const { changeTabsMeta, delVisitedRoute } = tabsStore
    const form = reactive<any>({ text: '' })
    const rate = ref<number>(Number.parseInt(route.query.rate))

    const goBack = async () => {
        await delVisitedRoute(handleActivePath(route, true))
        history.back()
    }

    const handleRefreshMainPage = () => {
        $pub('reload-router-view', 'ComprehensiveTable')
    }

    onMounted(() => {
        changeTabsMeta({
            title: '详情页',
            meta: {
                title: `${route.query.title} 详情页`,
            },
        })
    })
</script>

<style lang="scss" scoped>
    .default-table-detail-container {
        :deep() {
            .el-form--inline {
                .el-form-item {
                    margin-right: 10px;
                }
            }

            .el-descriptions__label {
                min-width: 80px !important;
                text-align: right;
            }
        }
    }
</style>
