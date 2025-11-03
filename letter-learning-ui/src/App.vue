<template>
    <vab-app />
</template>

<script lang="ts" setup>
    import DisableDevtool from 'disable-devtool'
    import { noDebugger } from '@/config/index'

    defineOptions({
        name: 'App',
    })

    const route = useRoute()

    onMounted(() => {
        // 是否允许生产环境进行代码调试，请前往config/cli.config.ts文件配置

        setTimeout(() => {
            if (
                !location.hostname.includes('127') &&
                !location.hostname.includes('localhost') &&
                (location.hostname.includes('beautiful') ||
                    location.hostname.includes('vuejs-core') ||
                    noDebugger) &&
                route.query &&
                route.query.debugger !== 'auto'
            )
                DisableDevtool({
                    url: 'https://vuejs-core.cn/debugger',
                    timeOutUrl: 'https://vuejs-core.cn/debugger',
                })
        }, 500)
    })
</script>
