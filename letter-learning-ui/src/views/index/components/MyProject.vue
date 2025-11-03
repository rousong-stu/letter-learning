<template>
    <vab-card shadow="never">
        <template #header>
            <vab-icon icon="github-line" />
            开源项目
            <el-tag class="card-header-tag">爱我别走</el-tag>
        </template>
        <el-row :gutter="20">
            <el-col
                v-for="(item, index) in list"
                :key="index"
                :lg="12"
                :md="12"
                :sm="24"
                :xl="12"
                :xs="24"
            >
                <vab-colorful-card
                    :color-from="item.colorFrom"
                    :color-to="item.colorTo"
                    :icon="item.icon"
                    :title="item.title"
                    @click="handleOpenWindow(item.url)"
                >
                    <div class="project-card-description">
                        {{ item.description }}
                    </div>
                </vab-colorful-card>
            </el-col>
        </el-row>
    </vab-card>
</template>

<script>
    export default defineComponent({
        setup() {
            const list = [
                {
                    title: 'vue-admin-better',
                    description:
                        '一款基于rapack + element-ui开发的绝佳的中后台前端开发管理框架',
                    colorFrom: 'var(--el-color-primary)',
                    colorTo: 'var(--el-color-transition)',
                    icon: 'vuejs-line',
                    url: 'https://github.com/zxwk1998/vue-admin-better',
                },
                {
                    title: 'vue-admin-arco',
                    description: '一款基于vite + arco-design开发的前端框架',
                    colorFrom: 'var(--el-color-primary)',
                    colorTo: 'var(--el-color-transition)',
                    icon: 'dashboard-line',
                    url: 'https://github.com/zxwk1998/vue-admin-arco',
                },
                {
                    title: 'vue3-admin-better',
                    description: '一款基于rapack + element-plus开发的前端框架',
                    colorFrom: 'var(--el-color-primary)',
                    colorTo: 'var(--el-color-transition)',
                    icon: 'dashboard-line',
                    url: 'https://github.com/zxwk1998/vue3-admin-better',
                },
            ]

            const handleOpenWindow = (url) => {
                window.open(url)
            }

            return {
                list,
                handleOpenWindow,
            }
        },
    })
</script>

<style lang="scss" scoped>
    :deep() {
        .el-card__body {
            padding-bottom: 0 !important;
        }
    }

    .project-card {
        &-description {
            width: calc(100% - 100px);
            margin-right: 45px;
            font-size: 12px;
            font-weight: normal;
            line-height: 20px;
            color: #fff;
        }
    }
</style>
