<template>
    <div class="personal-center-container">
        <el-row :gutter="20">
            <el-col :xs="24" :sm="24" :md="10" :lg="8" :xl="8">
                <vab-card shadow="never">
                    <div class="profile-summary">
                        <el-upload
                            :http-request="handleAvatarUpload"
                            :show-file-list="false"
                            :before-upload="beforeAvatarUpload"
                        >
                            <div class="profile-avatar">
                                <el-avatar :size="100" :src="avatarPreview" />
                                <span class="avatar-edit">更换头像</span>
                            </div>
                        </el-upload>
                        <h2 class="profile-name">
                            {{ profile.user.displayName || profile.user.username }}
                        </h2>
                        <p class="profile-signature">
                            {{
                                profile.user.signature ||
                                '这位同学还没有留下介绍'
                            }}
                        </p>
                        <p v-if="profile.detail.bio" class="profile-bio">
                            {{ profile.detail.bio }}
                        </p>
                        <el-descriptions border column="1" size="small">
                            <el-descriptions-item label="用户名">
                                {{ profile.user.username }}
                            </el-descriptions-item>
                            <el-descriptions-item label="真实姓名">
                                {{ formatDisplay(profile.detail.realName) }}
                            </el-descriptions-item>
                            <el-descriptions-item label="昵称">
                                {{ profile.user.displayName || '未填写' }}
                            </el-descriptions-item>
                            <el-descriptions-item label="性别">
                                {{ formatGender(profile.user.gender) }}
                            </el-descriptions-item>
                            <el-descriptions-item label="生日">
                                {{ formatDate(profile.user.birthday) }}
                            </el-descriptions-item>
                            <el-descriptions-item label="证件号/学号">
                                {{ formatDisplay(profile.detail.idNumber) }}
                            </el-descriptions-item>
                            <el-descriptions-item label="邮箱">
                                {{ formatDisplay(profile.user.email) }}
                            </el-descriptions-item>
                            <el-descriptions-item label="手机号">
                                {{ formatDisplay(profile.user.phone) }}
                            </el-descriptions-item>
                            <el-descriptions-item label="联系地址">
                                {{ formatDisplay(profile.detail.address) }}
                            </el-descriptions-item>
                            <el-descriptions-item label="语言">
                                {{ formatDisplay(profile.user.locale, '默认') }}
                            </el-descriptions-item>
                            <el-descriptions-item label="时区">
                                {{ formatDisplay(profile.user.timezone, '默认') }}
                            </el-descriptions-item>
                            <el-descriptions-item label="微信">
                                {{ formatDisplay(profile.detail.wechat) }}
                            </el-descriptions-item>
                            <el-descriptions-item label="QQ">
                                {{ formatDisplay(profile.detail.qq) }}
                            </el-descriptions-item>
                            <el-descriptions-item label="LinkedIn">
                                <a
                                    v-if="profile.detail.linkedin"
                                    :href="normalizeLink(profile.detail.linkedin)"
                                    target="_blank"
                                    rel="noopener"
                                >
                                    {{ profile.detail.linkedin }}
                                </a>
                                <span v-else>未填写</span>
                            </el-descriptions-item>
                            <el-descriptions-item label="个人网站">
                                <a
                                    v-if="profile.detail.website"
                                    :href="normalizeLink(profile.detail.website)"
                                    target="_blank"
                                    rel="noopener"
                                >
                                    {{ profile.detail.website }}
                                </a>
                                <span v-else>未填写</span>
                            </el-descriptions-item>
                            <el-descriptions-item label="最近修改密码">
                                {{
                                    profile.user.passwordUpdatedAt
                                        ? formatDateTime(
                                              profile.user.passwordUpdatedAt
                                          )
                                        : '未记录'
                                }}
                            </el-descriptions-item>
                        </el-descriptions>
                    </div>
                </vab-card>

                <vab-card shadow="never" class="login-card">
                    <template #header>
                        <span>最近登录</span>
                    </template>
                    <el-table
                        :data="loginLogs"
                        :empty-text="loginLogsLoading ? '加载中...' : '暂无记录'"
                        size="small"
                    >
                        <el-table-column
                            label="时间"
                            prop="loginAt"
                            min-width="150"
                        >
                            <template #default="{ row }">
                                {{ formatDateTime(row.loginAt) }}
                            </template>
                        </el-table-column>
                        <el-table-column
                            label="IP"
                            prop="ipAddress"
                            min-width="120"
                        />
                        <el-table-column
                            label="设备"
                            prop="deviceName"
                            min-width="120"
                        />
                        <el-table-column
                            label="状态"
                            prop="successful"
                            width="80"
                        >
                            <template #default="{ row }">
                                <el-tag
                                    :type="row.successful ? 'success' : 'danger'"
                                    size="small"
                                >
                                    {{ row.successful ? '成功' : '失败' }}
                                </el-tag>
                            </template>
                        </el-table-column>
                    </el-table>
                </vab-card>
            </el-col>

            <el-col :xs="24" :sm="24" :md="14" :lg="16" :xl="16">
                <vab-card shadow="never">
                    <el-tabs v-model="activeTab">
                        <el-tab-pane label="基本信息" name="basic">
                            <el-form
                                ref="basicFormRef"
                                :model="form"
                                :rules="formRules"
                                label-width="100px"
                            >
                                <el-form-item label="真实姓名" prop="realName">
                                    <el-input
                                        v-model="form.realName"
                                        placeholder="请输入真实姓名"
                                    />
                                </el-form-item>
                                <el-form-item label="证件号/学号" prop="idNumber">
                                    <el-input
                                        v-model="form.idNumber"
                                        placeholder="请输入证件号或学号"
                                    />
                                </el-form-item>
                                <el-form-item label="昵称" prop="displayName">
                                    <el-input
                                        v-model="form.displayName"
                                        placeholder="显示名称"
                                    />
                                </el-form-item>
                                <el-form-item label="性别" prop="gender">
                                    <el-radio-group v-model="form.gender">
                                        <el-radio :label="0">保密</el-radio>
                                        <el-radio :label="1">男</el-radio>
                                        <el-radio :label="2">女</el-radio>
                                    </el-radio-group>
                                </el-form-item>
                                <el-form-item label="生日" prop="birthday">
                                    <el-date-picker
                                        v-model="form.birthday"
                                        type="date"
                                        value-format="YYYY-MM-DD"
                                        placeholder="请选择日期"
                                        style="width: 100%"
                                    />
                                </el-form-item>
                                <el-form-item label="邮箱" prop="email">
                                    <el-input
                                        v-model="form.email"
                                        placeholder="请输入邮箱"
                                    />
                                </el-form-item>
                                <el-form-item label="手机号" prop="phone">
                                    <el-input
                                        v-model="form.phone"
                                        placeholder="请输入手机号"
                                    />
                                </el-form-item>
                                <el-form-item label="语言" prop="locale">
                                    <el-input
                                        v-model="form.locale"
                                        placeholder="如 zh-CN"
                                    />
                                </el-form-item>
                                <el-form-item label="时区" prop="timezone">
                                    <el-input
                                        v-model="form.timezone"
                                        placeholder="如 Asia/Shanghai"
                                    />
                                </el-form-item>
                                <el-form-item label="个性签名" prop="signature">
                                    <el-input
                                        v-model="form.signature"
                                        type="textarea"
                                        :rows="2"
                                        maxlength="255"
                                        show-word-limit
                                    />
                                </el-form-item>
                                <el-form-item label="个人简介" prop="bio">
                                    <el-input
                                        v-model="form.bio"
                                        type="textarea"
                                        :rows="4"
                                        maxlength="500"
                                        show-word-limit
                                    />
                                </el-form-item>
                                <el-form-item label="地址" prop="address">
                                    <el-input
                                        v-model="form.address"
                                        placeholder="联系地址"
                                    />
                                </el-form-item>
                                <el-form-item label="社交账号">
                                    <div class="social-inputs">
                                        <el-input
                                            v-model="form.wechat"
                                            placeholder="微信"
                                        />
                                        <el-input
                                            v-model="form.qq"
                                            placeholder="QQ"
                                        />
                                        <el-input
                                            v-model="form.linkedin"
                                            placeholder="LinkedIn"
                                        />
                                        <el-input
                                            v-model="form.website"
                                            placeholder="个人网站"
                                        />
                                    </div>
                                </el-form-item>
                                <el-form-item>
                                    <el-button
                                        :loading="saving"
                                        type="primary"
                                        @click="onSubmit"
                                    >
                                        保存
                                    </el-button>
                                </el-form-item>
                            </el-form>
                        </el-tab-pane>

                        <el-tab-pane label="账号安全" name="security">
                            <el-form
                                ref="passwordFormRef"
                                :model="passwordForm"
                                :rules="passwordRules"
                                label-width="120px"
                            >
                                <el-form-item
                                    label="当前密码"
                                    prop="oldPassword"
                                >
                                    <el-input
                                        v-model="passwordForm.oldPassword"
                                        type="password"
                                        autocomplete="off"
                                    />
                                </el-form-item>
                                <el-form-item label="新密码" prop="newPassword">
                                    <el-input
                                        v-model="passwordForm.newPassword"
                                        type="password"
                                        autocomplete="off"
                                    />
                                </el-form-item>
                                <el-form-item
                                    label="确认新密码"
                                    prop="confirmPassword"
                                >
                                    <el-input
                                        v-model="passwordForm.confirmPassword"
                                        type="password"
                                        autocomplete="off"
                                    />
                                </el-form-item>
                                <el-form-item>
                                    <el-button
                                        :loading="passwordSaving"
                                        type="primary"
                                        @click="onChangePassword"
                                    >
                                        修改密码
                                    </el-button>
                                    <span class="password-tip">
                                        修改密码后将自动要求重新登录
                                    </span>
                                </el-form-item>
                            </el-form>
                        </el-tab-pane>
                    </el-tabs>
                </vab-card>
            </el-col>
        </el-row>
    </div>
</template>

<script lang="ts" setup>
    import { ref, reactive, onMounted, inject } from 'vue'
    import { useRouter } from 'vue-router'
    import { storeToRefs } from 'pinia'
    import {
        fetchProfile,
        updateProfile,
        changePassword,
        uploadAvatar,
        fetchLoginLogs,
    } from '@/api/profile'
    import dayjs from 'dayjs'
    import { useUserStore } from '@/store/modules/user'

    const $baseMessage = inject('$baseMessage') as any
    const router = useRouter()
    const userStore = useUserStore()
    const { avatar } = storeToRefs(userStore)

    const profile = reactive({
        user: {
            username: '',
            email: '',
            phone: '',
            displayName: '',
            gender: 0,
            birthday: '',
            locale: '',
            timezone: '',
            signature: '',
            avatarUrl: '',
            passwordUpdatedAt: '',
        } as any,
        detail: {
            realName: '',
            idNumber: '',
            address: '',
            wechat: '',
            qq: '',
            linkedin: '',
            website: '',
            bio: '',
        },
    })

    const loginLogs = ref<any[]>([])
    const loginLogsLoading = ref(false)

    const activeTab = ref('basic')
    const basicFormRef = ref()
    const passwordFormRef = ref()

    const form = reactive({
        realName: '',
        displayName: '',
        idNumber: '',
        gender: 0,
        birthday: '',
        email: '',
        phone: '',
        locale: '',
        timezone: '',
        signature: '',
        bio: '',
        address: '',
        wechat: '',
        qq: '',
        linkedin: '',
        website: '',
    })

    const passwordForm = reactive({
        oldPassword: '',
        newPassword: '',
        confirmPassword: '',
    })

    const saving = ref(false)
    const passwordSaving = ref(false)
    const avatarPreview = ref<string | undefined>(avatar.value)

    const formRules = {
        email: [
            { required: true, message: '请输入邮箱', trigger: 'blur' },
            { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
        ],
        phone: [{ min: 0, trigger: 'blur' }],
    }

    const passwordRules = {
        oldPassword: [{ required: true, message: '请输入当前密码' }],
        newPassword: [
            { required: true, message: '请输入新密码' },
            { min: 6, message: '至少 6 位字符' },
        ],
        confirmPassword: [
            { required: true, message: '请确认新密码' },
            {
                validator: (_: any, value: string, callback: any) => {
                    if (value !== passwordForm.newPassword) {
                        callback(new Error('两次输入密码不一致'))
                    } else callback()
                },
            },
        ],
    }

    const loadProfile = async () => {
        const {
            data: { user, profile: profileDetail, loginLogs: logs },
        } = await fetchProfile()
        const detail = profileDetail || {}
        profile.user = user
        Object.assign(profile.detail, {
            realName: detail.realName || '',
            idNumber: detail.idNumber || '',
            address: detail.address || '',
            wechat: detail.wechat || '',
            qq: detail.qq || '',
            linkedin: detail.linkedin || '',
            website: detail.website || '',
            bio: detail.bio || '',
        })
        avatarPreview.value = user.avatarUrl || avatar.value
        Object.assign(form, {
            realName: detail.realName || '',
            displayName: user.displayName || '',
            idNumber: detail.idNumber || '',
            gender:
                typeof user.gender === 'number'
                    ? user.gender
                    : Number(user.gender || 0),
            birthday: user.birthday || '',
            email: user.email || '',
            phone: user.phone || '',
            locale: user.locale || '',
            timezone: user.timezone || '',
            signature: user.signature || '',
            bio: detail.bio || '',
            address: detail.address || '',
            wechat: detail.wechat || '',
            qq: detail.qq || '',
            linkedin: detail.linkedin || '',
            website: detail.website || '',
        })
        loginLogs.value = logs || []
        await loadLoginLogs()
        if (user.displayName) userStore.setUsername(user.displayName)
        if (user.avatarUrl) userStore.setAvatar(user.avatarUrl)
    }

    const loadLoginLogs = async () => {
        loginLogsLoading.value = true
        try {
            const {
                data: { list },
            } = await fetchLoginLogs({ limit: 10 })
            loginLogs.value = list
        } finally {
            loginLogsLoading.value = false
        }
    }

    const onSubmit = async () => {
        if (!basicFormRef.value) return
        await basicFormRef.value.validate(async (valid: boolean) => {
            if (!valid) return
            saving.value = true
            try {
                const { data } = await updateProfile(form)
                const detail = data.profile || {}
                $baseMessage(
                    '资料保存成功',
                    'success',
                    'vab-hey-message-success'
                )
                profile.user = data.user
                Object.assign(profile.detail, {
                    realName: detail.realName || '',
                    idNumber: detail.idNumber || '',
                    address: detail.address || '',
                    wechat: detail.wechat || '',
                    qq: detail.qq || '',
                    linkedin: detail.linkedin || '',
                    website: detail.website || '',
                    bio: detail.bio || '',
                })
                if (data.user.displayName)
                    userStore.setUsername(data.user.displayName)
            } catch (error) {
                console.error(error)
            } finally {
                saving.value = false
            }
        })
    }

    const onChangePassword = async () => {
        if (!passwordFormRef.value) return
        await passwordFormRef.value.validate(async (valid: boolean) => {
            if (!valid) return
            passwordSaving.value = true
            try {
                await changePassword(passwordForm)
                $baseMessage(
                    '密码修改成功，请重新登录',
                    'success',
                    'vab-hey-message-success'
                )
                await userStore.resetAll()
                await router.push('/login')
            } catch (error) {
                console.error(error)
            } finally {
                passwordSaving.value = false
            }
        })
    }

    const beforeAvatarUpload = (file: File) => {
        const isImage = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'].includes(
            file.type
        )
        const isLt2M = file.size / 1024 / 1024 < 2
        if (!isImage)
            $baseMessage('仅支持 PNG/JPG/WEBP 图片', 'error', 'vab-hey-message-error')
        if (!isLt2M)
            $baseMessage('图片大小不能超过 2MB', 'error', 'vab-hey-message-error')
        return isImage && isLt2M
    }

    const handleAvatarUpload = async (option: any) => {
        const formData = new FormData()
        formData.append('file', option.file)
        try {
            const { data } = await uploadAvatar(formData)
            avatarPreview.value = data.avatarUrl
            userStore.setAvatar(data.avatarUrl)
            $baseMessage(
                '头像更新成功',
                'success',
                'vab-hey-message-success'
            )
            option.onSuccess(data, option.file)
        } catch (error) {
            option.onError(error)
        }
    }

    const formatDisplay = (
        value: string | null | undefined,
        fallback = '未填写'
    ) => {
        if (!value) return fallback
        return value
    }

    const formatGender = (value: number | string | null | undefined) => {
        const num = typeof value === 'string' ? Number(value) : value
        if (num === 1) return '男'
        if (num === 2) return '女'
        return '未填写'
    }

    const formatDate = (value: string | null | undefined) => {
        if (!value) return '未填写'
        return dayjs(value).format('YYYY-MM-DD')
    }

    const normalizeLink = (value: string | null | undefined) => {
        if (!value) return ''
        if (/^https?:\/\//i.test(value)) return value
        return `https://${value}`
    }

    const formatDateTime = (value: string | null | undefined) => {
        if (!value) return ''
        return dayjs(value).format('YYYY-MM-DD HH:mm')
    }

    onMounted(async () => {
        await loadProfile()
    })
</script>

<style lang="scss" scoped>
    .personal-center-container {
        padding: 0 !important;
        background: $base-color-background !important;
    }

    .profile-summary {
        text-align: center;

        .profile-avatar {
            position: relative;
            display: inline-block;
            cursor: pointer;

            .avatar-edit {
                position: absolute;
                bottom: -6px;
                left: 50%;
                transform: translateX(-50%);
                padding: 2px 8px;
                font-size: 12px;
                border-radius: 10px;
                background-color: var(--el-color-primary);
                color: #fff;
            }
        }

        .profile-name {
            margin-top: 16px;
            font-size: 20px;
            font-weight: 600;
        }

        .profile-signature {
            margin: 8px 0 16px;
            color: var(--el-text-color-secondary);
        }

        .profile-bio {
            margin: 0 0 16px;
            color: var(--el-text-color-regular);
            line-height: 1.6;
        }
    }

    .login-card {
        margin-top: 20px;
    }

    .social-inputs {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 10px;
        width: 100%;
    }

    .password-tip {
        margin-left: 12px;
        font-size: 12px;
        color: var(--el-text-color-secondary);
    }
</style>
