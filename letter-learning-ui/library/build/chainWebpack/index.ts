const { createGzip } = require('./gzip/index.ts')
const { createBanner } = require('./banner/index.ts')
// const { createBuild7z } = require('./build7z/index.ts')   // 已禁用，避免 ESM 报错
const { createSvgSprite } = require('./svgSprite/index.ts')
const { createOptimization } = require('./optimization/index.ts')
const { createSourceInjector } = require('./sourceInjector/index.ts')
const { createImageCompression } = require('./imageCompression/index.ts')

// 从配置中移除 build7z
const { buildGzip, imageCompression } = require('../../../src/config')
const path = require('path')

module.exports = {
    createChainWebpack: (env, config) => {
        config.resolve.symlinks(true)

        createBanner(config)
        createSvgSprite(config)

        if (env === 'production') {
            // if (build7z) createBuild7z(config)    // ❌ 注释掉 7z 打包功能（导致构建失败）
            if (buildGzip) createGzip(config)

            if (imageCompression && process.env.VAB_VARIABLE !== 'website') {
                createImageCompression(config)
            }

            createOptimization(config)
        }

        if (env === 'development') {
            config.devtool('cheap-module-source-map')
        }

        createSourceInjector(config)

        // 仅处理 src 与 library，提高构建速度
        config.module
            .rule('js')
            .include.add(path.resolve('src'))
            .add(path.resolve('library'))
            .end()
            .exclude.add(/node_modules/)
            .end()

        // ts check 优化
        config.plugin('fork-ts-checker').tap((options) => {
            options[0].formatter = 'codeframe'
            options[0].async = false
            return options
        })
    },
}