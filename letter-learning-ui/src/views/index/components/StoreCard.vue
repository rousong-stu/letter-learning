<script lang="ts" setup>
    const $baseAlert: any = inject('$baseAlert')
    const router = useRouter()

    const iconList = [
        {
            icon: 'apps-line',
            color: '#95de64',
            title: '应用管理',
            description: '管理系统应用',
            route: '/vab/table/comprehensiveTable',
        },
        {
            icon: 'brush-2-line',
            color: '#69c0ff',
            title: '主题设置',
            description: '个性化主题',
            route: '/other/theme',
        },
        {
            icon: 'upload-cloud-2-line',
            color: '#ffd666',
            title: '文件上传',
            description: '上传文件管理',
            route: '/other/upload',
        },
        {
            icon: 'baidu-line',
            color: '#1890FF',
            title: '数据统计',
            description: '查看数据报表',
            route: '/vab/echarts',
        },
        {
            icon: 'video-line',
            color: '#ffc069',
            title: '媒体中心',
            description: '视频图片管理',
            route: '/other/notice',
        },
        {
            icon: 'table-line',
            color: '#5cdbd3',
            title: '表格组件',
            description: '数据表格展示',
            route: '/vab/table/customTable',
        },
    ]

    const handleClick = (item: any) => {
        if (item.route) {
            router.push(item.route)
        } else {
            $baseAlert('功能开发中，敬请期待！')
        }
    }
</script>

<template>
    <vab-card shadow="never">
        <template #header>
            <vab-icon icon="anticlockwise-2-line" />
            快捷方式
        </template>

        <el-row :gutter="20">
            <el-col
                v-for="(item, index) in iconList"
                :key="index"
                :lg="8"
                :md="8"
                :sm="8"
                :xl="8"
                :xs="12"
            >
                <vab-card class="icon-panel" @click="handleClick(item)">
                    <div :style="{ background: item.color }">
                        <vab-icon :icon="item.icon" />
                    </div>
                    <div class="icon-info">
                        <div class="icon-title">{{ item.title }}</div>
                        <div class="icon-description">
                            {{ item.description }}
                        </div>
                    </div>
                </vab-card>
            </el-col>
        </el-row>
    </vab-card>
</template>

<style lang="scss" scoped>
    .icon-panel {
        margin-bottom: 20px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;

        &:hover {
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            transform: translateY(-4px);
        }

        .el-card__body {
            height: 140px;
            padding: 16px;

            &:hover {
                i {
                    transform: scale(1.1);
                }
            }

            > div:first-child {
                display: flex;
                align-items: center;
                justify-content: center;
                width: 60px;
                height: 60px;
                margin: 0 auto 12px;
                border-radius: 12px;

                i {
                    font-size: 30px;
                    color: #fff;
                    transition: all ease-in-out 0.3s;
                }
            }
        }

        .icon-info {
            text-align: center;

            .icon-title {
                margin-bottom: 8px;
                font-size: 14px;
                font-weight: 600;
                line-height: 1.2;
                color: #333;
            }

            .icon-description {
                font-size: 12px;
                line-height: 1.5;
                color: #999;
                word-break: break-all;
            }
        }
    }
</style>
