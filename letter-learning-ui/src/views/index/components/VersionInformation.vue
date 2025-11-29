<script lang="ts" setup>
    import { getCurrentUserPlan } from '@/api/userWordBook'

    const bookInfo = reactive({
        title: '尚未选择单词书',
        description: '请选择或上传一个单词书，开始学习旅程。',
        coverUrl: '',
        tags: [] as string[],
        totalWords: 0,
        status: '',
        language: '',
        level: '',
    })

    const loadPlan = async () => {
        try {
            const resp = await getCurrentUserPlan()
            const payload = resp.data
            if (payload && payload.word_book) {
                const book = payload.word_book
                bookInfo.title = book.title || '未命名单词书'
                bookInfo.description = book.description || '暂无简介'
                bookInfo.coverUrl = book.cover_url || ''
                bookInfo.tags = book.tags || []
                bookInfo.totalWords = book.total_words || 0
                bookInfo.language = book.language || ''
                bookInfo.level = book.level || ''
                bookInfo.status =
                    payload.status === 'active' ? '进行中' : payload.status || ''
            }
        } catch (error) {
            // 保持默认占位
            console.error('加载单词书失败', error)
        }
    }

    onMounted(() => {
        loadPlan()
    })
</script>

<template>
    <vab-card class="version-information" shadow="never">
        <template #header>
            <vab-icon icon="information-line" />
            当前单词书
        </template>
        <div class="book-card">
            <div class="cover">
                <img
                    v-if="bookInfo.coverUrl"
                    :src="bookInfo.coverUrl"
                    alt="cover"
                />
                <div v-else class="placeholder">封面</div>
            </div>
            <div class="book-info">
                <div class="book-title">{{ bookInfo.title }}</div>
                <div class="book-desc">{{ bookInfo.description }}</div>
                <div class="book-meta">
                    <el-tag v-if="bookInfo.status" size="small" type="success">
                        {{ bookInfo.status }}
                    </el-tag>
                    <el-tag v-if="bookInfo.language" size="small" effect="plain">
                        {{ bookInfo.language }}
                    </el-tag>
                    <el-tag v-if="bookInfo.level" size="small" effect="plain">
                        {{ bookInfo.level }}
                    </el-tag>
                </div>
                <div class="book-extra">
                    <span>总词数：{{ bookInfo.totalWords }}</span>
                    <div class="tags">
                        <el-tag
                            v-for="tag in bookInfo.tags"
                            :key="tag"
                            size="small"
                            effect="plain"
                        >
                            {{ tag }}
                        </el-tag>
                    </div>
                </div>
            </div>
        </div>
    </vab-card>
</template>

<style lang="scss" scoped>
    .version-information {
        .book-card {
            display: flex;
            gap: 16px;
            align-items: flex-start;
        }
        .cover {
            width: 120px;
            height: 160px;
            border-radius: 8px;
            overflow: hidden;
            background: #f5f7fa;
            display: grid;
            place-items: center;
            color: #999;
            font-weight: 600;
            img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
        }
        .book-info {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .book-title {
            font-size: 18px;
            font-weight: 700;
        }
        .book-desc {
            color: #666;
            line-height: 1.5;
        }
        .book-meta {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .book-extra {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            align-items: center;
            color: #444;
            .tags {
                display: flex;
                gap: 6px;
                flex-wrap: wrap;
            }
        }
    }
</style>
