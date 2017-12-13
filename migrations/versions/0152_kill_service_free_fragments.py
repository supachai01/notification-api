"""

Revision ID: 0152_kill_service_free_fragments
Revises: 0151_refactor_letter_rates
Create Date: 2017-12-01 16:49:51.178455

"""
from alembic import op
import sqlalchemy as sa

revision = '0152_kill_service_free_fragments'
down_revision = '0151_refactor_letter_rates'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('services', 'free_sms_fragment_limit')
    op.drop_column('services_history', 'free_sms_fragment_limit')


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('services_history', sa.Column('free_sms_fragment_limit', sa.BIGINT(), autoincrement=False, nullable=True))
    op.add_column('services', sa.Column('free_sms_fragment_limit', sa.BIGINT(), autoincrement=False, nullable=True))
