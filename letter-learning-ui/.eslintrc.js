/* eslint-disable */
const { defineConfig } = require('eslint-define-config')

module.exports = defineConfig({
    root: true,
    env: {
        node: true,
        browser: true,
        // ❌ 删除此行：'vue/setup-compiler-macros': true
    },
    globals: {
        defineOptions: 'writable',
    },
    parser: 'vue-eslint-parser',
    parserOptions: {
        parser: '@typescript-eslint/parser',
        sourceType: 'module',
        ecmaVersion: 2020,
    },
    rules: {
        // 所有规则继续保留
    },
})