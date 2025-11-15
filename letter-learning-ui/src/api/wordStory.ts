import request from '@/utils/request'

export type WordStoryRecord = {
    id: number
    story_date: string
    generated_at: string
    words: string[]
    story_text: string
    story_tokens?: number
    model_name?: string
    image_url?: string
    image_caption?: string
}

export function fetchTodayWordStory(
    params: { auto_generate?: boolean; force?: boolean } = {}
) {
    return request<WordStoryRecord>({
        url: '/word-stories/today',
        method: 'get',
        params,
        timeout: 120000,
    })
}

export function generateWordStory(payload: {
    words?: string[]
    story_date?: string
    force?: boolean
}) {
    return request<WordStoryRecord>({
        url: '/word-stories/generate',
        method: 'post',
        data: payload,
        timeout: 120000,
    })
}

export function fetchWordStoryHistory(limit = 10) {
    return request<{ items: WordStoryRecord[] }>({
        url: '/word-stories/history',
        method: 'get',
        params: { limit },
    })
}
