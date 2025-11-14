-- Letter Learning 用户体系基础结构（精简版）
-- 在 MySQL 8.x 环境中执行，执行前请切换到目标数据库（示例：USE letter_learning;）。

SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 用户表：保存账号核心信息。
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
    username VARCHAR(128) NOT NULL COMMENT '唯一登录名',
    email VARCHAR(255) NULL COMMENT '邮箱',
    phone VARCHAR(32) NULL COMMENT '手机号',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    display_name VARCHAR(255) NULL COMMENT '展示名称',
    avatar_url VARCHAR(512) NULL COMMENT '头像地址',
    gender TINYINT NOT NULL DEFAULT 0 COMMENT '0=未知,1=男,2=女',
    birthday DATE NULL COMMENT '生日',
    locale VARCHAR(16) NULL COMMENT '语言偏好',
    timezone VARCHAR(64) NULL COMMENT '时区',
    signature VARCHAR(255) NULL COMMENT '个性签名',
    password_updated_at DATETIME NULL COMMENT '最后一次密码修改时间',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '1=启用，0=禁用',
    last_login_at DATETIME NULL COMMENT '最近登录',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_username (username),
    UNIQUE KEY uq_users_email (email),
    UNIQUE KEY uq_users_phone (phone),
    KEY idx_users_status (status)
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
-- 用户资料表：保存扩展信息（个人中心使用）。
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户主键',
    real_name VARCHAR(128) NULL COMMENT '真实姓名',
    id_number VARCHAR(64) NULL COMMENT '证件号/学号',
    address VARCHAR(255) NULL COMMENT '联系地址',
    wechat VARCHAR(64) NULL COMMENT '微信',
    qq VARCHAR(64) NULL COMMENT 'QQ',
    linkedin VARCHAR(128) NULL COMMENT 'LinkedIn',
    website VARCHAR(255) NULL COMMENT '个人主页',
    bio TEXT NULL COMMENT '简介',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    CONSTRAINT fk_user_profiles_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 密码历史：记录密码变更，用于安全审计。
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_password_history (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    changed_by BIGINT UNSIGNED NULL COMMENT '操作者',
    PRIMARY KEY (id),
    KEY idx_password_history_user (user_id),
    CONSTRAINT fk_password_history_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_password_history_changed_by
        FOREIGN KEY (changed_by) REFERENCES users (id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 登录日志：个人中心查询最近登录记录。
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_login_logs (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NOT NULL,
    login_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(64) NULL,
    user_agent VARCHAR(512) NULL,
    device_name VARCHAR(128) NULL,
    location VARCHAR(128) NULL,
    successful TINYINT NOT NULL DEFAULT 1,
    token_id VARCHAR(255) NULL,
    logout_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_login_logs_user (user_id),
    CONSTRAINT fk_login_logs_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- AI 词汇短文：记录每日生成的短文。
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS word_stories (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NOT NULL,
    story_date DATE NOT NULL,
    generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    words JSON NOT NULL COMMENT '词汇数组',
    story_text TEXT NOT NULL COMMENT 'AI 生成短文',
    story_tokens INT NULL COMMENT 'token 消耗',
    model_name VARCHAR(128) NULL COMMENT '模型/智能体',
    status VARCHAR(32) NOT NULL DEFAULT 'success',
    extra JSON NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_word_stories_user_story_date (user_id, story_date),
    KEY idx_word_stories_user_id (user_id),
    KEY idx_word_stories_story_date (story_date),
    CONSTRAINT fk_word_stories_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 创建默认管理员账号。密码哈希对应 bcrypt('admin123')。
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
