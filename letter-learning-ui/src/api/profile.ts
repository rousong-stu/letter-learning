import request from '@/utils/request'

export function fetchProfile() {
    return request({
        url: '/profile/me',
        method: 'get',
    })
}

export function updateProfile(data: any) {
    return request({
        url: '/profile/me',
        method: 'put',
        data,
    })
}

export function changePassword(data: any) {
    return request({
        url: '/profile/password',
        method: 'post',
        data,
    })
}

export function uploadAvatar(data: FormData) {
    return request({
        url: '/profile/avatar',
        method: 'post',
        headers: { 'Content-Type': 'multipart/form-data' },
        data,
    })
}

export function fetchLoginLogs(params: any) {
    return request({
        url: '/profile/loginLogs',
        method: 'get',
        params,
    })
}

