/**
 * @description 导出网络配置
 **/
module.exports = {
    // 接口地址在 .env.* 中配置，默认使用 VUE_APP_BASE_URL
    // 也可以按需改为完整地址，如 "https://api.xxx.com"

    // 支持多环境接口地址配置的方法
    // 开发环境去.env.development改，生产环境去.env.production改，测试环境去.env.test改
    baseURL: `${process.env.VUE_APP_BASE_URL}`,
    // 配后端数据的接收方式application/json;charset=UTF-8 或 application/x-www-form-urlencoded;charset=UTF-8
    contentType: 'application/json;charset=UTF-8',
    // 最长请求时间
    requestTimeout: 10000,
    // 操作正常code，支持String、Array、int多种类型
    successCode: [200, 0, '200', '0'],
    // 数据状态的字段名称
    statusName: 'code',
    // 状态信息的字段名称
    messageName: 'msg',
}
