"""empty message

Revision ID: 6e2656ef034b
Revises: f8f949ce4522
Create Date: 2019-11-26 11:05:54.376467

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6e2656ef034b'
down_revision = 'f8f949ce4522'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('tickettypes_name_key', 'tickettypes', type_='unique')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('tickettypes_name_key', 'tickettypes', ['name'])
    # ### end Alembic commands ###
