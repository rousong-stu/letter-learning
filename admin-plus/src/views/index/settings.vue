<template>
    <div class="settings-container">
        <el-tabs v-model="activeTab" type="border-card">
            <el-tab-pane label="基本设置" name="basic">
                <el-form
                    class="settings-form"
                    label-width="120px"
                    :model="basicSettings"
                >
                    <el-form-item label="网站名称">
                        <el-input
                            v-model="basicSettings.siteName"
                            placeholder="请输入网站名称"
                        />
                    </el-form-item>

                    <el-form-item label="网站描述">
                        <el-input
                            v-model="basicSettings.siteDescription"
                            placeholder="请输入网站描述"
                            :rows="3"
                            type="textarea"
                        />
                    </el-form-item>

                    <el-form-item label="网站Logo">
                        <el-input
                            v-model="basicSettings.siteLogo"
                            placeholder="请输入Logo图片地址"
                        />
                    </el-form-item>

                    <el-form-item label="网站状态">
                        <el-switch
                            v-model="basicSettings.siteStatus"
                            active-text="开启"
                            inactive-text="关闭"
                        />
                    </el-form-item>

                    <el-form-item label="维护模式">
                        <el-switch
                            v-model="basicSettings.maintenanceMode"
                            active-text="开启"
                            inactive-text="关闭"
                        />
                    </el-form-item>

                    <el-form-item label="备案号">
                        <el-input
                            v-model="basicSettings.icpNumber"
                            placeholder="请输入备案号"
                        />
                    </el-form-item>

                    <el-form-item>
                        <el-button type="primary" @click="saveBasicSettings">
                            保存设置
                        </el-button>
                        <el-button @click="resetBasicSettings">重置</el-button>
                    </el-form-item>
                </el-form>
            </el-tab-pane>

            <el-tab-pane label="邮件设置" name="email">
                <el-form
                    class="settings-form"
                    label-width="120px"
                    :model="emailSettings"
                >
                    <el-form-item label="SMTP服务器">
                        <el-input
                            v-model="emailSettings.smtpServer"
                            placeholder="请输入SMTP服务器地址"
                        />
                    </el-form-item>

                    <el-form-item label="SMTP端口">
                        <el-input
                            v-model="emailSettings.smtpPort"
                            placeholder="请输入SMTP端口"
                        />
                    </el-form-item>

                    <el-form-item label="邮箱账号">
                        <el-input
                            v-model="emailSettings.emailAccount"
                            placeholder="请输入邮箱账号"
                        />
                    </el-form-item>

                    <el-form-item label="邮箱密码">
                        <el-input
                            v-model="emailSettings.emailPassword"
                            placeholder="请输入邮箱密码"
                            show-password
                            type="password"
                        />
                    </el-form-item>

                    <el-form-item label="发件人名称">
                        <el-input
                            v-model="emailSettings.senderName"
                            placeholder="请输入发件人名称"
                        />
                    </el-form-item>

                    <el-form-item>
                        <el-button type="primary" @click="saveEmailSettings">
                            保存设置
                        </el-button>
                        <el-button @click="resetEmailSettings">重置</el-button>
                        <el-button @click="testEmailSettings">
                            测试连接
                        </el-button>
                    </el-form-item>
                </el-form>
            </el-tab-pane>

            <el-tab-pane label="安全设置" name="security">
                <el-form
                    class="settings-form"
                    label-width="150px"
                    :model="securitySettings"
                >
                    <el-form-item label="密码最小长度">
                        <el-input-number
                            v-model="securitySettings.passwordMinLength"
                            :max="20"
                            :min="6"
                        />
                    </el-form-item>

                    <el-form-item label="密码复杂度">
                        <el-checkbox-group
                            v-model="securitySettings.passwordComplexity"
                        >
                            <el-checkbox label="大写字母" />
                            <el-checkbox label="小写字母" />
                            <el-checkbox label="数字" />
                            <el-checkbox label="特殊字符" />
                        </el-checkbox-group>
                    </el-form-item>

                    <el-form-item label="登录失败次数限制">
                        <el-input-number
                            v-model="securitySettings.loginFailureLimit"
                            :max="10"
                            :min="0"
                        >
                            <template #append>次</template>
                        </el-input-number>
                        <div class="form-item-tip">0表示不限制</div>
                    </el-form-item>

                    <el-form-item label="自动锁定时间">
                        <el-input-number
                            v-model="securitySettings.autoLockDuration"
                            :max="1440"
                            :min="1"
                        >
                            <template #append>分钟</template>
                        </el-input-number>
                    </el-form-item>

                    <el-form-item label="会话超时时间">
                        <el-input-number
                            v-model="securitySettings.sessionTimeout"
                            :max="1440"
                            :min="1"
                        >
                            <template #append>分钟</template>
                        </el-input-number>
                    </el-form-item>

                    <el-form-item>
                        <el-button type="primary" @click="saveSecuritySettings">
                            保存设置
                        </el-button>
                        <el-button @click="resetSecuritySettings">
                            重置
                        </el-button>
                    </el-form-item>
                </el-form>
            </el-tab-pane>
        </el-tabs>
    </div>
</template>

<script lang="ts" setup>
    import { ref } from 'vue'
    import { ElMessage } from 'element-plus'

    defineOptions({
        name: 'Settings',
    })

    const activeTab = ref('basic')

    // 基本设置
    const basicSettings = ref({
        siteName: 'Admin Plus管理系统',
        siteDescription: '一个功能强大的后台管理系统',
        siteLogo: '',
        siteStatus: true,
        maintenanceMode: false,
        icpNumber: '京ICP备12345678号',
    })

    // 邮件设置
    const emailSettings = ref({
        smtpServer: 'smtp.example.com',
        smtpPort: '465',
        emailAccount: 'admin@example.com',
        emailPassword: '',
        senderName: 'Admin Plus',
    })

    // 安全设置
    const securitySettings = ref({
        passwordMinLength: 8,
        passwordComplexity: ['大写字母', '小写字母', '数字'],
        loginFailureLimit: 5,
        autoLockDuration: 30,
        sessionTimeout: 30,
    })

    // 保存基本设置
    const saveBasicSettings = () => {
        ElMessage.success('基本设置保存成功')
    }

    // 重置基本设置
    const resetBasicSettings = () => {
        basicSettings.value = {
            siteName: 'Admin Plus管理系统',
            siteDescription: '一个功能强大的后台管理系统',
            siteLogo: '',
            siteStatus: true,
            maintenanceMode: false,
            icpNumber: '京ICP备12345678号',
        }
        ElMessage.info('基本设置已重置')
    }

    // 保存邮件设置
    const saveEmailSettings = () => {
        ElMessage.success('邮件设置保存成功')
    }

    // 重置邮件设置
    const resetEmailSettings = () => {
        emailSettings.value = {
            smtpServer: 'smtp.example.com',
            smtpPort: '465',
            emailAccount: 'admin@example.com',
            emailPassword: '',
            senderName: 'Admin Plus',
        }
        ElMessage.info('邮件设置已重置')
    }

    // 测试邮件设置
    const testEmailSettings = () => {
        ElMessage.info('正在测试邮件连接...')
        // 模拟测试过程
        setTimeout(() => {
            ElMessage.success('邮件连接测试成功')
        }, 1000)
    }

    // 保存安全设置
    const saveSecuritySettings = () => {
        ElMessage.success('安全设置保存成功')
    }

    // 重置安全设置
    const resetSecuritySettings = () => {
        securitySettings.value = {
            passwordMinLength: 8,
            passwordComplexity: ['大写字母', '小写字母', '数字'],
            loginFailureLimit: 5,
            autoLockDuration: 30,
            sessionTimeout: 30,
        }
        ElMessage.info('安全设置已重置')
    }
</script>

<style lang="scss" scoped>
    .settings-container {
        padding: 0 !important;
        background: $base-color-background !important;

        .card-header {
            font-size: 18px;
            font-weight: bold;
        }

        .settings-form {
            max-width: 600px;
            margin: 20px 0;

            .form-item-tip {
                margin-top: 5px;
                font-size: 12px;
                color: #999;
            }
        }
    }
</style>
