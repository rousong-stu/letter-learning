<template>
    <div class="auth-page">
        <transition name="fade-fast">
            <div v-if="loading" class="lottie-overlay">
                <lottie-player
                    src="/loading-text.lottie"
                    background="transparent"
                    speed="1"
                    loop
                    autoplay
                    style="width: 180px; height: 180px"
                />
                <p class="lottie-desc">欢迎选择Lumilyx，智慧学习即刻开始！</p>
            </div>
        </transition>

        <el-form
            ref="formRef"
            class="auth-form"
            label-position="left"
            :model="form"
            :rules="rules"
            @keyup.enter.stop
        >
            <div class="title">欢迎回来，学友！</div>
            <div class="title-tips">
                A journey of a thousand miles begins with a single word！
            </div>
            <el-form-item prop="username">
                <el-input
                    v-model.trim="form.username"
                    v-focus
                    :placeholder="translateTitle('请输入用户名')"
                    tabindex="1"
                    type="text"
                >
                    <template #prefix>
                        <vab-icon icon="user-line" />
                    </template>
                </el-input>
            </el-form-item>
            <el-form-item prop="password">
                <el-input
                    :key="passwordType"
                    ref="passwordRef"
                    v-model.trim="form.password"
                    :placeholder="translateTitle('请输入密码')"
                    tabindex="2"
                    :type="passwordType"
                    @keyup.enter.stop
                >
                    <template #prefix>
                        <vab-icon icon="lock-line" />
                    </template>
                    <template v-if="passwordType === 'password'" #suffix>
                        <vab-icon
                            class="show-password"
                            icon="eye-off-line"
                            @click="handlePassword"
                        />
                    </template>
                    <template v-else #suffix>
                        <vab-icon
                            class="show-password"
                            icon="eye-line"
                            @click="handlePassword"
                        />
                    </template>
                </el-input>
            </el-form-item>
            <el-form-item prop="captchaCode" class="captcha-row">
                <div class="captcha-field">
                    <el-input
                        v-model.trim="form.captchaCode"
                        :placeholder="translateTitle('请输入验证码')"
                        tabindex="3"
                    >
                        <template #prefix>
                            <vab-icon icon="barcode-box-line" />
                        </template>
                    </el-input>
                    <img
                        class="captcha-img"
                        :src="captchaImg"
                        alt="captcha"
                        @click="fetchCaptcha"
                    />
                </div>
            </el-form-item>
            <el-form-item>
                <el-checkbox v-model="remember">记住密码</el-checkbox>
            </el-form-item>
            <el-form-item>
                <el-button
                    class="login-btn"
                    :loading="loading"
                    type="primary"
                    @click="handleLogin"
                >
                    {{ translateTitle('登录') }}
                </el-button>
            </el-form-item>
            <el-form-item class="register-link">
                <router-link to="/register">
                    {{ translateTitle('注册') }}
                </router-link>
            </el-form-item>
        </el-form>
    </div>
</template>

<script>
    import { useSettingsStore } from '@/store/modules/settings'
    import { useUserStore } from '@/store/modules/user'
    import { translate } from '@/i18n'
    import '@lottiefiles/lottie-player'
    import { isPassword } from '@/utils/validate'
    import { getCaptcha } from '@/api/user'

    export default defineComponent({
        name: 'Login',
        directives: {
            focus: {
                mounted(el) {
                    el.querySelector('input').focus()
                },
            },
        },
        setup() {
            const route = useRoute()
            const router = useRouter()

            const userStore = useUserStore()
            const settingsStore = useSettingsStore()

            const login = (form) => userStore.login(form)

            const validateUsername = (rule, value, callback) => {
                if ('' === value)
                    callback(new Error(translate('用户名不能为空')))
                else callback()
            }
            const validatePassword = (rule, value, callback) => {
                if (!isPassword(value))
                    callback(new Error(translate('密码不能少于6位')))
                else callback()
            }

            const state = reactive({
                formRef: null,
                passwordRef: null,
                form: {
                    username: '',
                    password: '',
                    remember: false,
                    captchaCode: '',
                },
                rules: {
                    username: [
                        {
                            required: true,
                            trigger: 'blur',
                            validator: validateUsername,
                        },
                    ],
                    password: [
                        {
                            required: true,
                            trigger: 'blur',
                            validator: validatePassword,
                        },
                    ],
                    captchaCode: [
                        {
                            required: true,
                            trigger: 'blur',
                            message: translate('请输入验证码'),
                        },
                    ],
                },
                loading: false,
                passwordType: 'password',
                redirect: undefined,
                timer: 0,
                captchaToken: '',
                captchaImg: '',
            })

            const handleRoute = () => {
                return state.redirect === '/404' || state.redirect === '/403'
                    ? '/'
                    : state.redirect
            }
            const handlePassword = () => {
                state.passwordType === 'password'
                    ? (state.passwordType = '')
                    : (state.passwordType = 'password')
                nextTick(() => {
                    state['passwordRef'].focus()
                })
            }
            const fetchCaptcha = async () => {
                try {
                    const resp = await getCaptcha()
                    state.captchaToken = resp.data?.captchaToken || ''
                    state.captchaImg = resp.data?.image || ''
                    state.form.captchaCode = ''
                } catch (error) {
                    console.error('获取验证码失败', error)
                }
            }

            const handleLogin = async () => {
                state['formRef'].validate(async (valid) => {
                    if (valid)
                        try {
                            state.loading = true
                            await login({
                                ...state.form,
                                captchaToken: state.captchaToken,
                            })
                                .then(() => {
                                    if (state.form.remember) {
                                        localStorage.setItem(
                                            'remember_login',
                                            JSON.stringify({
                                                username: state.form.username,
                                                password: state.form.password,
                                            })
                                        )
                                    } else {
                                        localStorage.removeItem('remember_login')
                                    }
                                })
                                .catch(() => {
                                    fetchCaptcha()
                                })
                            await router.push(handleRoute())
                        } finally {
                            state.loading = false
                        }
                })
            }
            onBeforeMount(() => {
                const saved = localStorage.getItem('remember_login')
                if (saved) {
                    try {
                        const parsed = JSON.parse(saved)
                        state.form.username = parsed.username || ''
                        state.form.password = parsed.password || ''
                        state.form.remember = true
                    } catch (e) {
                        localStorage.removeItem('remember_login')
                    }
                } else {
                    state.form.username = 'admin'
                    state.form.password = '123456'
                }
                fetchCaptcha()
            })

            watchEffect(() => {
                state.redirect = (route.query && route.query.redirect) || '/'
            })

            onBeforeRouteLeave((to, from, next) => {
                clearInterval(state.timer)
                next()
            })

            return {
                translateTitle: translate,
                ...toRefs(state),
                title: settingsStore.getTitle,
                handlePassword,
                handleLogin,
                fetchCaptcha,
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
        width: min(420px, 90vw);
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

        .login-btn {
            width: 100%;
            height: 46px;
            font-weight: 600;
        }

        .register-link {
            margin-top: -8px;
            text-align: right;
        }

        .show-password {
            width: 32px;
            height: 32px;
            font-size: 16px;
        }

        .captcha-row {
            margin-top: 6px;
        }

        .captcha-field {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .captcha-field :deep(.el-input) {
            flex: 1;
        }

        .captcha-img {
            width: 102px;
            height: 32px;
            border-radius: 10px;
            cursor: pointer;
            box-shadow: inset 0 0 0 1px #e0e6ed;
            object-fit: contain;
            background: #fff;
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

    .lottie-overlay {
        position: fixed;
        inset: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.85);
        z-index: 99;
        backdrop-filter: blur(3px);

        .lottie-desc {
            margin-top: 10px;
            color: #4a5b73;
            font-weight: 600;
        }
    }

    .fade-fast-enter-active,
    .fade-fast-leave-active {
        transition: opacity 0.25s ease;
    }
    .fade-fast-enter-from,
    .fade-fast-leave-to {
        opacity: 0;
    }
</style>
