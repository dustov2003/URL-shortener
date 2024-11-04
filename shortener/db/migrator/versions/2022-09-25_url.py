"""Table for urls

Revision ID: 4acb92a8f909
Revises: 
Create Date: 2022-09-25 15:43:25.973097

"""

from datetime import timedelta

import sqlalchemy as sa
from alembic import op
from sqlalchemy import func
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "4acb92a8f909"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "url_storage",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("long_url", sa.TEXT(), nullable=False),
        sa.Column("short_url", sa.TEXT(), nullable=False),
        sa.Column(
            "secret_key", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=True
        ),
        sa.Column("number_of_clicks", sa.INTEGER(), server_default=sa.text("0"), nullable=False),
        sa.Column("dt_created", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column(
            "dt_deleted",
            postgresql.TIMESTAMP(timezone=True),
            server_default=func.now() + timedelta(days=1),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__url_storage")),
        sa.UniqueConstraint("id", name=op.f("uq__url_storage__id")),
    )
    op.create_index(op.f("ix__url_storage__long_url"), "url_storage", ["long_url"], unique=False)
    op.create_index(op.f("ix__url_storage__secret_key"), "url_storage", ["secret_key"], unique=True)
    op.create_index(op.f("ix__url_storage__short_url"), "url_storage", ["short_url"], unique=True)
    op.create_unique_constraint(op.f("uq__url_storage__id"), "url_storage", ["id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f("uq__url_storage__id"), "url_storage", type_="unique")
    op.drop_index(op.f("ix__url_storage__short_url"), table_name="url_storage")
    op.drop_index(op.f("ix__url_storage__secret_key"), table_name="url_storage")
    op.drop_index(op.f("ix__url_storage__long_url"), table_name="url_storage")
    op.drop_table("url_storage")
    # ### end Alembic commands ###
