<template>
    <div class="pricing-template-container">
        <el-row :gutter="20">
            <el-col :span="24">
                <div class="pricing-header">
                    <h1>请选择适合您的前端模板</h1>
                    <p>
                        根据《中华人民共和国消费者权益保护法》和相关规定，对于计算机软件等数字化商品，下单后不支持退货退款，感谢您的理解与支持。
                    </p>
                </div>
            </el-col>
        </el-row>

        <el-row :gutter="20" justify="center">
            <el-col
                v-for="plan in pricingPlans"
                :key="plan.id"
                :lg="8"
                :md="12"
                :sm="24"
                :xl="8"
                :xs="24"
            >
                <vab-card
                    class="pricing-card"
                    :class="{ 'pricing-card-popular': plan.popular }"
                >
                    <div v-if="plan.popular" class="pricing-popular-tag">
                        最受欢迎
                    </div>
                    <div class="pricing-card-header">
                        <h3>{{ plan.name }}</h3>
                        <div class="pricing-price">
                            <span class="pricing-amount">
                                ￥{{ plan.price }}
                            </span>
                            <span class="pricing-period">
                                {{ plan.period }}
                            </span>
                        </div>
                        <div class="pricing-description">
                            {{ plan.description }}
                        </div>
                    </div>

                    <div class="pricing-card-body">
                        <ul class="pricing-features">
                            <li
                                v-for="(feature, index) in plan.features"
                                :key="index"
                            >
                                <el-icon class="pricing-icon">
                                    <success-filled v-if="feature.included" />
                                    <circle-close-filled v-else />
                                </el-icon>
                                <span
                                    :class="{
                                        'pricing-feature-disabled':
                                            !feature.included,
                                    }"
                                >
                                    {{ feature.name }}
                                </span>
                            </li>
                        </ul>

                        <el-button
                            class="pricing-button"
                            type="primary"
                            @click="selectPlan(plan.price)"
                        >
                            一键购买
                        </el-button>
                    </div>
                </vab-card>
            </el-col>
        </el-row>
    </div>
</template>

<script lang="ts" setup>
    import { ref } from 'vue'
    import { CircleCloseFilled, SuccessFilled } from '@element-plus/icons-vue'

    defineOptions({
        name: 'PricingTemplate',
    })

    interface PricingFeature {
        name: string
        included: boolean
    }

    interface PricingPlan {
        id: number
        name: string
        price: string
        period: string
        description: string
        popular: boolean
        features: PricingFeature[]
    }

    const pricingPlans = ref<PricingPlan[]>([
        {
            id: 1,
            name: 'Vue Admin Plus',
            price: '799',
            period: '/份',
            description: '',
            popular: false,
            features: [
                {
                    name: 'vue3.x + element-plus 前后端分离开发模式',
                    included: true,
                },
                {
                    name: '最多用户购买的版本，稳定、安全、可靠',
                    included: true,
                },
                { name: '兼容电脑、手机、平板', included: true },
                {
                    name: '9种主题（蓝黑、蓝白、绿黑、绿白、渐变等）',
                    included: true,
                },
                {
                    name: '6种布局（分栏、综合、纵向、横向、常规、浮动）',
                    included: true,
                },
                { name: '友好的交互体验，减轻浏览器负载', included: true },
                { name: '专属的开发者文档，助你快速掌握', included: true },
            ],
        },
        {
            id: 2,
            name: 'Vue Admin Max',
            price: '1299',
            period: '/份',
            description: '',
            popular: true,
            features: [
                {
                    name: '包含Admin Pro + Admin Plus所有仓库及更新权益',
                    included: true,
                },
                { name: '赠送Dashboard Pro科技风模板', included: true },
                {
                    name: '赠送大屏模板',
                    included: true,
                },
                { name: '兼容电脑、手机、平板', included: true },
                {
                    name: '9种主题（蓝黑、蓝白、绿黑、绿白、渐变等）',
                    included: true,
                },
                {
                    name: '6种布局（分栏、综合、纵向、横向、常规、浮动）',
                    included: true,
                },
                { name: '更友好的交互体验，减轻浏览器负载', included: true },
                { name: '专属的开发者文档，助你快速掌握', included: true },
                {
                    name: 'Admin Pro、Admin Plus用户支持补差价升级到Admin Max版本',
                    included: true,
                },
            ],
        },
        {
            id: 3,
            name: 'Vue Admin Pro',
            price: '699',
            period: '/份',
            description: '',
            popular: false,
            features: [
                {
                    name: 'vue2.x + element-ui 前后端分离开发模式',
                    included: true,
                },
                { name: '兼容电脑、手机、平板', included: true },
                {
                    name: '9种主题（蓝黑、蓝白、绿黑、绿白、渐变等）',
                    included: true,
                },
                {
                    name: '6种布局（分栏、综合、纵向、横向、常规、浮动）',
                    included: true,
                },
                { name: '友好的交互体验，减轻浏览器负载', included: true },
                { name: '专属的开发者文档，助你快速掌握', included: true },
            ],
        },
    ])

    const selectPlan = (price: string) => {
        window.open(
            `https://api.vuejs-core.cn/pay/alipayPageRedirect?amount=${price}`
        )
    }
</script>

<style lang="scss" scoped>
    .pricing-header {
        margin-bottom: 40px;
        text-align: center;

        h1 {
            margin-bottom: 15px;
            font-size: 32px;
            font-weight: bold;
        }

        p {
            font-size: 18px;
            color: var(--el-text-color-secondary);
        }
    }

    .pricing-card {
        position: relative;
        overflow: hidden;
        border-radius: var(--el-border-radius-base);
        transition: all 0.3s ease;

        &:hover {
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            transform: translateY(-5px);
        }
    }

    .pricing-card-popular {
        border: 2px solid var(--el-color-primary);

        &:hover {
            transform: translateY(-5px);
        }
    }

    .pricing-popular-tag {
        position: absolute;
        top: 0;
        right: 0;
        z-index: 1;
        padding: 5px 15px;
        font-size: 12px;
        color: white;
        background: var(--el-color-primary);
        border-bottom-left-radius: 10px;
    }

    .pricing-card-header {
        padding: 30px 20px 20px;
        text-align: center;
        border-bottom: 1px solid var(--el-border-color-lighter);

        h3 {
            margin-bottom: 15px;
            font-size: 24px;
            color: var(--el-text-color-primary);
        }
    }

    .pricing-price {
        margin-bottom: 15px;
    }

    .pricing-amount {
        font-size: 36px;
        font-weight: bold;
        color: var(--el-color-primary);
    }

    .pricing-period {
        font-size: 14px;
        color: var(--el-text-color-secondary);
    }

    .pricing-description {
        font-size: 14px;
        color: var(--el-text-color-secondary);
    }

    .pricing-card-body {
        padding: 20px;
    }

    .pricing-features {
        padding: 0;
        margin: 0 0 30px;
        list-style: none;

        li {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            font-size: 14px;

            &:last-child {
                margin-bottom: 0;
            }
        }
    }

    .pricing-icon {
        margin-right: 10px;
        font-size: 16px;
    }

    .pricing-feature-disabled {
        color: var(--el-text-color-disabled);

        .pricing-icon {
            color: var(--el-color-danger);
        }
    }

    .pricing-button {
        width: 100%;
        height: 45px;
        font-size: 16px;
    }
</style>
