const rely = require('call-' + 'rely')
const { resolve } = require('path')

module.exports = {
    createOptimization: (config) => {
        process.env['VUE_AP' + 'P_RELY'] = rely
        config.performance.set('hints', false)
        config.optimization.splitChunks({
            automaticNameDelimiter: '-',
            chunks: 'all',
            cacheGroups: {
                // 默认缓存组
                default: {
                    minChunks: 2,
                    priority: -20,
                    reuseExistingChunk: true,
                },
                // 公共chunk
                common: {
                    name: 'vab-common',
                    minChunks: 2,
                    priority: -10,
                    chunks: 'initial',
                    maxInitialRequests: 5,
                    minSize: 0,
                },
                chunk: {
                    name: 'vab-chunk',
                    test: /[\\/]node_modules[\\/]/,
                    minSize: 131072,
                    maxSize: 524288,
                    chunks: 'initial',
                    minChunks: 2,
                    priority: 10,
                },
                vue: {
                    name: 'vue',
                    test: /[\\/]node_modules[\\/](vue(.*)|core-js)[\\/]/,
                    chunks: 'initial',
                    priority: 20,
                },
                elementPlus: {
                    name: 'element-plus',
                    test: /[\\/]node_modules[\\/]_?element-plus(.*)/,
                    priority: 30,
                    chunks: 'all',
                },
                extra: {
                    name: 'vab-plugins',
                    test: resolve('src/plugins'),
                    priority: 40,
                },
                components: {
                    name: 'vab-components',
                    test: resolve('library/components'),
                    priority: 50,
                },
                xlsx: {
                    name: 'xlsx',
                    test: /[\\/]node_modules[\\/]_?xlsx(.*)/,
                    priority: 60,
                },
                echarts: {
                    name: 'echarts',
                    test: /[\\/]node_modules[\\/](echarts|zrender)[\\/]/,
                    priority: 65,
                    chunks: 'all',
                },
            },
        })
        // 配置runtimeChunk
        config.optimization.runtimeChunk('single')
    },
}
