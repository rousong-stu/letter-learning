# Coze Chat v3 集成开发文档（给协作AI看的）

> 目的：把 **Coze 对话 API v3** 的关键信息、参数约束、典型代码、调试与排错流程系统化，便于让“AI 开发助手”直接依此参与编码与联调。
>
> ⚠️ 安全提醒：**不要**在任何对外文档或代码仓库中粘贴真实密钥/令牌。本文示例使用占位符（如 `pat_***` / `sat_***`）。真实凭证请放在环境变量或安全配置中心。

---

## 0. 名词与对象速览

* **会话（Conversation）**：用户与 Bot 的一个持续上下文容器，可包含多条消息。
* **对话（Chat）**：在会话中的一次调用（一次问答生成流程），**一个会话同一时刻只能有一个进行中的对话**（否则 4016）。
* **消息（Message）**：单条交互信息，`role ∈ {user, assistant}`，`content_type ∈ {text, object_string, card, audio}` 等。

相关对象：

* **Chat Object**：包含 `id`（Chat ID）、`conversation_id`、`status`（`created/in_progress/completed/failed/requires_action/canceled`）、`usage` 等。
* **Message Object**：包含 `id`、`role`、`type`（`question/answer/function_call/tool_response/follow_up/verbose`）等。

---

## 1. 基础信息（Base Info）

* **Base URL**：`https://api.coze.cn`
* **发起对话（Chat v3）**：`POST /v3/chat`
* **可选 Query**：`conversation_id=...`（对话发生在哪个会话里）
* **鉴权（HTTP Header）**：

  * `Authorization: Bearer <ACCESS_TOKEN>`（个人访问令牌 PAT 或服务访问令牌 SAT，需具备 `chat` 权限）
  * `Content-Type: application/json`

> 令牌开通权限参考：鉴权方式概述（PAT / Service Token / OAuth 等）。

---

## 2. 发起对话（/v3/chat）请求体结构

```jsonc
{
  "bot_id": "7348************",             // 必填：目标智能体ID
  "user_id": "user-123",                    // 必填：业务侧自定义用户ID（用于上下文与记忆隔离）
  "stream": false,                           // 可选：是否返回流式SSE
  "auto_save_history": true,                 // 可选：是否保存本次对话记录（非流式必须为 true）
  "conversation_id": "可放在query中",        // Query 中传
  "additional_messages": [                   // 可选：最多100条
    {
      "role": "user",                      // user/assistant
      "content": "你好，今天天气如何？",     // 文本或序列化的 object_string
      "content_type": "text"               // text / object_string
      // type 可选；当 auto_save_history=true 时仅支持 question/answer
    }
  ],
  "custom_variables": {                      // 可选：仅用于 Prompt 中声明的变量（Jinja2可用）
    "bot_name": "小助教"
  },
  "meta_data": {                             // 可选：任意业务侧透传，查看对话详情时会回传
    "trace_id": "abc-123"
  },
  "extra_params": {                          // 可选：特殊场景参数（例如经纬度）
    "latitude": "39.98",
    "longitude": "116.30"
  },
  "shortcut_command": {                      // 可选：触发已绑定的快捷指令
    "command_id": "cmd_***",
    "parameters": "[序列化的object_string数组字符串]"
  },
  "parameters": {                            // 可选：对话流模式下，传入对话流自定义参数
    "user": [ { "user_id": "123", "user_name": "Alice" } ]
  },
  "enable_card": false,                      // 可选：问答节点是否以卡片返回
  "publish_status": "published_online",     // 可选：published_online / unpublished_draft
  "bot_version": "v1.2.3"                  // 可选：与历史版本对话（draft下不可填）
}
```

### 2.1 `additional_messages` 用法

* 不传：模型只看会话中已有消息，**最后一条**视为这次的用户输入，其余作为上下文。
* 传入：模型会合并会话历史与此数组；**数组最后一条**视为这次的用户输入，其他作为上下文。
* **顺序规则**：按时间递增排序，**最后一条应为 `role=user`**。
* **多模态**：使用 `content_type: object_string`；内容是 **序列化后的数组字符串**，数组元素取值：

  * `{ type: "text", text: "..." }`
  * `{ type: "image" | "file" | "audio", file_id: "..." }` 或 `{ ..., file_url: "https://..." }`
  * 纯图片/纯文件消息的前后，必须至少有一条 `content_type=text` 的文本消息作为语境。

**object_string 示例（未序列化 → 序列化字符串）**：

```json
[
  { "type": "text", "text": "帮我理解这张图" },
  { "type": "image", "file_url": "https://example.com/pic.png" },
  { "type": "file",  "file_id": "144423***" }
]
```

序列化后传入 `content`：

```json
"[{\"type\":\"text\",\"text\":\"帮我理解这张图\"},{\"type\":\"image\",\"file_url\":\"https://example.com/pic.png\"},{\"type\":\"file\",\"file_id\":\"144423***\"}]"
```

---

## 3. 响应模式：流式 vs 非流式

### 3.1 流式（`stream=true`）

* 通过 **SSE 事件**持续返回：

  * `conversation.chat.created`
  * `conversation.chat.in_progress`
  * `conversation.message.delta`（增量文本）
  * `conversation.audio.delta`（增量音频，输入含音频时才有）
  * `conversation.message.completed`（单条消息拼接完成）
  * `conversation.chat.completed` / `conversation.chat.failed`
  * `conversation.chat.requires_action`（需要提交工具执行结果）
  * `error` / `done`
* 终止标记：`event: done` + `data: [DONE]`。
* **多 answer** 场景：会有 `type=verbose` 包（`content.msg_type=generate_answer_finish`）标识全部 answer 完毕。

### 3.2 非流式（`stream=false`）

* 立即返回 `data`（Chat Object 元数据），**不含最终答案**。
* 客户端需：

  1. 轮询 `GET /v3/chat/{id}`（查看对话详情）直至 `status` 进入终态（`completed/failed/requires_action/canceled`）。
  2. 再 `GET /v3/messages?conversation_id=...&chat_id=...`（查看消息详情）取得模型最终回复。
* **要求**：非流式下 `auto_save_history` 必须为 `true`。

---

## 4. 典型代码片段

> 用占位符：`COZE_TOKEN`、`BOT_ID`、`CONVERSATION_ID`、`USER_ID`。

### 4.1 cURL（非流式）

```bash
curl -X POST "https://api.coze.cn/v3/chat?conversation_id=$CONVERSATION_ID" \
  -H "Authorization: Bearer $COZE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_id": "'"$BOT_ID"'",
    "user_id": "'"$USER_ID"'",
    "stream": false,
    "auto_save_history": true,
    "additional_messages": [
      {"role":"user","content":"今天杭州天气如何","content_type":"text"}
    ]
  }'
```

### 4.2 Node.js（fetch，流式SSE）

```js
import fetch from "node-fetch";

async function chatStream() {
  const url = `https://api.coze.cn/v3/chat?conversation_id=${process.env.CONV_ID}`;
  const res = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${process.env.COZE_TOKEN}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      bot_id: process.env.BOT_ID,
      user_id: process.env.USER_ID,
      stream: true,
      auto_save_history: true,
      additional_messages: [
        { role: "user", content: "给我三条学习计划建议", content_type: "text" }
      ]
    })
  });

  if (!res.ok) throw new Error(`HTTP ${res.status}`);

  for await (const chunk of res.body) {
    const line = chunk.toString();
    // 解析 SSE: 形如 "event: xxx" / "data: {..}"
    process.stdout.write(line);
  }
}

chatStream().catch(console.error);
```

### 4.3 Python（requests，非流式 + 轮询）

```python
import os, time, requests

BASE = "https://api.coze.cn"
TOKEN = os.environ["COZE_TOKEN"]
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

# 1) 发起非流式对话
r = requests.post(
    f"{BASE}/v3/chat",
    params={"conversation_id": os.environ.get("CONV_ID", "")},
    json={
        "bot_id": os.environ["BOT_ID"],
        "user_id": os.environ.get("USER_ID", "u1"),
        "stream": False,
        "auto_save_history": True,
        "additional_messages": [
            {"role": "user", "content": "列三个OKR范例", "content_type": "text"}
        ],
    },
    headers=HEADERS,
    timeout=60,
)
res = r.json()["data"]
chat_id = res["id"]
conv_id = res["conversation_id"]

# 2) 轮询对话状态
while True:
    detail = requests.get(f"{BASE}/v3/chat/{chat_id}", headers=HEADERS, timeout=30).json()
    status = detail["data"]["status"]
    if status in {"completed", "failed", "requires_action", "canceled"}:
        break
    time.sleep(1.2)

# 3) 拉取消息详情（示意，具体以消息接口为准）
msgs = requests.get(
    f"{BASE}/v3/messages",
    params={"conversation_id": conv_id, "chat_id": chat_id},
    headers=HEADERS,
    timeout=60,
).json()
print(msgs)
```

### 4.4 Go（标准库，非流式）

```go
client := &http.Client{Timeout: 60 * time.Second}
reqBody := strings.NewReader(`{
  "bot_id": "` + os.Getenv("BOT_ID") + `",
  "user_id": "u1",
  "stream": false,
  "auto_save_history": true,
  "additional_messages":[{"role":"user","content":"来三句名言","content_type":"text"}]
}`)
req, _ := http.NewRequest("POST", "https://api.coze.cn/v3/chat", reqBody)
req.Header.Set("Authorization", "Bearer "+os.Getenv("COZE_TOKEN"))
req.Header.Set("Content-Type", "application/json")
resp, err := client.Do(req)
// 处理 resp 并轮询 chat/detail …
```

> 更多：可结合官方 **Python/Node/Java/Go SDK**（文末“相关链接”）进行更优封装（如重试、SSE解析、类型定义）。

---

## 5. 关联 API（强烈建议接入）

1. **创建会话**：`POST /v1/conversation/create`  —— 预置历史上下文消息（按时间递增）后，再用 `/v3/chat` 继续对话。
2. **查看对话详情**：`GET /v3/chat/{chat_id}` —— 轮询状态用。
3. **查看对话消息详情**：`GET /v3/messages?conversation_id=...&chat_id=...` —— 拉取最终答案/中间过程。
4. **取消进行中的对话**：`POST /v3/chat/cancel` —— 终止长耗时任务。
5. **提交工具执行结果**：`POST /v3/chat/submit_tool_outputs` —— 处理 `requires_action` 场景（工具函数/工作流问答节点需要外部结果）。
6. **消息评价**：`POST /v3/message/feedback` / 删除评价 —— 训练内闭环与质检。

> 建议同时了解 **消息 type 说明**、**错误码表** 以快速定位问题。

---

## 6. 变量与 Prompt 定制

* 在智能体 Prompt 中声明变量（如 `{{bot_name}}`），可通过 `custom_variables` 传值；支持 **Jinja2 语法**：

  ```jinja2
  {% if key -%}
  prompt1
  {%- else %}
  prompt2
  {% endif %}
  ```
* **限制**：仅作用于智能体 Prompt 声明的变量；不等同于“智能体变量/工作流参数”。
* 对话流参数：通过 `parameters` 注入，仅对“单 Agent（对话流模式）”已发布 API/ChatSDK 生效。

---

## 7. 多模态（object_string）规则清单

* 一个数组中**最多包含一条 `type=text`**，可包含多张图片/多个文件/音频。
* 若包含 `type=text`，**必须**至少再包含一条 `image` 或 `file`（不能只发text）。
* 可发送纯图片或纯文件，但**相邻前后**必须存在一条纯文本消息用于语境说明（否则 4000 参数错误）。
* 媒体来源可用 `file_id`（需先通过“上传文件”接口获取）或 `file_url`（公网可访问）。

---

## 8. 发布版本与版本选择

* `publish_status`：`published_online`（默认）/`unpublished_draft`（草稿）。
* `bot_version`：用于与历史版本对话（**draft 场景不可填**）。
* 实践建议：

  * 线上只指向发布版；灰度/测试环境可显式指定某版本。
  * 在 `meta_data` 中携带 `env/build/git_sha` 便于追踪。

---

## 9. 错误码与常见坑（重点）

* **4016**：同一会话已有进行中对话。—— 客户端应在发起前检查/或在失败后退避重试；必要时改用新会话。
* **4000**：参数错误（常见：`additional_messages` 序列化格式、object_string 规则不合规、最后一条非 user、纯多媒体缺文本语境）。
* **4100/4101**：鉴权问题或权限不足（令牌无 `chat` 权限/过期/空间未授权）。
* **5000**：`auto_save_history=false` 时调用插件并尝试 `submit_tool_outputs` 会报该错误。
* 其它：请结合“错误码文档”快速检索。

**调试心法**：

* 开发期建议先走**非流式** + `auto_save_history=true`，便于留痕排障，再切到流式体验。
* 记录三元组：`conversation_id` / `chat_id` / `trace_id`（自定义），遇错能完整还原现场。
* 对象边界：`Message.type` 与 `auto_save_history` 的组合限制不同，注意文档表格里的搭配关系。

---

## 10. 测试计划（可交给AI自动生成用例）

* **单元**：

  * 参数校验（缺字段 / 类型不匹配 / object_string 结构非法）。
  * 多模态组合合法性（含/不含 text、纯图/纯文件边界）。
  * 非流式轮询终态判断、消息抓取正确性。
* **集成**：

  * 同会话并发触发 → 触发 4016 → 退避重试。
  * `requires_action` → 伪造工具执行结果 → `submit_tool_outputs` 继续对话。
  * 版本选择：`published_online` vs 指定 `bot_version`。
* **回归**：

  * 令牌滚动（过期/吊销） → 4100/4101 快速定位。
  * `auto_save_history=false` 下的能力边界验证。
* **压测**：

  * QPS 分层脚本（流式 vs 非流式）；
  * 上下文长度极端值（`additional_messages` 接近 100 条、长文本）。

---

## 11. 安全与合规建议

* 令牌管理：环境变量/密钥管控平台；按空间与最小权限授予 `chat`。
* 日志脱敏：拦截器对 `Authorization`、用户隐私字段脱敏。
* 限流与重试：对 429/5xx 设置指数退避；流式连接设置超时与心跳。
* 文件与URL白名单：仅允许可信外链作为 `file_url` 输入。

---

## 12. 与工作流/语音的扩展（选学）

* **对话流（Workflow Chat）**：如需编排节点、问答节点、多Answer与工具调用，配合 `workflow_chat`、`get_node_execute_history_response` 等文档。
* **音视频**：ASR/TTS/WebSocket Streaming Chat 可实现双向语音对话；配合 `list_voices`、`text_to_speech`、`audio_transcriptions`、`streaming_chat_api` 等。
* **知识库**：`upload_files` / `create_dataset` / `create_knowledge_files` 等为 RAG 方案提供数据入口。

---

## 13. 前端嵌入（Chat SDK / Web SDK）

* Chat SDK（Web/Node 等）可快速落地嵌入式聊天窗组件，自动处理会话/流式渲染。
* Web SDK（UI Builder）可定制 UI；如需卡片渲染，请在 `enable_card=true` 的同时实现前端卡片组件。

---

## 14. 目录索引（便于AI让你打开的页面）

> 若某页未开，我方AI无法读取细节，请按需打开：

* 会话与消息：

  * 创建会话 `create_conversation`
  * 发起对话 `chat_v3`（**当前页**）
  * 查看对话详情 `retrieve_chat`
  * 查看对话消息详情 `list_chat_messages`
  * 取消进行中的对话 `chat_cancel`
  * 提交工具执行结果 `chat_submit_tool_outputs`
  * 消息 type 说明 `message_type`
* 鉴权：

  * 鉴权方式概述 `authentication`
  * PAT / Service Token / OAuth（`pat` / `service_token` / `oauth_*` 全套）
* 错误码：`coze_error_codes`
* 变量/Prompt：`read_variable` / `update_variable` / Prompt 变量（本页）
* 文件与知识库：`upload_files` / `create_dataset` / `create_knowledge_files`
* SDK：Web/Chat SDK 概述与安装、Python/Node/Java/Go SDK 快速开始
* 语音与Realtime：`streaming_chat_api`、`asr_api`、`tts_api`

---

## 15. 落地集成 Checklist（交付准则）

* [ ] `.env`：`COZE_TOKEN`、`BOT_ID`、`CONV_ID`、`USER_ID` 分环境配置
* [ ] 非流式路径打通：发起→轮询→拉消息→渲染
* [ ] 流式路径打通：SSE 解析、断线重连、心跳与超时
* [ ] 多模态最小可用：文本+图片 / 仅图片（相邻文本）
* [ ] `requires_action` 正/反例测试与工具结果上报
* [ ] 错误码表接入：统一异常映射（含 4016/4000/4100/4101）
* [ ] 日志与可观测：request/response 摘要、trace_id、usage 采集
* [ ] 版本与环境：`publish_status`/`bot_version`、`meta_data.env/build`

---

## 16. FAQ（快速决策）

* **我只有一问一答要不要建会话？** 不强制；不传 `conversation_id` 也可用，系统会自动创建会话。
* **最后一条必须 `role=user` 吗？** 是；否则影响模型效果且可能触发 4000。
* **为什么我发了纯图片报错？** 纯图片前后需有一条文本消息提供语境。
* **如何避免 4016？** 对每个 `conversation_id` 维护一个“进行中锁”；或失败后退避重试/更换会话。
* **非流式拿不到答案？** 先 `retrieve_chat` 等到终态，再 `list_chat_messages` 拉完整消息。

---

## 17. 相关链接（供AI索引）

> 以下是 Coze 文档站内的板块关键词（让你的人类同事“打开对应页面”即可）：

* `发起对话（/v3/chat）`
* `创建会话（/v1/conversation/create）`
* `查看对话详情（retrieve_chat）`
* `查看对话消息详情（list_chat_messages）`
* `取消进行中的对话（chat_cancel）`
* `提交工具执行结果（chat_submit_tool_outputs）`
* `消息 type 说明（message_type）`
* `错误码（coze_error_codes）`
* `Prompt 变量`
* `上传文件 / 知识库 / Web SDK / Chat SDK / 各语言 SDK`

---

### 尾注

* 以上内容基于当前文档页的可见信息整理，若你需要我补充某一小节的**参数表、响应示例或代码**，请直接点名对应页面，我会立刻扩充到本文档中。
