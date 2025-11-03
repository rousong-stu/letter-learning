# Letter Learning 用户体系数据库说明

该目录存放项目最初的 MySQL 建表脚本，主要用于搭建认证与用户管理的基础设施，执行后将具备以下能力：

- 系统初始角色（管理员、教师、学生）
- 用户账号与密码哈希、基础信息字段
- 用户与角色的关联关系（支持多角色）
- 刷新令牌的持久化存储，便于令牌轮换与撤销
- 注册、登录、找回密码等场景的验证码存储
- 密码重置令牌的发放与使用记录
- 安全审计日志，记录敏感操作

## 表结构概览

- `roles`：平台角色字典，预置管理员/教师/学生。
- `users`：用户核心信息（用户名、密码哈希、联系方式、状态标记）。
- `user_roles`：用户与角色的多对多关系表。
- `refresh_tokens`：刷新令牌存储，可针对单个令牌进行撤销。
- `verification_codes`：验证码存储，支持邮箱/短信以及多种用途。
- `password_reset_requests`：密码重置请求记录及其生命周期。
- `audit_logs`：安全事件日志，如登录、角色调整等。

脚本内已创建默认管理员账号，用户名 `admin`，密码 `admin123`（使用 bcrypt，成本值 12）。

## 导入步骤

1. 确保 MySQL 8.x 已运行，并且已经创建目标数据库（例如 `letter_learning`）。
2. 在终端执行：
   ```bash
   mysql -u <数据库账号> -p -h <数据库地址> <数据库名> < backend/sql/initial_schema.sql
   ```
   - 如果是本机，可省略 `-h`；将尖括号内内容替换成实际参数。
3. 导入完成后，可执行以下语句检查：
   ```sql
   USE letter_learning;
   SHOW TABLES;
   SELECT username, status FROM users;
   SELECT slug FROM roles;
   ```
4. 确认无误后，即可让后端服务连接该数据库开展后续开发。

