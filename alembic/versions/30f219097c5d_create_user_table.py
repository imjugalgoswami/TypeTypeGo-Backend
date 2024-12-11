"""create_user_table

Revision ID: 30f219097c5d
Revises: 
Create Date: 2024-12-12 01:59:14.771863

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '30f219097c5d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create UserRole enum type if it doesn't exist
    connection = op.get_bind()
    
    # Check if enum exists using PostgreSQL's system catalog
    result = connection.execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole')")
    ).scalar()
    
    if not result:
        # Create enum only if it doesn't exist
        connection.execute(sa.text("CREATE TYPE userrole AS ENUM ('USER', 'ADMIN')"))
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=12), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', postgresql.ENUM('USER', 'ADMIN', name='userrole', create_type=False), nullable=False, server_default='USER'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verify', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notification_preferences', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.utcnow()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,default=sa.func.utcnow()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Create indexes
    op.create_index(op.f('ix_users_phone_number'), 'users', ['phone_number'], unique=True)
    op.create_unique_constraint('uq_users_email', 'users', ['email'])


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_users_phone_number'), table_name='users')
    op.drop_constraint('uq_users_email', 'users', type_='unique')
    
    # Drop users table
    op.drop_table('users')
    
    # Drop UserRole enum type using the same check
    connection = op.get_bind()
    result = connection.execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole')")
    ).scalar()
    
    if result:
        connection.execute(sa.text("DROP TYPE userrole"))