<script lang="ts" setup>
    const carouselItems = ref([
        {
            title: '系统监控',
            description: '实时监控系统性能，快速定位问题',
            image: 'https://gcore.jsdelivr.net/gh/zxwk1998/image/table/vab-image-1.jpg',
            color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        },
        {
            title: '数据可视化',
            description: '丰富的图表组件，直观展示数据趋势',
            image: 'https://gcore.jsdelivr.net/gh/zxwk1998/image/table/vab-image-2.jpg',
            color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        },
        {
            title: '用户管理',
            description: '完善的用户权限管理，保障系统安全',
            image: 'https://gcore.jsdelivr.net/gh/zxwk1998/image/table/vab-image-3.jpg',
            color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        },
        {
            title: '工作流引擎',
            description: '灵活的工作流配置，提升业务效率',
            image: 'https://gcore.jsdelivr.net/gh/zxwk1998/image/table/vab-image-4.jpg',
            color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
        },
    ])
</script>

<template>
    <el-carousel height="180px" :interval="4000">
        <el-carousel-item v-for="(item, index) in carouselItems" :key="index">
            <div class="carousel-content" :style="{ background: item.color }">
                <div class="carousel-overlay"></div>
                <img :alt="item.title" :src="item.image" />
                <div class="carousel-text">
                    <h3>{{ item.title }}</h3>
                    <p>{{ item.description }}</p>
                </div>
            </div>
        </el-carousel-item>
    </el-carousel>
</template>

<style lang="scss" scoped>
    .el-carousel {
        margin-bottom: 20px;
        overflow: hidden;
        border-radius: 8px;

        &__item {
            .carousel-content {
                position: relative;
                display: flex;
                align-items: center;
                width: 100%;
                height: 100%;
                overflow: hidden;

                img {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    opacity: 0.8;
                }

                .carousel-overlay {
                    position: absolute;
                    top: 0;
                    left: 0;
                    z-index: 1;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.3);
                }

                .carousel-text {
                    position: relative;
                    z-index: 2;
                    padding: 0 24px;
                    color: #fff;
                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);

                    h3 {
                        margin: 0 0 8px 0;
                        font-size: 24px;
                        font-weight: 600;
                        line-height: 1.2;
                    }

                    p {
                        margin: 0;
                        font-size: 14px;
                        line-height: 1.4;
                        opacity: 0.9;
                    }
                }
            }
        }

        :deep(.el-carousel__indicators) {
            bottom: 20px;

            .el-carousel__indicator {
                .el-carousel__button {
                    width: 8px;
                    height: 8px;
                    background-color: rgba(255, 255, 255, 0.6);
                    border-radius: 50%;
                }

                &.is-active .el-carousel__button {
                    background-color: #fff;
                    transform: scale(1.2);
                }
            }
        }
    }
</style>
