"""create_otp_table

Revision ID: 5b12166ccc41
Revises: 30f219097c5d
Create Date: 2024-12-12 02:08:33.047467

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b12166ccc41'
down_revision: Union[str, None] = '30f219097c5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create otps table
    op.create_table(
        'otps',
        sa.Column('id', sa.String(length=12), nullable=False),
        sa.Column('user_id', sa.String(12), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on user_id
    op.create_index(op.f('ix_otps_user_id'), 'otps', ['user_id'])


def downgrade():
    # Drop index
    op.drop_index(op.f('ix_otps_user_id'), table_name='otps')
    
    # Drop otps table
    op.drop_table('otps')