# 📘 对话流工作流 API 调用开发文档（Syntexia）

**版本：v1.1（新增“图片解析与下载”章节）**  
**适用项目：Letter Learning AI 英语短文生成 / 学习进度追踪**  
**工作流名称：Syntexia 对话流工作流**  
**工作流 ID：7572622349360758824**  
**空间 ID：7558388129191739455**  
**API 调用方式：Coze / Workflows / Chat API**

---

## 1. 工作流概述（Workflow Overview）

该工作流基于 Coze「对话流（Chatflow）」能力，实现：

- 接收用户输入单词组；
- 调用大模型生成短文、点评或其他教学内容；
- 执行多节点流程（大模型、图像生成节点等）；
- 支持流式输出（stream），便于前端实时显示回复；
- 支持多参数输入（英语水平、班级、词汇数量等）；
- 支持图片生成（图像节点返回图片 URL）。

工作流已在 Coze 空间中正式发布，可通过官方 API **直接调用，无需发布为独立智能体（bot）**：

```http
POST https://api.coze.cn/v1/workflows/chat
```

---

## 2. 工作流输入参数说明（Input Parameters）

工作流的「开始节点」定义了多个输入参数，分为两类：

1. 对话输入（USER_INPUT）：必须通过 `additional_messages` 传递；
2. 自定义参数（CONVERSATION_NAME / USER_CLASS / USER_ENGLISH_LEVEL / USER_TARGETWORD_NUM）：必须通过 `parameters` 传递。

### 2.1 对话流用户输入（USER_INPUT）

> 必须通过 additional_messages 提供，不能写在 parameters 里。

| 参数名      | 类型   | 必填 | 说明                                           |
|-------------|--------|------|------------------------------------------------|
| USER_INPUT  | string | 必填 | 用户输入的文本，例如单词列表或提示性文字内容。|

USER_INPUT 对应的具体位置示例（在 additional_messages 中）：

```json
"additional_messages": [
  {
    "content": "这些是今天的单词：achieve, display, survey...",
    "content_type": "text",
    "role": "user",
    "type": "question"
  }
]
```

---

### 2.2 其他自定义工作流参数（parameters）

> 所有自定义参数必须通过 `parameters` 顶层字段传入。

| 参数名              | 类型          | 必填 | 说明                                      |
|---------------------|---------------|------|-------------------------------------------|
| CONVERSATION_NAME   | string        | 可选 | 会话名称，不传则使用默认值               |
| USER_CLASS          | string        | 可选 | 用户班级，如“商务英语”、“大学英语2班”等 |
| USER_ENGLISH_LEVEL  | string        | 可选 | 用户英语水平，如“英语四级”、“B1”等     |
| USER_TARGETWORD_NUM | string/number | 可选 | 单词数量，例如 "20" 或 20                |

示例：

```json
"parameters": {
  "CONVERSATION_NAME": "Default",
  "USER_CLASS": "商务英语",
  "USER_ENGLISH_LEVEL": "英语四级",
  "USER_TARGETWORD_NUM": "20"
}
```

---

## 3. API 基础信息（API Specification）

### 3.1 请求 URL

```http
POST https://api.coze.cn/v1/workflows/chat
```

---

### 3.2 鉴权方式（Authorization）

Coze 使用 Bearer Token 进行鉴权。推荐使用「服务身份（service identity）」生成长期凭证。

HTTP Header 示例：

```http
Authorization: Bearer <SERVICE_IDENTITY_TOKEN>
Content-Type: application/json
```

示例 token 仅用于本地/内网测试，不要在 GitHub、前端代码或公开环境暴露：

```text
sat_5b3p8D4mZVDsJHkjNVkUxaVjlWr57Jm2ubdjbK3g3CL7twJk0hDl6GqXac188Cfm
```

---

### 3.3 Content-Type

```http
Content-Type: application/json
```

---

## 4. API 请求体结构（Request Body）

一个完整的请求体包括三个部分：

1. `workflow_id`：对话流 ID；
2. `additional_messages`：包含 USER_INPUT 的对话输入数组；
3. `parameters`：自定义工作流参数。

### 4.1 完整请求示例

```json
{
  "workflow_id": "7572622349360758824",

  "additional_messages": [
    {
      "content": "这些是今天的单词：achieve, display, survey...",
      "content_type": "text",
      "role": "user",
      "type": "question"
    }
  ],

  "parameters": {
    "CONVERSATION_NAME": "Default",
    "USER_CLASS": "商务英语",
    "USER_ENGLISH_LEVEL": "英语四级",
    "USER_TARGETWORD_NUM": "20"
  }
}
```

---

## 5. Python 示例代码（基础调用 + 流式输出）

下面示例演示如何用 Python 调用该对话流，并以流式方式打印所有返回事件。

```python
import requests
import json

API_KEY = "sat_5b3p8D4mZVDsJHkjNVkUxaVjlWr57Jm2ubdjbK3g3CL7twJk0hDl6GqXac188Cfm"
WORKFLOW_ID = "7572622349360758824"

url = "https://api.coze.cn/v1/workflows/chat"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "workflow_id": WORKFLOW_ID,

    "additional_messages": [
        {
            "content": "achieve, display, survey, ...",
            "content_type": "text",
            "role": "user",
            "type": "question"
        }
    ],

    "parameters": {
        "CONVERSATION_NAME": "Default",
        "USER_CLASS": "商务英语",
        "USER_ENGLISH_LEVEL": "英语四级",
        "USER_TARGETWORD_NUM": "20"
    }
}

with requests.post(url, json=payload, headers=headers, stream=True) as r:
    for raw in r.iter_lines():
        if not raw:
            continue
        try:
            event = json.loads(raw.decode("utf-8"))
            print(event)
        except Exception:
            print(raw.decode("utf-8"))
```

运行后可看到如下类型的事件：

- conversation.chat.created（对话已创建）
- conversation.chat.in_progress（对话处理中）
- conversation.message.delta（增量输出，如逐字输出）
- conversation.message.completed（单条消息完成）
- conversation.chat.completed（对话整体完成）
- done（整个流式过程结束）

---

## 6. 返回结构说明（Response Events）

对话流采用「流式返回」，服务端会持续推送多个 JSON 事件。

### 6.1 常见事件类型

| event                         | 说明                       |
|-------------------------------|----------------------------|
| conversation.chat.created     | 对话已创建                 |
| conversation.chat.in_progress | 对话处理中                 |
| conversation.message.delta    | 消息增量输出（逐段/逐字）  |
| conversation.message.completed | 单条消息完成              |
| conversation.chat.completed   | 整个对话流执行完成         |
| done                          | 本次流式返回正常结束       |

### 6.2 文本内容的获取

- 增量内容：在 `conversation.message.delta` 的 `data` 字段中；
- 完整内容：在 `conversation.message.completed` 的 `data.content` 中（包含 text / image 等内容块）。

---

## 7. 图片解析说明（Image Parsing Guide）

该工作流包含图像生成节点（如 Seedream / ImageGen），会生成图片并以 URL 的形式返回。

注意：图片不会出现在 final_output / done 中，必须从流式事件里自己解析。

### 7.1 Coze 可能返回的图片结构

为了保证兼容性，建议开发端支持以下所有形式。

#### 格式 1：data.type = "image"

```json
{
  "event": "conversation.message.delta",
  "data": {
    "type": "image",
    "url": "https://xxx/image.png"
  }
}
```

#### 格式 2：data.content[].type = "image_url"

```json
{
  "event": "conversation.message.completed",
  "data": {
    "content": [
      {
        "type": "image_url",
        "image_url": {
          "url": "https://xxx/image.png"
        }
      }
    ]
  }
}
```

#### 格式 3：data.images 数组

```json
{
  "data": {
    "images": [
      { "url": "https://xxx1.png" },
      { "url": "https://xxx2.png" }
    ]
  }
}
```

#### 格式 4：data.content[].type = "images"

```json
{
  "data": {
    "content": [
      {
        "type": "images",
        "images": [
          { "url": "https://xxx1.png" }
        ]
      }
    ]
  }
}
```

#### 格式 5：图片内容在 delta 字段中

某些场景中，图片信息可能出现在 `delta` 字段而非 `data` 中：

```json
{
  "event": "conversation.message.delta",
  "delta": {
    "content": [
      {
        "type": "image_url",
        "image_url": {
          "url": "https://xxx.png"
        }
      }
    ]
  }
}
```

---

### 7.2 通用图片解析函数（Python）

下面是一个兼容多种 Coze 图片返回格式的通用解析函数，建议直接拷贝到项目中使用：

```python
def extract_image_urls(event_json):
    """从 Coze 对话流事件 JSON 中提取图片 URL。

    兼容以下常见格式：
    1) data = {"type": "image", "url": "..."}
    2) data = {"content":[{"type":"image_url","image_url":{"url":"..."}}]}
    3) data = {"images":[{"url":"..."}, ...]}
    4) data = {"content":[{"type":"images","images":[{"url":"..."}]}]}
    5) delta = {...} 中出现与上面类似的结构
    """
    urls = []

    # 收集所有可能的容器（data / delta）
    containers = []
    if isinstance(event_json, dict):
        if isinstance(event_json.get("data"), dict):
            containers.append(event_json["data"])
        if isinstance(event_json.get("delta"), dict):
            containers.append(event_json["delta"])

    for container in containers:
        # Case 1: data 本身是 {type:image, url:...}
        if container.get("type") == "image" and "url" in container:
            urls.append(container["url"])

        # Case 2: data.images = [...]
        if "images" in container and isinstance(container["images"], list):
            for img in container["images"]:
                if isinstance(img, dict) and "url" in img:
                    urls.append(img["url"])

        # Case 3: data.content = [...]
        content = container.get("content")
        if isinstance(content, list):
            for block in content:
                if not isinstance(block, dict):
                    continue

                # type = image_url
                if block.get("type") == "image_url":
                    img_info = block.get("image_url") or {}
                    url = img_info.get("url")
                    if url:
                        urls.append(url)

                # type = image
                if block.get("type") == "image":
                    img_info = block.get("image") or {}
                    url = img_info.get("url")
                    if url:
                        urls.append(url)

                # type = images（数组）
                if block.get("type") == "images":
                    imgs = block.get("images") or []
                    for img in imgs:
                        if isinstance(img, dict):
                            url = img.get("url")
                            if url:
                                urls.append(url)

    # 去重 & 过滤空值
    return [u for u in dict.fromkeys(urls) if u]
```

---

### 7.3 在流式调用中使用图片解析函数

示例：与流式请求结合使用，将所有图片 URL 收集到列表中：

```python
import requests
import json

image_urls = []

with requests.post(url, json=payload, headers=headers, stream=True) as r:
    for raw in r.iter_lines():
        if not raw:
            continue

        try:
            event = json.loads(raw.decode("utf-8"))
        except Exception:
            # 非 JSON 行可忽略或打印日志
            continue

        # 解析图片 URL
        urls = extract_image_urls(event)
        if urls:
            image_urls.extend(urls)
            print("收到图片 URL:", urls)

        # 其他事件可按需处理
        # print(event)

print("最终图片 URL 列表:", image_urls)
```

---

### 7.4 下载图片示例（可选）

如需将生成的图片保存至本地，可使用以下示例：

```python
import os
import requests

def download_images(urls, dest_dir="downloaded_images"):
    os.makedirs(dest_dir, exist_ok=True)
    saved_paths = []
    for i, url in enumerate(urls, start=1):
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            filename = os.path.join(dest_dir, f"workflow_image_{i}.png")
            with open(filename, "wb") as f:
                f.write(resp.content)
            saved_paths.append(filename)
            print(f"[OK] 已保存图片: {filename}")
        except Exception as e:
            print(f"[FAIL] 下载图片失败: {url} 错误: {e}")
    return saved_paths
```

---

## 8. 工作流调用注意事项（Important Notes）

1. USER_INPUT 必须在 additional_messages 中传入，不能写进 parameters。  
2. 所有自定义参数必须位于 `parameters` 顶层 JSON 中。  
3. 本工作流调用不需要 `bot_id` 或 `app_id`（直接调用资源库中的对话流）。  
4. 使用前必须在 Coze 控制台中点击「发布」工作流，否则调用会返回错误码 `4200`。  
5. 服务身份 token / 个人 token 禁止 放在前端、公开仓库或客户端代码中。  
6. 如需上传文件、图片作为输入参数，必须先调用「上传文件」API 获取 `file_id` 或提供公网可访问的 URL。  
7. 图片解析须依赖流式事件，前端/后端代码必须实现对 `image_url` / `images` 等结构的解析。  

---

## 9. 常见错误及排查（Troubleshooting）

| 错误 / 现象                 | 可能原因                                   | 解决办法                                                   |
|----------------------------|--------------------------------------------|------------------------------------------------------------|
| 4200 工作流未发布          | 工作流尚未正式发布                         | 在 Coze 控制台中点击「发布」后再调用                       |
| USER_INPUT 无效 / 为空     | 传到了 `parameters` 中                     | 确保 USER_INPUT 只出现在 `additional_messages[*].content` |
| 401 unauthorized           | token 错误、过期或无权限                   | 在「服务身份及凭证」中重新生成 Service Identity Token     |
| 对话无输出                 | 请求体结构错误或参数缺失                   | 检查 workflow_id / additional_messages / parameters 格式   |
| 解析不到图片 URL           | 解析逻辑只处理了单一格式                   | 使用本文第 7 章的通用 `extract_image_urls` 函数           |
| 下载图片失败               | 图片 URL 无效或网络问题                    | 打印 URL、HTTP 状态码，确认 URL 可直接访问                |

---

## 10. 二次封装建议（可扩展）

在实际项目中，可基于上述逻辑进行进一步封装，例如：

- 封装为 Python SDK 类：  
  - 提供 `send_message(text)` / `get_images()` 等方法；  
  - 自动管理 `conversation_id`、追加历史消息等。

- Java / Spring Boot 后端：  
  - 使用 WebClient 或 OkHttp 进行流式请求；  
  - 将增量输出通过 WebSocket 推送给前端。

- Vue 前端：  
  - 使用 WebSocket 或 Server-Sent Events (SSE) 接收后端推送；  
  - 实时渲染对话文本与图片卡片。

如需更具体的「类设计示例」或「Java / Node / 前端版本」，可以在此文档基础上进一步扩展。

---

文档到此结束。
