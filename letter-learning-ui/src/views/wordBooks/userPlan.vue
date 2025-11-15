<template>
    <div class="user-word-plan-page">
        <el-row :gutter="18">
            <el-col :lg="10" :md="10" :sm="24" :xs="24">
                <el-card shadow="hover" class="book-list-card">
                    <template #header>
                        <div class="card-header">
                            <span>选择单词书</span>
                            <el-button text size="small" @click="fetchWordBooks">
                                刷新
                            </el-button>
                        </div>
                    </template>

                    <el-empty
                        v-if="bookLoading && wordBooks.length === 0"
                        description="正在加载单词书..."
                    />

                    <el-table
                        v-else
                        :data="wordBooks"
                        border
                        height="480"
                        highlight-current-row
                        @current-change="handleBookSelect"
                        :row-class-name="rowClassName"
                    >
                        <el-table-column prop="title" label="书名" min-width="160">
                            <template #default="{ row }">
                                <div class="book-title">
                                    <el-avatar
                                        :size="32"
                                        :src="row.cover_url"
                                        icon="Picture"
                                    />
                                    <div>
                                        <div>{{ row.title }}</div>
                                        <small class="text-secondary">
                                            {{ row.level || '未指定级别' }}
                                        </small>
                                    </div>
                                </div>
                            </template>
                        </el-table-column>
                        <el-table-column
                            prop="total_words"
                            label="词数"
                            width="90"
                            align="center"
                        />
                        <el-table-column
                            prop="tags"
                            label="标签"
                            width="140"
                        >
                            <template #default="{ row }">
                                <el-tag
                                    v-for="tag in row.tags"
                                    :key="tag"
                                    size="small"
                                    type="success"
                                >
                                    {{ tag }}
                                </el-tag>
                            </template>
                        </el-table-column>
                    </el-table>
                </el-card>
            </el-col>
            <el-col :lg="14" :md="14" :sm="24" :xs="24">
                <el-card class="plan-form-card" shadow="hover">
                    <template #header>
                        <span>配置学习计划</span>
                    </template>

                    <el-alert
                        v-if="currentPlan"
                        type="info"
                        :closable="false"
                        class="current-plan-alert"
                    >
                        <template #title>
                            当前计划：{{ currentPlan.word_book.title }}
                        </template>
                        <div class="current-plan-description">
                            每日 {{ currentPlan.daily_quota }} 词 ·
                            开始于 {{ formatDate(currentPlan.start_date) }} ·
                            预计 {{ currentPlan.total_days }} 天
                        </div>
                    </el-alert>

                    <div class="selected-book-summary" v-if="activeBook">
                            <div class="cover">
                                <el-image
                                    :src="activeBook.cover_url"
                                    fit="cover"
                                    style="width: 96px; height: 128px"
                                >
                                    <template #error>
                                        <div class="cover-placeholder">
                                            <vab-remix-icon icon="image-line" />
                                        </div>
                                    </template>
                                </el-image>
                            </div>
                            <div class="meta">
                                <h3>{{ activeBook.title }}</h3>
                                <p>{{ activeBook.description || '暂无简介' }}</p>
                                <div class="meta-tags">
                                    <el-tag size="small" effect="plain">
                                        {{ activeBook.language || 'English' }}
                                    </el-tag>
                                    <el-tag size="small" type="info" effect="plain">
                                        {{ activeBook.level || '未设置级别' }}
                                    </el-tag>
                                    <el-tag
                                        v-for="tag in activeBook.tags"
                                        :key="tag"
                                        size="small"
                                        type="success"
                                        effect="plain"
                                    >
                                        {{ tag }}
                                    </el-tag>
                                </div>
                                <div class="meta-stats">
                                    <span>总词数：{{ activeBook.total_words }}</span>
                                    <span
                                        >预计天数：{{
                                            estimatedDays || '--'
                                        }}</span
                                    >
                                </div>
                            </div>
                        </div>

                        <div v-else class="summary-placeholder">
                            <el-empty description="请先在左侧选择单词书" />
                        </div>

                    <el-divider />

                    <el-form
                        ref="planFormRef"
                        :model="planForm"
                        :rules="planRules"
                        label-width="120px"
                        class="plan-form"
                    >
                        <el-form-item label="每日学习词数" prop="dailyQuota">
                            <el-input-number
                                v-model="planForm.dailyQuota"
                                :min="5"
                                :max="40"
                                :step="5"
                                :disabled="formDisabled"
                            />
                            <span class="form-tip">范围 5 - 40 个单词</span>
                        </el-form-item>
                        <el-form-item label="学习课程" prop="courseCode">
                            <el-select
                                v-model="planForm.courseCode"
                                placeholder="选择课程"
                                filterable
                                :disabled="formDisabled"
                            >
                                <el-option label="基础巩固班" value="basic" />
                                <el-option label="考研冲刺班" value="postgraduate" />
                                <el-option label="托福强化班" value="toefl" />
                                <el-option label="雅思口语班" value="ielts" />
                            </el-select>
                        </el-form-item>
                        <el-form-item label="开始日期" prop="startDate">
                            <el-date-picker
                                v-model="planForm.startDate"
                                type="date"
                                placeholder="选择日期"
                                :disabled-date="disabledDate"
                                :disabled="formDisabled"
                            />
                        </el-form-item>

                        <el-form-item label="每日短文提醒">
                            <el-switch
                                v-model="planForm.enableReminder"
                                :disabled="formDisabled"
                                active-text="开启"
                                inactive-text="关闭"
                            />
                        </el-form-item>
                        <el-form-item label="备注">
                            <el-input
                                v-model.trim="planForm.notes"
                                type="textarea"
                                :rows="3"
                                :disabled="formDisabled"
                                placeholder="可记录任选说明、学习目标等"
                            />
                        </el-form-item>

                        <el-form-item>
                            <el-button
                                type="primary"
                                :loading="submitting"
                                :disabled="formDisabled"
                                @click="handleSubmit"
                            >
                                {{ primaryButtonText }}
                            </el-button>
                            <el-button
                                @click="resetForm"
                                :disabled="formDisabled"
                            >
                                恢复默认
                            </el-button>
                        </el-form-item>
                    </el-form>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElForm, ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import {
    createUserLearningPlan,
    getCurrentUserPlan,
    listWordBooks,
} from '@/api/userWordBook'

type WordBook = {
    id: number
    title: string
    description?: string
    cover_url?: string
    language?: string
    level?: string
    tags: string[]
    total_words: number
    created_at?: string
    updated_at?: string
}

type CurrentPlan = {
    id: number
    word_book: WordBook
    daily_quota: number
    course_code?: string | null
    start_date: string
    total_days: number
}

const wordBooks = ref<WordBook[]>([])
const bookLoading = ref(false)
const activeBook = ref<WordBook | null>(null)
const currentPlan = ref<CurrentPlan | null>(null)
const planFormRef = ref<InstanceType<typeof ElForm> | null>(null)

const planForm = reactive({
    dailyQuota: 30,
    courseCode: 'basic',
    startDate: dayjs().add(1, 'day').toDate(),
    enableReminder: true,
    notes: '',
})

const planRules = {
    dailyQuota: [
        { required: true, message: '请输入每日词数', trigger: 'blur' },
        { type: 'number', min: 5, max: 40, message: '范围 5-40', trigger: 'blur' },
    ],
    courseCode: [
        { required: true, message: '请选择学习课程', trigger: 'change' },
    ],
    startDate: [
        { required: true, message: '请选择开始日期', trigger: 'change' },
    ],
}

const submitting = ref(false)
const formDisabled = computed(() => !activeBook.value)
const hasExistingPlan = computed(() => !!currentPlan.value)
const primaryButtonText = computed(() =>
    hasExistingPlan.value ? '重置计划' : '保存计划'
)

const fetchWordBooks = async () => {
    bookLoading.value = true
    try {
        const { data } = await listWordBooks()
        wordBooks.value = data?.items || []
    } catch (error: any) {
        const message = error?.msg || '获取单词书失败'
        ElMessage.error(message)
    } finally {
        bookLoading.value = false
    }
}

const applyPlanToForm = (plan: CurrentPlan) => {
    planForm.dailyQuota = plan.daily_quota
    planForm.courseCode = plan.course_code || 'basic'
    planForm.startDate = dayjs(plan.start_date).toDate()
}

const fetchCurrentPlan = async () => {
    try {
        const { data } = await getCurrentUserPlan()
        if (data) {
            currentPlan.value = data
            activeBook.value = data.word_book
            applyPlanToForm(data)
            planFormRef.value?.clearValidate()
        } else {
            currentPlan.value = null
        }
    } catch (error: any) {
        const message = error?.msg || '获取学习计划失败'
        ElMessage.error(message)
    }
}

const handleBookSelect = (row: WordBook) => {
    activeBook.value = row
}

const disabledDate = (date: Date) => date < dayjs().subtract(1, 'day').toDate()

const resetForm = () => {
    planForm.dailyQuota = 30
    planForm.courseCode = 'basic'
    planForm.startDate = dayjs().add(1, 'day').toDate()
    planForm.enableReminder = true
    planForm.notes = ''
    planFormRef.value?.clearValidate()
}

const estimatedDays = computed(() => {
    if (!activeBook.value || !planForm.dailyQuota) return 0
    return Math.ceil(activeBook.value.total_words / planForm.dailyQuota)
})

const submitPlan = async (reset: boolean) => {
    if (!activeBook.value) return
    submitting.value = true
    try {
        await createUserLearningPlan({
            word_book_id: activeBook.value.id,
            daily_quota: planForm.dailyQuota,
            course_code: planForm.courseCode,
            start_date: dayjs(planForm.startDate).format('YYYY-MM-DD'),
            enable_reminder: planForm.enableReminder,
            notes: planForm.notes,
            reset,
        })
        ElMessage.success(reset ? '学习计划已重置' : '学习计划已保存')
        await fetchCurrentPlan()
    } catch (error: any) {
        const message = error?.msg || '保存失败，请稍后重试'
        ElMessage.error(message)
    } finally {
        submitting.value = false
    }
}

const handleSubmit = () => {
    planFormRef.value?.validate(async (valid) => {
        if (!valid) return
        if (!activeBook.value) {
            ElMessage.warning('请先选择单词书')
            return
        }
        const isReset = hasExistingPlan.value
        if (isReset) {
            try {
                await ElMessageBox.confirm(
                    '重置后将删除当前学习计划及所有历史学习记录，确定继续吗？',
                    '确认重置',
                    {
                        type: 'warning',
                        confirmButtonText: '确定重置',
                        cancelButtonText: '取消',
                    }
                )
            } catch {
                return
            }
        }
        await submitPlan(isReset)
    })
}

const rowClassName = (row: { row: WordBook }) =>
    activeBook.value && row.row.id === activeBook.value.id ? 'active-row' : ''

const formatDate = (value: string | Date) => dayjs(value).format('YYYY-MM-DD')

onMounted(() => {
    fetchWordBooks()
    fetchCurrentPlan()
})
</script>

<style lang="scss" scoped>
.user-word-plan-page {
    padding: 12px;

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .book-title {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .selected-book-summary {
        display: flex;
        gap: 20px;

        .meta {
            flex: 1;

            h3 {
                margin: 0 0 6px;
                font-size: 20px;
            }

            p {
                margin: 0 0 8px;
                color: var(--el-text-color-secondary);
            }

            .meta-tags {
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
                margin-bottom: 8px;
            }

            .meta-stats {
                display: flex;
                gap: 16px;
                color: var(--el-text-color-secondary);
            }
        }
    }

    .plan-form {
        margin-top: 16px;

        .form-tip {
            margin-left: 12px;
            color: var(--el-text-color-secondary);
        }
    }

    .current-plan-alert {
        margin-bottom: 16px;

        .current-plan-description {
            margin-top: 6px;
            font-size: 13px;
            color: var(--el-text-color-secondary);
        }
    }

    :deep(.active-row) {
        td {
            background: var(--el-color-primary-light-9) !important;
        }
    }
}
</style>
