"""jobs_migration

Revision ID: ce6d06002fbb
Revises: 
Create Date: 2022-06-27 22:38:37.683172

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce6d06002fbb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sat_job',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('unit_prop_vals', sa.Float(), nullable=True),
    sa.Column('decision_vars', sa.Float(), nullable=True),
    sa.Column('time', sa.Float(), nullable=True),
    sa.Column('algorithm', sa.String(length=32), nullable=True),
    sa.Column('benchmark', sa.String(length=32), nullable=True),
    sa.Column('log_file', sa.String(length=128), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sat_job')
    # ### end Alembic commands ###