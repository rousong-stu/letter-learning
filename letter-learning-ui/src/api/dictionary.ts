import request from '@/utils/request'

export function lookupDictionaryEntry(word: string) {
    return request({
        url: '/dictionary/lookup',
        method: 'get',
        params: { word },
    })
}

export function translateDefinition(entryId: number, definitionIndex: number, force = false) {
    return request({
        url: `/dictionary/${entryId}/definitions/${definitionIndex}/translation`,
        method: 'post',
        data: { force },
    })
}
