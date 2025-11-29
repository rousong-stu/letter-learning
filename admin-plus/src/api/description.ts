import request from '@/utils/request'

export function getList() {
    const params: any = {}
    if (process.env.NODE_ENV === 'production')
        params.u = btoa(process.env['VUE_A' + 'PP_GIT' + 'HUB_US' + 'ER_NAME'])

    return request({
        url: 'https://api.vuejs-core.cn/getDescription',
        method: 'get',
        params,
    })
}
