# 项目说明（正式版 v1.0）

## 项目概览
- 名称：Lumilyx 英语学习平台
- 版本：v1.0（正式版）
- 主要功能
  - 登录/注册（含验证码）
  - 首页学习概览与数据看板
  - “Lumilyx 短文伴学”模块（AI 生成短文、再学一篇、词典/单词卡片/对话）
  - 词典查询、学习计划配置、单词书上传（管理员）
  - AI 生成短文：每日限制 2 篇，可弹窗确认继续超额
  - 点击短文或“今日词汇”中的单词，自动跳转至词典并查询
  - Lottie 加载动画（首页加载、生成短文/AI 生成中）
  - 站点统一页脚版权/备案信息

## 技术栈
- 前端：Vue 3 + TypeScript + Element Plus + Vite/webpack（基于 Vue Admin Plus 自定义）
- 后端：FastAPI + SQLAlchemy + Alembic
- 数据库：MySQL 8.x
- 缓存/会话：Redis
- 部署：Nginx 反向代理；后端推荐 Docker 运行；前端本地打包 dist 后通过 rsync 上传

## 关键目录
- `backend/`：FastAPI 服务、数据库模型与迁移
  - `app/api/v1/`：接口定义
  - `app/services/`：业务逻辑（词汇短文、用户计划等）
  - `app/schemas/`：Pydantic 模型
  - `migrations/`：Alembic 迁移
- `letter-learning-ui/`：前端代码
  - `src/views/wordStory/`：Lumilyx 短文伴学页
  - `src/views/home/`：首页看板
  - `src/views/login/`：登录页
  - `library/components/VabFooter/`：全局页脚版权与备案

## 核心业务流程
1. 登录/注册：前端表单 + 后端验证码校验，登录成功后自动加载今日短文（若无则生成，受每日 2 篇限制）。
2. Lumilyx 短文伴学：
   - 再学一篇：超出 2 篇时先弹窗确认，允许继续生成。
   - 点击单词（今日词汇或正文）：自动切到“词典”Tab 并查询。
   - 侧边卡片包含：Lumilyx（对话）、单词卡片、词典。
3. 学习设置：配置学习计划、上传单词书（管理员），更新后全站刷新以获取新计划。

## 配置要点
- 环境变量（后端 `.env` 示例）
  - `DB_USER/DB_PASSWORD/DB_HOST/DB_PORT/DB_NAME`
  - `REDIS_URL`
  - `JWT_SECRET/ACCESS_TOKEN_EXPIRE_MINUTES/REFRESH_TOKEN_EXPIRE_DAYS`
  - Coze/AI 相关 token（如有）
- 备案/版权：已统一在页脚和登录页最底部展示，并链接至工信部备案系统。

## 版本特性与改动摘要（v1.0）
- 登录页：新增验证码、Lottie 加载动画、手写体副标题、底部备案版权信息。
- 短文伴学：点击单词跳转词典；超额弹窗确认；加载动画；词典/单词卡片滚动条优化。
- 菜单调整：主菜单“开始学习”→“Lumilyx短文伴学”；上传单词书移到“学习设置”下；首页优先显示。
- 统一页脚：`Copyright ©2025 www.lumilyx.cn | 蜀ICP备2025152100号-2 | 四川大成迅龙数据科技有限公司 版权所有`

## 已知注意事项
- 每日短文默认自动生成上限 2 篇，超额需用户确认。
- 依赖 MySQL/Redis，请确保网络与凭证正确。
- 老数据迁移：部署前请备份数据库，执行 Alembic 时确认 `alembic_version` 与表状态；已有用户/学习记录需保留，避免删除库。

