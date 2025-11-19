const { createUnPlugin } = require('vue-' + 'unplugins')
const { createWebpackBar } = require('./webpack' + 'Bar/index.ts')
const { createDefineOptions } = require('./defineOptions/index.ts')
const { createDefinePlugin } = require('./definePlugin/index.ts')
const { createProvidePlugin } = require('./providePlugin/index.ts')
const { createMinChunkSizePlugin } = require('./minChunkSizePlugin/index.ts')

const dev = process.env.NODE_ENV === 'development'

module.exports = {
    createVuePlugin: () => [
        ...createDefineOptions(),
        ...createUnPlugin(),
        // ❌ 移除 unplugin-element-plus（因为它是 ESM，不支持 require）
        // require('unplugin-element-plus/webpack')(),

        ...createWebpackBar(),
        ...createDefinePlugin(),
        ...createProvidePlugin(),
        ...(dev ? [] : createMinChunkSizePlugin()),
    ],
}