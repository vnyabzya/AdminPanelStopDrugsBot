"""empty message

Revision ID: 2f7434df2918
Revises: 14fe46262708
Create Date: 2019-09-13 01:40:38.680556

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2f7434df2918'
down_revision = '14fe46262708'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('objects_status_of_the_report_id_type_object_id_city_id_regi_key', 'objects', type_='unique')
    op.create_unique_constraint(None, 'objects', ['status_of_the_report_id', 'type_object_id', 'city_id', 'region_id', 'street_type_id', 'street_id', 'category_id'])
    op.drop_constraint('objects_settlement_area_id_fkey', 'objects', type_='foreignkey')
    op.drop_column('objects', 'settlement_area_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('objects', sa.Column('settlement_area_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('objects_settlement_area_id_fkey', 'objects', 'settlement_areas', ['settlement_area_id'], ['id'])
    op.drop_constraint(None, 'objects', type_='unique')
    op.create_unique_constraint('objects_status_of_the_report_id_type_object_id_city_id_regi_key', 'objects', ['status_of_the_report_id', 'type_object_id', 'city_id', 'region_id', 'street_type_id', 'street_id', 'settlement_area_id', 'category_id'])
    # ### end Alembic commands ###