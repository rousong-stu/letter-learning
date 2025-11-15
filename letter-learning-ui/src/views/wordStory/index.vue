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
                                    再学一篇
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

                    <div class="story-content-wrapper">
                        <div class="story-visual-fixed">
                            <div class="visual-frame" v-if="storyImageUrl">
                                <el-image
                                    :src="storyImageUrl"
                                    fit="cover"
                                    :preview-src-list="[storyImageUrl]"
                                >
                                    <template #error>
                                        <div class="image-fallback">
                                            <vab-remix-icon icon="image-line" />
                                            <span>插图加载失败</span>
                                        </div>
                                    </template>
                                </el-image>
                            </div>
                            <div class="visual-frame placeholder" v-else>
                                <div class="image-fallback">
                                    <vab-remix-icon icon="image-add-line" />
                                    <span>生成插图后将在此展示</span>
                                </div>
                            </div>
                        </div>
                        <el-scrollbar class="story-content" always>
                            <div class="story-flow">
                                <transition-group name="paragraph-fade" tag="div">
                                    <p
                                        v-for="(paragraph, index) in storyParagraphs"
                                        :key="`paragraph-${index}`"
                                    >
                                        {{ paragraph }}
                                    </p>
                                </transition-group>
                            </div>
                        </el-scrollbar>
                    </div>
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
                                <div class="conversation-section">
                                    <div class="conversation-section__header">
                                        <el-button
                                            class="start-conversation-btn"
                                            type="primary"
                                            :loading="conversationSessionLoading"
                                            :disabled="!isStoryReady || conversationSessionLoading"
                                            @click="startNewConversation"
                                        >
                                            开始新对话
                                        </el-button>
                                    </div>
                                    <div class="conversation-section__body">
                                        <el-scrollbar ref="chatScrollbarRef" class="chat-scroll" always>
                                            <div
                                                v-for="message in conversationMessages"
                                                :key="message.id"
                                                class="chat-message"
                                                :class="message.sender"
                                            >
                                                <el-avatar
                                                    class="chat-avatar"
                                                    :src="
                                                        message.sender === 'ai'
                                                            ? aiAvatar
                                                            : userAvatar || defaultUserAvatar
                                                    "
                                                />
                                                <div class="chat-bubble">
                                                    <div
                                                        v-if="message.status === 'pending'"
                                                        class="bubble-loading"
                                                    >
                                                        <span class="dot" />
                                                        <span class="dot" />
                                                        <span class="dot" />
                                                    </div>
                                                    <p v-else class="bubble-text">
                                                        {{ message.text }}
                                                    </p>
                                                </div>
                                            </div>
                                        </el-scrollbar>
                                    </div>
                                    <div class="conversation-section__footer">
                                        <el-input
                                            v-model="conversationInput"
                                            placeholder="问短文相关的任何问题"
                                            class="chat-inline-input"
                                            @keyup.enter="handleConversationSend"
                                        />
                                        <el-button
                                            type="primary"
                                            class="chat-send-btn"
                                            :disabled="
                                                chatSending ||
                                                !activeChatSession ||
                                                !conversationInput.trim()
                                            "
                                            :loading="chatSending"
                                            @click="handleConversationSend"
                                        >
                                            <vab-remix-icon icon="send-plane-2-line" />
                                            发送
                                        </el-button>
                                    </div>
                                </div>
                            </el-tab-pane>
                            <el-tab-pane label="单词卡片" name="cards">
                                <div class="review-pane">
                                    <div class="review-header">
                                        <div>
                                            <h4>今日学习中的单词</h4>
                                            <p class="review-subtitle">
                                                快速回忆这些单词，判断是否掌握。
                                            </p>
                                        </div>
                                    </div>
                                    <div
                                        v-if="learningCardError"
                                        class="review-placeholder"
                                    >
                                        <p>{{ learningCardError }}</p>
                                        <el-button
                                            type="primary"
                                            size="small"
                                            @click="loadLearningCards"
                                        >
                                            重试
                                        </el-button>
                                    </div>
                                    <div
                                        v-else-if="learningCardLoading"
                                        class="review-placeholder"
                                    >
                                        <vab-remix-icon icon="loader-2-line" class="loading-icon" />
                                        <p>正在准备单词卡片...</p>
                                    </div>
                                    <div
                                        v-else-if="!currentLearningCard"
                                        class="review-placeholder"
                                    >
                                        <vab-remix-icon
                                            icon="sparkling-2-line"
                                            class="placeholder-icon"
                                        />
                                        <p>暂无学习中的单词，完成学习计划后再来看看吧。</p>
                                    </div>
                                    <div v-else class="learning-card-board">
                                        <div class="learning-word-main">
                                            <h2 class="learning-word">
                                                {{ currentLearningCard.word }}
                                            </h2>
                                        </div>
                                        <div
                                            v-if="learningCardViewMode === 'hint'"
                                            class="learning-card-hint"
                                        >
                                            <h5>提示</h5>
                                            <p>
                                                {{
                                                    currentLearningHintExample ||
                                                    '暂无例句，试着直接回忆它的含义吧。'
                                                }}
                                            </p>
                                        </div>
                                        <div
                                            v-if="learningCardViewMode === 'detail'"
                                            class="learning-card-detail"
                                        >
                                            <div v-if="learningCardDictionaryLoading" class="review-placeholder">
                                                <vab-remix-icon icon="loader-2-line" class="loading-icon" />
                                                <p>正在查询词典...</p>
                                            </div>
                                            <template v-else-if="currentLearningDictionaryEntry">
                                                <div class="detail-phonetics">
                                                    <span
                                                        v-for="item in currentLearningDictionaryEntry.phonetics || []"
                                                        :key="item.notation"
                                                    >
                                                        {{ formatPhonetic(item.notation) }}
                                                    </span>
                                                </div>
                                                <div class="detail-definitions">
                                                    <div
                                                        v-for="(definition, index) in currentLearningDictionaryEntry.definitions"
                                                        :key="index"
                                                        class="detail-definition"
                                                    >
                                                        <strong>释义 {{ index + 1 }}</strong>
                                                        <p>{{ definition.meaning }}</p>
                                                        <p v-if="definition.translation" class="definition-translation">
                                                            {{ definition.translation }}
                                                        </p>
                                                        <ul v-if="definition.examples?.length">
                                                            <li v-for="(example, idx) in definition.examples" :key="idx">
                                                                {{ example }}
                                                            </li>
                                                        </ul>
                                                    </div>
                                                </div>
                                            </template>
                                            <p v-else class="review-placeholder">
                                                暂无词典详情。
                                            </p>
                                        </div>
                                        <div class="learning-card-actions">
                                            <el-button
                                                type="success"
                                                plain
                                                :loading="learningCardActionLoading"
                                                @click="handleLearningTooEasy"
                                            >
                                                太简单
                                            </el-button>
                                            <el-button
                                                type="primary"
                                                plain
                                                :loading="learningCardActionLoading"
                                                @click="handleLearningKnown"
                                            >
                                                我认识
                                            </el-button>
                                            <el-button
                                                plain
                                                @click="handleLearningHint"
                                                :disabled="learningCardViewMode !== 'minimal'"
                                            >
                                                提示
                                            </el-button>
                                        </div>
                                        <div class="learning-card-actions secondary">
                                            <el-button @click="handleLearningReveal">
                                                没想起来
                                            </el-button>
                                            <el-button @click="handleLearningReveal">
                                                想起来了
                                            </el-button>
                                            <el-button @click="handleLearningReveal">
                                                不认识
                                            </el-button>
                                        </div>
                                        <el-button
                                            v-if="learningCardViewMode === 'detail'"
                                            type="primary"
                                            class="next-card-btn"
                                            @click="handleLearningNext"
                                        >
                                            下一个单词
                                        </el-button>
                                    </div>
                                </div>
                            </el-tab-pane>
                            <el-tab-pane label="词典" name="word">
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
                                        <el-alert
                                            v-if="wordCardError"
                                            :title="wordCardError"
                                            type="error"
                                            :closable="false"
                                            show-icon
                                            class="word-card__alert"
                                        />
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
                                                            :loading="isDefinitionTranslationLoading(index)"
                                                            @click="handleDefinitionTranslation(index)"
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
import {
    computed,
    nextTick,
    onBeforeUnmount,
    onMounted,
    reactive,
    ref,
    watch,
} from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
    fetchTodayWordStory,
    generateWordStory,
    type WordStoryRecord,
} from '@/api/wordStory'
import {
    createAiChatSession,
    sendAiChatMessage,
} from '@/api/aiChat'
import type { AiChatMessage, AiChatSession } from '@/api/aiChat'
import { lookupDictionaryEntry, translateDefinition } from '@/api/dictionary'
import {
    fetchLearningWordCards,
    applyWordCardAction,
    type WordCardItem as LearningWordCard,
} from '@/api/wordCards'
import speakerIcon from '@/assets/speaker-icon.svg'
import { useUserStore } from '@/store/modules/user'
import { storeToRefs } from 'pinia'

type WordInfo = {
    word: string
    phonetic: string
    translation: string
    example: string
    note: string
}

type ConversationMessage = {
    id: number
    sender: 'ai' | 'user'
    text: string
    createdAt: string
    status?: 'pending' | 'done'
}

type DictionaryEntry = {
    id: number
    word: string
    part_of_speech?: string
    phonetics?: Array<{ notation: string; audio_url?: string }>
    variants?: string[]
    inflections?: string[]
    definitions: Array<{
        meaning: string
        translation?: string
        examples?: string[]
    }>
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

const userStore = useUserStore()
const { avatar: userAvatar } = storeToRefs(userStore)
const aiAvatar = new URL('@/assets/lumilyx-avatar.jpeg', import.meta.url).href
const defaultUserAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const MAX_CHAT_ROUNDS = 12
const conversationMessages = ref<ConversationMessage[]>([])
const activeChatSession = ref<AiChatSession | null>(null)
const conversationSessionLoading = ref(false)
const conversationSending = ref(false)

const mapBackendMessage = (message: AiChatMessage): ConversationMessage => ({
    id: message.id,
    sender: message.sender,
    text: message.content,
    createdAt: message.created_at,
    status: 'done',
})

let localMessageSeed = -1

const showRoundLimitAlert = () =>
    ElMessageBox.alert('每次对话最多持续12轮', '提示', {
        confirmButtonText: '我知道了',
    }).catch(() => undefined)

const appendMessages = (messages: AiChatMessage[]) => {
    if (!messages || !messages.length) return
    conversationMessages.value = [
        ...conversationMessages.value,
        ...messages.map(mapBackendMessage),
    ]
}

const createLocalMessage = (
    text: string,
    sender: 'ai' | 'user',
    status: ConversationMessage['status'] = 'done'
): ConversationMessage => ({
    id: localMessageSeed--,
    sender,
    text,
    createdAt: new Date().toISOString(),
    status,
})

const pushLocalUserMessage = (text: string) => {
    const message = createLocalMessage(text, 'user')
    conversationMessages.value = [...conversationMessages.value, message]
    nextTick(scrollChatToBottom)
    return message.id
}

const removeMessageById = (id: number) => {
    const index = conversationMessages.value.findIndex(
        (item) => item.id === id
    )
    if (index !== -1) {
        const list = [...conversationMessages.value]
        list.splice(index, 1)
        conversationMessages.value = list
    }
}

const upsertPendingAiMessage = () => {
    const message = createLocalMessage('', 'ai', 'pending')
    conversationMessages.value = [...conversationMessages.value, message]
    nextTick(scrollChatToBottom)
    return message.id
}

const updateMessageContent = (
    id: number,
    text: string,
    status: ConversationMessage['status'] = 'done'
) => {
    const index = conversationMessages.value.findIndex(
        (item) => item.id === id
    )
    if (index === -1) return
    const list = [...conversationMessages.value]
    list[index] = {
        ...list[index],
        text,
        status,
    }
    conversationMessages.value = list
    nextTick(scrollChatToBottom)
}

const storyLoading = ref(false)
const pageLoading = ref(true)
const storyText = ref('')
const currentStoryId = ref<number | null>(null)
const storyImageUrl = ref('')
const storyImageCaption = ref('')
const activeWordIndex = ref(0)
const currentWords = ref<string[]>(DEFAULT_WORDS.map((item) => item.word))
const conversationInput = ref('')
const activeSideTab = ref('conversation')
const chatScrollbarRef = ref<{ setScrollTop: (value: number) => void }>()
const definitionTranslationsVisible = ref<Record<number, boolean>>({})
const isStoryReady = computed(() => !!storyText.value.trim())
const currentStoryKey = computed(() => {
    const snapshot = storyText.value.trim()
    if (currentStoryId.value) {
        return `id:${currentStoryId.value}|text:${snapshot}`
    }
    return snapshot ? `text:${snapshot}` : ''
})
const lastStoryKeyUsed = ref('')
const pendingAutoConversation = ref(false)
const PAGE_LAYOUT_CLASS = 'word-story-no-footer'

const learningWordCards = ref<LearningWordCard[]>([])
const learningCardLoading = ref(false)
const learningCardError = ref('')
const learningCardActionLoading = ref(false)
const learningCardDictionaryLoading = ref(false)
const learningCardViewMode = ref<'minimal' | 'hint' | 'detail'>('minimal')
const learningDictionaryCache = reactive<Record<string, DictionaryEntry>>({})

const wordSearch = ref('abandon')
const wordCardLoading = ref(false)
const wordCardError = ref('')
const definitionTranslationLoading = ref<Record<number, boolean>>({})
const wordCard = reactive({
    id: 0,
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
        parenthetical: [],
    },
    etymology: '',
})

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

const currentLearningCard = computed(() => learningWordCards.value[0] || null)
const currentDictionaryKey = computed(() =>
    currentLearningCard.value?.word?.toLowerCase() || ''
)
const currentLearningDictionaryEntry = computed<DictionaryEntry | null>(() => {
    const key = currentDictionaryKey.value
    if (!key) return null
    return learningDictionaryCache[key] || null
})
const currentLearningHintExample = computed(() => {
    const entry = currentLearningDictionaryEntry.value
    if (!entry) return ''
    for (const definition of entry.definitions || []) {
        if (definition.examples && definition.examples.length) {
            return definition.examples[0]
        }
    }
    return ''
})

const formatPhonetic = (notation?: string) =>
    notation?.replace(/\s*\(.*?\)\s*$/, '') ?? ''

const displayDate = new Intl.DateTimeFormat('zh-CN', {
    month: 'long',
    day: 'numeric',
    weekday: 'long',
}).format(new Date())

const scrollChatToBottom = () => {
    chatScrollbarRef.value?.setScrollTop?.(9999)
}

const handleRegenerate = () => {
    storyLoading.value = true
    generateWordStory({
        force: true,
    })
        .then((response) => {
            updateStoryState(response.data)
            ElMessage.success('已向智能体请求新的短文')
        })
        .catch((error) => {
            console.error(error)
            ElMessage.error('再学一篇失败，请稍后重试')
        })
        .finally(() => {
            storyLoading.value = false
        })
}

const applyWordCardPayload = (payload: any, fallbackWord: string) => {
    const labels = payload?.labels || {}
    wordCard.id = payload?.id ?? 0
    wordCard.word = payload?.word || fallbackWord
    wordCard.part_of_speech = payload?.part_of_speech || ''
    wordCard.phonetics = payload?.phonetics ?? []
    wordCard.variants = payload?.variants ?? []
    wordCard.inflections = payload?.inflections ?? []
    wordCard.definitions = (payload?.definitions ?? []).map((item: any) => ({
        meaning: item?.meaning || '',
        examples: Array.isArray(item?.examples) ? item.examples : [],
        translation: item?.translation || '',
    }))
    wordCard.synonyms = payload?.synonyms ?? []
    wordCard.antonyms = payload?.antonyms ?? []
    wordCard.labels = {
        general: labels.general ?? [],
        usage: labels.usage ?? [],
        parenthetical: labels.parenthetical ?? [],
    }
    wordCard.etymology = payload?.etymology ?? ''
    definitionTranslationsVisible.value = {}
    definitionTranslationLoading.value = {}
}

const handleWordSearch = async () => {
    const query = wordSearch.value.trim()
    if (!query) {
        ElMessage.warning('请输入英文单词')
        return
    }
    wordCardLoading.value = true
    wordCardError.value = ''
    try {
        const { data } = await lookupDictionaryEntry(query)
        applyWordCardPayload(data, query)
        ElMessage.success(`已获取 ${data.word || query} 的最新词典信息`)
    } catch (error: any) {
        const message =
            error?.msg ||
            error?.message ||
            '查询词典失败，请稍后重试'
        wordCardError.value = message
        ElMessage.error(message)
    } finally {
        wordCardLoading.value = false
    }
}

const setDefinitionTranslationLoading = (index: number, value: boolean) => {
    definitionTranslationLoading.value = {
        ...definitionTranslationLoading.value,
        [index]: value,
    }
}

const handleDefinitionTranslation = async (index: number) => {
    const definition = wordCard.definitions[index]
    if (!definition) return
    const isVisible = definitionTranslationsVisible.value[index]
    if (isVisible) {
        definitionTranslationsVisible.value = {
            ...definitionTranslationsVisible.value,
            [index]: false,
        }
        return
    }
    if (!definition.translation) {
        if (!wordCard.id) {
            ElMessage.warning('请先查询单词')
            return
        }
        setDefinitionTranslationLoading(index, true)
        try {
            const { data } = await translateDefinition(wordCard.id, index)
            definition.translation = data.translation
            ElMessage.success('中文释义已生成')
        } catch (error: any) {
            const message =
                error?.msg || error?.message || '生成中文释义失败'
            ElMessage.error(message)
            return
        } finally {
            setDefinitionTranslationLoading(index, false)
        }
    }
    definitionTranslationsVisible.value = {
        ...definitionTranslationsVisible.value,
        [index]: true,
    }
}

const isDefinitionTranslationLoading = (index: number) =>
    !!definitionTranslationLoading.value[index]

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

const startNewConversation = async () => {
    if (conversationSessionLoading.value) return
    if (!isStoryReady.value) {
        ElMessage.warning('短文尚未加载完成')
        return
    }
    conversationSessionLoading.value = true
    try {
        const { data } = await createAiChatSession({
            story_text: storyText.value,
            word_story_id: currentStoryId.value ?? undefined,
        })
        activeChatSession.value = data.session
        conversationMessages.value = data.messages.map(mapBackendMessage)
        lastStoryKeyUsed.value = currentStoryKey.value
        conversationInput.value = ''
        nextTick(scrollChatToBottom)
    } catch (error: any) {
        const message =
            error?.msg || error?.message || '开启新对话失败，请稍后再试'
        ElMessage.error(message)
    } finally {
        conversationSessionLoading.value = false
    }
}

const requestAutoConversationStart = () => {
    if (!isStoryReady.value) return
    pendingAutoConversation.value = true
    if (!conversationSessionLoading.value) {
        pendingAutoConversation.value = false
        startNewConversation().catch(() => {})
    }
}

const resetLearningCardState = () => {
    learningCardViewMode.value = 'minimal'
}

const loadLearningCards = async () => {
    learningCardLoading.value = true
    learningCardError.value = ''
    try {
        const { data } = await fetchLearningWordCards(10)
        learningWordCards.value = data.items || []
        resetLearningCardState()
    } catch (error: any) {
        const message =
            error?.msg || error?.message || '获取单词卡片失败，请稍后再试'
        learningCardError.value = message
        ElMessage.error(message)
    } finally {
        learningCardLoading.value = false
    }
}

const ensureDictionaryEntry = async () => {
    const word = currentDictionaryKey.value
    if (!word) return null
    if (learningDictionaryCache[word]) return learningDictionaryCache[word]
    learningCardDictionaryLoading.value = true
    try {
        const { data } = await lookupDictionaryEntry(word)
        learningDictionaryCache[word] = data
        return data
    } catch (error: any) {
        const message =
            error?.msg || error?.message || '获取词典信息失败，请稍后再试'
        ElMessage.error(message)
        return null
    } finally {
        learningCardDictionaryLoading.value = false
    }
}

const submitLearningAction = async (
    action: 'too_easy' | 'know' | 'review'
) => {
    const current = currentLearningCard.value
    if (!current) return
    learningCardActionLoading.value = true
    try {
        await applyWordCardAction(current.id, action)
    } catch (error: any) {
        const message =
            error?.msg || error?.message || '操作失败，请稍后再试'
        ElMessage.error(message)
        throw error
    } finally {
        learningCardActionLoading.value = false
    }
}

const moveToNextLearningCard = async () => {
    if (learningWordCards.value.length) {
        learningWordCards.value = learningWordCards.value.slice(1)
    }
    resetLearningCardState()
    if (!learningWordCards.value.length && !learningCardLoading.value) {
        await loadLearningCards()
    }
}

const handleLearningTooEasy = async () => {
    if (!currentLearningCard.value) return
    try {
        await submitLearningAction('too_easy')
        await moveToNextLearningCard()
    } catch {
        // handled
    }
}

const handleLearningKnown = async () => {
    if (!currentLearningCard.value) return
    try {
        await submitLearningAction('know')
        await moveToNextLearningCard()
    } catch {
        // handled
    }
}

const handleLearningHint = async () => {
    const entry = await ensureDictionaryEntry()
    if (!entry) return
    if (
        !entry.definitions ||
        !entry.definitions.length ||
        !(entry.definitions[0].examples || []).length
    ) {
        ElMessage.info('暂无可用例句')
    }
    learningCardViewMode.value = 'hint'
}

const handleLearningReveal = async () => {
    const entry = await ensureDictionaryEntry()
    if (!entry) return
    try {
        await submitLearningAction('review')
    } catch {
        return
    }
    learningCardViewMode.value = 'detail'
}

const handleLearningNext = async () => {
    await moveToNextLearningCard()
}

const handleConversationSend = async () => {
    const text = conversationInput.value.trim()
    if (!text) return

    if (!activeChatSession.value || conversationSessionLoading.value) {
        ElMessage.warning('请先开始新对话')
        return
    }

    if (activeChatSession.value.total_rounds >= MAX_CHAT_ROUNDS) {
        await showRoundLimitAlert()
        return
    }

    if (conversationSending.value) return
    conversationSending.value = true
    const localMessageId = pushLocalUserMessage(text)
    const pendingAiId = upsertPendingAiMessage()
    conversationInput.value = ''
    try {
        const { data } = await sendAiChatMessage(
            activeChatSession.value.id,
            text
        )
        const aiMessages = (data.new_messages || []).filter(
            (item) => item.sender === 'ai'
        )
        if (aiMessages.length) {
            const [first, ...rest] = aiMessages
            updateMessageContent(pendingAiId, first.content, 'done')
            if (rest.length) {
                appendMessages(rest)
            }
        } else {
            updateMessageContent(pendingAiId, 'AI 正在思考中...', 'pending')
        }
        activeChatSession.value = data.session
        nextTick(scrollChatToBottom)
    } catch (error: any) {
        removeMessageById(localMessageId)
        removeMessageById(pendingAiId)
        conversationInput.value = text
        const message =
            error?.msg || error?.message || '发送失败，请稍后重试'
        if (message.includes('每次对话最多持续12轮')) {
            await showRoundLimitAlert()
            if (activeChatSession.value) {
                activeChatSession.value.total_rounds = MAX_CHAT_ROUNDS
                activeChatSession.value.status = 'completed'
            }
        } else {
            ElMessage.error(message)
        }
    } finally {
        conversationSending.value = false
    }
}

watch(
    () => currentStoryKey.value,
    (key) => {
        if (!key) return
        if (key === lastStoryKeyUsed.value) return
        requestAutoConversationStart()
    }
)

watch(
    () => conversationSessionLoading.value,
    (loading) => {
        if (!loading && pendingAutoConversation.value) {
            pendingAutoConversation.value = false
            startNewConversation().catch(() => {})
        }
    }
)

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
    currentStoryId.value = record.id ?? null
    storyText.value = (record.story_text || '').trim()
    storyImageUrl.value = record.image_url || ''
    storyImageCaption.value = record.image_caption || ''
    if (record.words && record.words.length) {
        currentWords.value = record.words
    }
    activeWordIndex.value = 0
}

const resetStoryState = () => {
    storyText.value = ''
    currentStoryId.value = null
    storyImageUrl.value = ''
    storyImageCaption.value = ''
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
            ElMessage.info('今日尚未生成短文，请点击“再学一篇”')
        } else {
            console.error(error)
            ElMessage.error('获取今日短文失败，请稍后重试')
        }
    } finally {
        pageLoading.value = false
    }
}

onMounted(() => {
    document.body.classList.add(PAGE_LAYOUT_CLASS)
    loadTodayStory()
})

onBeforeUnmount(() => {
    document.body.classList.remove(PAGE_LAYOUT_CLASS)
})

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

watch(
    () => activeSideTab.value,
    (tab) => {
        if (tab === 'cards' && !learningCardLoading.value) {
            if (!learningWordCards.value.length) {
                loadLearningCards()
            }
        }
    }
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

        .story-content-wrapper {
            flex: 1;
            min-height: 0;
            display: grid;
            grid-template-columns: minmax(160px, 20%) 1fr;
            gap: 24px;

            .story-visual-fixed {
                position: sticky;
                top: 0;
                align-self: flex-start;

                .visual-frame {
                    width: 100%;
                    max-width: 240px;
                    aspect-ratio: 682 / 1024;
                    border-radius: 16px;
                    overflow: hidden;
                    box-shadow: 0 12px 26px rgba(0, 0, 0, 0.1);
                    background: var(--el-fill-color-light);

                    :deep(.el-image) {
                        width: 100%;
                        height: 100%;
                    }

                    &.placeholder {
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        color: var(--el-text-color-secondary);
                        gap: 6px;
                        text-align: center;
                        font-size: 12px;

                        .vab-remix-icon {
                            font-size: 18px;
                        }
                    }
                }
            }

            .story-content {
                min-height: 0;
                padding-right: 6px;

                :deep(.el-scrollbar__wrap) {
                    height: 100%;
                    overflow-y: auto;
                }

                :deep(.el-scrollbar__view) {
                    min-height: 100%;
                    padding-right: 12px;
                }

                .story-flow {
                    font-size: 15px;
                    line-height: 1.8;
                    color: var(--el-text-color-primary);
                    text-indent: 24px;

                    p {
                        margin-bottom: 16px;
                    }
                }
            }

            @media (max-width: 1024px) {
                grid-template-columns: 1fr;

                .story-visual-fixed {
                    position: relative;
                    display: flex;
                    justify-content: center;
                    margin-bottom: 12px;
                }
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

        :deep(.el-tabs) {
            display: flex;
            flex-direction: column;
            height: 100%;
            min-height: 0;
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

        .conversation-section {
            flex: 1;
            display: flex;
            flex-direction: column;
            min-height: 0;
            gap: 14px;

            &__header {
                height: 64px;
                display: flex;
                align-items: center;
            }

            &__body {
                flex: 1;
                min-height: 0;
                border: 1px dashed var(--el-color-primary-light-5);
                border-radius: 12px;
                padding: 12px;
                display: flex;
                flex-direction: column;
            }

            &__footer {
                height: 52px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
        }

        .chat-scroll {
            flex: 1;
            min-height: 0;
            padding-right: 6px;

            :deep(.el-scrollbar__wrap) {
                height: 100%;
            }

            :deep(.el-scrollbar__view) {
                min-height: 100%;
            }
        }

        .chat-message {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            margin-bottom: 12px;

            &.ai .chat-bubble {
                background: var(--el-color-primary-light-9);
            }

            &.user {
                flex-direction: row-reverse;

                .chat-bubble {
                    background: var(--el-fill-color);
                    text-align: left;
                }
            }
        }

        .chat-avatar {
            width: 38px;
            height: 38px;
        }

        .chat-bubble {
            flex: 1;
            padding: 10px 14px;
            border-radius: 14px;
            background: var(--el-fill-color-lighter);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
            min-height: 38px;
        }

        .bubble-text {
            margin: 0;
            font-size: 14px;
            line-height: 1.7;
        }

        .bubble-loading {
            display: flex;
            align-items: center;
            gap: 6px;

            .dot {
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background: var(--el-text-color-placeholder);
                animation: bubble-pulse 0.9s infinite ease-in-out;

                &:nth-child(2) {
                    animation-delay: 0.2s;
                }

                &:nth-child(3) {
                    animation-delay: 0.4s;
                }
            }
        }

        .conversation-section__footer {
            .chat-inline-input {
                flex: 1;
            }

            .chat-inline-input :deep(.el-input__wrapper) {
                height: 38px;
                font-size: 14px;
                border-radius: 10px;
            }

            .chat-send-btn {
                height: 38px;
                padding: 0 18px;
                border-radius: 12px;
            }
        }
    }

    .side-tabs {
        :deep(.el-tabs__header) {
            margin-bottom: 12px;
        }
    }

    .start-conversation-btn {
        width: 100%;
        justify-content: center;
        font-size: 16px;
        padding: 14px 0;
        border-radius: 20px;
        box-shadow: 0 8px 20px rgba(64, 158, 255, 0.25);
        background: #e6edff;
        border: 1px solid rgba(64, 158, 255, 0.35);
        font-weight: 600;
        color: #2b4fb7;
    }

    /* ⭐ 单词卡片区域相关 */

    /* 单词卡片区域整体还是占满卡片高度 */
    .word-pane {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }

    .review-pane {
        display: flex;
        flex-direction: column;
        gap: 16px;

        .review-header {
            display: flex;
            justify-content: space-between;
            align-items: center;

            h4 {
                margin: 0;
            }

            .review-subtitle {
                margin: 4px 0 0;
                font-size: 12px;
                color: var(--el-text-color-secondary);
            }
        }
    }

    .learning-card-board {
        border: 1px solid var(--el-border-color);
        border-radius: 20px;
        padding: 24px;
        display: flex;
        flex-direction: column;
        gap: 16px;
        background: linear-gradient(135deg, #f0f7ff, #fdf7ff);
    }

    .learning-word-main {
        text-align: center;

        .learning-progress {
            font-size: 12px;
            color: var(--el-text-color-secondary);
        }

        .learning-word {
            margin: 8px 0 0;
            font-size: 40px;
            font-weight: 700;
            letter-spacing: 1px;
        }
    }

    .learning-card-actions {
        display: flex;
        justify-content: center;
        gap: 12px;
        flex-wrap: wrap;

        &.secondary {
            margin-top: 4px;
        }
    }

    .learning-card-hint,
    .learning-card-detail {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);

        h5 {
            margin: 0 0 8px;
            font-size: 14px;
            color: var(--el-color-primary);
        }
    }

    .learning-card-detail {
        .detail-phonetics {
            display: flex;
            gap: 12px;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 12px;
        }

        .detail-definition {
            margin-bottom: 12px;

            strong {
                font-size: 13px;
            }

            p {
                margin: 4px 0;
            }

            ul {
                margin: 4px 0 0 16px;
                padding: 0;
            }
        }
    }

    .review-placeholder {
        min-height: 120px;
        border: 1px dashed var(--el-border-color);
        border-radius: 16px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        gap: 8px;
        color: var(--el-text-color-secondary);

        .placeholder-icon,
        .loading-icon {
            font-size: 28px;
            color: var(--el-color-primary);
        }
    }

    .next-card-btn {
        align-self: center;
    }

    /* 上面是搜索框，下面整块是“可滚动内容区” */
    .word-card__body {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 16px;

        .word-card__alert {
            margin-bottom: 4px;
        }
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

:global(body.word-story-no-footer) {
    overflow: hidden;
}

:global(body.word-story-no-footer .vab-footer) {
    display: none;
}

:global(body.word-story-no-footer .app-main) {
    padding-bottom: 0;
}

@keyframes bubble-pulse {
    0% {
        opacity: 0.2;
        transform: scale(0.8);
    }

    50% {
        opacity: 1;
        transform: scale(1);
    }

    100% {
        opacity: 0.2;
        transform: scale(0.8);
    }
}
</style>
