"""initial migration

Revision ID: d1ff4b490406
Revises: 0711dfeddb3d
Create Date: 2024-06-27 14:23:47.343032

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1ff4b490406'
down_revision: Union[str, None] = '0711dfeddb3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('authenticationtoken',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=6), nullable=True),
    sa.Column('token_expiry', sa.Date(), nullable=True),
    sa.Column('token_type', sa.String(length=20), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('authenticationtoken')
    # ### end Alembic commands ###
