<template>
    <div class="errorLog-container">
        <el-button type="primary" @click="handleError">
            点击模拟一个zxwk1998jiayou的错误
        </el-button>
        <error-test v-if="show" />
    </div>
</template>

<script>
    import ErrorTest from './components/ErrorTest'

    export default defineComponent({
        name: 'ErrorLog',
        components: { ErrorTest },
        setup() {
            const $baseMessage = inject('$baseMessage')

            const state = reactive({
                show: false,
            })

            const handleError = () => {
                if (process.env.NODE_ENV === 'production') {
                    $baseMessage(
                        '\u4E3A\u4E86\u9632\u6B62\u5F15\u8D77\u6B67\u4E49\uFF0C\u6F14\u793A\u73AF\u5883\u4E0D\u5141\u8BB8\u6A21\u62DF\u9519\u8BEF\uFF0C\u8BF7\u4E0B\u8F7D\u6E90\u7801\u540E\u4F53\u9A8C\u6B64\u529F\u80FD\u3002',
                        'error',
                        'vab-hey-message-error'
                    )
                }
                state.show = true
            }
            return {
                ...toRefs(state),
                handleError,
            }
        },
    })
</script>
