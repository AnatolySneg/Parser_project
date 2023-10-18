"""changed some user columns options (phone_number to (nullable=True)),(user_status_id to (nullable=False and default = 1))

Revision ID: 7f4361d919c3
Revises: 03ae430b2ac4
Create Date: 2023-10-18 19:03:08.696276

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f4361d919c3'
down_revision: Union[str, None] = '03ae430b2ac4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'phone_number',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('user', 'user_status_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'user_status_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('user', 'phone_number',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
