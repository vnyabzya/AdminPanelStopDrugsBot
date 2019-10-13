"""empty message

Revision ID: e8baa2a6e51a
Revises: a8e15ccd3aa5
Create Date: 2019-09-13 03:00:13.973918

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8baa2a6e51a'
down_revision = 'a8e15ccd3aa5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('objects_estimated_value_status_of_the_report_id_type_object_key', 'objects', type_='unique')
    op.create_unique_constraint(None, 'objects', ['estimated_value', 'region_id', 'status_of_the_report_id', 'type_object_id', 'category_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'objects', type_='unique')
    op.create_unique_constraint('objects_estimated_value_status_of_the_report_id_type_object_key', 'objects', ['estimated_value', 'status_of_the_report_id', 'type_object_id', 'category_id'])
    # ### end Alembic commands ###
