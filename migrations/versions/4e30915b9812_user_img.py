"""user img

Revision ID: 4e30915b9812
Revises: ed8c85b10f5
Create Date: 2015-10-05 12:09:58.421250

"""

# revision identifiers, used by Alembic.
revision = '4e30915b9812'
down_revision = 'ed8c85b10f5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('avatar_hash', sa.String(length=32), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'avatar_hash')
    ### end Alembic commands ###