"""empty message

Revision ID: e1e7eb601b14
Revises: 
Create Date: 2019-09-12 22:50:53.683406

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1e7eb601b14'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('category')
    )
    op.create_table('cites',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('city', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('city')
    )
    op.create_table('object_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('type')
    )
    op.create_table('regions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('region', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('region')
    )
    op.create_table('report_status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('status')
    )
    op.create_table('settlement_areas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('settlement_area', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('settlement_area')
    )
    op.create_table('street_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('type')
    )
    op.create_table('streets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('street', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('street')
    )
    op.create_table('objects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('estimated_value', sa.String(), nullable=True),
    sa.Column('status_of_the_report_id', sa.Integer(), nullable=True),
    sa.Column('type_object_id', sa.Integer(), nullable=True),
    sa.Column('city_id', sa.Integer(), nullable=True),
    sa.Column('region_id', sa.Integer(), nullable=True),
    sa.Column('street_type_id', sa.Integer(), nullable=True),
    sa.Column('street_id', sa.Integer(), nullable=True),
    sa.Column('settlement_area_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['city_id'], ['cites.id'], ),
    sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ),
    sa.ForeignKeyConstraint(['settlement_area_id'], ['settlement_areas.id'], ),
    sa.ForeignKeyConstraint(['status_of_the_report_id'], ['report_status.id'], ),
    sa.ForeignKeyConstraint(['street_id'], ['streets.id'], ),
    sa.ForeignKeyConstraint(['street_type_id'], ['street_types.id'], ),
    sa.ForeignKeyConstraint(['type_object_id'], ['object_types.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('objects')
    op.drop_table('streets')
    op.drop_table('street_types')
    op.drop_table('settlement_areas')
    op.drop_table('report_status')
    op.drop_table('regions')
    op.drop_table('object_types')
    op.drop_table('cites')
    op.drop_table('categories')
    # ### end Alembic commands ###