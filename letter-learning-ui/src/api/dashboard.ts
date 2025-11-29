import request from '@/utils/request'

export function getDashboardSummary() {
    return request({
        url: '/dashboard/summary',
        method: 'get',
    })
}
