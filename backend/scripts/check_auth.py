"""
简单的接口校验脚本，用于在本地验证登录、获取用户信息、刷新令牌等流程。

运行方式：
    poetry run python scripts/check_auth.py --username admin --password admin123
"""

from __future__ import annotations

import argparse
import asyncio
from typing import Any, Dict, Optional

import httpx

BASE_URL = "http://127.0.0.1:8000"


async def call_api(
    client: httpx.AsyncClient,
    method: str,
    path: str,
    token: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = await client.request(method, path, headers=headers, **kwargs)
    response.raise_for_status()
    return response.json()


async def run_checks(username: str, password: str, base_url: str) -> None:
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        print(f"1. 登录 {username}")
        login_resp = await call_api(
            client,
            "POST",
            "/login",
            json={"username": username, "password": password},
        )
        print("登录返回:", login_resp)
        token = login_resp["data"]["token"]

        print("\n2. 获取用户信息")
        user_info = await call_api(client, "GET", "/userInfo", token=token)
        print("用户信息:", user_info)

        print("\n3. 检测令牌是否过期")
        expire_status = await call_api(client, "GET", "/expireToken", token=token)
        print("令牌状态:", expire_status)

        print("\n4. 刷新令牌")
        refresh_resp = await call_api(client, "GET", "/refreshToken", token=token)
        print("刷新结果:", refresh_resp)
        new_token = refresh_resp["data"]["token"]

        print("\n5. 退出登录")
        logout_resp = await call_api(client, "GET", "/logout", token=new_token)
        print("退出结果:", logout_resp)


def main() -> None:
    parser = argparse.ArgumentParser(description="校验认证相关接口")
    parser.add_argument("--username", required=True, help="登录用户名")
    parser.add_argument("--password", required=True, help="登录密码")
    parser.add_argument("--base-url", default=BASE_URL, help="后端服务地址")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/") or BASE_URL
    asyncio.run(run_checks(args.username, args.password, base_url))


if __name__ == "__main__":
    main()
