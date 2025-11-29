<script setup>
    import { useUserStore } from '@/store/modules/user'
    import VabAvatarList from '@/plugins/VabAvatarList'

    const userStore = useUserStore()
    const { avatar, username } = storeToRefs(userStore)

    const state = reactive({
        description: '你不是一个人在努力，无数个未来的你正在为现在的坚持鼓掌。',
        avatarList: [
            {
                avatar: 'https://i.gtimg.cn/club/item/face/img/2/15922_100.gif',
                username: 'good luck',
            },
            {
                avatar: 'https://gcore.jsdelivr.net/gh/zxwk1998/image/user/fwfmiao.gif',
                username: 'FlowPeakFish',
            },
            {
                avatar: 'https://i.gtimg.cn/club/item/face/img/3/15643_100.gif',
                username: '嘻嘻',
            },
        ],
    })

    const handleTips = () => {
        const hour = new Date().getHours()
        return hour < 8
            ? `早上好 ${username.value}，又是元气满满的一天。`
            : hour <= 11
              ? `上午好 ${username.value}，看到你我好开心。`
              : hour <= 13
                ? `中午好 ${username.value}，忙碌了一上午，记得吃午饭哦。`
                : hour < 18
                  ? `下午好 ${username.value}，欢迎回来。继续你的学习之旅吧，再小的进步，也是向前。`
                  : `晚上好 ${username.value}，愿你天黑有灯，下雨有伞。`
    }
</script>

<template>
    <el-col :span="24">
        <vab-card class="page-header" shadow="never">
            <el-avatar class="page-header-avatar" :src="avatar" />
            <div class="page-header-tip">
                <p class="page-header-tip-title">
                    {{ handleTips() }}
                </p>
                <p
                    class="page-header-tip-description"
                    v-html="state.description"
                ></p>
            </div>
            <div class="page-header-avatar-list">
                <vab-avatar-list :avatar-list="state.avatarList" />
                <p>participants</p>
            </div>
        </vab-card>
    </el-col>
</template>

<style lang="scss" scoped>
    .page-header {
        min-height: 145px;
        transition: none;

        :deep() {
            * {
                transition: none;
            }

            .el-card__body {
                display: flex;
                flex-wrap: wrap;
                align-items: center;
            }
        }

        &-avatar {
            width: 60px;
            height: 60px;
            margin-right: 20px;
            border-radius: 50%;
        }

        &-tip {
            flex: auto;
            width: calc(100% - 200px);
            min-width: 300px;

            &-title {
                margin-bottom: 12px;
                font-size: 20px;
                font-weight: bold;
                color: #3c4a54;
            }

            &-description {
                min-height: 20px;
                font-size: $base-font-size-default;
                color: #808695;
            }
        }

        &-avatar-list {
            flex: 1;
            min-width: 100px;
            margin-left: 20px;
            text-align: right;

            p {
                margin-right: 9px;
                line-height: 0;
            }
        }
    }
</style>
