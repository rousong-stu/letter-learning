<template>
    <div class="auth-page">
        <el-form
            ref="registerFormRef"
            class="auth-form"
            :model="form"
            :rules="registerRules"
        >
            <div class="title">创建账户</div>
            <div class="title-tips">{{ translateTitle('注册加入') }} {{ platformTitle }}</div>

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
            <el-form-item class="register-link">
                <router-link to="/login">
                    {{ translateTitle('已有账号？去登录') }}
                </router-link>
            </el-form-item>
        </el-form>
    </div>
</template>

<script>
    import { translate } from '@/i18n'
    import { useSettingsStore } from '@/store/modules/settings'
    import { isPassword } from '@/utils/validate'
    import { register } from '@/api/user'
    import { useUserStore } from '@/store/modules/user'

    export default defineComponent({
        name: 'Register',
        directives: {
            focus: {
                mounted(el) {
                    el.querySelector('input').focus()
                },
            },
        },
        setup() {
            const $baseConfirm = inject('$baseConfirm')

            const router = useRouter()

            const userStore = useUserStore()
            const { setToken } = userStore
            const settingsStore = useSettingsStore()

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
                platformTitle: settingsStore.getTitle,
                handleRegister,
            }
        },
    })
</script>

<style lang="scss" scoped>
    .auth-page {
        position: relative;
        min-height: 100vh;
        display: flex;
        align-items: center;
        padding: clamp(24px, 6vw, 60px);
        background-color: #f5f7ff;
        overflow: hidden;

        &::before {
            content: '';
            position: absolute;
            inset: 0;
            background: url('~@/assets/login_images/home_bg_final.jpg')
                center center / cover no-repeat;
            z-index: 0;
        }
    }

    .auth-form {
        width: min(440px, 90vw);
        padding: clamp(20px, 4vw, 32px);
        background: rgba(255, 255, 255, 0.92);
        border-radius: 16px;
        box-shadow: 0 18px 48px rgba(31, 47, 74, 0.12);
        backdrop-filter: blur(6px);
        margin-left: clamp(12px, 4vw, 48px);
        position: relative;
        z-index: 1;
        animation: float-in 450ms ease 30ms both;

        .title {
            font-size: 32px;
            font-weight: 700;
            color: #1f2f4a;
        }

        .title-tips {
            margin-top: 6px;
            margin-bottom: 18px;
            font-size: 16px;
            color: #5f6f85;
        }

        .register-btn {
            width: 100%;
            height: 46px;
            font-weight: 600;
        }

        .register-link {
            margin-top: -8px;
            text-align: right;
        }

        :deep() {
            .el-form-item {
                margin: 14px 0;
            }

            .el-input__wrapper {
                border-radius: 12px;
            }
        }
    }

    @keyframes float-in {
        from {
            transform: translateY(18px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
</style>
