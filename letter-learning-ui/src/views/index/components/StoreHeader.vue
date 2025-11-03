<template>
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
                @click="handleOpenWindow(item.url, item.isExternal)"
            >
                <div class="project-card-description">
                    {{ item.description }}
                </div>
            </vab-colorful-card>
        </el-col>
    </el-row>
</template>

<script setup>
    import { useRouter } from 'vue-router'

    defineOptions({
        name: 'StoreHeader',
    })

    const router = useRouter()

    const list = ref([
        {
            title: '学习必备',
            description: 'Vue3 + TypeScript 开发指南',
            colorFrom: '#1890ffb3',
            colorTo: '#1890ff',
            icon: 'mac-line',
            url: '/vab/table/comprehensiveTable',
            isExternal: false,
        },
        {
            title: '分享讨论',
            description: '技术交流与经验分享',
            colorFrom: '#1bea7ab3',
            colorTo: '#1bea7a',
            icon: 'chat-heart-line',
            url: '/other/notice',
            isExternal: false,
        },
    ])

    const handleOpenWindow = (url, isExternal) => {
        if (isExternal) {
            window.open(url, '_blank')
        } else {
            router.push(url)
        }
    }
</script>

<style lang="scss" scoped>
    :deep() {
        .vab-colorful-card {
            .el-card__header {
                font-size: 24px;
            }

            i {
                top: 25px;
                transform: none;
            }
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
