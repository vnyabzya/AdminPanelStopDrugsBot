"""empty message

Revision ID: 418404d117a7
Revises: d616f6d6a24e
Create Date: 2019-10-13 00:03:58.236582

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '418404d117a7'
down_revision = 'd616f6d6a24e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('regions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('regions__telegram_shops',
    sa.Column('regions_id', sa.Integer(), nullable=True),
    sa.Column('telegram_shops_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['regions_id'], ['regions.id'], ),
    sa.ForeignKeyConstraint(['telegram_shops_id'], ['telegram_shops.id'], ),
    sa.UniqueConstraint('regions_id', 'telegram_shops_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('regions__telegram_shops')
    op.drop_table('regions')
    # ### end Alembic commands ###
