module.exports = [
    {
        url: '/menuManagement/getTree',
        type: 'get',
        response() {
            return {
                code: 200,
                msg: 'success',
                data: {
                    total: 999,
                    list: [
                        {
                            id: 'root',
                            label: '管理员',
                            children: [
                                {
                                    id: '@id',
                                    role: 'admin',
                                    label: '管理员',
                                },
                            ],
                        },
                    ],
                },
            }
        },
    },
    {
        url: '/menuManagement/doEdit',
        type: 'post',
        response() {
            return {
                code: 200,
                msg: '模拟保存成功',
            }
        },
    },
    {
        url: '/menuManagement/doDelete',
        type: 'post',
        response() {
            return {
                code: 200,
                msg: '模拟删除成功',
            }
        },
    },
]
