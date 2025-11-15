# 智能体多轮对话 API 使用说明文档（完整版）

## 1. 概述
本文档详细说明如何通过 **扣子智能体 API（/v3/chat）** 实现**多轮对话（multi-turn conversation）**。

智能体对话接口不同于“对话流 Workflow Chat”，它是真正的自由对话聊天接口，支持：
- 多轮上下文保持
- assistant/user 消息结构化传递
- function_call / tool_response
- 流式与非流式输出
- 图像、文件、文本混合消息
- conversation_id 管理（决定是否连续对话）

---

## 2. API 基础信息

### 2.1 请求 URL
```
POST https://api.coze.cn/v3/chat
```

### 2.2 鉴权方式  
Header 必须包含：

```
Authorization: Bearer <your service identity token>
Content-Type: application/json
```

### 2.3 Content-Type  
```
application/json
```

示例：
```
Authorization: Bearer sat_xxx...
```

---

## 3. 多轮对话的核心机制（非常重要）

智能体多轮对话依赖两个关键机制：

---

### ✔ 3.1 conversation_id（多轮上下文的关键）

- **不传 conversation_id → 新建会话**
- **传 conversation_id → 继续同一个对话上下文**
- 服务端会返回一个 conversation_id，必须保存用于下一轮调用

示例返回：
```json
{
  "conversation_id": "74392384920293",
  "messages": [{...}]
}
```

---

### ✔ 3.2 messages 数组（必须携带完整历史）

每一轮 API 调用必须传入完整历史对话：

```json
"messages": [
  {"role": "user", "content": "你好"},
  {"role": "assistant", "content": "你好，我是 Syntexia AI"},
  {"role": "user", "content": "帮我写一段英语短文"}
]
```

原则：

1. 按时间顺序排列  
2. **最后一条必须是 user**  
3. assistant 的历史回复必须写回 messages，否则 AI 会失忆  

---

## 4. 完整请求体结构（/v3/chat）

```json
{
  "conversation_id": "optional",
  "bot_id": "<智能体ID>",
  "messages": [
    {"role": "user", "content": "你好，你是谁？"}
  ],
  "stream": false
}
```

字段说明：

字段 | 类型 | 必填 | 说明
---|---|---|---
bot_id | string | 是 | 智能体 ID
messages | array | 是 | 多轮对话历史
conversation_id | string | 否 | 是否继续对话
stream | boolean | 否 | 流式输出

---

## 5. 第一轮对话（无 conversation_id）

Python 示例：

```python
import requests
import json

API = "https://api.coze.cn/v3/chat"
TOKEN = "sat_xxx"
BOT_ID = "你的智能体ID"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "bot_id": BOT_ID,
    "messages": [
        {"role": "user", "content": "你好，你是谁？"}
    ],
    "stream": False
}

resp = requests.post(API, headers=headers, json=payload)
data = resp.json()

print("assistant 回复:", data["messages"][0]["content"])
print("conversation_id =", data["conversation_id"])
```

---

## 6. 第二轮及后续对话（必须传 conversation_id + 全量 messages）

```python
conv_id = data["conversation_id"]

payload2 = {
    "bot_id": BOT_ID,
    "conversation_id": conv_id,
    "messages": [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好，我是Syntexia AI"},
        {"role": "user", "content": "帮我写一个英语短文"}
    ],
    "stream": False
}

resp2 = requests.post(API, headers=headers, json=payload2)
data2 = resp2.json()

print("assistant 回复:", data2["messages"][0]["content"])
```

---

## 7. 流式输出（stream=true）

```python
payload["stream"] = True

with requests.post(API, headers=headers, json=payload, stream=True) as r:
    for line in r.iter_lines():
        if line:
            obj = json.loads(line.decode("utf-8"))
            if obj.get("event") == "message.delta":
                print(obj["data"]["content"], end="", flush=True)
```

常见事件：
- `message.delta`（增量字节）
- `message.completed`
- `done`
- `chat.completed`

---

## 8. 支持图片、文件输入（多模态）

### 8.1 file_id 图片
```json
{
  "role": "user",
  "content": [
    {"type": "image", "file_id": "1122334455"}
  ]
}
```

### 8.2 URL 图片
```json
{
  "role": "user",
  "content": [
    {"type": "image_url", "url": "https://example.com/xx.png"}
  ]
}
```

---

## 9. 智能体 function_call（自动调用插件/工作流）

assistant 可能返回：

```json
{
  "role": "assistant",
  "type": "function_call",
  "function_call": {
    "name": "search_news",
    "arguments": {"keyword": "AI"}
  }
}
```

你需要调用插件接口，然后返回：

```json
{
  "role": "tool",
  "type": "tool_response",
  "tool_response": {
    "name": "search_news",
    "content": "插件的返回内容"
  }
}
```

智能体会继续对话，保持自动化流程。

---

## 10. 多轮对话完整封装类（可直接用于项目）

```python
class CozeAgent:
    def __init__(self, token, bot_id):
        self.api = "https://api.coze.cn/v3/chat"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.bot_id = bot_id
        self.conversation_id = None
        self.messages = []

    def ask(self, text):
        # 添加用户消息
        self.messages.append({"role": "user", "content": text})

        payload = {
            "bot_id": self.bot_id,
            "messages": self.messages,
            "stream": False
        }

        if self.conversation_id:
            payload["conversation_id"] = self.conversation_id

        r = requests.post(self.api, json=payload, headers=self.headers)
        data = r.json()

        # 保存 conversation_id
        self.conversation_id = data["conversation_id"]

        # 取 AI 回复
        reply = data["messages"][0]["content"]

        # 写入 messages 历史
        self.messages.append({"role": "assistant", "content": reply})

        return reply
```

---

## 11. 最佳实践

### ✔ 必须保存 conversation_id  
否则无法继续对话。

### ✔ 每次都必须带全量 messages  
否则 AI 上下文会断裂。

### ✔ assistant 回复必须写回 messages  
否则 AI 无法记住自己说过的话。

### ✔ 不要在前端暴露 Token  
必须后端中转调用 API。

### ✔ 保存对话到数据库（推荐）  
`conversation_id + messages` 可以直接落盘，用于恢复会话。

---

## 12. 常见问题

问题 | 原因 | 解决
---|---|---
AI 忘记上文 | messages 未传全量 | 必须带所有历史消息
对话断开 | conversation_id 丢失 | 保存并传入 conversation_id
多轮对话提示错误 4100 | 消息格式错误 | 检查 messages 数组结构
多模态输入无效 | content 数组格式错误 | type 必须是 image 或 image_url

---

如需我帮你：
- 生成多轮对话 + 文件解析版本  
- 生成 WebSocket 多轮对话  
- 或基于你的智能体写一个 SDK  

我可以继续为你扩展。  
