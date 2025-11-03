<template>
    <div class="friendly-tip-container">
        <div class="friendly-tip-content">
            <el-card class="disclaimer-card" shadow="never">
                <template #header>
                    <span class="disclaimer-title">温馨提示</span>
                </template>
                <ul class="disclaimer-list">
                    <li>
                        本演示站点所展示的所有接口数据均为 Node Mock
                        技术模拟生成，仅用于功能演示和体验，数据不具备任何真实性和参考价值。
                    </li>
                    <li>
                        本框架及演示站点所涉及的所有源代码、界面设计、文档资料等，均受著作权法及相关法律法规保护，未经授权禁止复制、传播、出售、转让。
                    </li>
                    <li>
                        用户不得利用本框架从事任何违法犯罪活动，包括但不限于攻击他人系统、传播恶意软件、侵犯他人隐私或知识产权等行为。
                    </li>
                    <li>
                        用户在使用本框架过程中如发现安全漏洞或其他问题，应及时反馈给作者，不得恶意利用或公开相关漏洞。
                    </li>
                    <li>
                        本框架可能会集成第三方服务或依赖第三方开源库，如Vue、Element
                        Plus、Vue
                        Router、Vuex、Axios、Mock.js等，相关风险和责任由用户自行承担，作者不对第三方服务的可用性和安全性负责。
                    </li>
                    <li>
                        为保障正版用户的合法权益，在您购买本项目时，我们将收集并记录您的公司名称、GitHub账号、授权信息等相关资料。上述信息仅用于授权管理、售后服务及合规性核查。我们承诺严格遵守相关法律法规，采取合理的安全措施保护您的数据安全和隐私，绝不会将您的信息用于与本项目无关的用途，亦不会泄露给任何无关第三方。
                    </li>
                    <li>
                        作者有权随时对使用条款进行修改、补充或解释，且无需提前通知用户，请您务必定期关注条款内容的更新，若您不同意或无法接受最新条款，请立即停止使用本框架及相关演示服务。
                    </li>
                    <li>
                        严禁任何形式的盗版或破解版使用，若发现盗版或破解版行为，用户需承担法律责任并赔偿由此造成的全部损失，若因使用盗版或破解版造成项目无法使用，授权终止等一切后果由用户自行承担，作者不承担任何责任。
                    </li>
                    <li>
                        本框架的所有使用条款、许可协议、功能限制等，均以作者最新公布为准。任何因未遵守条款而导致的后果，均由用户自行承担，作者不承担任何责任。
                    </li>
                    <li>
                        只要您使用开发工具运行本项目，即代表你同意以上全部条款和隐私协议，若用户违反本免责声明或相关法律法规，作者有权随时中止其使用权，并保留追究法律责任的权利。
                    </li>
                </ul>
                <div class="disclaimer-footer">感谢您的理解与支持！</div>
            </el-card>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ElCard } from 'element-plus'
</script>

<style scoped>
    .disclaimer-card {
        padding-bottom: 0;
        margin-top: 32px;
        background: var(--el-bg-color);
    }

    .disclaimer-title {
        color: #a66a00;
    }
    .disclaimer-list {
        padding: 18px 28px 0 28px;
        margin: 0;
        font-size: 15px;
        line-height: 2.1;
        color: #a66a00;
        list-style: decimal inside;
        background: none;
    }
    .disclaimer-list li {
        padding-left: 0;
        margin-bottom: 8px;
        background: none;
        border: none;
        border-radius: 0;
    }
    .disclaimer-footer {
        padding: 18px 28px 18px 28px;
        font-size: 15px;
        color: #a66a00;
        text-align: right;
        letter-spacing: 1px;
        background: none;
    }
</style>
