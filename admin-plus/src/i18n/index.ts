import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import pinia from '@/store'
import { useSettingsStore } from '@/store/modules/settings'
import type { LanguageType } from '/#/store'

const messages: Record<LanguageType, any> = {
    en: {
        ...en,
    },
    zh: {},
}

function getLanguage() {
    const { getLanguage } = useSettingsStore(pinia)
    return getLanguage
}

export const i18n = createI18n({
    legacy: false,
    locale: getLanguage(),
    fallbackLocale: 'zh',
    messages,
})

export function setupI18n(app: any) {
    app.use(i18n)
    return i18n
}

export function translate(message: string | undefined) {
    if (!message) {
        return ''
    }
    return (
        [getLanguage(), 'vabI18n', message].reduce(
            (o, k) => (o || {})[k],
            messages as any
        ) || message
    )
}

export { default as enLocale } from 'element-plus/dist/locale/en'
export { default as zhLocale } from 'element-plus/dist/locale/zh-cn'
