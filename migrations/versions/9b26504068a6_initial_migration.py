"""initial migration

Revision ID: 9b26504068a6
Revises: d1ff4b490406
Create Date: 2024-06-27 14:29:57.440667

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b26504068a6'
down_revision: Union[str, None] = 'd1ff4b490406'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('authenticationtoken')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('authenticationtoken',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('token', sa.VARCHAR(length=6), autoincrement=False, nullable=True),
    sa.Column('token_expiry', sa.DATE(), autoincrement=False, nullable=True),
    sa.Column('token_type', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='authenticationtoken_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='authenticationtoken_pkey')
    )
    # ### end Alembic commands ###
