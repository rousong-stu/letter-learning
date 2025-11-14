<template>
    <el-dialog
        v-model="dialogFormVisible"
        :title="title"
        width="500px"
        @close="close"
    >
        <el-form ref="formRef" label-width="80px" :model="form" :rules="rules">
            <el-form-item label="用户名" prop="username">
                <el-input v-model.trim="form.username" />
            </el-form-item>
            <el-form-item label="密码" prop="password">
                <el-input
                    v-model.trim="form.password"
                    :placeholder="title === '编辑' ? '不修改请留空' : '请输入密码'"
                    autocomplete="new-password"
                    type="password"
                />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
                <el-input
                    v-model.trim="form.email"
                    type="email"
                    placeholder="请输入邮箱"
                />
            </el-form-item>
        </el-form>
        <template #footer>
            <el-button @click="close">取 消</el-button>
            <el-button type="primary" @click="save">确 定</el-button>
        </template>
    </el-dialog>
</template>

<script>
    import { doEdit } from '@/api/userManagement'

    export default defineComponent({
        name: 'UserManagementEdit',
        emits: ['fetch-data'],
        setup(props, { emit }) {
            const $baseMessage = inject('$baseMessage')

            const validatePassword = (rule, value, callback) => {
                if (!state.form.id && !value) {
                    callback(new Error('请输入密码'))
                } else callback()
            }

            const state = reactive({
                formRef: null,
                form: {
                    id: undefined,
                    username: '',
                    password: '',
                    email: '',
                },
                rules: {
                    username: [
                        {
                            required: true,
                            trigger: 'blur',
                            message: '请输入用户名',
                        },
                    ],
                    password: [
                        { validator: validatePassword, trigger: 'blur' },
                    ],
                    email: [
                        {
                            required: true,
                            trigger: 'blur',
                            message: '请输入邮箱',
                        },
                    ],
                },
                title: '',
                dialogFormVisible: false,
            })

            const showEdit = (row) => {
                if (!row) {
                    state.title = '添加'
                    state.form = {
                        id: undefined,
                        username: '',
                        password: '',
                        email: '',
                    }
                } else {
                    state.title = '编辑'
                    state.form = {
                        id: row.id,
                        username: row.username,
                        password: '',
                        email: row.email || '',
                    }
                }
                state.dialogFormVisible = true
            }
            const close = () => {
                state['formRef'].resetFields()
                state.form = {
                    id: undefined,
                    username: '',
                    password: '',
                    email: '',
                }
                state.dialogFormVisible = false
            }
            const save = () => {
                state['formRef'].validate(async (valid) => {
                    if (valid) {
                        const payload = { ...state.form }
                        if (!payload.password) delete payload.password
                        const { msg } = await doEdit(payload)
                        $baseMessage(msg, 'success', 'vab-hey-message-success')
                        emit('fetch-data')
                        close()
                    }
                })
            }

            return {
                ...toRefs(state),
                showEdit,
                close,
                save,
            }
        },
    })
</script>
