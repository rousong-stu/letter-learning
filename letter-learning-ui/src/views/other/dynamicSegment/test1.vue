<template>
    <div class="test1-container">
        <el-alert :closable="false" show-icon title="params" type="success" />
        <vab-json-viewer copyable :expand-depth="5" sort :value="route" />
    </div>
</template>

<script>
    import VabJsonViewer from 'vue-json-viewer'
    import { useTabsStore } from '@/store/modules/tabs'

    export default defineComponent({
        name: 'Test1',
        components: { VabJsonViewer },
        setup() {
            const route = useRoute()

            const tabsStore = useTabsStore()
            const { changeTabsMeta } = tabsStore

            const state = reactive({
                route: {},
            })
            const handleParams = () => {
                nextTick(() => {
                    changeTabsMeta({
                        title: 'Query',
                        meta: {
                            title: `Query Id=${route.query.id}`,
                        },
                    })

                    const _route = route.matched[0].children.find(
                        (item) => item.name === 'Test1'
                    )
                    const id = route.path.substring(
                        route.path.lastIndexOf('/') + 1,
                        route.path.length
                    )

                    state.route = {
                        path: _route.path,
                        params: {
                            id,
                        },
                        name: _route.name,
                        meta: _route.meta,
                    }
                })
            }
            onMounted(() => {
                handleParams()
            })

            return {
                ...toRefs(state),
            }
        },
    })
</script>
