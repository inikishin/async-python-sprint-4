"""initial_migrate

Revision ID: f4e11d11f5d6
Revises: 
Create Date: 2023-03-24 11:04:41.695072

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f4e11d11f5d6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('link',
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('link', sa.String(), nullable=False),
    sa.Column('short_link', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('short_link')
    )
    op.create_index(op.f('ix_link_created_at'), 'link', ['created_at'], unique=False)
    op.create_index(op.f('ix_link_is_deleted'), 'link', ['is_deleted'], unique=False)
    op.create_table('link_click',
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('link_id', postgresql.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('client', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['link_id'], ['link.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_link_click_created_at'), 'link_click', ['created_at'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_link_click_created_at'), table_name='link_click')
    op.drop_table('link_click')
    op.drop_index(op.f('ix_link_is_deleted'), table_name='link')
    op.drop_index(op.f('ix_link_created_at'), table_name='link')
    op.drop_table('link')
    # ### end Alembic commands ###
