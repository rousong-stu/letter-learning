<template>
    <vab-card class="authorization" shadow="never">
        <template #header>
            <vab-icon icon="brain-line" />
            记忆曲线
            <el-tag class="card-header-tag" type="warning">周</el-tag>
        </template>
        <vab-chart
            :init-options="initOptions"
            :option="option"
            theme="vab-echarts-theme"
        />
        <div class="bottom">
            <span>
                记忆达成率:
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
        name: 'Authorization',
        components: {
            VabChart,
            VabCount,
        },
        setup() {
            const settingsStore = useSettingsStore()
            const { echartsGraphic2 } = storeToRefs(settingsStore)
            const state = reactive({
                countConfig: {
                    startVal: 0,
                    endVal: _.random(60, 100),
                    decimals: 0,
                    prefix: '',
                    suffix: '%',
                    separator: '',
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
                            data: ['11/12', '11/13', '11/14', '11/15', '11/16', '11/17'],
                            axisTick: { alignWithLabel: true },
                        },
                    ],
                    yAxis: [{ type: 'value', max: 100 }],
                    series: [
                        {
                            name: '记忆达成率',
                            type: 'line',
                            smooth: true,
                            data: [62, 68, 70, 72, 75, 78],
                            areaStyle: {},
                            itemStyle: {
                                color: new VabChart.graphic.LinearGradient(
                                    0,
                                    0,
                                    0,
                                    1,
                                    echartsGraphic2.value.map((color, offset) => ({
                                        color,
                                        offset,
                                    }))
                                ),
                            },
                        },
                    ],
                },
            })

            watch(
                () => echartsGraphic2.value,
                () => {
                    state.option.series[0].itemStyle.color =
                        new VabChart.graphic.LinearGradient(
                            0,
                            0,
                            0,
                            1,
                            echartsGraphic2.value.map((color, offset) => ({
                                color,
                                offset,
                            }))
                        )
                }
            )

            onMounted(() => {
                getDashboardSummary()
                    .then((resp) => {
                        const curve = resp.data?.memory_curve || []
                        state.option.xAxis[0].data = curve.map((c) =>
                            c.date ? c.date.slice(5) : ''
                        )
                        state.option.series[0].data = curve.map(
                            (c) => c.rate || 0
                        )
                        state.countConfig.endVal =
                            resp.data?.summary?.completion_rate || 0
                    })
                    .catch((err) => console.error(err))
            })

            return {
                ...toRefs(state),
            }
        },
    })
</script>
