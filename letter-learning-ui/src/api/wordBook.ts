import request from '@/utils/request'

export function createWordBook(data: FormData) {
    return request({
        url: '/word-books',
        method: 'post',
        data,
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    })
}
