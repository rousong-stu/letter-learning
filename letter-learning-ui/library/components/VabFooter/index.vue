<template>
    <footer class="vab-footer">
        <span>Copyright ©2025 </span>
        <a href="https://www.lumilyx.cn" target="_blank" rel="noopener">www.lumilyx.cn</a>
        <span> | </span>
        <a
            class="icp-link"
            href="https://beian.miit.gov.cn"
            target="_blank"
            rel="noopener"
        >
            蜀ICP备2025152100号-2
        </a>
        <span> | 四川大成迅龙数据科技有限公司 版权所有</span>
    </footer>
</template>

<style lang="scss" scoped>
    .vab-footer {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 55px;
        padding: 0 #{$base-padding} 0 #{$base-padding};
        color: rgba(0, 0, 0, 0.45);
        background: var(--el-color-white);
        border-top: 1px dashed #{$base-border-color};

        a {
            color: rgba(0, 0, 0, 0.45);
            text-decoration: none;
        }

        a:hover {
            color: var(--el-color-primary);
            text-decoration: underline;
        }

        .icp-link {
            margin: 0 4px;
        }
    }
</style>
