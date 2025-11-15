<template>
    <div class="word-book-upload-page">
        <el-page-header
            class="page-header"
            content="上传全新的单词书，供学生挑选学习。"
        >
            <template #title>
                <span class="header-title">单词书上传</span>
            </template>
        </el-page-header>

        <el-row :gutter="24">
            <el-col :lg="16" :md="18" :sm="24" :xs="24">
                <el-card shadow="hover">
                    <template #header>
                        <div class="card-header">
                            <span>单词书信息</span>
                            <el-tag type="warning" effect="plain">
                                仅 Admin 可见
                            </el-tag>
                        </div>
                    </template>
                    <el-form
                        ref="formRef"
                        :model="formModel"
                        :rules="formRules"
                        label-width="110px"
                        @submit.prevent
                    >
                        <el-form-item label="书名" prop="title">
                            <el-input
                                v-model.trim="formModel.title"
                                placeholder="例如：小学高频词 1000"
                                maxlength="120"
                                show-word-limit
                            />
                        </el-form-item>
                        <el-form-item label="简介">
                            <el-input
                                v-model.trim="formModel.description"
                                type="textarea"
                                :rows="3"
                                placeholder="简要介绍这本单词书的定位或特色"
                            />
                        </el-form-item>
                        <el-row :gutter="16">
                            <el-col :md="12" :sm="24">
                                <el-form-item label="语言">
                                    <el-select
                                        v-model="formModel.language"
                                        placeholder="默认 English"
                                    >
                                        <el-option label="English" value="en" />
                                        <el-option label="Spanish" value="es" />
                                        <el-option label="German" value="de" />
                                    </el-select>
                                </el-form-item>
                            </el-col>
                            <el-col :md="12" :sm="24">
                                <el-form-item label="水平">
                                    <el-select
                                        v-model="formModel.level"
                                        placeholder="选择词书定位"
                                    >
                                        <el-option label="小学" value="primary" />
                                        <el-option label="初中" value="junior" />
                                        <el-option label="高中" value="senior" />
                                        <el-option label="大学/CET" value="college" />
                                        <el-option label="托福/IELTS" value="toefl" />
                                    </el-select>
                                </el-form-item>
                            </el-col>
                        </el-row>
                        <el-form-item label="标签">
                            <el-select
                                v-model="formModel.tags"
                                multiple
                                filterable
                                allow-create
                                default-first-option
                                placeholder="按 Enter 回车可创建自定义标签"
                            >
                                <el-option label="高频词" value="high-frequency" />
                                <el-option label="考试" value="exam" />
                                <el-option label="生活" value="daily" />
                            </el-select>
                        </el-form-item>
                        <el-form-item label="封面图片">
                            <el-upload
                                class="cover-upload"
                                drag
                                :auto-upload="false"
                                :on-change="handleCoverChange"
                                :limit="1"
                                accept="image/*"
                            >
                                <vab-remix-icon icon="image-add-line" />
                                <div class="el-upload__text">
                                    拖拽或点击上传
                                    <em> JPG/PNG </em>
                                </div>
                                <template #tip>
                                    <div class="el-upload__tip">
                                        推荐尺寸 600×800，大小 &lt; 1MB
                                    </div>
                                </template>
                            </el-upload>
                        </el-form-item>
                        <el-form-item label="单词清单" required>
                            <div class="word-file-actions">
                                <span>请上传 Excel（.xlsx / .xls），包含示例模板中的列。</span>
                                <el-button
                                    type="primary"
                                    link
                                    size="small"
                                    @click="downloadTemplate"
                                >
                                    下载模板
                                </el-button>
                            </div>
                            <el-upload
                                class="word-file-upload"
                                drag
                                :auto-upload="false"
                                :on-change="handleWordFileChange"
                                :limit="1"
                                accept=".xlsx,.xls"
                            >
                                <vab-remix-icon icon="file-upload-line" />
                                <div class="el-upload__text">
                                    上传 Excel 文件，包含“word、meaning_zh、meaning_en、example”列
                                </div>
                                <template #tip>
                                    <div class="el-upload__tip">
                                        若文件较大，请分批上传；首行需保留模板中的列标题。
                                    </div>
                                </template>
                            </el-upload>
                        </el-form-item>
                        <el-form-item>
                            <el-button
                                type="primary"
                                :loading="submitting"
                                @click="handleSubmit"
                            >
                                发布
                            </el-button>
                            <el-button @click="resetForm">重置</el-button>
                        </el-form-item>
                    </el-form>
                </el-card>
            </el-col>
            <el-col :lg="8" :md="6" :sm="24" :xs="24">
                <el-card shadow="never" class="tips-card">
                    <template #header>
                        <div class="card-header">
                            <span>上传说明</span>
                        </div>
                    </template>
                    <ul class="tips-list">
                        <li>· 单词书仅管理员可上传，提交后即对学生可见。</li>
                        <li>· 封面用于首页展示，建议使用高分辨率图片。</li>
                        <li>· 单词清单请使用模板列名，Excel 内最多 10,000 行。</li>
                        <li>· 若需编辑/下架，可进入后台管理页面操作。</li>
                    </ul>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { ElMessage, type FormInstance } from 'element-plus'
import type { UploadFile } from 'element-plus'
import { createWordBook } from '@/api/wordBook'
import { useUserStore } from '@/store/modules/user'

type FormModel = {
    title: string
    description: string
    language: string
    level: string
    tags: string[]
}

const defaultForm: FormModel = {
    title: '',
    description: '',
    language: 'en',
    level: '',
    tags: [],
}

const formModel = reactive<FormModel>({ ...defaultForm })
const formRef = ref<FormInstance>()
const submitting = ref(false)
const coverFile = ref<File | null>(null)
const wordListFile = ref<File | null>(null)
const userStore = useUserStore()
const isAdminUser = computed(
    () => userStore.getUsername?.toLowerCase?.() === 'admin'
)

const formRules = {
    title: [
        { required: true, message: '请输入单词书名称', trigger: 'blur' },
        { min: 2, max: 120, message: '长度为 2-120 个字符', trigger: 'blur' },
    ],
}

const handleCoverChange = (uploadFile: UploadFile) => {
    if (uploadFile.raw) {
        coverFile.value = uploadFile.raw
    }
}

const handleWordFileChange = (uploadFile: UploadFile) => {
    if (uploadFile.raw) {
        wordListFile.value = uploadFile.raw
    }
}

const resetForm = () => {
    Object.assign(formModel, defaultForm)
    coverFile.value = null
    wordListFile.value = null
    formRef.value?.resetFields()
}

const handleSubmit = () => {
    if (!isAdminUser.value) {
        ElMessage.error('仅管理员可上传单词书，请联系管理员')
        return
    }
    formRef.value?.validate(async (valid) => {
        if (!valid) return
        if (!wordListFile.value) {
            ElMessage.warning('请上传单词清单文件')
            return
        }

        const formData = new FormData()
        formData.append('title', formModel.title)
        formData.append('description', formModel.description || '')
        formData.append('language', formModel.language || 'en')
        formData.append('level', formModel.level || '')
        formData.append('tags', JSON.stringify(formModel.tags))
        if (coverFile.value) {
            formData.append('cover', coverFile.value)
        }
        formData.append('word_file', wordListFile.value)

        submitting.value = true
        try {
            await createWordBook(formData)
            ElMessage.success('单词书已提交，等待后台处理')
            resetForm()
        } catch (error: any) {
            const message =
                error?.msg || error?.message || '上传失败，请稍后重试'
            ElMessage.error(message)
        } finally {
            submitting.value = false
        }
    })
}

const downloadTemplate = () => {
    window.open('/templates/word-book-template.xlsx', '_blank')
}
</script>

<style lang="scss" scoped>
.word-book-upload-page {
    padding: 12px;

    .page-header {
        margin-bottom: 18px;

        .header-title {
            font-size: 20px;
            font-weight: 600;
        }
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .tips-card {
        height: 100%;
    }

    .tips-list {
        margin: 0;
        padding-left: 16px;
        line-height: 1.8;
        color: var(--el-text-color-secondary);
    }

    .cover-upload,
    .word-file-upload {
        width: 100%;
    }

    .word-file-actions {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
        color: var(--el-text-color-secondary);

        .el-button {
            padding: 0;
        }
    }
}
</style>
