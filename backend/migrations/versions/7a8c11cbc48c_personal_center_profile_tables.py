"""personal center profile tables

Revision ID: 7a8c11cbc48c
Revises: 1bbf83c969d8
Create Date: 2025-11-06 16:13:58.184204

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql


def bigint():
    base = sa.BigInteger()
    base = base.with_variant(sa.Integer(), "sqlite")
    base = base.with_variant(mysql.BIGINT(unsigned=True), "mysql")
    return base


# revision identifiers, used by Alembic.
revision = '7a8c11cbc48c'
down_revision = '1bbf83c969d8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    added_gender = False

    if "gender" not in user_columns:
        op.add_column(
            'users',
            sa.Column(
                'gender',
                sa.SmallInteger(),
                nullable=False,
                server_default='0',
                comment='0=未知,1=男,2=女',
            ),
        )
        added_gender = True
    if "birthday" not in user_columns:
        op.add_column('users', sa.Column('birthday', sa.Date(), nullable=True, comment='生日'))
    if "locale" not in user_columns:
        op.add_column('users', sa.Column('locale', sa.String(length=16), nullable=True, comment='语言偏好'))
    if "timezone" not in user_columns:
        op.add_column('users', sa.Column('timezone', sa.String(length=64), nullable=True, comment='时区'))
    if "signature" not in user_columns:
        op.add_column('users', sa.Column('signature', sa.String(length=255), nullable=True, comment='个性签名'))
    if "password_updated_at" not in user_columns:
        op.add_column(
            'users',
            sa.Column(
                'password_updated_at',
                sa.DateTime(),
                nullable=True,
                comment='最后一次密码修改时间',
            ),
        )

    existing_tables = set(inspector.get_table_names())

    if "user_profiles" not in existing_tables:
        op.create_table(
            'user_profiles',
            sa.Column(
                'user_id',
                bigint(),
                nullable=False,
                comment='用户主键',
            ),
            sa.Column('real_name', sa.String(length=128), nullable=True, comment='真实姓名'),
            sa.Column('id_number', sa.String(length=64), nullable=True, comment='证件号/学号'),
            sa.Column('address', sa.String(length=255), nullable=True, comment='联系地址'),
            sa.Column('wechat', sa.String(length=64), nullable=True, comment='微信'),
            sa.Column('qq', sa.String(length=64), nullable=True, comment='QQ'),
            sa.Column('linkedin', sa.String(length=128), nullable=True, comment='LinkedIn'),
            sa.Column('website', sa.String(length=255), nullable=True, comment='个人主页'),
            sa.Column('bio', sa.Text(), nullable=True, comment='个人简介'),
            sa.Column(
                'created_at',
                sa.DateTime(),
                nullable=False,
                server_default=sa.text('CURRENT_TIMESTAMP'),
                comment='创建时间',
            ),
            sa.Column(
                'updated_at',
                sa.DateTime(),
                nullable=False,
                server_default=sa.text('CURRENT_TIMESTAMP'),
                comment='更新时间',
                server_onupdate=sa.text('CURRENT_TIMESTAMP'),
            ),
            sa.PrimaryKeyConstraint('user_id'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        )

    if "user_password_history" not in existing_tables:
        op.create_table(
            'user_password_history',
            sa.Column('id', bigint(), primary_key=True, autoincrement=True, comment='主键'),
            sa.Column('user_id', bigint(), nullable=False, comment='用户主键'),
            sa.Column('password_hash', sa.String(length=255), nullable=False, comment='密码哈希'),
            sa.Column(
                'changed_at',
                sa.DateTime(),
                nullable=False,
                server_default=sa.text('CURRENT_TIMESTAMP'),
                comment='修改时间',
            ),
            sa.Column('changed_by', bigint(), nullable=True, comment='操作者'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['changed_by'], ['users.id'], ondelete='SET NULL'),
            sa.Index('idx_user_password_history_user', 'user_id'),
        )

    if "user_login_logs" not in existing_tables:
        op.create_table(
            'user_login_logs',
            sa.Column('id', bigint(), primary_key=True, autoincrement=True, comment='主键'),
            sa.Column('user_id', bigint(), nullable=False, comment='用户主键'),
            sa.Column(
                'login_at',
                sa.DateTime(),
                nullable=False,
                server_default=sa.text('CURRENT_TIMESTAMP'),
                comment='登录时间',
            ),
            sa.Column('ip_address', sa.String(length=64), nullable=True, comment='IP 地址'),
            sa.Column('user_agent', sa.String(length=512), nullable=True, comment='User-Agent'),
            sa.Column('device_name', sa.String(length=128), nullable=True, comment='设备'),
            sa.Column('location', sa.String(length=128), nullable=True, comment='地理位置'),
            sa.Column(
                'successful',
                sa.SmallInteger(),
                nullable=False,
                server_default='1',
                comment='是否登录成功 1=是 0=否',
            ),
            sa.Column('token_id', sa.String(length=255), nullable=True, comment='关联的刷新令牌ID'),
            sa.Column('logout_at', sa.DateTime(), nullable=True, comment='登出时间'),
            sa.Column(
                'created_at',
                sa.DateTime(),
                nullable=False,
                server_default=sa.text('CURRENT_TIMESTAMP'),
                comment='记录时间',
            ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.Index('idx_user_login_logs_user', 'user_id'),
        )

    if added_gender:
        op.alter_column('users', 'gender', server_default=None)


def downgrade() -> None:
    op.drop_table('user_login_logs')
    op.drop_table('user_password_history')
    op.drop_table('user_profiles')

    op.drop_column('users', 'password_updated_at')
    op.drop_column('users', 'signature')
    op.drop_column('users', 'timezone')
    op.drop_column('users', 'locale')
    op.drop_column('users', 'birthday')
    op.drop_column('users', 'gender')
