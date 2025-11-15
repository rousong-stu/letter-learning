import request from '@/utils/request'

export type AiChatSession = {
    id: number
    word_story_id?: number | null
    total_rounds: number
    status: string
    started_at: string
    ended_at?: string | null
}

export type AiChatMessage = {
    id: number
    sender: 'ai' | 'user'
    content: string
    sequence: number
    created_at: string
}

export function createAiChatSession(payload: {
    story_text: string
    word_story_id?: number | null
}) {
    return request<{ session: AiChatSession; messages: AiChatMessage[] }>({
        url: '/ai-chats',
        method: 'post',
        data: payload,
    })
}

export function fetchAiChatSession(chatId: number) {
    return request<{ session: AiChatSession; messages: AiChatMessage[] }>({
        url: `/ai-chats/${chatId}`,
        method: 'get',
    })
}

export function sendAiChatMessage(chatId: number, content: string) {
    return request<{ session: AiChatSession; new_messages: AiChatMessage[] }>({
        url: `/ai-chats/${chatId}/messages`,
        method: 'post',
        data: { content },
        timeout: 60000,
    })
}
