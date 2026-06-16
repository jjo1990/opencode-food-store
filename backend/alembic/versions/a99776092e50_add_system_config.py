"""add_system_config

Revision ID: a99776092e50
Revises: 34a1e2321620
Create Date: 2026-06-16 20:14:20.178721

"""

from collections.abc import Sequence
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import column, table

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a99776092e50"
down_revision: str | Sequence[str] | None = "34a1e2321620"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "system_config",
        sa.Column("clave", sa.String(length=100), nullable=False),
        sa.Column("valor", sa.String(length=500), nullable=False),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["updated_by"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("clave"),
    )

    now = datetime.utcnow()
    system_config = table(
        "system_config",
        column("clave", sa.String),
        column("valor", sa.String),
        column("updated_by", sa.UUID),
        column("updated_at", sa.DateTime),
    )
    op.bulk_insert(
        system_config,
        [
            {"clave": "horario_apertura", "valor": "08:00", "updated_by": None, "updated_at": now},
            {"clave": "horario_cierre", "valor": "22:00", "updated_by": None, "updated_at": now},
            {
                "clave": "zona_entrega",
                "valor": '{"lat": -34.6037, "lng": -58.3816, "radio_km": 5}',
                "updated_by": None,
                "updated_at": now,
            },
            {"clave": "costo_envio", "valor": "150.00", "updated_by": None, "updated_at": now},
            {
                "clave": "mensaje_bienvenida",
                "valor": "¡Bienvenido a Food Store!",
                "updated_by": None,
                "updated_at": now,
            },
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("system_config")
