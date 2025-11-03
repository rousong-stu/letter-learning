<script lang="ts" setup>
    const appList = ref([
        {
            icon: 'vuejs-fill',
            color: '#42b883',
            title: 'Vue.js Admin',
            type: '管理后台',
            downloads: '12.5k',
            rating: 4.8,
            description: '基于Vue3的管理系统模板',
        },
        {
            icon: 'reactjs-line',
            color: '#61dafb',
            title: 'React Dashboard',
            type: '数据面板',
            downloads: '8.9k',
            rating: 4.6,
            description: 'React数据可视化面板',
        },
        {
            icon: 'angularjs-line',
            color: '#dd0031',
            title: 'Angular Admin',
            type: '企业应用',
            downloads: '6.2k',
            rating: 4.4,
            description: 'Angular企业级管理系统',
        },
        {
            icon: 'flutter-line',
            color: '#02569b',
            title: 'Flutter App',
            type: '移动应用',
            downloads: '15.3k',
            rating: 4.9,
            description: '跨平台移动应用框架',
        },
    ])

    const getRatingColor = (rating: number) => {
        if (rating >= 4.5) return '#52c41a'
        if (rating >= 4.0) return '#faad14'
        return '#f5222d'
    }
</script>

<template>
    <vab-card shadow="never">
        <template #header>
            <vab-icon icon="medal-line" />
            热门应用
        </template>
        <div class="medal-list">
            <div
                v-for="(item, index) in appList"
                :key="index"
                class="medal-list-item"
            >
                <div class="medal-list-item-rank"></div>
                <div class="medal-list-item-img">
                    <div :style="{ background: item.color }">
                        <vab-icon :icon="item.icon" />
                    </div>
                </div>
                <div class="medal-list-item-left">
                    <div class="item-title">{{ item.title }}</div>
                    <div class="item-stats">
                        <span class="downloads">
                            <vab-icon icon="download-line" />
                            {{ item.downloads }}
                        </span>
                        <span
                            class="rating"
                            :style="{ color: getRatingColor(item.rating) }"
                        >
                            <vab-icon icon="star-fill" />
                            {{ item.rating }}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </vab-card>
</template>

<style lang="scss" scoped>
    .medal-list {
        &-item {
            position: relative;
            clear: both;
            display: block;
            width: 100%;
            height: 80px;
            background: #fff;
            border-radius: 0;

            $position: (
                1: -5px -122px,
                2: -64px -83px,
                3: -123px -5px,
                4: -123px -39px,
                5: -123px -73px,
            );

            @each $key, $item in $position {
                &:nth-child(#{$key}) {
                    .medal-list-item-rank {
                        background-position: $item;
                    }
                }
            }

            &::after {
                position: absolute;
                right: 20px;
                bottom: 0;
                left: 20px;
                width: calc(100% - 40px);
                height: 1px;
                content: '';
                background: #f0f0f0;
            }

            &-img {
                float: left;
                margin: 10px 16px 25px 56px;
            }

            &-img > div {
                width: 56px;
                height: 56px;
                margin: auto;
                line-height: 56px;
                text-align: center;
                border-radius: 12px;

                i {
                    display: block;
                    width: 50px;
                    height: 50px;
                    margin: auto;
                    font-size: 30px;
                    color: #fff;
                    transition: all ease-in-out 0.3s;
                }
            }

            &-rank {
                position: absolute;
                top: 26px;
                left: 20px;
                width: 24px;
                height: 24px;
                background-image: url('~@/assets/rank_images/rank.png');
                background-size: 152px 151px;
            }

            &-left {
                float: left;
                height: 48px;
                margin: 10px 0 18px;

                .item-title {
                    width: 175px;
                    margin-bottom: 10px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    font-size: 20px;
                    color: #333;
                    white-space: nowrap;
                }

                .item-stats {
                    display: flex;
                    gap: 16px;
                    margin-top: 8px;

                    .downloads,
                    .rating {
                        display: flex;
                        align-items: center;
                        font-size: 12px;
                        color: #666;

                        i {
                            margin-right: 4px;
                            font-size: 14px;
                        }
                    }
                }
            }
        }
    }
</style>
