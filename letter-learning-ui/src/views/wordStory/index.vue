<template>
    <div class="word-story-page">
        <el-row class="word-story-row" :gutter="24">
            <el-col
                class="story-column"
                :lg="16"
                :md="16"
                :sm="24"
                :xs="24"
            >
                <el-card
                    class="story-card"
                    shadow="hover"
                    v-loading="pageLoading"
                    element-loading-text="正在加载短文..."
                >
                    <template #header>
                        <div class="story-card__header">
                            <div>
                                <div class="headline">
                                    <span class="eyebrow">AI 生成短文</span>
                                    <strong>今日词包记忆任务</strong>
                                </div>
                                <div class="subtitle">
                                    词汇数量：{{ displayWords.length }} ·
                                    {{ displayDate }}
                                </div>
                            </div>
                            <div class="actions">
                                <el-button
                                    type="primary"
                                    :loading="storyLoading"
                                    @click="handleRegenerate"
                                >
                                    <vab-remix-icon icon="refresh-line" />
                                    重新生成
                                </el-button>
                            </div>
                        </div>
                    </template>

                    <div class="story-meta">
                        <span class="meta-label">今日词汇：</span>
                        <el-tag
                            v-for="word in displayWords"
                            :key="word.word"
                            size="small"
                            effect="plain"
                            class="word-tag"
                        >
                            {{ word.word }}
                        </el-tag>
                    </div>

                    <el-alert
                        title="短文基于今日词汇生成，后端打通后将实时获取 Coze 智能体返回内容。"
                        type="success"
                        :closable="false"
                        class="story-hint"
                        show-icon
                    />

                    <el-scrollbar class="story-content" always>
                        <transition-group name="paragraph-fade" tag="div">
                            <p
                                v-for="(paragraph, index) in storyParagraphs"
                                :key="`paragraph-${index}`"
                            >
                                {{ paragraph }}
                            </p>
                        </transition-group>
                    </el-scrollbar>
                </el-card>
            </el-col>

                        <el-col
                class="side-column"
                :lg="8"
                :md="8"
                :sm="24"
                :xs="24"
            >
                <div class="side-panels">
                    <el-card class="side-card fill-card" shadow="hover">
                        <el-tabs v-model="activeSideTab" class="side-tabs">
                            <template #tab="{ tab }">
                                <span class="tab-label">
                                    <vab-remix-icon
                                        v-if="tab.props.name === 'conversation'"
                                        icon="chat-1-line"
                                    />
                                    <vab-remix-icon v-else icon="book-read-line" />
                                    {{ tab.props.label }}
                                </span>
                            </template>
                            <el-tab-pane label="AI 对话" name="conversation">
                                <div class="pane-header">
                                    <div>
                                        <div class="title">AI 对话区</div>
                                        <div class="subtitle">
                                            结合短文内容随时追问、做语法复盘
                                        </div>
                                    </div>
                                    <el-tag type="success" size="small">预览</el-tag>
                                </div>
                                <div class="conversation-body">
                                    <div class="chat-intro">
                                        <div class="chat-title">多轮对话（演示）</div>
                                        <div class="chat-prompts">
                                            <el-tag
                                                v-for="prompt in quickPrompts"
                                                :key="prompt"
                                                size="small"
                                                effect="plain"
                                                @click="handleQuickPrompt(prompt)"
                                            >
                                                {{ prompt }}
                                            </el-tag>
                                        </div>
                                    </div>
                                    <el-scrollbar ref="chatScrollbarRef" class="chat-scroll" always>
                                        <div
                                            v-for="message in conversationMessages"
                                            :key="message.id"
                                            class="chat-bubble"
                                            :class="message.sender"
                                        >
                                            <div class="bubble-meta">
                                                <span class="sender">
                                                    {{ message.sender === 'ai' ? '智能体' : '我' }}
                                                </span>
                                                <span class="time">{{ message.time }}</span>
                                            </div>
                                            <p class="bubble-text">{{ message.text }}</p>
                                        </div>
                                    </el-scrollbar>
                                    <div class="conversation-input">
                                        <el-input
                                            v-model="conversationInput"
                                            type="textarea"
                                            placeholder="就短文抛出一个问题，或请 AI 帮你改写句子"
                                            :rows="3"
                                            resize="none"
                                            class="chat-textarea"
                                        />
                                        <div class="input-actions">
                                            <el-button text size="small" @click="handleClearInput">清空</el-button>
                                            <el-button
                                                type="primary"
                                                :disabled="!conversationInput.trim()"
                                                @click="handleConversationSend"
                                            >
                                                <vab-remix-icon icon="send-plane-2-line" />
                                                发送
                                            </el-button>
                                        </div>
                                    </div>
                                </div>
                            </el-tab-pane>
                            <el-tab-pane label="单词卡片" name="word">
                                <div class="word-pane">
                                    <div class="word-search">
                                        <el-input
                                            v-model="wordSearch"
                                            placeholder="输入英文单词，例如 abandon"
                                            size="large"
                                            @keyup.enter="handleWordSearch"
                                        >
                                            <template #prepend>
                                                <vab-remix-icon icon="search-eye-line" />
                                            </template>
                                        </el-input>
                                        <el-button
                                            type="primary"
                                            size="large"
                                            :loading="wordCardLoading"
                                            @click="handleWordSearch"
                                        >
                                            查询
                                        </el-button>
                                    </div>
                                    <div class="word-card__body">
                                        <el-scrollbar class="word-scroll" always>
                                            <div class="word-header">
                                                <div>
                                                    <div class="word-title">
                                                        <span>{{ wordCard.word }}</span>
                                                        <el-tag
                                                            v-if="wordCard.part_of_speech"
                                                            class="pos-tag"
                                                            type="info"
                                                            size="small"
                                                            effect="plain"
                                                            round
                                                        >
                                                            {{ wordCard.part_of_speech }}
                                                        </el-tag>
                                                    </div>
                                                    <div class="word-tags">
                                                        <el-tag
                                                            v-for="tag in wordCardLabels"
                                                            :key="tag"
                                                            size="small"
                                                            type="success"
                                                            effect="plain"
                                                        >
                                                            {{ tag }}
                                                        </el-tag>
                                                    </div>
                                                </div>
                                                <div class="word-actions">
                                                    <el-button
                                                        class="word-audio-btn"
                                                        text
                                                        type="primary"
                                                        @click="playWordAudio(wordCard.phonetics?.[0]?.audio_url)"
                                                    >
                                                        <img :src="speakerIcon" alt="播放发音" class="audio-image" />
                                                    </el-button>
                                                </div>
                                            </div>

                                            <div class="word-basic">
                                                <div class="phonetics">
                                                    <div class="phonetic-row">
                                                        <div
                                                            v-for="item in primaryPhonetics"
                                                            :key="item.notation"
                                                            class="phonetic-item"
                                                        >
                                                            <span>{{ formatPhonetic(item.notation) }}</span>
                                                            <el-button
                                                                v-if="item.audio_url"
                                                                text
                                                                size="small"
                                                                class="phonetic-audio"
                                                                @click="playWordAudio(item.audio_url)"
                                                            >
                                                                <img :src="speakerIcon" alt="播放音标" />
                                                            </el-button>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div class="variants" v-if="wordCard.variants?.length">
                                                    <span class="label">变体</span>
                                                    <el-tag
                                                        v-for="variant in wordCard.variants"
                                                        :key="variant"
                                                        effect="dark"
                                                        size="small"
                                                    >
                                                        {{ variant }}
                                                    </el-tag>
                                                </div>
                                                <div class="variants" v-if="wordCard.inflections?.length">
                                                    <span class="label">词形</span>
                                                    <el-tag
                                                        v-for="inflection in wordCard.inflections"
                                                        :key="inflection"
                                                        effect="plain"
                                                        size="small"
                                                    >
                                                        {{ inflection }}
                                                    </el-tag>
                                                </div>
                                            </div>

                                            <section class="info-block definition-block">
                                                <h4>英文释义与例句</h4>
                                                <div
                                                    v-for="(definition, index) in wordCard.definitions"
                                                    :key="index"
                                                    class="definition-item"
                                                >
                                                    <div class="definition-heading">
                                                        <span class="definition-index">
                                                            释义 {{ index + 1 }}
                                                        </span>
                                                        <el-button
                                                            text
                                                            size="small"
                                                            class="translation-trigger"
                                                            @click="toggleDefinitionTranslation(index)"
                                                        >
                                                            中文释义
                                                        </el-button>
                                                    </div>
                                                    <p class="definition-text">
                                                        {{ definition.meaning }}
                                                    </p>
                                                    <p
                                                        v-if="definitionTranslationsVisible[index]"
                                                        class="definition-translation"
                                                    >
                                                        {{ definition.translation || '示例中文释义：等待 AI 翻译' }}
                                                    </p>
                                                    <ul
                                                        v-if="definition.examples?.length"
                                                        class="example-list"
                                                    >
                                                        <li
                                                            v-for="(example, idx) in definition.examples"
                                                            :key="idx"
                                                        >
                                                            {{ example }}
                                                        </li>
                                                    </ul>
                                                </div>
                                            </section>

                                            <section class="info-block syn-ant-block">
                                                <div class="syn-ant-group">
                                                    <div class="syn-ant-header">
                                                        <h4>同义词</h4>
                                                        <span class="group-count" v-if="wordCard.synonyms?.length">
                                                            {{ wordCard.synonyms.length }}
                                                        </span>
                                                    </div>
                                                    <div class="chip-list" v-if="wordCard.synonyms?.length">
                                                        <span
                                                            class="chip chip-syn"
                                                            v-for="item in wordCard.synonyms"
                                                            :key="item"
                                                        >
                                                            {{ item }}
                                                        </span>
                                                    </div>
                                                    <p v-else class="empty-tip">等待接口返回</p>
                                                </div>
                                                <div class="syn-ant-group">
                                                    <div class="syn-ant-header">
                                                        <h4>反义词</h4>
                                                        <span class="group-count" v-if="wordCard.antonyms?.length">
                                                            {{ wordCard.antonyms.length }}
                                                        </span>
                                                    </div>
                                                    <div class="chip-list" v-if="wordCard.antonyms?.length">
                                                        <span
                                                            class="chip chip-ant"
                                                            v-for="item in wordCard.antonyms"
                                                            :key="item"
                                                        >
                                                            {{ item }}
                                                        </span>
                                                    </div>
                                                    <p v-else class="empty-tip">暂无数据</p>
                                                </div>
                                            </section>
                                        </el-scrollbar>
                                    </div>
                                </div>
                            </el-tab-pane>


                        </el-tabs>
                    </el-card>
                </div>
            </el-col>
        </el-row>
    </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
    fetchTodayWordStory,
    generateWordStory,
    type WordStoryRecord,
} from '@/api/wordStory'
import speakerIcon from '@/assets/speaker-icon.svg'

type WordInfo = {
    word: string
    phonetic: string
    translation: string
    example: string
    note: string
}

type PreviewMessage = {
    id: number
    sender: 'ai' | 'user'
    text: string
    time: string
}

const DEFAULT_WORDS: WordInfo[] = [
    {
        word: 'abandon',
        phonetic: '/əˈbændən/',
        translation: '放弃；抛弃',
        example:
            'The explorer refused to abandon her dream despite the harsh weather.',
        note: '常与 plan, attempt 等词搭配，强调彻底放弃。',
    },
    {
        word: 'accurate',
        phonetic: '/ˈækjərət/',
        translation: '准确的；精确的',
        example: 'Keep accurate notes to analyze your progress later.',
        note: '与 measurement, description 等搭配频繁出现。',
    },
    {
        word: 'acquire',
        phonetic: '/əˈkwaɪr/',
        translation: '获得；习得',
        example: 'Learners acquire vocabulary faster when using it in context.',
        note: '可搭配 knowledge, habit, taste，语气较正式。',
    },
    {
        word: 'adapt',
        phonetic: '/əˈdæpt/',
        translation: '适应；改编',
        example: 'Writers adapt their approach based on reader feedback.',
        note: 'adapt to 与 adapt for 的语义不同，注意区分。',
    },
    {
        word: 'analyze',
        phonetic: '/ˈænəˌlaɪz/',
        translation: '分析；解读',
        example: 'Analyze each paragraph to determine its core message.',
        note: '后接 data, result, structure 等名词效果自然。',
    },
    {
        word: 'approach',
        phonetic: '/əˈproʊtʃ/',
        translation: '方法；接近',
        example: 'Try a narrative approach to make memory vivid.',
        note: '名词和动词形式一致，可灵活使用。',
    },
    {
        word: 'assume',
        phonetic: '/əˈsuːm/',
        translation: '假设；承担',
        example: 'Assume each clue matters when reading the passage.',
        note: '搭配 responsibility/role 时意为“承担”。',
    },
    {
        word: 'benefit',
        phonetic: '/ˈbɛnɪfɪt/',
        translation: '益处；受益',
        example: 'Students benefit from reviewing challenging words daily.',
        note: '可与 from/benefit of 结构搭配。',
    },
    {
        word: 'challenge',
        phonetic: '/ˈtʃælɪndʒ/',
        translation: '挑战；难题',
        example:
            'Facing a new challenge each day keeps the routine refreshing.',
        note: '常作可数名词，注意冠词使用。',
    },
    {
        word: 'contribute',
        phonetic: '/kənˈtrɪbjuːt/',
        translation: '贡献；促成',
        example:
            'Each word you master will contribute to more confident writing.',
        note: 'contribute to 后接名词或 V-ing。',
    },
    {
        word: 'decline',
        phonetic: '/dɪˈklaɪn/',
        translation: '下降；拒绝',
        example:
            'Do not let motivation decline when the story feels complex.',
        note: '名词、动词拼写相同，注意重音。',
    },
    {
        word: 'define',
        phonetic: '/dɪˈfaɪn/',
        translation: '定义；界定',
        example:
            'Define the purpose of each paragraph to keep writing efficient.',
        note: 'define A as B 结构高频出现。',
    },
    {
        word: 'demand',
        phonetic: '/dɪˈmænd/',
        translation: '需要；要求',
        example:
            'Good writing skills demand patience and repeated revision.',
        note: 'demand 后接 that 从句时动词常用原形。',
    },
    {
        word: 'determine',
        phonetic: '/dɪˈtɜːrmɪn/',
        translation: '决定；判定',
        example:
            'Focus words can determine the emotional tone of the passage.',
        note: 'determine to do sth. 表示“下定决心”。',
    },
    {
        word: 'efficient',
        phonetic: '/ɪˈfɪʃənt/',
        translation: '高效的；有成效的',
        example:
            'Efficient study sessions mix reading, speaking, and reflection.',
        note: '多与 system, method, workflow 一起使用。',
    },
    {
        word: 'essential',
        phonetic: '/ɪˈsɛnʃəl/',
        translation: '必要的；本质的',
        example:
            'Staying curious is essential when tackling demanding topics.',
        note: 'essential to/for + 名词都可。',
    },
    {
        word: 'evidence',
        phonetic: '/ˈɛvɪdəns/',
        translation: '证据；依据',
        example:
            'Collect evidence from context to infer the author’s intention.',
        note: '不可数名词，指“证据”时无需加 s。',
    },
    {
        word: 'function',
        phonetic: '/ˈfʌŋkʃən/',
        translation: '功能；作用',
        example:
            'Each paragraph serves a function—introduction, contrast, or summary.',
        note: '动词形式可表示“正常运转”。',
    },
    {
        word: 'impact',
        phonetic: '/ˈɪmpækt/',
        translation: '影响；冲击',
        example:
            'Highlighting emotional impact helps readers maintain attention.',
        note: '作动词时重音在后。',
    },
    {
        word: 'maintain',
        phonetic: '/meɪnˈteɪn/',
        translation: '维持；坚持',
        example:
            'Maintain a daily writing habit to acquire vocabulary naturally.',
        note: 'maintain that + 从句，表示“坚称”。',
    },
]

const wordDictionary = DEFAULT_WORDS.reduce<Record<string, WordInfo>>(
    (acc, item) => {
        acc[item.word.toLowerCase()] = item
        return acc
    },
    {}
)
const fallbackWordInfo: WordInfo = {
    word: 'loading',
    phonetic: '',
    translation: '加载中',
    example: '',
    note: '',
}

const conversationMessages = ref<PreviewMessage[]>([
    {
        id: 1,
        sender: 'ai',
        text: '这段短文强调以“调查者心态”复盘单词，等上线后我可以针对细节继续追问。',
        time: '09:10',
    },
    {
        id: 2,
        sender: 'user',
        text: '我觉得 evidence 这一段还可以更生动一些，怎么改更好？',
        time: '09:10',
    },
    {
        id: 3,
        sender: 'ai',
        text: '可以尝试把 evidence 的来源具象化，比如“旧笔记里被圈起的短句”。',
        time: '09:11',
    },
    {
        id: 4,
        sender: 'user',
        text: '那 maintain 这个词是不是也应该在结尾再出现一次？',
        time: '09:12',
    },
    {
        id: 5,
        sender: 'ai',
        text: '是的，结尾强调保持习惯，可以加强整段的闭合感。',
        time: '09:12',
    },
])

const storyLoading = ref(false)
const pageLoading = ref(true)
const storyText = ref('')
const activeWordIndex = ref(0)
const currentWords = ref<string[]>(DEFAULT_WORDS.map((item) => item.word))
const conversationInput = ref('')
const activeSideTab = ref('conversation')
const chatScrollbarRef = ref<{ setScrollTop: (value: number) => void }>()
const definitionTranslationsVisible = ref<Record<number, boolean>>({})

const wordSearch = ref('abandon')
const wordCardLoading = ref(false)
const wordCard = reactive({
    word: 'Abandon',
    part_of_speech: 'verb',
    phonetics: [
        {
            notation: '/əˈbændən/ (美)',
            audio_url:
                'https://media.merriam-webster.com/audio/prons/en/us/mp3/a/abando02.mp3',
        },
        {
            notation: '/əˈbandən/ (英)',
            audio_url:
                'https://media.merriam-webster.com/audio/prons/en/uk/mp3/a/abandon01.mp3',
        },
    ],
    variants: ['abandoned', 'abandoning'],
    inflections: ['abandons', 'abandoned', 'abandoning'],
    definitions: [
        {
            meaning:
                'to give up to the control or influence of another person or agent',
            translation: '将主导权或影响力交给他人',
            examples: [
                'The explorer refused to abandon her dream despite the harsh weather.',
            ],
        },
        {
            meaning: 'to withdraw from often in the face of danger or difficulty',
            translation: '在危险或困难面前撤离、放弃',
            examples: ['Villagers were forced to abandon their homes during the flood.'],
        },
    ],
    synonyms: ['cede', 'surrender', 'desert'],
    antonyms: ['keep', 'maintain'],
    labels: {
        general: ['often passive'],
        usage: ['formal'],
    },
})

const aiReplyTemplates = [
    '收到，我可以从结构、语气或证据角度再补充分析。',
    '好的，等正式接入后我会引用短文中的句子来佐证观点。',
    '了解，我稍后可以帮你总结 impact 相关的搭配。',
    '可以的，我们还能一起改写段落，保持词汇出现频率。',
]

const quickPrompts = [
    '请帮我提炼短文的主旨句？',
    '把 impact 相关的句子换成更口语化的表达。',
    '指出 maintain 出现的句子是否需要调整时态。',
]

const displayWords = computed<WordInfo[]>(() =>
    currentWords.value.map((word) => {
        const meta = wordDictionary[word.toLowerCase()]
        return (
            meta ?? {
                word,
                phonetic: '',
                translation: '',
                example: '',
                note: '',
            }
        )
    })
)

const primaryPhonetics = computed(() => {
    const list = wordCard.phonetics || []
    return list.length ? [list[0]] : []
})

const storyParagraphs = computed(() =>
    storyText.value
        ? storyText.value
              .split(/\n{2,}/)
              .map((paragraph) => paragraph.trim())
              .filter(Boolean)
        : []
)

const activeWord = computed(() => {
    const current = displayWords.value[activeWordIndex.value]
    return current ?? displayWords.value[0] ?? fallbackWordInfo
})

const wordCardLabels = computed(() => {
    const general = wordCard.labels?.general || []
    const usage = wordCard.labels?.usage || []
    return [...general, ...usage]
})

const formatPhonetic = (notation?: string) =>
    notation?.replace(/\s*\(.*?\)\s*$/, '') ?? ''

const displayDate = new Intl.DateTimeFormat('zh-CN', {
    month: 'long',
    day: 'numeric',
    weekday: 'long',
}).format(new Date())

const formatTime = () =>
    new Intl.DateTimeFormat('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
    }).format(new Date())

const scrollChatToBottom = () => {
    chatScrollbarRef.value?.setScrollTop?.(9999)
}

const handleRegenerate = () => {
    const fallbackWords = currentWords.value.length
        ? currentWords.value
        : DEFAULT_WORDS.map((item) => item.word)
    storyLoading.value = true
    generateWordStory({
        words: fallbackWords,
        force: true,
    })
        .then((response) => {
            updateStoryState(response.data)
            ElMessage.success('已向智能体请求新的短文')
        })
        .catch((error) => {
            console.error(error)
            ElMessage.error('重新生成失败，请稍后重试')
        })
        .finally(() => {
            storyLoading.value = false
        })
}

const handleWordSearch = () => {
    if (!wordSearch.value.trim()) {
        ElMessage.warning('请输入英文单词')
        return
    }
    wordCardLoading.value = true
    window.setTimeout(() => {
        wordCard.word = wordSearch.value.trim()
        wordCard.part_of_speech = 'verb'
        wordCard.definitions = [
            {
                meaning: `示例释义：${wordCard.word} 的 Merriam-Webster 解释`,
                translation: `${wordCard.word} 的中文释义示例`,
                examples: ['此处将在接入后端后展示真实例句。'],
            },
        ]
        wordCard.synonyms = ['synonym']
        wordCard.antonyms = []
        wordCardLoading.value = false
        ElMessage.info('界面预览，等待后端接入 Merriam-Webster API')
    }, 600)
}

const toggleDefinitionTranslation = (index: number) => {
    const current = definitionTranslationsVisible.value[index] ?? false
    definitionTranslationsVisible.value = {
        ...definitionTranslationsVisible.value,
        [index]: !current,
    }
}

const playWordAudio = (url?: string) => {
    if (!url) {
        ElMessage.warning('暂无音频资源')
        return
    }
    const audio = new Audio(url)
    audio.play().catch(() => {
        ElMessage.error('音频播放失败，请稍后重试')
    })
}

const handleConversationSend = () => {
    const text = conversationInput.value.trim()
    if (!text) return

    conversationMessages.value.push({
        id: Date.now(),
        sender: 'user',
        text,
        time: formatTime(),
    })
    conversationInput.value = ''
    nextTick(scrollChatToBottom)

    window.setTimeout(() => {
        conversationMessages.value.push({
            id: Date.now(),
            sender: 'ai',
            text:
                aiReplyTemplates[
                    Math.floor(Math.random() * aiReplyTemplates.length)
                ],
            time: formatTime(),
        })
        nextTick(scrollChatToBottom)
    }, 600)
}

const handleQuickPrompt = (prompt: string) => {
    conversationInput.value = prompt
}

const handleClearInput = () => {
    conversationInput.value = ''
}

const nextWord = () => {
    const total = displayWords.value.length || 1
    activeWordIndex.value = (activeWordIndex.value + 1) % total
}

const prevWord = () => {
    const total = displayWords.value.length || 1
    activeWordIndex.value =
        (activeWordIndex.value - 1 + total) % total
}

const updateStoryState = (record?: WordStoryRecord) => {
    if (!record) return
    storyText.value = (record.story_text || '').trim()
    if (record.words && record.words.length) {
        currentWords.value = record.words
    }
    activeWordIndex.value = 0
}

const resetStoryState = () => {
    storyText.value = ''
    currentWords.value = DEFAULT_WORDS.map((item) => item.word)
    activeWordIndex.value = 0
}

const loadTodayStory = async () => {
    try {
        const { data } = await fetchTodayWordStory({
            auto_generate: false,
        })
        updateStoryState(data)
    } catch (error: any) {
        if (error?.code === 404) {
            resetStoryState()
            ElMessage.info('今日尚未生成短文，请点击“重新生成”')
        } else {
            console.error(error)
            ElMessage.error('获取今日短文失败，请稍后重试')
        }
    } finally {
        pageLoading.value = false
    }
}

onMounted(loadTodayStory)

watch(
    () => currentWords.value,
    () => {
        activeWordIndex.value = 0
    }
)

watch(
    () => wordCard.definitions,
    () => {
        definitionTranslationsVisible.value = {}
    },
    { deep: true }
)
</script>

<style lang="scss" scoped>
.word-story-page {
    padding: 12px;
    height: calc(100vh - 120px);
    display: flex;
    flex-direction: column;
    overflow: hidden;

    .word-story-row {
        height: 100%;
    }

    .story-column,
    .side-column {
        height: 100%;
        display: flex;
        flex-direction: column;
        min-height: 0;
    }

    .story-card {
        flex: 1;
        display: flex;
        flex-direction: column;
        min-height: 0;
        overflow: hidden;

        :deep(.el-card__body) {
            flex: 1;
            display: flex;
            flex-direction: column;
            min-height: 0;
            padding-top: 0;
        }

        &__header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;

            .headline {
                display: flex;
                flex-direction: column;
                line-height: 1.4;

                .eyebrow {
                    font-size: 12px;
                    letter-spacing: 0.1em;
                    color: var(--el-color-primary);
                    text-transform: uppercase;
                }

                strong {
                    font-size: 18px;
                }
            }

            .subtitle {
                color: var(--el-text-color-secondary);
                font-size: 13px;
            }
        }

        .story-meta {
            margin-bottom: 12px;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
            font-size: 13px;

            .meta-label {
                color: var(--el-text-color-regular);
                font-weight: 600;
            }

            .word-tag {
                text-transform: lowercase;
            }
        }

        .story-hint {
            margin-bottom: 16px;
        }

        .story-content {
            flex: 1;
            min-height: 0;
            padding-right: 4px;
            overflow: hidden;

            p {
                font-size: 15px;
                line-height: 1.8;
                margin-bottom: 16px;
                text-indent: 24px;
            }

            :deep(.el-scrollbar__wrap) {
                height: 100%;
            }

            :deep(.el-scrollbar__view) {
                min-height: 100%;
                padding-right: 10px;
            }
        }
    }

    .side-panels {
        display: flex;
        flex-direction: column;
        gap: 24px;
        height: 100%;
        min-height: 0;
    }

    .fill-card {
        flex: 1;
        display: flex;
        flex-direction: column;
        min-height: 0;
        overflow: hidden;

        :deep(.el-card__body) {
            flex: 1;
            display: flex;
            flex-direction: column;
            min-height: 0;
            padding-top: 0;
        }
    }

    /* ⭐ 这里把 side-card 也做成标准“可滚动卡片”布局 */
    .side-card {
        display: flex;
        flex-direction: column;
        flex: 1;
        min-height: 0;
        overflow: hidden;

        :deep(.el-card__body) {
            flex: 1;
            display: flex;
            flex-direction: column;
            min-height: 0;
            padding-top: 0;
        }

        .conversation-body {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 12px;
            min-height: 0;
        }

        .chat-intro {
            border: 1px dashed var(--el-color-primary-light-5);
            border-radius: 10px;
            padding: 10px 12px;
            background: var(--el-color-primary-light-9);
        }

        .chat-title {
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 6px;
            color: var(--el-color-primary);
        }

        .chat-prompts {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }

        .chat-scroll {
            flex: 1;
            min-height: 0;
            padding-right: 6px;

            :deep(.el-scrollbar__wrap),
            :deep(.el-scrollbar__view) {
                max-height: 100%;
            }
        }

        .chat-bubble {
            padding: 12px;
            border-radius: 12px;
            background: var(--el-fill-color-lighter);
            margin-bottom: 10px;
            position: relative;

            &.ai {
                border-left: 3px solid var(--el-color-primary);
                background: var(--el-color-primary-light-9);
            }

            &.user {
                border-left: 3px solid var(--el-color-success);
            }
        }

        .bubble-meta {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            margin-bottom: 4px;
            color: var(--el-text-color-secondary);
        }

        .bubble-text {
            margin: 0;
            font-size: 14px;
            line-height: 1.7;
        }

        .conversation-input {
            display: flex;
            flex-direction: column;
            gap: 8px;

            .chat-textarea :deep(textarea) {
                font-size: 14px;
            }

            .input-actions {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
        }
    }

    .side-tabs {
        :deep(.el-tabs__header) {
            margin-bottom: 12px;
        }
    }

    .pane-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;

        .title {
            font-size: 16px;
            font-weight: 600;
        }

        .subtitle {
            font-size: 13px;
            color: var(--el-text-color-secondary);
        }
    }

    /* ⭐ 单词卡片区域相关 */

    /* 单词卡片区域整体还是占满卡片高度 */
    .word-pane {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }

    /* 上面是搜索框，下面整块是“可滚动内容区” */
    .word-card__body {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 16px;
    }

    /* ⭐ 关键：把真正滚动的容器高度“锁死”，超出的就滚动 */
    .word-scroll {
        max-height: 380px;
    }

    /* ⭐ el-scrollbar 内部真正负责滚动的是这个 wrap，我们在这里做限制 */
    .word-scroll :deep(.el-scrollbar_wrap),
    .word-scroll :deep(.el-scrollbar_wrap--hidden-default) {
        max-height: 380px;
        overflow-y: auto;
    }

    /* 可选：让 view 至少跟 wrap 一样高 */
    .word-scroll :deep(.el-scrollbar_view) {
        min-height: 100%;
    }

    .word-index {
        position: absolute;
        top: 0;
        right: 0;
        font-size: 12px;
        color: var(--el-text-color-secondary);
    }

    .word-main {
        .word-text {
            font-size: 28px;
            font-weight: 700;
            text-transform: capitalize;
        }

        .word-phonetic {
            color: var(--el-text-color-secondary);
            margin-top: 4px;
        }

        .word-translation {
            margin-top: 8px;
            font-size: 15px;
        }
    }

    .word-example,
    .word-note {
        margin: 0;
        line-height: 1.6;
        font-size: 14px;
    }

    .card-actions {
        display: flex;
        align-items: center;

        .el-button {
            padding: 4px;
        }
    }

    .word-search {
        display: flex;
        gap: 12px;
        align-items: center;
    }

    .word-header {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        align-items: flex-start;

        .word-title {
            display: flex;
            gap: 10px;
            align-items: center;

            span {
                font-size: 26px;
                font-weight: 600;
                text-transform: capitalize;
            }
        }

        .word-tags {
            margin-top: 8px;
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }

        .word-actions {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 6px;
            color: var(--el-text-color-secondary);
            font-size: 13px;

            .word-audio-btn {
                padding: 0;
                background: transparent;
                border: none;
                min-height: auto;
                line-height: 0;

                &:hover {
                    background: transparent;
                    transform: scale(1.05);
                }
            }

            .audio-image {
                width: 32px;
                height: 32px;
                display: block;
            }
        }
    }

    .pos-tag {
        font-size: 8px;
        line-height: 1;
        text-transform: lowercase;
        padding: 2px 6px;
        color: var(--el-text-color-secondary);
        background: var(--el-fill-color);
        border-color: var(--el-border-color);
    }

    .word-basic {
        background: var(--el-fill-color-lighter);
        border-radius: 12px;
        padding: 12px;
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    .phonetics {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .phonetic-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .phonetic-item {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 6px 10px;
        border-radius: 8px;
        background: var(--el-color-primary-light-9);
        font-family: 'JetBrains Mono', monospace;

        .phonetic-audio {
            padding: 0;
            background: transparent;
            border: none;
            box-shadow: none;
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;

            img {
                width: 20px;
                height: 20px;
            }
        }
    }

    .variants {
        display: flex;
        align-items: center;
        gap: 8px;

        .label {
            color: var(--el-text-color-secondary);
        }
    }

    .info-block {
        background: var(--el-fill-color-lighter);
        border-radius: 12px;
        padding: 16px;

        h4 {
            margin: 0 0 10px;
        }
    }

    .empty-tip {
        margin: 0;
        color: var(--el-text-color-secondary);
    }

    .definition-text {
        font-size: 15px;
        font-weight: 500;
    }

    .example-list {
        margin: 8px 0 0 16px;
        padding: 0;
        list-style: disc;
        color: var(--el-text-color-secondary);
    }

    .definition-block {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }

    .definition-item {
        padding: 12px;
        border-radius: 12px;
        background: var(--el-fill-color);
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .definition-heading {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .definition-index {
        font-weight: 600;
        color: var(--el-color-primary);
    }

    .translation-trigger {
        font-size: 12px;
        padding: 0 8px;
    }

    .definition-translation {
        margin: 0;
        padding: 8px 10px;
        border-radius: 8px;
        background: var(--el-color-info-light-9);
        font-size: 14px;
        color: var(--el-color-info-dark-2);
    }

    .syn-ant-block {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }

    .syn-ant-group {
        background: var(--el-fill-color-lighter);
        border-radius: 12px;
        padding: 12px;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .syn-ant-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 8px;

        h4 {
            margin: 0;
        }
    }

    .group-count {
        font-size: 12px;
        color: var(--el-text-color-secondary);
    }

    .chip-list {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .chip {
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 13px;
        line-height: 1.2;
        background: var(--el-fill-color-dark);
    }

    .chip-syn {
        border: 1px solid var(--el-color-success-light-5);
        background: var(--el-color-success-light-9);
        color: var(--el-color-success-dark-2);
    }

    .chip-ant {
        border: 1px solid var(--el-color-danger-light-5);
        background: var(--el-color-danger-light-9);
        color: var(--el-color-danger-dark-2);
    }
}

/* 左侧短文和右侧对话滚动条样式（单词卡片保持默认样式也可以） */
:deep(.story-content .el-scrollbar__bar.is-vertical),
:deep(.chat-scroll .el-scrollbar__bar.is-vertical) {
    width: 6px;
    right: 0;
}

:deep(.story-content .el-scrollbar__thumb),
:deep(.chat-scroll .el-scrollbar__thumb) {
    background-color: var(--el-color-primary-light-5);
}

:deep(.el-tabs__content) {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
}

:deep(.el-tab-pane) {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
}

@media (max-width: 1024px) {
    .word-story-page {
        height: auto;
        overflow: visible;
    }

    .word-story-row,
    .story-column,
    .side-column,
    .side-panels {
        height: auto !important;
        min-height: auto;
    }

    .fill-card {
        height: auto;
    }
}

.paragraph-fade-enter-active,
.paragraph-fade-leave-active {
    transition: opacity 0.4s;
}

.paragraph-fade-enter-from,
.paragraph-fade-leave-to {
    opacity: 0;
}
</style>
