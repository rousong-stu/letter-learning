<template>
    <div></div>
</template>

<script setup lang="ts">
    defineOptions({
        name: 'Direct',
    })

    const route = useRoute()
    const router = useRouter()
    const query = route.query

    // 根据query中的path参数进行路由跳转
    if (query.path) {
        router.push(query.path as string)
    }
</script>
