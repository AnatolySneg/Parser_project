"""Currency table - removed (dimensions=30) option from requested_banks ARRAY object

Revision ID: 81532cafb027
Revises: 2c354c71fd2a
Create Date: 2023-11-01 15:38:24.729170

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '81532cafb027'
down_revision: Union[str, None] = '2c354c71fd2a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###