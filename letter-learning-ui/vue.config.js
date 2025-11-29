/* eslint-disable @typescript-eslint/no-unused-vars */

/**
 * @description vue.config.js全局配置
 */

const {
    baseURL,
    title,
    devPort,
    assetsDir,
    outputDir,
    lintOnSave,
    publicPath,
    transpileDependencies,
} = require('./src/config')
const dayjs = require('dayjs')
const pkg = require('./package.json')

const { resolve, relative } = require('path')
const { defineConfig } = require('@vue/cli-service')
const {
    createVuePlugin,
    createChainWebpack,
} = require('./library/build/index.ts')

const pc = require('picocolors')

const info = {
    ...pkg,
    lastBuildTime: dayjs().format('YYYY-MM-DD HH:mm:ss'),
}

process.env.VUE_APP_TITLE = title
process.env.VUE_APP_AUTHOR = pkg.author
process.env.VUE_APP_INFO = JSON.stringify(info)
process.env.VUE_APP_UPDATE_TIME = info.lastBuildTime
process.env.VUE_APP_GITHUB_USER_NAME = process.env.VUE_GITHUB_USER_NAME
process.env.VUE_APP_RANDOM = `${info.lastBuildTime}-${process.env.VUE_GITHUB_USER_NAME}`

module.exports = defineConfig({
    publicPath,
    assetsDir,
    outputDir,
    lintOnSave: false,   // ← 这里才是正确位置
    transpileDependencies,
    parallel: true,
    devServer: {
        compress: true,
        client: {
            progress: false,
            overlay: {
                warnings: false,
                errors: true,
            },
        },
        hot: true,
        port: devPort,
    },
    configureWebpack() {
        return {
            cache: {
                type: 'filesystem',
                buildDependencies: {
                    config: [__filename],
                },
                version: pkg.version,
            },
            resolve: {
                alias: {
                    '~': resolve(__dirname, '.'),
                    '@': resolve(__dirname, 'src'),
                    '/#': resolve(__dirname, 'types'),
                    '@vab': resolve(__dirname, 'library'),
                    '@gp': resolve(__dirname, 'library/plugins/vab'), // ← 修正
                },
                fallback: {
                    fs: false,
                    path: require.resolve('path-browserify'),
                },
            },
            plugins: createVuePlugin(),
            performance: {
                hints: false,
            },
        }
    },
    chainWebpack(config) {
        createChainWebpack(process.env.NODE_ENV, config)
        // 将 lottie-player 视为自定义元素，避免 Vue 解析组件报错
        config.module
            .rule('vue')
            .use('vue-loader')
            .tap((options) => {
                options.compilerOptions = options.compilerOptions || {}
                const origin = options.compilerOptions.isCustomElement
                options.compilerOptions.isCustomElement = (tag) => {
                    if (origin && origin(tag)) return true
                    return tag === 'lottie-player'
                }
                return options
            })
    },
    runtimeCompiler: false,
    productionSourceMap: false,
    css: {
        sourceMap: false,
        extract:
            process.env.NODE_ENV === 'production'
                ? {
                      ignoreOrder: true,
                  }
                : false,
        loaderOptions: {
            sass: {
                sassOptions: { outputStyle: 'expanded' },
                additionalData(content, { rootContext, resourcePath }) {
                    const relativePath = relative(rootContext, resourcePath)
                    if (
                        relativePath.replace(/\\/g, '/') !==
                        'library/styles/variables/variables.module.scss'
                    )
                        return `@use "~@vab/styles/variables/variables.module.scss" as *;${content}`
                    return content
                },
            },
        },
    },
})
