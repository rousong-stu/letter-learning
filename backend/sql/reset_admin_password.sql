-- 重置管理员账号密码，将密码设置为 admin123。
-- 请在执行前确认使用的数据库为 letter_learning。

UPDATE users
SET password_hash = '$2b$12$/Znhr8AkcELjhN93NxxwkuBfLlVrcnUjT/X.Cj2uMxpCJPDKiB17u'
WHERE username = 'admin';
