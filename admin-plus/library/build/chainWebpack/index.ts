const { createGzip } = require('./gzip/index.ts')
const { createBanner } = require('./banner/index.ts')
const { createBuild7z } = require('./build7z/index.ts')
const { createSvgSprite } = require('./svgSprite/index.ts')
const { createOptimization } = require('./optimization/index.ts')
const { createSourceInjector } = require('./sourceInjector/index.ts')
const { createImageCompression } = require('./imageCompression/index.ts')
const { build7z, buildGzip, imageCompression } = require('../../../src/config')
const path = require('path')

module.exports = {
    createChainWebpack: (env, config) => {
        config.resolve.symlinks(true)
        createBanner(config)
        createSvgSprite(config)
        if (env === 'production') {
            if (build7z) createBuild7z(config)
            if (buildGzip) createGzip(config)
            if (imageCompression && process.env.VAB_VARIABLE !== 'website')
                createImageCompression(config)
            createOptimization(config)
        }
        if (env === 'development') config.devtool('cheap-module-source-map')
        createSourceInjector(config)

        // 添加一些构建优化
        // 避免处理node_modules中已经编译过的文件
        config.module
            .rule('js')
            .include.add(path.resolve('src'))
            .add(path.resolve('library'))
            .end()
            .exclude.add(/node_modules/)
            .end()

        // 优化构建性能
        config.plugin('fork-ts-checker').tap((options) => {
            options[0].formatter = 'codeframe'
            options[0].async = false
            return options
        })
    },
}
