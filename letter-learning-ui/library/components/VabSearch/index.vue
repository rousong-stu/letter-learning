<script lang="ts" setup>
    import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
    import { useRouter } from 'vue-router'
    import { storeToRefs } from 'pinia'
    import { useRoutesStore } from '@/store/modules/routes'

    const isMac = /macintosh|mac os x/i.test(navigator.userAgent)
    const MOD_KEY = isMac ? 'metaKey' : 'ctrlKey'

    const show = ref(false)
    const search = ref('')
    const activeIndex = ref(0)
    const inputRef = ref<HTMLInputElement | null>(null)

    const routesStore = useRoutesStore()
    const { getRoutes } = storeToRefs(routesStore)
    const router = useRouter()

    // 递归平铺所有菜单项
    function flattenMenus(
        routes: any[],
        basePath = '',
        parentIcon = undefined
    ): any[] {
        let result: any[] = []
        routes.forEach((route) => {
            if (route.meta && route.meta.hidden) return
            const fullPath = route.path.startsWith('/')
                ? route.path
                : `${basePath}/${route.path}`
            const icon =
                route.meta && route.meta.icon ? route.meta.icon : parentIcon
            if (route.meta && route.meta.title) {
                result.push({
                    title: route.meta.title,
                    path: fullPath,
                    icon,
                    ...route.meta,
                })
            }
            if (route.children && route.children.length > 0) {
                result = result.concat(
                    flattenMenus(route.children, fullPath, icon)
                )
            }
        })
        return result
    }

    const menuList = computed(() => flattenMenus(getRoutes.value))

    // 搜索历史（localStorage）
    const HISTORY_KEY = 'vab_search_history'
    const searchHistory = ref<string[]>([])
    function loadHistory() {
        const raw = localStorage.getItem(HISTORY_KEY)
        searchHistory.value = raw ? JSON.parse(raw) : []
    }
    function saveHistory(keyword: string) {
        if (!keyword) return
        let arr = searchHistory.value.filter((item) => item !== keyword)
        arr.unshift(keyword)
        if (arr.length > 8) arr = arr.slice(0, 8)
        searchHistory.value = arr
        localStorage.setItem(HISTORY_KEY, JSON.stringify(arr))
    }
    function removeHistory(keyword: string) {
        searchHistory.value = searchHistory.value.filter(
            (item) => item !== keyword
        )
        localStorage.setItem(HISTORY_KEY, JSON.stringify(searchHistory.value))
    }
    function clearHistory() {
        searchHistory.value = []
        localStorage.removeItem(HISTORY_KEY)
    }

    // 简单模糊搜索（可扩展为拼音/多字段）
    const filteredMenus = computed(() => {
        if (!search.value) return menuList.value
        return menuList.value.filter(
            (item) =>
                item.title.toLowerCase().includes(search.value.toLowerCase()) ||
                (item.path &&
                    item.path
                        .toLowerCase()
                        .includes(search.value.toLowerCase()))
        )
    })

    function openSearch() {
        show.value = true
        search.value = ''
        activeIndex.value = 0
        loadHistory()
        nextTick(() => {
            inputRef.value?.focus()
        })
    }
    function closeSearch() {
        show.value = false
    }
    function selectMenu(index: number) {
        const item = filteredMenus.value[index]
        if (item && item.path) {
            saveHistory(search.value)
            closeSearch()

            // 检查是否为外链
            if (
                item.target === '_blank' ||
                item.path.startsWith('http://') ||
                item.path.startsWith('https://') ||
                item.path.startsWith('//')
            ) {
                // 外链使用window.open
                window.open(item.path, '_blank')
            } else {
                // 内部路由使用router.push
                router.push(item.path)
            }
        }
    }
    function selectHistory(keyword: string) {
        search.value = keyword
        activeIndex.value = 0
        nextTick(() => {
            inputRef.value?.focus()
        })
    }
    function onKeydown(e: KeyboardEvent) {
        if (show.value) {
            if (e.key === 'Escape') {
                closeSearch()
            } else if (e.key === 'ArrowDown') {
                e.preventDefault()
                activeIndex.value =
                    (activeIndex.value + 1) % filteredMenus.value.length
            } else if (e.key === 'ArrowUp') {
                e.preventDefault()
                activeIndex.value =
                    (activeIndex.value - 1 + filteredMenus.value.length) %
                    filteredMenus.value.length
            } else if (e.key === 'Enter') {
                selectMenu(activeIndex.value)
            }
        } else {
            if ((e as any)[MOD_KEY] && e.key.toLowerCase() === 'k') {
                e.preventDefault()
                openSearch()
            }
        }
    }
    onMounted(() => {
        window.addEventListener('keydown', onKeydown)
    })
    onUnmounted(() => {
        window.removeEventListener('keydown', onKeydown)
    })

    function onItemClick(idx: number) {
        selectMenu(idx)
    }
    function onInputKeydown(e: KeyboardEvent) {
        if (
            e.key === 'ArrowDown' ||
            e.key === 'ArrowUp' ||
            e.key === 'Enter' ||
            e.key === 'Escape'
        ) {
            // 交由全局keydown处理
            e.preventDefault()
        }
    }
</script>

<template>
    <span class="vab-search-trigger">
        <vab-icon
            icon="search-line"
            title="菜单搜索 ({{ isMac ? '⌘+K' : 'Ctrl+K' }})"
            @click="openSearch"
        />
    </span>
    <teleport to="body">
        <transition name="fade">
            <div
                v-if="show"
                class="vab-spotlight-mask"
                @click.self="closeSearch"
            >
                <div class="vab-spotlight-card">
                    <div class="vab-spotlight-input-wrap">
                        <vab-icon
                            class="vab-spotlight-input-icon"
                            icon="search-line"
                        />
                        <input
                            ref="inputRef"
                            v-model="search"
                            autocomplete="off"
                            class="vab-spotlight-input"
                            :placeholder="
                                isMac ? '搜索菜单… (⌘+K)' : '搜索菜单… (Ctrl+K)'
                            "
                            @keydown="onInputKeydown"
                        />
                    </div>
                    <div
                        v-if="searchHistory.length"
                        class="vab-spotlight-history-wrap"
                    >
                        <div class="vab-spotlight-history">
                            <div class="vab-spotlight-history-title">
                                搜索历史
                                <span
                                    class="vab-spotlight-history-clear"
                                    @click="clearHistory"
                                >
                                    清空
                                </span>
                            </div>
                            <div class="vab-spotlight-history-list">
                                <span
                                    v-for="item in searchHistory"
                                    :key="item"
                                    class="vab-spotlight-history-item"
                                >
                                    <span @click="selectHistory(item)">
                                        {{ item }}
                                    </span>
                                    <vab-icon
                                        class="vab-spotlight-history-del"
                                        icon="close-circle-fill"
                                        @click.stop="removeHistory(item)"
                                    />
                                </span>
                            </div>
                        </div>
                    </div>
                    <ul class="vab-spotlight-list">
                        <li
                            v-for="(item, idx) in filteredMenus"
                            :key="item.path + item.title"
                            :class="[
                                'vab-spotlight-item',
                                { active: idx === activeIndex },
                            ]"
                            @mousedown.prevent="onItemClick(idx)"
                            @mouseenter="activeIndex = idx"
                        >
                            <vab-icon
                                v-if="item.icon"
                                class="vab-spotlight-item-icon"
                                :icon="item.icon"
                            />
                            <div class="vab-spotlight-item-content">
                                <div class="vab-spotlight-item-title">
                                    {{ item.title }}
                                </div>
                                <div class="vab-spotlight-item-path">
                                    {{ item.path }}
                                </div>
                            </div>
                        </li>
                        <li
                            v-if="filteredMenus.length === 0"
                            class="vab-spotlight-empty"
                        >
                            <div v-if="!search">请输入关键词进行搜索</div>
                            <div v-else>无匹配菜单</div>
                        </li>
                    </ul>
                </div>
            </div>
        </transition>
        <button
            class="vab-spotlight-fab"
            title="菜单搜索 ({{ isMac ? '⌘+K' : 'Ctrl+K' }})"
            @click="openSearch"
        >
            <vab-icon icon="search-line" />
        </button>
    </teleport>
</template>

<style lang="scss" scoped>
    .fade-enter-active,
    .fade-leave-active {
        transition: opacity 0.18s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .fade-enter-from,
    .fade-leave-to {
        opacity: 0;
    }
    .vab-spotlight-mask {
        position: fixed;
        inset: 0;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(30, 34, 45, 0.25);
        backdrop-filter: blur(2px);
    }
    .vab-spotlight-card {
        display: flex;
        flex-direction: column;
        width: 600px;
        max-width: 96vw;
        padding: 0 0 8px 0;
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 18px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.18);
        backdrop-filter: blur(12px) saturate(120%);
        animation: fadeInUp 0.18s cubic-bezier(0.4, 0, 0.2, 1);
    }
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(40px);
        }
        to {
            opacity: 1;
            transform: none;
        }
    }
    .vab-spotlight-input-wrap {
        display: flex;
        align-items: center;
        padding: 24px 28px 12px 28px;
    }
    .vab-spotlight-input-icon {
        margin-right: 10px;
        font-size: 22px;
        color: #666;
    }
    .vab-spotlight-input {
        flex: 1;
        padding: 8px 0;
        font-size: 20px;
        color: #222;
        outline: none;
        background: transparent;
        border: none;
    }
    .vab-spotlight-list {
        max-height: 340px;
        padding: 0 8px 0 8px;
        margin: 0;
        overflow-y: auto;
        list-style: none;
    }
    .vab-spotlight-item {
        display: flex;
        align-items: center;
        padding: 12px 18px;
        margin-bottom: 2px;
        cursor: pointer;
        border-radius: 10px;
        transition: background 0.18s;
        &:last-child {
            margin-bottom: 0;
        }
        &.active,
        &:hover {
            background: #f5f5f5;
        }
    }
    .vab-spotlight-item-icon {
        margin-right: 14px;
        font-size: 26px !important;
        color: #666;
    }
    .vab-spotlight-item-content {
        display: flex;
        flex-direction: column;
        min-width: 0;
    }
    .vab-spotlight-item-title {
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 16px;
        font-weight: 600;
        line-height: 1.2;
        color: #222;
        white-space: nowrap;
    }
    .vab-spotlight-item-path {
        margin-top: 2px;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 12px;
        color: #8c8c8c;
        white-space: nowrap;
    }
    .vab-spotlight-empty {
        padding: 32px 0 24px 0;
        font-size: 15px;
        color: #aaa;
        text-align: center;
    }
    .vab-spotlight-fab {
        position: fixed;
        right: 32px;
        bottom: 32px;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 56px;
        height: 56px;
        font-size: 28px;
        color: #fff;
        cursor: pointer;
        outline: none;
        background: #666;
        border: none;
        border-radius: 50%;
        box-shadow: 0 4px 16px 0 rgba(102, 102, 102, 0.18);
        transition:
            background 0.18s,
            box-shadow 0.18s,
            transform 0.18s;
        &:hover {
            background: #888;
            box-shadow: 0 8px 32px 0 rgba(102, 102, 102, 0.18);
            transform: translateY(-2px) scale(1.06);
        }
        &:active {
            background: #555;
            transform: scale(0.98);
        }
    }
    @media (max-width: 600px) {
        .vab-spotlight-card {
            width: 98vw;
            min-width: 0;
            padding: 0 0 8px 0;
        }
        .vab-spotlight-input-wrap {
            padding: 18px 10px 10px 10px;
        }
        .vab-spotlight-fab {
            right: 16px;
            bottom: 16px;
            width: 48px;
            height: 48px;
            font-size: 22px;
        }
    }
    .vab-search-trigger {
        display: inline-flex;
        align-items: center;
        font-size: 22px;
        color: #666;
        cursor: pointer;
        transition: color 0.18s;
        &:hover {
            color: #666;
        }
    }
    .vab-spotlight-history-wrap {
        padding: 0 28px 0 28px;
        margin-bottom: 8px;
    }
    .vab-spotlight-history-title {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 4px;
        font-size: 13px;
        color: #888;
    }
    .vab-spotlight-history-clear {
        margin-left: 8px;
        font-size: 12px;
        color: #aaa;
        cursor: pointer;
        &:hover {
            color: #ff4d4f;
        }
    }
    .vab-spotlight-history-list {
        display: flex;
        flex-wrap: wrap;
        gap: 8px 12px;
        margin-bottom: 8px;
    }
    .vab-spotlight-history-item {
        display: inline-flex;
        align-items: center;
        padding: 2px 12px 2px 10px;
        font-size: 14px;
        color: #666;
        cursor: pointer;
        background: #f5f7fa;
        border-radius: 16px;
        transition:
            background 0.18s,
            color 0.18s;
        &:hover {
            color: #666;
            background: #f5f5f5;
        }
    }
    .vab-spotlight-history-del {
        margin-left: 4px;
        font-size: 14px;
        color: #bbb;
        cursor: pointer;
        &:hover {
            color: #ff4d4f;
        }
    }
</style>
