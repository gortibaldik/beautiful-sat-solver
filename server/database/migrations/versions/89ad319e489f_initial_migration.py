"""initial_migration

Revision ID: 89ad319e489f
Revises: bc1230848d4f
Create Date: 2022-08-26 19:22:59.673849

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '89ad319e489f'
down_revision = 'bc1230848d4f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sat_jobs', sa.Column('Max Learned Clauses', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sat_jobs', 'Max Learned Clauses')
    # ### end Alembic commands ###