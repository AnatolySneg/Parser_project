"""Changed table name to 'currency'

Revision ID: c8d54feb92d2
Revises: d318e3b17154
Create Date: 2023-10-30 12:34:17.581502

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c8d54feb92d2'
down_revision: Union[str, None] = 'd318e3b17154'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('currency',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('request_date', sa.TIMESTAMP(), nullable=True),
    sa.Column('requested_banks', sa.ARRAY(sa.String(), dimensions=30), nullable=True),
    sa.Column('request_source', sa.String(length=50), nullable=True),
    sa.Column('currency_data', sa.JSON(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.drop_table('currency_requests')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('currency_requests',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('request_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('requested_banks', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=True),
    sa.Column('request_source', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('currency_data', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='currency_requests_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='currency_requests_pkey')
    )
    op.drop_table('currency')
    # ### end Alembic commands ###