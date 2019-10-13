"""empty message

Revision ID: d6885125121a
Revises: 49cc085ef589
Create Date: 2019-09-23 10:50:07.789352

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6885125121a'
down_revision = '49cc085ef589'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('admins', sa.Column('rule', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'admins', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'admins', type_='unique')
    op.drop_column('admins', 'rule')
    # ### end Alembic commands ###