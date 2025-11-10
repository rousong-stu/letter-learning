<template>
    <div class="student-home">
        <el-row :gutter="20">
            <el-col :lg="16" :md="16" :sm="24" :xs="24">
                <el-card class="chat-card" shadow="hover">
                    <template #header>
                        <div class="card-header">
                            <div>
                                <div class="title">AI 对话练习</div>
                                <div class="subtitle">
                                    今日目标生词
                                    <el-tag
                                        v-for="word in focusWords"
                                        :key="word.word"
                                        size="small"
                                        type="info"
                                    >
                                        {{ word.word }}
                                    </el-tag>
                                </div>
                            </div>
                            <el-tag type="success" effect="light">
                                连续学习 {{ stats.streak }} 天
                            </el-tag>
                        </div>
                    </template>
                    <div class="chat-window">
                        <div
                            v-for="message in conversation"
                            :key="message.id"
                            class="chat-message"
                            :class="message.sender"
                        >
                            <div class="avatar" :class="message.sender">
                                <span>
                                    {{
                                        message.sender === 'ai'
                                            ? 'AI'
                                            : '我'
                                    }}
                                </span>
                            </div>
                            <div class="bubble">
                                <div class="bubble-header">
                                    <span class="sender">
                                        {{
                                            message.sender === 'ai'
                                                ? '记忆助手'
                                                : '我'
                                        }}
                                    </span>
                                    <span class="time">{{ message.time }}</span>
                                </div>
                                <div class="content">
                                    {{ message.text }}
                                </div>
                                <div
                                    v-if="message.glossary && message.glossary.length"
                                    class="glossary"
                                >
                                    <el-tag
                                        v-for="item in message.glossary"
                                        :key="item"
                                        size="small"
                                        effect="dark"
                                        type="success"
                                    >
                                        {{ item }}
                                    </el-tag>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="chat-footer">
                        <div class="quick-replies">
                            <span>快速回复：</span>
                            <el-tag
                                v-for="reply in quickReplies"
                                :key="reply"
                                size="small"
                                class="reply"
                                @click="handleQuickReply(reply)"
                            >
                                {{ reply }}
                            </el-tag>
                        </div>
                        <el-input
                            v-model="userInput"
                            type="textarea"
                            placeholder="输入你想说的话，或请求记忆助手提供帮助..."
                            :rows="3"
                            resize="none"
                        />
                        <div class="actions">
                            <div class="hints">
                                <el-tag
                                    v-for="word in focusWords"
                                    :key="`${word.word}-hint`"
                                    size="small"
                                    type="warning"
                                    effect="plain"
                                >
                                    试着用 {{ word.word }}
                                </el-tag>
                            </div>
                            <el-button type="primary" @click="handleSend">
                                发送
                            </el-button>
                        </div>
                    </div>
                </el-card>
            </el-col>

            <el-col :lg="8" :md="8" :sm="24" :xs="24">
                <el-card class="dictionary-card" shadow="hover">
                    <template #header>
                        <div class="card-header">
                            <div class="title">今日词典速览</div>
                            <el-tag type="info" size="small">新词包</el-tag>
                        </div>
                    </template>
                    <div class="word-list">
                        <div
                            v-for="word in focusWords"
                            :key="`${word.word}-full`"
                            class="word-item"
                        >
                            <div class="word-head">
                                <div class="word">{{ word.word }}</div>
                                <div class="phonetic">{{ word.phonetic }}</div>
                            </div>
                            <div class="definition">
                                {{ word.translation }}
                            </div>
                            <div class="example">
                                例句：{{ word.example }}
                            </div>
                        </div>
                    </div>
                </el-card>

                <el-card class="progress-card" shadow="hover">
                    <template #header>
                        <div class="card-header">
                            <div class="title">学习曲线</div>
                            <el-tag type="success" size="small">
                                今日完成 {{ stats.todayDone }}/5
                            </el-tag>
                        </div>
                    </template>
                    <div class="trend-chart">
                        <div
                            v-for="point in weeklyTrend"
                            :key="point.day"
                            class="trend-bar"
                        >
                            <div
                                class="bar"
                                :style="{
                                    height: `${Math.max(
                                        (point.value / maxTrendValue) * 100,
                                        8
                                    )}%`,
                                }"
                            ></div>
                            <span class="label">{{ point.day }}</span>
                        </div>
                    </div>
                    <el-divider content-position="left">今日掌握度</el-divider>
                    <div class="mastery">
                        <el-progress
                            :percentage="stats.mastery"
                            status="success"
                            :stroke-width="10"
                            :format="(percent) => `${percent}%`"
                        />
                        <div class="summary">
                            已掌握 {{ stats.wordsMastered }} 个单词，
                            待复习 {{ stats.wordsPending }} 个
                        </div>
                    </div>
                </el-card>

                <el-card class="schedule-card" shadow="hover">
                    <template #header>
                        <div class="card-header">
                            <div class="title">学习节奏</div>
                            <el-tag type="warning" size="small">
                                下一步安排
                            </el-tag>
                        </div>
                    </template>
                    <el-timeline>
                        <el-timeline-item
                            v-for="session in upcomingSessions"
                            :key="session.time"
                            :timestamp="session.time"
                            placement="top"
                        >
                            <h4>{{ session.title }}</h4>
                            <p>{{ session.description }}</p>
                        </el-timeline-item>
                    </el-timeline>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script lang="ts">
    import { computed, defineComponent, ref } from 'vue'

    interface Message {
        id: number
        sender: 'student' | 'ai'
        time: string
        text: string
        glossary?: string[]
    }

    interface FocusWord {
        word: string
        phonetic: string
        translation: string
        example: string
    }

    interface TrendPoint {
        day: string
        value: number
    }

    export default defineComponent({
        name: 'StudentHomePreview',
        setup() {
            const focusWords = ref<FocusWord[]>([
                {
                    word: 'immerse',
                    phonetic: '/iˈmɜːrs/',
                    translation: 'v. 沉浸；使专心',
                    example:
                        'Try to immerse yourself in the conversation to remember the words.',
                },
                {
                    word: 'articulate',
                    phonetic: '/ɑːrˈtɪkjələt/',
                    translation: 'adj. 善于表达的；v. 清晰地表达',
                    example:
                        'Could you articulate why this word is difficult for you?',
                },
                {
                    word: 'retention',
                    phonetic: '/rɪˈtenʃən/',
                    translation: 'n. 记忆力；保持',
                    example:
                        'Spaced repetition can improve your vocabulary retention.',
                },
                {
                    word: 'contextual',
                    phonetic: '/kənˈtekstʃuəl/',
                    translation: 'adj. 上下文的；情境的',
                    example:
                        'Using new words in a contextual dialogue helps you remember them.',
                },
                {
                    word: 'prompt',
                    phonetic: '/prɑːmpt/',
                    translation: 'n. 提示；v. 激发',
                    example:
                        'The AI will prompt you to use each new vocabulary item.',
                },
            ])

            const conversation = ref<Message[]>([
                {
                    id: 1,
                    sender: 'ai',
                    time: '09:00',
                    text: 'Good morning! Ready to immerse yourself in today’s practice?',
                    glossary: ['immerse'],
                },
                {
                    id: 2,
                    sender: 'student',
                    time: '09:02',
                    text: 'I am! I hope I can articulate the new words better today.',
                    glossary: ['articulate'],
                },
                {
                    id: 3,
                    sender: 'ai',
                    time: '09:05',
                    text: 'Great start! Let us build a contextual story using all five words.',
                    glossary: ['contextual'],
                },
                {
                    id: 4,
                    sender: 'ai',
                    time: '09:05',
                    text: 'What strategies help your retention the most?',
                    glossary: ['retention'],
                },
            ])

            const quickReplies = ref([
                '给我一个使用 immerse 的例句',
                '请再解释一次 prompt',
                '我准备好了，开始吧',
            ])

            const stats = ref({
                streak: 6,
                mastery: 68,
                wordsMastered: 126,
                wordsPending: 18,
                todayDone: 3,
            })

            const weeklyTrend = ref<TrendPoint[]>([
                { day: 'Mon', value: 3 },
                { day: 'Tue', value: 4 },
                { day: 'Wed', value: 5 },
                { day: 'Thu', value: 2 },
                { day: 'Fri', value: 5 },
                { day: 'Sat', value: 4 },
                { day: 'Sun', value: 3 },
            ])

            const upcomingSessions = ref([
                {
                    title: '场景对话：旅行机场',
                    time: '今天 19:30',
                    description: '和 AI 模拟机场值机场景，加深对 prompt 的运用。',
                },
                {
                    title: '词根词缀拆解',
                    time: '明天 09:00',
                    description: '分析 immerse 与 retention 的构词法，提升记忆效率。',
                },
                {
                    title: '同伴共学回顾',
                    time: '周三 20:00',
                    description: '分享今日对话成果，互相提供 contextual 用法示例。',
                },
            ])

            const userInput = ref('')

            const maxTrendValue = computed(() =>
                weeklyTrend.value.reduce(
                    (max, item) => (item.value > max ? item.value : max),
                    1
                )
            )

            const handleSend = () => {
                const content = userInput.value.trim()
                if (!content) return

                conversation.value.push({
                    id: Date.now(),
                    sender: 'student',
                    time: new Date().toLocaleTimeString('zh-CN', {
                        hour: '2-digit',
                        minute: '2-digit',
                    }),
                    text: content,
                })

                userInput.value = ''

                setTimeout(() => {
                    conversation.value.push({
                        id: Date.now() + 1,
                        sender: 'ai',
                        time: new Date().toLocaleTimeString('zh-CN', {
                            hour: '2-digit',
                            minute: '2-digit',
                        }),
                        text: 'Nice! Try weaving another sentence that connects retain and contextual.',
                        glossary: ['retention', 'contextual'],
                    })
                }, 600)
            }

            const handleQuickReply = (reply: string) => {
                userInput.value = reply
                handleSend()
            }

            return {
                focusWords,
                conversation,
                quickReplies,
                stats,
                weeklyTrend,
                upcomingSessions,
                userInput,
                maxTrendValue,
                handleSend,
                handleQuickReply,
            }
        },
    })
</script>

<style lang="scss" scoped>
    .student-home {
        padding: 12px;
        background-color: #f5f7fb;

        .el-card {
            border-radius: 14px;
        }
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .title {
            font-size: 16px;
            font-weight: 600;
            color: #1f2d3d;
        }

        .subtitle {
            margin-top: 6px;
            color: #86909c;

            .el-tag {
                margin-left: 8px;
            }
        }
    }

    .chat-card {
        display: flex;
        flex-direction: column;

        .chat-window {
            flex: 1;
            max-height: 480px;
            padding-right: 8px;
            overflow-y: auto;
        }

        .chat-message {
            display: flex;
            margin-bottom: 18px;

            &.student {
                flex-direction: row-reverse;

                .bubble {
                    background: linear-gradient(135deg, #4b8bff, #2f6bff);
                    color: #fff;
                    margin-left: 20px;
                    margin-right: 0;
                }

                .bubble::after {
                    border-left-color: #2f6bff;
                    border-right: none;
                    left: auto;
                    right: -8px;
                }
            }

            &.ai {
                .bubble {
                    background: #f3f4f8;
                }
            }

            .avatar {
                display: flex;
                justify-content: center;
                align-items: center;
                width: 38px;
                height: 38px;
                margin-top: 4px;
                border-radius: 50%;
                background: #e9efff;
                font-size: 13px;
                font-weight: 600;
                color: #4b8bff;

                &.student {
                    background: #2f6bff;
                    color: #fff;
                }
            }

            .bubble {
                position: relative;
                flex: 1;
                padding: 12px 16px;
                margin-left: 20px;
                border-radius: 16px;
                box-shadow: 0 4px 12px rgba(79, 111, 182, 0.08);

                &::after {
                    position: absolute;
                    top: 14px;
                    left: -8px;
                    width: 0;
                    height: 0;
                    border-top: 8px solid transparent;
                    border-bottom: 8px solid transparent;
                    border-right: 8px solid #f3f4f8;
                    content: '';
                }
            }

            .bubble-header {
                display: flex;
                justify-content: space-between;
                margin-bottom: 6px;

                .sender {
                    font-weight: 600;
                }

                .time {
                    font-size: 12px;
                    color: #a0a9b8;
                }
            }

            .glossary {
                margin-top: 10px;

                .el-tag {
                    margin-right: 6px;
                    margin-bottom: 4px;
                }
            }
        }

        .chat-footer {
            margin-top: 20px;

            .quick-replies {
                margin-bottom: 12px;
                color: #86909c;
                font-size: 13px;

                .reply {
                    margin-left: 8px;
                    cursor: pointer;
                }
            }

            .actions {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 12px;

                .hints {
                    flex: 1;

                    .el-tag {
                        margin-right: 8px;
                    }
                }
            }
        }
    }

    .dictionary-card {
        margin-bottom: 20px;

        .word-list {
            display: flex;
            flex-direction: column;
            gap: 14px;
        }

        .word-item {
            padding: 12px;
            border-radius: 12px;
            background: #f6f8fd;

            .word-head {
                display: flex;
                justify-content: space-between;
                font-weight: 600;
                color: #1f2d3d;
            }

            .phonetic {
                font-size: 13px;
                color: #86909c;
            }

            .definition {
                margin-top: 8px;
                color: #4e5969;
            }

            .example {
                margin-top: 6px;
                font-size: 13px;
                color: #86909c;
            }
        }
    }

    .progress-card {
        margin-bottom: 20px;

        .trend-chart {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            height: 180px;
            padding: 0 4px 16px;

            .trend-bar {
                display: flex;
                flex-direction: column;
                align-items: center;
                width: 100%;
                max-width: 34px;

                .bar {
                    width: 16px;
                    border-radius: 12px 12px 4px 4px;
                    background: linear-gradient(135deg, #7fade8, #4b8bff);
                    transition: height 0.3s ease;
                }

                .label {
                    margin-top: 8px;
                    font-size: 12px;
                    color: #a0a9b8;
                }
            }
        }

        .mastery {
            .summary {
                margin-top: 10px;
                color: #86909c;
                font-size: 13px;
            }
        }
    }

    .schedule-card {
        .el-timeline-item__timestamp {
            color: #a0a9b8;
        }

        h4 {
            margin: 0 0 6px;
            font-size: 14px;
            font-weight: 600;
        }

        p {
            margin: 0;
            color: #4e5969;
            font-size: 13px;
            line-height: 1.6;
        }
    }

    @media screen and (max-width: 992px) {
        .student-home {
            padding: 0;
        }

        .chat-card .chat-window {
            max-height: 360px;
        }
    }
</style>
