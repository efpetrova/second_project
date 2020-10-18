"""empty message

Revision ID: c2cdea5a4695
Revises: 8e4be3407664
Create Date: 2020-10-18 19:17:04.518930

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2cdea5a4695'
down_revision = '8e4be3407664'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bookings', sa.Column('teacher_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'bookings', 'teachers', ['teacher_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'bookings', type_='foreignkey')
    op.drop_column('bookings', 'teacher_id')
    # ### end Alembic commands ###