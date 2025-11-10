#!/usr/bin/env bash

# 用途：将当前数据库的 Alembic 版本指针标记到最新迁移（head）。
# 使用方式：
#   1. 确保已经在项目根目录复制并配置好 backend/.env，数据库可访问。
#   2. 在 backend 目录下执行：bash scripts/db_stamp_head.sh
#   3. 如需查看结果，可在数据库中查询 alembic_version 表。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

poetry run alembic stamp head

echo "Alembic 版本已标记为 head。"
