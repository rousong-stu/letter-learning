import request from '@/utils/request'

export function getIconList(params?: any) {
    return request({
        url: '/defaultIcon/getList',
        method: 'get',
        params,
    })
}
