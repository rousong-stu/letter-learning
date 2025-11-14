import pytest


REGISTER_URL = "/register"
LOGIN_URL = "/login"
USER_INFO_URL = "/userInfo"
USER_LIST_URL = "/userManagement/getList"
USER_EDIT_URL = "/userManagement/doEdit"
USER_DELETE_URL = "/userManagement/doDelete"


async def _login(client, username="admin", password="admin123"):
    response = await client.post(
        LOGIN_URL,
        json={"username": username, "password": password},
    )
    payload = response.json()
    assert payload["code"] == 200
    return payload["data"]["token"]


@pytest.mark.asyncio
async def test_register_login_flow(client):
    register_payload = {
        "username": "student001",
        "password": "Passw0rd!",
        "passwordConfirm": "Passw0rd!",
        "inviteCode": "letter-learning",
        "email": "student001@example.com",
    }
    response = await client.post(REGISTER_URL, json=register_payload)
    data = response.json()
    assert data["code"] == 200
    token = data["data"]["token"]
    assert token

    user_info = await client.get(
        USER_INFO_URL, headers={"Authorization": f"Bearer {token}"}
    )
    info_data = user_info.json()
    assert info_data["code"] == 200
    assert info_data["data"]["username"] == "student001"

    # 登录新账户
    login_resp = await client.post(
        LOGIN_URL,
        json={"username": "student001", "password": "Passw0rd!"},
    )
    login_data = login_resp.json()
    assert login_data["code"] == 200
    assert login_data["data"]["token"]


@pytest.mark.asyncio
async def test_register_duplicate_username(client):
    payload = {
        "username": "dupuser",
        "password": "Secret123",
        "passwordConfirm": "Secret123",
        "inviteCode": "letter-learning",
        "email": "dupuser@example.com",
    }
    resp1 = await client.post(REGISTER_URL, json=payload)
    assert resp1.json()["code"] == 200

    resp2 = await client.post(REGISTER_URL, json=payload)
    assert resp2.json()["code"] == 400
    assert "用户名已存在" in resp2.json()["msg"]


@pytest.mark.asyncio
async def test_login_invalid_password(client):
    payload = {"username": "admin", "password": "wrong-password"}
    response = await client.post(LOGIN_URL, json=payload)
    data = response.json()
    assert data["code"] == 401


@pytest.mark.asyncio
async def test_user_management_crud(client):
    admin_token = await _login(client)

    headers = {"Authorization": f"Bearer {admin_token}"}

    create_payload = {
        "username": "teacher001",
        "password": "TeacherPass1",
        "email": "teacher001@example.com",
    }
    create_resp = await client.post(USER_EDIT_URL, json=create_payload, headers=headers)
    create_data = create_resp.json()
    assert create_data["code"] == 200
    user_id = create_data["data"]["id"]

    list_resp = await client.get(
        USER_LIST_URL,
        params={"pageNo": 1, "pageSize": 20},
        headers=headers,
    )
    list_data = list_resp.json()
    assert list_data["code"] == 200
    users = list_data["data"]["list"]
    target = next((item for item in users if item["id"] == user_id), None)
    assert target is not None
    assert target is not None

    update_payload = {
        "id": user_id,
        "username": "teacher001",
        "email": "teacher001@example.com",
    }
    update_resp = await client.post(USER_EDIT_URL, json=update_payload, headers=headers)
    update_data = update_resp.json()
    assert update_data["code"] == 200

    post_update = await client.get(
        USER_LIST_URL,
        params={"pageNo": 1, "pageSize": 20},
        headers=headers,
    )
    post_update_data = post_update.json()
    updated_entry = next(
        (item for item in post_update_data["data"]["list"] if item["id"] == user_id),
        None,
    )
    assert updated_entry is not None
    assert updated_entry is not None

    delete_resp = await client.post(
        USER_DELETE_URL,
        json={"ids": str(user_id)},
        headers=headers,
    )
    delete_data = delete_resp.json()
    assert delete_data["code"] == 200

    post_delete = await client.get(
        USER_LIST_URL,
        params={"pageNo": 1, "pageSize": 20},
        headers=headers,
    )
    post_delete_data = post_delete.json()
    ids_after_delete = {item["id"] for item in post_delete_data["data"]["list"]}
    assert user_id not in ids_after_delete


@pytest.mark.asyncio
async def test_profile_endpoints(client):
    register_payload = {
        "username": "centeruser",
        "password": "InitPass123!",
        "passwordConfirm": "InitPass123!",
        "inviteCode": "letter-learning",
        "email": "centeruser@example.com",
    }
    resp = await client.post(REGISTER_URL, json=register_payload)
    assert resp.json()["code"] == 200

    token = resp.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile_resp = await client.get("/profile/me", headers=headers)
    profile_data = profile_resp.json()
    assert profile_data["code"] == 200
    assert profile_data["data"]["user"]["email"] == "centeruser@example.com"

    update_payload = {
        "displayName": "中心用户",
        "realName": "测试用户",
        "gender": 1,
        "signature": "教育改变生活",
        "bio": "擅长单词记忆训练",
    }
    update_resp = await client.put("/profile/me", json=update_payload, headers=headers)
    update_data = update_resp.json()
    assert update_data["code"] == 200
    assert update_data["data"]["user"]["displayName"] == "中心用户"
    assert update_data["data"]["profile"]["realName"] == "测试用户"

    password_payload = {
        "oldPassword": "InitPass123!",
        "newPassword": "NewPass456!",
        "confirmPassword": "NewPass456!",
    }
    password_resp = await client.post(
        "/profile/password", json=password_payload, headers=headers
    )
    assert password_resp.json()["code"] == 200

    login_resp = await client.post(
        LOGIN_URL,
        json={"username": "centeruser", "password": "NewPass456!"},
    )
    login_data = login_resp.json()
    assert login_data["code"] == 200
    new_token = login_data["data"]["token"]
    headers = {"Authorization": f"Bearer {new_token}"}

    files = {"file": ("avatar.png", b"fake image data", "image/png")}
    avatar_resp = await client.post("/profile/avatar", headers=headers, files=files)
    avatar_data = avatar_resp.json()
    assert avatar_data["code"] == 200
    assert avatar_data["data"]["avatarUrl"].startswith("/static/avatars/")

    logs_resp = await client.get("/profile/loginLogs", headers=headers, params={"limit": 5})
    logs_data = logs_resp.json()
    assert logs_data["code"] == 200
    assert len(logs_data["data"]["list"]) >= 1
