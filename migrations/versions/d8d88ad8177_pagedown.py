"""pagedown

Revision ID: d8d88ad8177
Revises: 44d841372bc9
Create Date: 2015-10-14 10:32:22.022358

"""

# revision identifiers, used by Alembic.
revision = 'd8d88ad8177'
down_revision = '44d841372bc9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('body_html', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'body_html')
    ### end Alembic commands ###
