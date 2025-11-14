# 数据库清理方案（单管理员架构）

## 1. 背景与目标
- 现有数据库沿用了多角色、验证码、密码找回、审计等完整后台系统设计，导致 `User` 模型加载时会自动访问 `roles`、`verification_codes`、`password_reset_requests`、`audit_logs` 等关系。
- 登录接口和任何依赖 `get_current_user` 的请求都会触发大量冗余 SQL（见终端日志），显著拖慢响应。
- 项目最新的产品定位：单一管理员账号、聚焦词汇/短文练习，不再需要多角色、权限树、验证码、密码重置等复杂能力。
- 目标：精简数据库结构，只保留当前功能真正依赖的表，从根源上消除多余关联查询，并为后续逻辑重构（例如移除角色相关代码）打下基础。

## 2. 当前表清单与评估
| 表名 | 来源模型 | 当前用途 | 处理建议 |
| --- | --- | --- | --- |
| `users` | `User` | 核心用户表，注册/登录/词文都依赖 | **保留** |
| `user_profiles` | `UserProfile` | 个人资料页使用 | **保留** |
| `user_password_history` | `UserPasswordHistory` | 修改密码记录 | **保留**（或后续按需裁剪） |
| `user_login_logs` | `UserLoginLog` | 个人中心登录日志、登出记录 | **保留** |
| `word_stories` | `WordStory` | AI 词汇短文核心数据 | **保留** |
| `refresh_tokens` | `RefreshToken` | JWT 刷新令牌校验 | **保留** |
| `menus` | `Menu` | 菜单管理接口使用，前端暂未接入 | 可保留待评估或一起下线 |
| `roles` / `user_roles` | `Role` / `UserRole` | 多角色体系；前端已弃用 | **删除** |
| `role_permissions` | `RolePermission` | 菜单权限映射；依赖角色 | **删除**（若保留菜单则改写为无角色模式） |
| `verification_codes` | `VerificationCode` | 验证码 / MFA；未使用 | **删除** |
| `password_reset_requests` | `PasswordResetRequest` | 忘记密码；未使用 | **删除** |
| `audit_logs` | `AuditLog` | 安全审计；未使用 | **删除** |

> 说明：`menus` 目前仅在后端接口和 mock 数据中存在，如果近期无菜单管理需求，可在后续阶段连同 `menu_management` 相关接口一起移除；本轮清理的核心目的是先移除与角色系统直接相关的表。

## 3. 清理步骤
1. **模型与关系调整**
   - 从 `User` 模型移除 `roles`、`verification_codes`、`password_reset_requests`、`audit_logs` 等 `relationship` 定义。
   - 移除 `Role`、`UserRole`、`RolePermission`、`VerificationCode`、`PasswordResetRequest`、`AuditLog` 模型类，并更新 `app/models/__init__.py`。
   - 删除对应的 Pydantic Schema 字段（如 `UserInfoData.roles`，`menu` 相关 schema）。
2. **业务代码同步**
   - `auth_service` / `auth` 接口：停止生成/返回 `roles`，改为固定返回 `["Admin"]` 或直接省略；`issue_token_pair` 不再写入 `roles` claim。
   - `menu_management`、`role_management` 服务：若后续不保留，可在业务层直接下线；如果暂时保留菜单展示，改为静态配置或仅管理员可见的全量菜单。
   - 移除 `get_current_user` 中 `session.refresh(user, attribute_names=["roles"])` 的调用，消除重复查询。
3. **数据库迁移**
   - 编写 Alembic 迁移脚本或（若未启用）SQL 脚本，依次执行：
     ```sql
     DROP TABLE IF EXISTS role_permissions;
     DROP TABLE IF EXISTS user_roles;
     DROP TABLE IF EXISTS roles;
     DROP TABLE IF EXISTS verification_codes;
     DROP TABLE IF EXISTS password_reset_requests;
     DROP TABLE IF EXISTS audit_logs;
     ```
   - 若未来也不需要菜单管理，可额外删除 `menus` 表及相关索引。
   - 更新 `backend/sql/initial_schema.sql` 与迁移文件，确保新成员初始化数据库时即是精简版结构。
4. **数据校验与回归**
   - 运行 `alembic upgrade head`（或相应的初始化脚本），确认库中仅剩保留表。
   - 执行后端单测（若暂缺，可至少手动验证注册、登录、`/word-stories` 全流程）。
   - 清理测试夹具 `backend/tests/conftest.py` 中的角色创建逻辑，避免向不存在的表插入数据。
5. **文档与运维**
   - 在 `README` 或运维手册中记载新的数据库结构。
   - 对生产/预发布环境：提前备份数据库，使用事务性迁移，必要时记录回滚 SQL。

## 4. 后续工作排期建议
| 阶段 | 事项 | 说明 |
| --- | --- | --- |
| Phase 1 | 模型 & API 调整 | 先改代码再生成迁移，避免运行期访问已删除的关系 |
| Phase 2 | 执行迁移 | 在本地/测试库验证无误后再推广 |
| Phase 3 | 移除冗余接口 | 下线 `role_management`、`menu_management`、验证码/密码找回相关接口及前端入口 |
| Phase 4 | 优化登录链路 | 登录接口和 `user_info` 仅查询 `users` + `refresh_tokens`，验证性能改善 |

## 5. 风险与缓解
- **潜在旧数据依赖**：删除表前务必确认无外部系统依赖角色/验证码等数据，可提前导出备份。
- **代码遗漏访问**：若有遗漏的 `session.refresh(user, ["roles"])` 或 `user.roles` 访问，将在运行时抛错；建议通过 `rg "roles"` 全局搜索并清理。
- **测试脚本失效**：现有测试创建的角色/菜单数据会失败，需要同步更新或暂时跳过相关用例。
- **迁移顺序**：若曾经手动建表而非 Alembic，需要保证清理脚本在所有环境一致执行，避免 schema 不一致。

---
该方案完成后，用户登录只需查询 `users`、`refresh_tokens` 等少量表，能够显著降低数据库压力，并让后端与前端保持一致的“单管理员”模式。确认方案可行后，可进入模型/接口实际改造阶段。***
