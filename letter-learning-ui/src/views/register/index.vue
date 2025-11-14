<template>
    <div class="register-container">
        <el-row>
            <el-col :lg="14" :md="11" :sm="24" :xl="14" :xs="24">
                <div style="color: transparent">占位符</div>
            </el-col>
            <el-col :lg="9" :md="12" :sm="24" :xl="9" :xs="24">
                <el-form
                    ref="registerFormRef"
                    class="register-form"
                    :model="form"
                    :rules="registerRules"
                >
                    <div class="title">hello !</div>
                    <div class="title-tips">{{ translateTitle('注册') }}</div>
                    <el-form-item prop="username">
                        <el-input
                            v-model.trim="form.username"
                            v-focus
                            auto-complete="off"
                            :placeholder="translateTitle('请输入用户名')"
                            type="text"
                        >
                            <template #prefix>
                                <vab-icon icon="user-line" />
                            </template>
                        </el-input>
                    </el-form-item>
                    <el-form-item prop="password">
                        <el-input
                            v-model.trim="form.password"
                            autocomplete="new-password"
                            :placeholder="translateTitle('请输入密码')"
                            type="password"
                        >
                            <template #prefix>
                                <vab-icon icon="lock-line" />
                            </template>
                        </el-input>
                    </el-form-item>
            <el-form-item prop="passwordConfirm">
                <el-input
                    v-model.trim="form.passwordConfirm"
                    autocomplete="new-password"
                    :placeholder="translateTitle('请再次输入密码')"
                    type="password"
                >
                    <template #prefix>
                        <vab-icon icon="lock-line" />
                    </template>
                </el-input>
            </el-form-item>
            <el-form-item prop="email">
                <el-input
                    v-model.trim="form.email"
                    :placeholder="translateTitle('请输入邮箱')"
                    type="email"
                >
                    <template #prefix>
                        <vab-icon icon="mail-line" />
                    </template>
                </el-input>
            </el-form-item>
            <el-form-item prop="inviteCode">
                <el-input
                    v-model.trim="form.inviteCode"
                    :placeholder="translateTitle('请输入邀请码')"
                    type="text"
                        >
                            <template #prefix>
                                <vab-icon icon="ticket-line" />
                            </template>
                        </el-input>
                    </el-form-item>
                    <el-form-item>
                        <el-button
                            class="register-btn"
                            type="primary"
                            @click.prevent="handleRegister"
                        >
                            {{ translateTitle('注册') }}
                        </el-button>
                    </el-form-item>
                    <el-form-item>
                        <router-link to="/login">
                            {{ translateTitle('登录') }}
                        </router-link>
                    </el-form-item>
                </el-form>
            </el-col>
            <el-col :lg="1" :md="1" :sm="24" :xl="1" :xs="24">
                <div style="color: transparent">占位符</div>
            </el-col>
        </el-row>
    </div>
</template>

<script>
    import { translate } from '@/i18n'
    import { isPassword } from '@/utils/validate'
    import { register } from '@/api/user'
    import { useUserStore } from '@/store/modules/user'

    export default defineComponent({
        name: 'Register',
        directives: {
            focus: {
                inserted(el) {
                    el.querySelector('input').focus()
                },
            },
        },
        setup() {
            const $baseConfirm = inject('$baseConfirm')

            const router = useRouter()

            const userStore = useUserStore()
            const { setToken } = userStore

            const validateUsername = (rule, value, callback) => {
                if ('' === value) {
                    callback(new Error(translate('用户名不能为空')))
                } else {
                    callback()
                }
            }
            const validatePassword = (rule, value, callback) => {
                if (!isPassword(value)) {
                    callback(new Error(translate('密码不能少于6位')))
                } else {
                    callback()
                }
            }
            const validatePasswordConfirm = (rule, value, callback) => {
                if (value !== state.form.password) {
                    callback(new Error(translate('两次输入的密码不一致')))
                } else {
                    callback()
                }
            }

            const validateEmail = (rule, value, callback) => {
                if (!value) {
                    callback(new Error(translate('请输入邮箱')))
                } else {
                    callback()
                }
            }

            const state = reactive({
                registerFormRef: null,
                form: {
                    username: '',
                    password: '',
                    passwordConfirm: '',
                    inviteCode: 'letter-learning',
                    email: '',
                },
                registerRules: {
                    username: [
                        {
                            required: true,
                            trigger: 'blur',
                            message: translate('请输入用户名'),
                        },
                        { validator: validateUsername, trigger: 'blur' },
                    ],
                    password: [
                        {
                            required: true,
                            trigger: 'blur',
                            message: translate('请输入密码'),
                        },
                        { validator: validatePassword, trigger: 'blur' },
                    ],
                    passwordConfirm: [
                        {
                            required: true,
                            trigger: 'blur',
                            message: translate('请再次输入密码'),
                        },
                        { validator: validatePasswordConfirm, trigger: 'blur' },
                    ],
                    email: [
                        {
                            required: true,
                            trigger: 'blur',
                            message: translate('请输入邮箱'),
                        },
                        { validator: validateEmail, trigger: 'blur' },
                    ],
                    inviteCode: [
                        {
                            required: true,
                            trigger: 'blur',
                            message: translate('请输入邀请码'),
                        },
                    ],
                },
                loading: false,
            })

            const handleRegister = () => {
                state['registerFormRef'].validate(async (valid) => {
                    if (valid) {
                        const {
                            msg,
                            data: { token },
                        } = await register(state.form).catch(() => {})
                        //$baseMessage(msg, 'success', 'vab-hey-message-success')
                        $baseConfirm(
                            `${msg}，点击确定进入管理员首页`,
                            null,
                            async () => {
                                setToken(token)
                                await router.push('/index')
                            }
                        )
                    }
                })
            }

            return {
                translateTitle: translate,
                ...toRefs(state),
                handleRegister,
            }
        },
    })
</script>

<style lang="scss" scoped>
    .register-container {
        height: 100vh;
        min-height: 700px;
        background: url('~@/assets/login_images/background.jpg') center center
            fixed no-repeat;
        background-size: cover;

        .register-form {
            position: relative;
            max-width: 100%;
            padding: 4.5vh;
            margin: calc((100vh - 555px) / 2) 5vw 5vw;
            overflow: hidden;
            background: url('~@/assets/login_images/login_form.png');
            background-size: 100% 100%;

            .title {
                font-size: 54px;
                font-weight: 500;
                color: var(--el-color-white);
            }

            .title-tips {
                margin-top: 29px;
                text-overflow: ellipsis;
                font-size: 26px;
                font-weight: 400;
                color: var(--el-color-white);
                white-space: nowrap;
            }

            .register-btn {
                display: inherit;
                width: 220px;
                height: 50px;
                margin-top: 5px;
                background: var(--el-color-primary);
                border: 0;

                &:hover {
                    opacity: 0.9;
                }
            }

        }

        .tips {
            margin-bottom: 10px;
            font-size: $base-font-size-default;
            color: var(--el-color-white);

            span {
                &:first-of-type {
                    margin-right: 16px;
                }
            }
        }

        :deep() {
            .el-form-item {
                padding-right: 0;
                margin: 20px 0;
                color: #454545;
                background: transparent;
                border: 1px solid transparent;
                border-radius: 2px;

                &__content {
                    min-height: $base-input-height;
                    line-height: $base-input-height;
                }

                &__error {
                    position: absolute;
                    top: 100%;
                    left: 18px;
                    font-size: $base-font-size-small;
                    line-height: 18px;
                    color: var(--el-color-error);
                }
            }

            .el-input {
                box-sizing: border-box;

                input {
                    height: 48px;
                    line-height: 48px;
                    border: 0;
                }

                &__suffix-inner {
                    position: absolute;
                    right: 15px;
                    cursor: pointer;

                    .el-input__count {
                        position: absolute;
                        top: 25px;
                        right: 0;
                    }
                }
            }

            .code {
                position: absolute;
                top: 4px;
                right: 4px;
                cursor: pointer;
                border-radius: $base-border-radius;
            }
        }
    }
</style>
