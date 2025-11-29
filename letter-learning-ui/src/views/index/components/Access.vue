<template>
    <vab-card class="access" shadow="never">
        <template #header>
            <vab-icon icon="chat-smile-2-line" />
            对话次数
            <el-tag class="card-header-tag" type="success">日</el-tag>
        </template>
        <vab-chart
            :init-options="initOptions"
            :option="option"
            theme="vab-echarts-theme"
        />
        <div class="bottom">
            <span>
                日均对话轮次:
                <vab-count
                    :decimals="countConfig.decimals"
                    :duration="countConfig.duration"
                    :end-val="countConfig.endVal"
                    :prefix="countConfig.prefix"
                    :separator="countConfig.separator"
                    :start-val="countConfig.startVal"
                    :suffix="countConfig.suffix"
                />
            </span>
        </div>
    </vab-card>
</template>

<script>
    import _ from 'lodash'
    import VabChart from '@/plugins/VabChart'
    import VabCount from '@/plugins/VabCount'
    import { useSettingsStore } from '@/store/modules/settings'
    import { getDashboardSummary } from '@/api/dashboard'

    export default defineComponent({
        components: {
            VabChart,
            VabCount,
        },
        setup() {
            const settingsStore = useSettingsStore()
            const { echartsGraphic1 } = storeToRefs(settingsStore)
            const state = reactive({
                countConfig: {
                    startVal: 0,
                    endVal: _.random(100, 400),
                    decimals: 0,
                    prefix: '',
                    suffix: '',
                    separator: ',',
                    duration: 8000,
                },
                initOptions: {
                    renderer: 'svg',
                },
                option: {
                    tooltip: {
                        trigger: 'axis',
                        extraCssText: 'z-index:1',
                    },
                    grid: {
                        top: '5%',
                        left: '2%',
                        right: '4%',
                        bottom: '0%',
                        containLabel: true,
                    },
                    xAxis: [
                        {
                            type: 'category',
                            boundaryGap: false,
                            data: [],
                            axisTick: {
                                alignWithLabel: true,
                            },
                        },
                    ],
                    yAxis: [
                        {
                            type: 'value',
                        },
                    ],
                    series: [
                        {
                            name: '对话次数',
                            type: 'line',
                            data: [],
                            smooth: true,
                            areaStyle: {},
                            itemStyle: {
                                borderRadius: [0, 5, 5, 0],
                                color: new VabChart.graphic.LinearGradient(
                                    0,
                                    0,
                                    1,
                                    0,
                                    echartsGraphic1.value.map(
                                        (color, offset) => ({
                                            color,
                                            offset,
                                        })
                                    )
                                ),
                            },
                        },
                    ],
                },
            })

            watch(
                () => echartsGraphic1.value,
                () => {
                    state.option.series[0].itemStyle.color =
                        new VabChart.graphic.LinearGradient(
                            0,
                            0,
                            1,
                            0,
                            echartsGraphic1.value.map((color, offset) => ({
                                color,
                                offset,
                            }))
                        )
                }
            )

            const loadData = async () => {
                const resp = await getDashboardSummary()
                const trends = resp.data?.chat_trends || []
                state.option.xAxis[0].data = trends.map((t) =>
                    t.date ? t.date.slice(5) : ''
                )
                state.option.series[0].data = trends.map((t) => t.count || 0)
                state.countConfig.endVal = trends.reduce(
                    (sum, t) => sum + (t.count || 0),
                    0
                )
            }

            onMounted(() => {
                loadData().catch((err) => console.error(err))
            })

            return {
                ...toRefs(state),
            }
        },
    })
</script>
