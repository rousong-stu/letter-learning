# AI 词汇短文页面「点击词汇展示卡片」功能方案

## 背景与目标
- 当前 `AI 词汇短文` 页面展示的短文为纯文本，用户需要在侧栏手动切换词卡才能查看释义。
- 期望每个短文中的单词都可点击，点击后侧栏自动切换到对应的词卡，帮助用户在阅读过程中即时查看词汇信息。
- 目标是保持现有“重新生成”逻辑不变，仅提升短文与词卡之间的交互效率。

## 功能摘要
1. 将短文渲染从纯文本改为 token 化的结构，允许逐词绑定点击事件。
2. 点击任意单词时，根据单词内容定位到 `displayWords` 中对应的词条。
3. 自动更新右侧词卡展示（复用现有 `activeWord` / `activeWordIndex` 状态），并提供视觉反馈。
4. 对字典缺失的单词给予兜底展示，如显示“暂无词典信息”。

## 前端设计
### 组件涉及
- `src/views/wordStory/index.vue`

### 状态与计算
1. **词典映射**：已有 `wordDictionary`（基于 `displayWords`），继续沿用。
2. **token 化段落**：
   - 新增 `formattedStoryParagraphs` 计算属性，输出结构类似：
     ```ts
     type StoryToken = { text: string; isWord: boolean }
     type StoryParagraph = StoryToken[]
     ```
   - 正则可使用 `paragraph.split(/(\W+)/)`，保留标点与空格 token。
3. **当前词状态**：仍然使用 `activeWordIndex` 与 `activeWord`，在点击时调用 `focusWord(word: string)`，内部负责比对并更新索引；若未命中则设置 `pendingWordInfo` 作为临时展示。

### 模板渲染
- 将短文部分改为：
  ```vue
  <p v-for="(paragraph, pIndex) in formattedStoryParagraphs" :key="pIndex">
      <template v-for="(token, tIndex) in paragraph" :key="tIndex">
          <span
              v-if="token.isWord"
              class="story-word"
              @click="handleWordClick(token.text)"
          >
              {{ token.text }}
          </span>
          <span v-else>{{ token.text }}</span>
      </template>
  </p>
  ```
- 样式补充：
  ```scss
  .story-word {
      cursor: pointer;
      color: var(--el-color-primary);
      user-select: text;
      &:hover {
          text-decoration: underline;
      }
      &.is-active {
          font-weight: 600;
      }
  }
  ```

### 交互逻辑
1. `handleWordClick(word: string)`：
   - 规范化单词（`word.toLowerCase()`，去掉首尾标点）。
   - 在 `displayWords` / `wordDictionary` 中查找，命中后更新 `activeWordIndex`。
   - 未命中时，更新一个 `fallbackWordInfo` 并在词卡区提示“暂无词典信息”。
2. 侧栏词卡保持现有结构，只需在模板里展示 `activeWord` 或 `fallbackWordInfo`。
3. 可选增强：点击后将词卡区域滚动/闪烁，提示已切换。

## 开发步骤建议
1. **准备阶段**
   - 备份/记录 `storyParagraphs` 计算逻辑，确保新计算属性不影响其他使用方。
2. **实现 token 渲染**
   - 编写 `formatParagraph(paragraph: string): StoryParagraph` 方法。
   - 新增 `formattedStoryParagraphs` 计算属性并更新模板。
3. **点击选择逻辑**
   - 新增 `handleWordClick` / `focusWord` 方法，复用或更新 `activeWordIndex`。
   - 处理找不到词条的情况（提示 + fallback 展示）。
4. **样式优化**
   - 增加 `.story-word` 样式与激活状态 class。
5. **测试**
   - 确认含标点、大小写、重复词等情况都可点击。
   - 验证重新生成/切换日期时 token 与词卡联动正常。

## 可选扩展
- 点击单词时同步添加“查询记录”，便于统计用户关注词汇。
- 支持双击在对话区自动插入提问，例如“请解释单词 abandon 在文中的含义”。
- 与后端数据打通后，可根据点击频率自动推荐练习题。

## 潜在风险与注意事项
- AI 短文可能包含非常规字符，正则需要确保不会丢失内容。
- 大量 DOM 节点可能影响性能，建议只在展示区域渲染，可按需增加虚拟滚动或懒加载（目前文本量较小影响可忽略）。
- 若未来短文支持富文本/高亮，需再次评估 token 化方案（可以改为在生成阶段就返回分词结果）。

---
后续若决定实现，可以此文档为任务拆分依据，先完成 token 化与点击逻辑，再迭代扩展功能。***
