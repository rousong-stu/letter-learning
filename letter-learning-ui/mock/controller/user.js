const { Random } = require('mockjs')

const tokens = {
    admin: `admin-token-${Random.guid()}-${Date.now()}`,
    editor: `editor-token-${Random.guid()}-${Date.now()}`,
    test: `test-token-${Random.guid()}-${Date.now()}`,
}
const adminRoles = ['Admin']
const adminPermissions = ['read:system', 'write:system', 'delete:system']

module.exports = [
    {
        url: '/publicKey',
        type: 'get',
        response() {
            return {
                code: 200,
                msg: 'success',
                data: {
                    mockServer: true,
                    publicKey:
                        'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBT2vr+dhZElF73FJ6xiP181txKWUSNLPQQlid6DUJhGAOZblluafIdLmnUyKE8mMHhT3R+Ib3ssZcJku6Hn72yHYj/qPkCGFv0eFo7G+GJfDIUeDyalBN0QsuiE/XzPHJBuJDfRArOiWvH0BXOv5kpeXSXM8yTt5Na1jAYSiQ/wIDAQAB',
                },
            }
        },
    },
    {
        url: '/login',
        type: 'post',
        response(config) {
            const { username } = config.body
            const token = tokens[username]
            if (!token)
                return {
                    code: 500,
                    msg: '帐户或密码不正确',
                }
            return {
                code: 200,
                msg: 'success',
                data: { token },
            }
        },
    },
    {
        url: '/socialLogin',
        type: 'post',
        response(config) {
            const { code } = config.body
            if (!code)
                return {
                    code: 500,
                    msg: '未成功获取Token',
                }

            return {
                code: 200,
                msg: 'success',
                data: { token: tokens['admin'] },
            }
        },
    },
    {
        url: '/register',
        type: 'post',
        response() {
            return {
                code: 200,
                msg: '模拟注册成功',
                data: { token: tokens['admin'] },
            }
        },
    },
    {
        url: '/userInfo',
        type: 'get',
        response(config) {
            const authorization =
                config.headers.authorization || config.headers.Authorization
            if (!authorization.startsWith('Bearer '))
                return {
                    code: 401,
                    msg: '令牌无效',
                }
            const _authorization = authorization.replace('Bearer ', '')
            const isTrue = _authorization.includes('-token-')
            const username = isTrue
                ? _authorization.split('-token-')[0]
                : 'admin'
            return {
                code: 200,
                msg: 'success',
                data: {
                    username,
                    roles: adminRoles,
                    permissions: adminPermissions,
                    avatar: 'https://i.gtimg.cn/club/item/face/img/2/16022_100.gif',
                },
            }
        },
    },
    {
        url: '/logout',
        type: 'get',
        response() {
            return {
                code: 200,
                msg: 'success',
            }
        },
    },
]
