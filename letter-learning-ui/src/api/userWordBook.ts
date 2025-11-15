import request from '@/utils/request'

export function listWordBooks() {
    return request({
        url: '/word-books',
        method: 'get',
    })
}

export function getCurrentUserPlan() {
    return request({
        url: '/user-word-books/current',
        method: 'get',
    })
}

export function createUserLearningPlan(data: any) {
    return request({
        url: '/user-word-books',
        method: 'post',
        data,
    })
}
