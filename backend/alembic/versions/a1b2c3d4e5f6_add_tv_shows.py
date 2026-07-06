"""add tv shows

Revision ID: a1b2c3d4e5f6
Revises: d99f3fd6dad6
Create Date: 2026-07-06 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'd99f3fd6dad6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('tv_shows',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('first_air_date', sa.Date(), nullable=True),
    sa.Column('number_of_seasons', sa.Integer(), nullable=True),
    sa.Column('number_of_episodes', sa.Integer(), nullable=True),
    sa.Column('vote_average', sa.Numeric(precision=3, scale=1), nullable=True),
    sa.Column('popularity', sa.Float(), nullable=True),
    sa.Column('poster_path', sa.String(length=300), nullable=True),
    sa.Column('backdrop_path', sa.String(length=300), nullable=True),
    sa.Column('overview', sa.String(), nullable=True),
    sa.Column('raw', sa.JSON(), nullable=False),
    sa.Column('synced_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tv_show_genres',
    sa.Column('tv_show_id', sa.Integer(), nullable=False),
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['genre_id'], ['genres.id'], ),
    sa.ForeignKeyConstraint(['tv_show_id'], ['tv_shows.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tv_show_id', 'genre_id')
    )
    op.create_table('tv_show_credits',
    sa.Column('tv_show_id', sa.Integer(), nullable=False),
    sa.Column('person_id', sa.Integer(), nullable=False),
    sa.Column('credit_type', sa.String(length=10), nullable=False),
    sa.Column('job', sa.String(length=80), nullable=False),
    sa.Column('character', sa.String(length=255), nullable=True),
    sa.Column('cast_order', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['tv_show_id'], ['tv_shows.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['person_id'], ['people.id'], ),
    sa.PrimaryKeyConstraint('tv_show_id', 'person_id', 'credit_type', 'job')
    )


def downgrade() -> None:
    op.drop_table('tv_show_credits')
    op.drop_table('tv_show_genres')
    op.drop_table('tv_shows')
