# Letter Learning 后端服务说明

该目录存放基于 FastAPI + MySQL 的后端代码，用于支撑平台的用户体系、权限控制以及后续的学习业务能力。当前仓库引用 Poetry 管理依赖，建议搭配 Python 3.11 及以上版本。

## 目录结构

```
backend/
├── app/                    # 应用源码
│   ├── api/                # 路由与接口定义
│   ├── core/               # 配置、数据库、全局依赖
│   ├── models/             # SQLAlchemy ORM 实体
│   ├── schemas/            # Pydantic 数据模型
│   ├── services/           # 业务服务层
│   ├── repositories/       # 数据访问层
│   └── utils/              # 通用工具
├── migrations/             # Alembic 迁移脚本
├── scripts/                # 扩展脚本（初始化、任务等）
├── tests/                  # 自动化测试
├── docker/                 # Docker 相关配置
├── pyproject.toml          # Poetry 依赖定义
├── README.md               # 本说明文档
├── .env.example            # 环境变量示例
└── sql/                    # MySQL 建表脚本
```

## 环境准备

1. 安装 Python 3.11 及以上版本。
2. 安装 Poetry（https://python-poetry.org/docs/）。
3. 复制 `.env.example` 为 `.env`，根据实际环境填写数据库、JWT、Redis 等配置。
4. 执行 `poetry install` 安装依赖。

## 本地运行

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

首次运行前需确保：

- MySQL 数据库已创建，并导入 `sql/initial_schema.sql`。
- `.env` 中的数据库连接信息指向正确的实例。

## 迁移管理

使用 Alembic 管理数据库版本：

```bash
# 生成迁移
poetry run alembic revision --autogenerate -m "描述信息"

# 应用迁移
poetry run alembic upgrade head
```

首个迁移将与 `initial_schema.sql` 保持一致，后续表结构调整请新增迁移脚本。

## 测试

```bash
poetry run pytest
```

建议为关键接口编写异步测试，保持用户体系与安全逻辑的可靠性。

## 部署简述

- 推荐使用 Docker + Uvicorn/Gunicorn 多进程部署。
- 生产环境需结合反向代理（Nginx/Caddy）处理 HTTPS 与静态资源缓存。
- 配置日志采集、性能监控、异常告警，为后续业务扩张提供保障。

## 验证与运维流程

### 运行服务

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 重置管理员密码

如管理员密码被修改，可在 MySQL 中执行以下脚本恢复为默认 `admin123`：

```sql
SOURCE /path/to/repo/backend/sql/reset_admin_password.sql;
```

其中 `/path/to/repo` 替换为仓库实际路径。

### 快速校验接口

脚本 `scripts/check_auth.py` 支持一次性验证登录、获取用户信息、令牌刷新与注销流程：

```bash
poetry run python scripts/check_auth.py --username admin --password admin123
```

若服务地址调整，可加 `--base-url http://your-host:port`。

