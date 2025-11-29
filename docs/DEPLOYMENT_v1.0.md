# 项目部署说明（正式版 v1.0）

> 服务器：8.137.157.36（之前已部署过测试版，数据库已有用户数据）  
> 目标：在保留原有数据的基础上部署 v1.0，后端用 Docker，前端本地打包 dist 后 rsync 上传，Nginx 反向代理，使用 Redis。

---

## 1. 部署前准备
1) 备份现有数据（重要）
   - MySQL：`mysqldump -u<user> -p letter_learning > backup_$(date +%F).sql`
   - 如有 Redis 重要数据，可 `redis-cli SAVE` 或备份 dump.rdb。

2) 确认环境
   - 服务器需安装 Docker / Docker Compose（或直接 docker 命令）。
   - 已有 MySQL 实例（沿用原数据库，勿重建库），Redis 可本机或 Docker。
   - Nginx 已安装（测试版已有配置，可基于现有修改）。

3) 代码获取
   - 后端：在服务器放置 `/opt/letter-learning/backend`（可 git pull 或 rsync）。
   - 前端：在本地构建 dist 后 rsync 到服务器 `/opt/letter-learning/frontend/dist/`。

4) 环境变量（后端）
   - 在服务器 `backend/.env`（或挂载环境变量）：
     ```
     APP_ENV=production
     DB_USER=letter_user
     DB_PASSWORD=letter_password
     DB_HOST=127.0.0.1
     DB_PORT=3306
     DB_NAME=letter_learning
     REDIS_URL=redis://127.0.0.1:6379/0
     JWT_SECRET=自行设置
     JWT_ALGORITHM=HS256
     ACCESS_TOKEN_EXPIRE_MINUTES=30
     REFRESH_TOKEN_EXPIRE_DAYS=30
     LOG_LEVEL=INFO
     ```
   - 如有 Coze/AI 等 Token 亦写入 .env。

---

## 2. 数据库迁移（保留旧数据）
1) 确认当前 `alembic_version`
   ```
   mysql -u<user> -p -e "USE letter_learning; SELECT * FROM alembic_version;"
   ```
2) 在服务器 backend 目录执行（以宿主机 Python 或容器内运行均可）：
   ```
   cd /opt/letter-learning/backend
   poetry install  # 如用宿主机虚拟环境
   poetry run alembic upgrade head
   ```
   - 若使用 Docker 方式，可在容器启动后 exec 运行 `alembic upgrade head`。
3) 若迁移失败，先检查表与约束，再行修复；务必不要删除数据表。

---

## 3. 后端 Docker 部署
示例单容器运行（可按需写 docker-compose）：
```bash
cd /opt/letter-learning/backend
# 构建镜像
docker build -t letter-backend:v1.0 .

# 运行容器（示例端口 8000，挂载 .env）
docker run -d --name letter-backend \
  --env-file /opt/letter-learning/backend/.env \
  -p 8000:8000 \
  letter-backend:v1.0 \
  bash -c "poetry run alembic upgrade head && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000"
```
说明：
- 先执行迁移，再启动 uvicorn，确保数据结构最新。
- 如需 Redis、MySQL 容器，请调整网络与地址（保持 .env 一致）。

---

## 4. 前端构建与上传（本地 → 服务器）
1) 本地构建
   ```
   cd letter-learning-ui
   npm install   # 或 pnpm/yarn，保持锁文件一致
   npm run build
   ```
2) 上传 dist 到服务器（覆盖原测试版）
   ```
   rsync -avzP --delete dist/ root@8.137.157.36:/opt/letter-learning/frontend/dist/
   ```
3) 确认服务器目录 `/opt/letter-learning/frontend/dist` 内容完整。

---

## 5. Nginx 配置示例
假设：
- 前端静态目录：`/opt/letter-learning/frontend/dist`
- 后端接口：容器暴露 `http://127.0.0.1:8000`

```
server {
    listen 80;
    server_name 8.137.157.36;

    # 前端静态
    root /opt/letter-learning/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket (如需要)
    location /ws/ {
        proxy_pass http://127.0.0.1:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}
```
> 注意：若后端路径不含 `/api` 前缀，请调整 `proxy_pass`；保持前后端接口路径一致。

---

## 6. Redis
- 可使用宿主机 redis-server 或 Docker：
  ```
  docker run -d --name redis -p 6379:6379 redis:7-alpine
  ```
- 确保 `.env` 中 `REDIS_URL=redis://127.0.0.1:6379/0`。

---

## 7. 验证
1) 后端健康检查：`curl http://127.0.0.1:8000/docs`（Nginx 反代后通过 `http://8.137.157.36/api/docs`）。
2) 前端访问：`http://8.137.157.36/`，验证登录/注册、短文生成、词典点击等。
3) 查看短文超额弹窗、词典切换、加载动画、页脚版权/备案信息。

---

## 8. 升级与回滚
- 升级：拉取新代码 → 本地构建前端 → rsync 覆盖 → 后端重建镜像并重启容器 → 运行 `alembic upgrade head`。
- 回滚：保留数据库备份，切回上一版本镜像和 dist，或还原数据库备份。

---

## 9. 常见问题
- 迁移报错：检查 `alembic_version`、表结构差异；务必先备份。
- 前端 404 刷新：确保 Nginx `try_files` 指向 `index.html`。
- 接口 502：检查后端容器是否运行、端口/防火墙是否放行。
- 词典/AI 超时：检查网络与 Redis/MySQL 连接，或查看后端日志。

