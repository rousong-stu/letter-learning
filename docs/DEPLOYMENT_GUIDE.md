# Letter Learning 部署指南

本文档提供从开发环境到生产环境部署 Letter Learning 平台的详细步骤。默认假设后端运行在 Linux 服务器（Ubuntu / Debian），数据库使用 MySQL 8.x，前端为 Vue 项目。可根据实际情况做适当调整。

---

## 1. 前置条件

- **服务器资源**：建议 2 核 CPU、4 GB 内存以上，用于运行 FastAPI + MySQL + 前端静态资源或容器。
- **系统依赖**：
  - Python 3.11+
  - Poetry 1.6+
  - Node.js 16+（前端构建）
  - MySQL 8.x（或兼容的云数据库）
  - Git
- **网络**：能够访问项目仓库及所需依赖源；若需公网访问需开放 80/443 或自定义端口。

---

## 2. 准备数据库

1. 登录 MySQL，创建数据库并授权：
   ```sql
   CREATE DATABASE letter_learning CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'letter_user'@'%' IDENTIFIED BY 'letter_password';
   GRANT ALL PRIVILEGES ON letter_learning.* TO 'letter_user'@'%';
   FLUSH PRIVILEGES;
   ```

2. 初次部署可导入基础表结构：
   ```bash
   mysql -u letter_user -p letter_learning < backend/sql/initial_schema.sql
   ```
   或使用 Alembic 升级（见下文）。

---

## 3. 后端部署

### 3.1 拉取代码与安装依赖

```bash
git clone git@github.com:rousong-stu/letter-learning.git
cd letter-learning/backend
poetry install
```

### 3.2 配置环境变量

复制 `.env.example` 为 `.env`，按环境修改：

```bash
cp .env.example .env
```

重点变量：

| 变量 | 说明 | 示例 |
| ---- | ---- | ---- |
| `DB_USER` / `DB_PASSWORD` | 数据库账号 | `letter_user` / `letter_password` |
| `DB_HOST` / `DB_PORT` | 数据库地址、端口 | `127.0.0.1` / `3306` |
| `DB_NAME` | 数据库名称 | `letter_learning` |
| `JWT_SECRET` | JWT 密钥，生产环境务必修改 | `your-production-secret` |
| `APP_ENV` | 运行环境标签 | `production` |

### 3.3 迁移与数据标记

首次部署：执行迁移以建表并写入默认数据（管理员帐号 `admin/admin123`）：

```bash
poetry run alembic upgrade head
```

如果数据库已手动建表，可使用提供的脚本仅标记版本：

```bash
bash scripts/db_stamp_head.sh
```

验证 `alembic_version` 表是否存在且指向最新 revision。

### 3.4 启动服务

- **开发模式**：
  ```bash
  poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ```
- **生产模式（推荐 Gunicorn + UvicornWorker）**：
  ```bash
  poetry run gunicorn app.main:app \
    -k uvicorn.workers.UvicornWorker \
    -b 0.0.0.0:8000 \
    --workers 4 \
    --access-logfile - \
    --error-logfile -
  ```

### 3.5 进程守护（可选）

使用 systemd 维护进程：

```ini
# /etc/systemd/system/letter-learning.service
[Unit]
Description=Letter Learning FastAPI Service
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/letter-learning/backend
ExecStart=/usr/bin/env poetry run gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --workers 4
Restart=always
Environment=APP_ENV=production

[Install]
WantedBy=multi-user.target
```

部署后执行：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now letter-learning
```

---

## 4. 前端部署

1. 安装依赖并构建：
   ```bash
   cd letter-learning/letter-learning-ui
   pnpm install   # 或 npm install / yarn
   pnpm build     # 生成 dist 目录
   ```

2. 配置 `.env.production` 中的后端接口地址，例如：
   ```
   VUE_APP_BASE_URL='https://api.yourdomain.com'
   ```

3. 将 `dist` 目录上传到静态服务器（Nginx/OSS/CDN），或使用容器化方案部署。

示例 Nginx 配置（静态资源 + 代理接口）：

```nginx
server {
    listen 80;
    server_name www.yourdomain.com;

    root /var/www/letter-learning/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## 5. 验证部署

1. 使用浏览器访问前端域名，尝试管理员账户登陆，确认首页和用户管理页面数据加载正常。
2. 注册新用户（邀请码默认 `letter-learning`），确认自动登录并在用户管理列表中出现。
3. 使用 `poetry run pytest` 执行自动化测试，确保部署环境与开发环境一致。

---

## 6. 常见问题

| 问题 | 排查思路 |
| ---- | -------- |
| 连接数据库失败 | 检查 `.env` 配置、数据库监听地址、防火墙、账号权限。 |
| 登录提示 401/403 | 确认管理员账户是否存在、密码是否修改、数据库是否成功迁移。 |
| 注册提示邀请码错误 | 确认邀请码仍为默认 `letter-learning` 或根据业务调整常量。 |
| 静态资源 404 | 确保前端构建成功、Nginx `root` 指向 dist 目录，且 `try_files` 配置正确。 |
| 跨域问题 | 若前端和后端不同源，可在 FastAPI CORS 设置中指定 `allow_origins` 列表。 |

---

## 7. 后续建议

- **HTTPS**：使用 Certbot 或云厂商证书，为前端域名与 API 域名配置 HTTPS。
- **日志与监控**：整合 Prometheus/Grafana 或 Sentry，记录关键指标、错误日志。
- **自动化部署**：通过 CI/CD（GitHub Actions、GitLab CI 等）自动执行测试、构建、部署命令。
- **备份策略**：定期备份数据库（mysqldump）与前端构建产物，确保灾备能力。

以上流程完成后，即可在公网稳定运行 Letter Learning 平台。 
