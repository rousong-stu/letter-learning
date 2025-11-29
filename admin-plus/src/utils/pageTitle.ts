import pinia from '@/store'
import { translate } from '@/i18n'
import { titleReverse, titleSeparator } from '@/config'
import { useSettingsStore } from '@/store/modules/settings'

// 保存用户自定义的标题
let customTitle: string | null = null

/**
 * @description 设置标题
 * @param pageTitle
 * @returns {string}
 */
export default function getPageTitle(pageTitle: string | undefined) {
    const { getTitle } = useSettingsStore(pinia)
    let newTitles = []

    // 如果有用户自定义标题，优先使用自定义标题
    if (customTitle) {
        newTitles.push(customTitle)
    } else if (pageTitle) {
        newTitles.push(translate(pageTitle))
    }

    if (getTitle) newTitles.push(getTitle)
    if (titleReverse) newTitles = newTitles.reverse()
    return newTitles.join(titleSeparator)
}

// 提供设置自定义标题的方法
export function setCustomTitle(title: string | null) {
    customTitle = translate(title)
}
