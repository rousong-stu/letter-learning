# 脚本说明

该目录存放与数据库初始化、迁移执行、数据导入相关的辅助脚本。当前可按以下流程让 ORM 模型与数据库结构保持一致：

1. 在本地 MySQL 中执行 `sql/initial_schema.sql`（如果尚未导入）。
2. 生成首个 Alembic 迁移，让迁移记录与现有结构匹配：
   ```bash
   poetry run alembic revision --autogenerate -m "初始化用户体系"
   ```
3. 检查 `migrations/versions/` 下生成的脚本，确认字段、索引与 SQL 文件一致后执行：
   ```bash
   poetry run alembic upgrade head
   ```
4. 后续新增或调整表结构时，重复步骤 2-3 创建新的迁移脚本，避免直接修改 `initial_schema.sql`。

### 账号修复脚本

如果需要重置管理员账号密码，可执行 `backend/sql/reset_admin_password.sql`，密码默认为 `admin123`。

如需日后编写自动化脚本（批量导入词库、初始化管理员等），可放置在本目录。
