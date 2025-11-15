import request from '@/utils/request'

export type WordCardItem = {
    id: number
    word: string
    mastery_status: string
    consecutive_known_hits: number
}

export function fetchLearningWordCards(limit = 10) {
    return request<{ items: WordCardItem[] }>({
        url: '/word-cards/learning',
        method: 'get',
        params: { limit },
    })
}

export function applyWordCardAction(cardId: number, action: 'too_easy' | 'know' | 'review') {
    return request<{ item: WordCardItem }>({
        url: `/word-cards/${cardId}/actions`,
        method: 'post',
        data: { action },
    })
}
