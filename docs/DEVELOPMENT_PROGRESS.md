# Letter Learning 项目开发进度说明

本文档记录截至当前阶段的后端/前端建设进度、重要决策以及后续规划。团队可据此对齐工作状态，作为里程碑复盘与迭代计划的参考。

## 里程碑概览

| 时间节点 | 交付内容 | 说明 |
| -------- | -------- | ---- |
| M0 | 初始化项目骨架 | 选定 FastAPI + MySQL 架构，搭建 `backend/` 目录结构、配置加载、异步数据库会话、CORS、健康检查等基础设施。 |
| M0+ | 数据库建模 | 设计用户、角色、刷新令牌、验证码等核心表，编写 `backend/sql/initial_schema.sql` 及默认管理员种子数据。 |
| M0+ | 认证体系 | 实现登录 / 刷新 / 登出 / 注册接口，完成 JWT 发放、刷新令牌持久化、邀请码机制，并与前端模板对接。 |
| M0+ | 用户管理 | 新增 `/userManagement` 系列接口，实现用户分页查询、创建、编辑、删除以及角色分配，前端页面基本联通。 |
| M0+ | 其他配套 | 提供 `/notice/getList` 占位接口避免前端 404，补充 `.gitignore`、配置说明、Alembic 模板等基础设施。 |
| 当前阶段 | 自动化测试、部署指引 | 编写 `pytest-asyncio` 集成测试覆盖注册/登录/用户管理流程；准备 Alembic 标记脚本与部署流程文档；整理项目进度与部署指南。 |

## 详细进度

### 1. 基础框架与配置

- 建立模块化目录（`app/api`, `core`, `models`, `services`, `repositories` 等），实现应用创建与生命周期管理。
- `Settings` 配置支持 `.env`，输出同步/异步数据库 URL，后续可通过环境变量切换。
- 引入 `FastAPI` + `SQLAlchemy 2.x async` + `Alembic`，统一数据库访问方式。
- 添加 Docker/部署占位目录，为后续容器化留出空间。

### 2. 数据模型与迁移管理

- `users`, `roles`, `user_roles`, `refresh_tokens`, `verification_codes`, `password_reset_requests`, `audit_logs` 等表完成建模与脚本。
- 生成 Alembic 模板 `migrations/script.py.mako` 与初始版本 `1bbf83c969d8_initial_schema.py`，执行升级时同步写入默认角色与管理员账号。
- 提供 `scripts/db_stamp_head.sh` 便于在已有数据库上快速标记迁移版本。

### 3. 认证与注册逻辑

- 支持登录、刷新、登出、获取用户信息；JWT 内嵌角色信息，刷新令牌与清除机制可单独操作。
- 注册流程启用邀请码校验 (`letter-learning`)，并要求邮箱、密码二次输入一致。
- 前端登录/注册页全部切换到真实接口，默认管理员账号可直接体验。

### 4. 用户管理功能

- 后端：提供列表、创建/编辑、删除接口，支持角色分配与分页查询。
- 前端：用户管理页调用真实接口，编辑弹窗支持管理员/教师/学生多选，邮箱必填、编辑密码可选。
- 删除操作支持单选/批量，与后端逻辑保持一致。

### 5. 自动化测试

- 使用 `pytest-asyncio` + `httpx.AsyncClient` 编写集成测试（`backend/tests/test_auth_and_user_management.py`）：
  - 覆盖注册-登录-获取用户信息全流程。
  - 覆盖重复注册 / 错误登录等异常路径。
  - 覆盖用户管理的增、改、删、查。
- 构建独立的 SQLite 测试数据库（见 `backend/tests/conftest.py`），测试运行互不干扰真实数据。
- 提供 `pytest.ini`，默认开启 `asyncio_mode = auto`，测试命令：`poetry run pytest`.

### 6. 文档与指引

- `backend/README.md` 更新运行、迁移、验证说明。
- 当前文档即为开发进度记录；另附部署指南见 `docs/DEPLOYMENT_GUIDE.md`。

## 待办与规划

1. **业务扩展**：设计单词库、学习进度、对话记录等业务表结构与 API 契约。
2. **安全性提升**：完善密码重置、邮箱验证、邀请码管理后台等功能。
3. **系统监控**：接入日志采集、性能监控、告警（如 Sentry、Prometheus）。
4. **前端优化**：针对已启用接口的页面进行 UX 打磨、表单交互与错误提示优化。
5. **CI/CD**：后续可引入 GitHub Actions 或自建 CI 流程执行测试、构建与部署。

上述工作可按优先级与资源状况逐步推进。若需在文档中添加新的里程碑，请保持格式一致，确保团队成员快速了解项目状态。 

