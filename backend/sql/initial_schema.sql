-- Letter Learning 用户体系基础结构
-- 请在 MySQL 8.x 环境中执行，执行前先选择目标数据库（示例：USE letter_learning;）。

SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 角色表：定义平台角色类型，是 RBAC 的第一层。
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS roles (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    slug VARCHAR(64) NOT NULL COMMENT '角色唯一编码，例如 admin/student/teacher',
    name VARCHAR(128) NOT NULL COMMENT '角色显示名称',
    description VARCHAR(512) NULL,
    is_system TINYINT(1) NOT NULL DEFAULT 1 COMMENT '1=系统内置角色，0=自定义角色',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_roles_slug (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 用户表：保存账号核心信息，后续可拆分扩展资料。
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    username VARCHAR(128) NOT NULL COMMENT '唯一登录名',
    email VARCHAR(255) NULL,
    phone VARCHAR(32) NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NULL,
    avatar_url VARCHAR(512) NULL,
    status TINYINT NOT NULL DEFAULT 1 COMMENT '1=启用，0=禁用',
    last_login_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_username (username),
    UNIQUE KEY uq_users_email (email),
    UNIQUE KEY uq_users_phone (phone),
    KEY idx_users_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 用户角色关联表：支持账号绑定多个角色。
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_roles (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NOT NULL,
    role_id BIGINT UNSIGNED NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_user_roles_user_role (user_id, role_id),
    CONSTRAINT fk_user_roles_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_user_roles_role
        FOREIGN KEY (role_id) REFERENCES roles (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 刷新令牌表：持久化刷新令牌，便于单独撤销。
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NOT NULL,
    token VARCHAR(255) NOT NULL,
    issued_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    revoked_at DATETIME NULL,
    user_agent VARCHAR(512) NULL,
    ip_address VARCHAR(64) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_refresh_tokens_token (token),
    KEY idx_refresh_tokens_user (user_id),
    KEY idx_refresh_tokens_expires (expires_at),
    CONSTRAINT fk_refresh_tokens_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 验证码表：存储邮箱或短信验证码，适用于注册、登录、重置密码、多因子认证等场景。
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS verification_codes (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NULL COMMENT '允许为空，支持注册前的验证流程',
    channel ENUM('email', 'sms') NOT NULL,
    recipient VARCHAR(255) NOT NULL COMMENT '邮箱地址或手机号码',
    code VARCHAR(16) NOT NULL,
    purpose ENUM('register', 'login', 'reset_password', 'mfa') NOT NULL,
    expires_at DATETIME NOT NULL,
    consumed_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_verification_codes_user (user_id),
    KEY idx_verification_codes_recipient (recipient),
    KEY idx_verification_codes_expires (expires_at),
    CONSTRAINT fk_verification_codes_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 密码重置请求表：记录密码重置令牌的生命周期。
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS password_reset_requests (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NOT NULL,
    reset_token VARCHAR(255) NOT NULL,
    expires_at DATETIME NOT NULL,
    used_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_password_reset_requests_token (reset_token),
    KEY idx_password_reset_requests_user (user_id),
    KEY idx_password_reset_requests_expires (expires_at),
    CONSTRAINT fk_password_reset_requests_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 审计日志表：记录与安全相关的关键操作，便于追踪。
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NULL,
    action VARCHAR(128) NOT NULL,
    description VARCHAR(512) NULL,
    ip_address VARCHAR(64) NULL,
    user_agent VARCHAR(512) NULL,
    metadata JSON NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_audit_logs_user (user_id),
    KEY idx_audit_logs_action (action),
    CONSTRAINT fk_audit_logs_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 预置系统角色。
-- ---------------------------------------------------------------------------
INSERT INTO roles (slug, name, description, is_system)
VALUES
    ('admin', '管理员', '平台超级管理员', 1),
    ('teacher', '教师', '教师权限', 1),
    ('student', '学生', '学生权限', 1)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    description = VALUES(description);

-- ---------------------------------------------------------------------------
-- 创建默认管理员账号。密码哈希对应 bcrypt('admin123')。
-- 如需重新生成哈希，可执行：python - <<'PY'\nfrom passlib.hash import bcrypt\nprint(bcrypt.hash('admin123'))\nPY
-- ---------------------------------------------------------------------------
INSERT INTO users (
    username,
    email,
    password_hash,
    display_name,
    status
) VALUES (
    'admin',
    'admin@example.com',
    '$2b$12$2xBrVSusozhv6nEokxiYWuul3Sfrfv5nl2QKqKgvgUch55zglPDnW',
    '系统管理员',
    1
) ON DUPLICATE KEY UPDATE
    password_hash = VALUES(password_hash),
    status = VALUES(status);

-- ---------------------------------------------------------------------------
-- 绑定管理员账号到管理员角色。
-- ---------------------------------------------------------------------------
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id
FROM users u
JOIN roles r ON r.slug = 'admin'
WHERE u.username = 'admin'
ON DUPLICATE KEY UPDATE role_id = role_id;
