📘 单词卡片开发说明文档（Markdown 版本）

Version 1.0
Author：Rusong

1. 项目简介

本项目为英语学习平台的核心模块 「单词卡片」。
系统需根据用户输入的英文单词：

调用 Merriam-Webster Dictionary API 与 Thesaurus API

获取单词的发音、音标、英文释义、例句、同义词、词源等

将字段清洗并标准化，返回统一 JSON

提供给前端渲染单词卡片

中文释义（可选）由 AI 翻译生成。

2. API 信息
2.1 已申请的 API Key
Dictionary Key : 015c5134-71dc-4766-9b63-69aa5c2bec51
Thesaurus Key  : fbd67380-1208-4f60-93a5-ac4758820145

2.2 API 请求 URL

Dictionary：

https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key=YOUR_DICTIONARY_KEY


Thesaurus：

https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{word}?key=YOUR_THESAURUS_KEY

3. 数据字段说明（可用于单词卡片）

以下字段来自 Merriam-Webster JSON。

3.1 基本信息（必需）
内容	字段路径
单词	hwi.hw
音标	hwi.prs[].mw
音频文件名	hwi.prs[].sound.audio

音频 URL 拼接方式见后文。

3.2 词性（part of speech）
fl

3.3 变体拼写（variants）
vrs[].va
vrs[].vl

3.4 英文释义（definitions）
def[].sseq[][].sense.dt[]


"text" 为英文释义

"vis" 为例句

需清洗 {bc} {it} {wi} 这种 M-W 特殊格式 token

3.5 例句（example sentences）
dt[] → ["vis", [{"t": "..."}]]

3.6 标签（labels）
类型	字段
一般标签	lbs
语法/地域标签	sls
括号标签	psl

例如：chiefly British、informal。

3.7 词形变化（inflections）
ins[].if
ins[].ifc


例如：pajamas / ran / running。

3.8 词源（etymology）
et

3.9 首次出现年份
date

3.10 同义词/反义词（来自 Thesaurus API）
syn_list[][].wd
sim_list[][].wd
ant_list[][].wd

4. Python API 调用示例
import requests

DICT_KEY = "015c5134-71dc-4766-9b63-69aa5c2bec51"
THES_KEY = "fbd67380-1208-4f60-93a5-ac4758820145"

def fetch_dictionary(word):
    url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={DICT_KEY}"
    return requests.get(url).json()

def fetch_thesaurus(word):
    url = f"https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{word}?key={THES_KEY}"
    return requests.get(url).json()

5. 音频 URL 构造函数（Python）

官方子目录规则（bix / gg / number / 首字母）：

def build_audio_url(audio):
    if audio.startswith("bix"):
        sub = "bix"
    elif audio.startswith("gg"):
        sub = "gg"
    elif audio[0].isdigit() or not audio[0].isalpha():
        sub = "number"
    else:
        sub = audio[0]

    return f"https://media.merriam-webster.com/audio/prons/en/us/mp3/{sub}/{audio}.mp3"

6. JSON 字段解析逻辑（伪代码）
entry = dictionary_json[0]

word = entry["hwi"]["hw"]

phonetics = [
    {mw, audio_url}
]

part_of_speech = entry["fl"]

definitions = [
    {meaning, examples}
]

variants = [vrs[].va]

labels = lbs + sls + psl

inflections = ins[].if / ifc

etymology = entry["et"]

first_use = entry["date"]

synonyms = from thesaurus_json
antonyms = from thesaurus_json

7. 后端返回前端的标准 JSON Schema（最终格式）

后端必须返回如下格式：

{
  "word": "pajama",
  "phonetics": [
    {
      "notation": "pə-ˈjɑ-mə",
      "audio_url": "https://media.merriam-webster.com/audio/prons/en/us/mp3/p/pajama02.mp3"
    }
  ],
  "part_of_speech": "noun",
  "definitions": [
    {
      "meaning": "a loose-fitting garment worn for sleeping",
      "examples": ["He changed into his favorite pajamas before bed."]
    }
  ],
  "variants": ["pyjama"],
  "labels": {
    "general": ["often plural"],
    "usage": ["chiefly British"]
  },
  "inflections": {
    "plural": "pajamas"
  },
  "synonyms": ["sleepwear", "nightwear"],
  "antonyms": [],
  "etymology": "from Hindi pajama, from Persian pāy-jāmeh",
  "first_use_date": "1800",
  "chinese_translation": "睡衣；宽松睡袍"
}

8. 后端开发注意事项

API 返回为数组
如果返回数组第一个是字符串（如 "pajam" → ["pajamas","pajamaed"...]），需判断为“未找到单词”。

清理特殊 token {bc} {it} {wi} 等。

字段可能不存在
例如音标、例句、同义词，必须写字段存在性判断。

AI 中文翻译（可选）
可使用 DeepSeek：

meaning + examples → AI 翻译 → chinese_translation


推荐接口格式

GET /api/word/{word}

9. 可交付开发者的简要说明（可直接复制给外包团队）

请按文档开发 Merriam-Webster 单词卡片模块。

需实现：

Dictionary + Thesaurus API 请求

解析字段：word / phonetics / audio / pos / definitions / examples / variants / labels / inflections / synonyms / etymology / date

清理特殊符号

返回统一格式 JSON（见 Section 7）

开发语言 Python（推荐 FastAPI）

提供接口：GET /api/word/{word}