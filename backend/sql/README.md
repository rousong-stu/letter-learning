# Letter Learning 用户体系数据库说明

该目录存放项目当前使用的 MySQL 建表脚本，执行后将具备以下能力：

- 单一管理员体系的用户账号、密码哈希及扩展资料字段
- 刷新令牌的持久化存储，便于令牌轮换与撤销
- 密码修改历史、登录日志等基础审计信息
- AI 词汇短文（`word_stories`）所需的数据结构

## 表结构概览

- `users`：用户核心信息（用户名、密码哈希、联系方式、状态标记等）。
- `refresh_tokens`：刷新令牌存储，可针对单个令牌进行撤销。
- `user_profiles`：扩展资料，如真实姓名、联系方式、简介等。
- `user_password_history`：密码修改记录，便于安全审计。
- `user_login_logs`：登录/登出日志，供个人中心查询。
- `word_stories`：AI 词汇短文记录（词包、短文、模型信息等）。

脚本内仍会创建默认管理员账号，用户名 `admin`，密码 `admin123`（使用 bcrypt，成本值 12）。

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
   ```
4. 确认无误后，即可让后端服务连接该数据库开展后续开发。
