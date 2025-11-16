# Letter Learning 公网部署指南（Ubuntu 22.04，前端本地构建）

本文描述如何把 Letter Learning 部署到一台全新的 Ubuntu 22.04 服务器（示例公网 IP：`8.137.157.36`）。流程假设：

- 服务器干净、尚未安装任何组件；
- 后端运行在服务器上，数据库使用 MySQL 8.x；
- 前端在开发电脑本地构建 `dist/`，再上传到服务器；
- Nginx 在服务器上同时负责静态资源和 `/api` 反向代理。

## 1. 准备服务器

1. **SSH 登录**
   ```bash
   ssh ubuntu@8.137.157.36
   ```

2. **更新并安装基础依赖**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y git python3.11 python3.11-venv python3-pip build-essential \
       libmysqlclient-dev pkg-config nginx mysql-server
   ```

3. **创建部署目录**
   ```bash
   sudo mkdir -p /opt/letter-learning
   sudo chown -R $USER:$USER /opt/letter-learning
   ```

## 2. 配置 MySQL

1. **安全初始化（可选）**
   ```bash
   sudo mysql_secure_installation
   ```

2. **创建数据库与账号**
   ```sql
   -- 进入 MySQL shell
   sudo mysql

   CREATE DATABASE letter_learning CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'letter_user'@'%' IDENTIFIED BY 'letter_password';
   GRANT ALL PRIVILEGES ON letter_learning.* TO 'letter_user'@'%';
   FLUSH PRIVILEGES;
   EXIT;
   ```

如需对外访问数据库，记得在 `/etc/mysql/mysql.conf.d/mysqld.cnf` 中把 `bind-address` 调整为 `0.0.0.0` 或内网地址，再重启 `mysql`.

## 3. 部署后端（FastAPI）

1. **克隆仓库并安装 Poetry 依赖**
   ```bash
   cd /opt/letter-learning
   git clone https://github.com/rousong-stu/letter-learning.git .
   cd backend
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -U pip
   pip install poetry
   poetry install --without dev
   ```

2. **配置环境变量**
   ```bash
   cp .env.example .env
   nano .env
   ```
   根据服务器实际情况设置以下关键项：

   | 变量 | 示例值 |
   | ---- | ------ |
   | `DB_HOST` / `DB_PORT` | `127.0.0.1` / `3306` |
   | `DB_USER` / `DB_PASSWORD` | `letter_user` / `letter_password` |
   | `DB_NAME` | `letter_learning` |
   | `JWT_SECRET` | 生成新的随机字符串 |
   | `APP_ENV` / `APP_DEBUG` | `production` / `false` |

3. **执行数据库迁移**
   ```bash
   poetry run alembic upgrade head
   ```

4. **验证后端可运行**
   ```bash
   poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
   访问 `http://8.137.157.36:8000/health` 应返回 `{"status":"ok"}`。确认后 `Ctrl+C` 退出。

5. **配置 systemd 服务**
   ```ini
   # /etc/systemd/system/letter-learning.service
   [Unit]
   Description=Letter Learning FastAPI Service
   After=network.target

   [Service]
   WorkingDirectory=/opt/letter-learning/backend
   Environment="PATH=/opt/letter-learning/backend/.venv/bin"
   ExecStart=/opt/letter-learning/backend/.venv/bin/poetry run gunicorn app.main:app \
       -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 --workers 4
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```
   载入并启动：
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now letter-learning
   sudo systemctl status letter-learning
   ```
   后端将监听在本地 `127.0.0.1:8000`，不对公网暴露。

## 4. 本地构建前端

1. **在开发电脑上安装依赖并打包**
   ```bash
   cd /path/to/letter-learning/letter-learning-ui
   pnpm install        # 或 npm install / yarn
   pnpm build          # 生成 dist/ 目录
   ```

2. **准备上传包**
   ```bash
   cd dist
   tar czf letter-learning-dist.tar.gz *
   ```

3. **通过 SCP 上传到服务器（本地执行）**
   ```bash
   scp letter-learning-dist.tar.gz ubuntu@8.137.157.36:/tmp/
   ```

## 5. 服务器上安装前端静态文件

1. **解压并放到 Nginx 根目录**
   ```bash
   sudo mkdir -p /var/www/letter-learning
   cd /var/www/letter-learning
   sudo tar xzf /tmp/letter-learning-dist.tar.gz
   sudo chown -R www-data:www-data /var/www/letter-learning
   ```

2. **配置 Nginx**
   ```nginx
   # /etc/nginx/sites-available/letter-learning
   server {
       listen 80;
       server_name 8.137.157.36;  # 或绑定的域名

       root /var/www/letter-learning;
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
   使配置生效：
   ```bash
   sudo ln -s /etc/nginx/sites-available/letter-learning /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

3. **（可选）启用 HTTPS**
   - 安装 Certbot：`sudo snap install --classic certbot`
   - `sudo certbot --nginx -d your-domain.com`
   如果只有 IP，可暂时保持 HTTP。

## 6. 防火墙与端口

1. **启用 UFW 并放行必要端口**
   ```bash
   sudo ufw allow OpenSSH
   sudo ufw allow 'Nginx Full'    # 放行 80/443
   sudo ufw enable
   sudo ufw status
   ```

2. FastAPI 只监听 `127.0.0.1:8000`，外网只能通过 Nginx 访问 `/api`。

## 7. 验证部署

1. 访问 `http://8.137.157.36/`（或你的域名），应看到前端页面。
2. 使用默认管理员 `admin/admin123` 登录，确认首页数据展示。
3. 新注册一个用户（邀请码默认 `letter-learning`），应能成功并在后台数据表中出现。
4. 检查 `sudo journalctl -u letter-learning -f` 与 `sudo tail -f /var/log/nginx/error.log`，确保无异常。

## 8. 常见问题与排查

| 问题 | 排查思路 |
| ---- | -------- |
| 前端访问不到 `/api` | 检查 Nginx `location /api/` 是否转发成功；确认后端服务运行且监听 127.0.0.1:8000。 |
| 502 Bad Gateway | 通常是 FastAPI 未启动或崩溃；查看 `systemctl status letter-learning`。 |
| 数据库连接失败 | 核对 `.env` 中连接信息、MySQL 权限、防火墙，确认 `mysql -u letter_user -p -h 127.0.0.1 letter_learning` 可连接。 |
| 前端修改未生效 | 重新在本地 `pnpm build`，上传新的 `dist`，替换 `/var/www/letter-learning` 内容，最后 `sudo systemctl reload nginx`。 |
| 登录/注册 422 | 后端严格校验数据（邮箱必填、邀请码默认 `letter-learning`），按错误信息检查输入。 |

## 9. 维护建议

- **日志与监控**：通过 `journalctl` 观察后端日志，Nginx 日志位于 `/var/log/nginx/`。
- **定期备份**：使用 `mysqldump letter_learning > backup.sql`，并备份 `/var/www/letter-learning`。
- **滚动更新**：
  1. 本地更新代码并通过 `pnpm build` 产出新前端；
  2. 服务器 `git pull` + `poetry install`；
  3. `poetry run alembic upgrade head`；
  4. `sudo systemctl restart letter-learning && sudo systemctl reload nginx`。
- **安全**：及时更新系统补丁，使用强密码限制 SSH，必要时配置 Fail2ban。

按照上述步骤，Letter Learning 即可在公网服务器上稳定运行：后端常驻 systemd，前端静态文件由 Nginx 服务，所有 API 请求通过 `/api` 反向代理到本地 FastAPI。下一次升级也只需重复“本地构建 → 上传 dist → 重启服务”的流程即可。***
