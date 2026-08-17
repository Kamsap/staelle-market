"""Ajoute les tables cœur nécessaires aux comptes et aux commandes.

La première migration d'administration conservait volontairement les anciennes
tables lorsqu'elles existaient déjà. Sur une base MariaDB neuve, ces tables
n'étaient toutefois pas encore présentes, ce qui empêchait le tableau de bord
administratif de calculer les commandes en attente.
"""

from alembic import op
import sqlalchemy as sa


revision = "20260818_02"
down_revision = "20260818_01"
branch_labels = None
depends_on = None


def table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def column_names(table: str) -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table)}


def upgrade() -> None:
    existing = table_names()

    if "customers" not in existing:
        op.create_table(
            "customers",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("full_name", sa.String(100), nullable=False),
            sa.Column("email", sa.String(255), nullable=False),
            sa.Column("phone", sa.String(30), nullable=False),
            sa.Column("password_hash", sa.String(255), nullable=False),
            sa.Column("points", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.UniqueConstraint("email"),
        )
        op.create_index("ix_customers_email", "customers", ["email"], unique=True)

    if "orders" not in existing:
        op.create_table(
            "orders",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("reference", sa.String(40), nullable=False),
            sa.Column("customer_id", sa.Integer(), nullable=True),
            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("variant_id", sa.Integer(), nullable=True),
            sa.Column("product_name", sa.String(180), nullable=False),
            sa.Column("displayed_price", sa.Integer(), nullable=False),
            sa.Column("amount_paid", sa.Integer(), nullable=True),
            sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
            sa.Column("points_earned", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
            sa.ForeignKeyConstraint(["variant_id"], ["product_variants.id"]),
            sa.UniqueConstraint("reference"),
        )
        op.create_index("ix_orders_reference", "orders", ["reference"], unique=True)
    elif "variant_id" not in column_names("orders"):
        if op.get_bind().dialect.name == "sqlite":
            with op.batch_alter_table("orders") as batch:
                batch.add_column(sa.Column("variant_id", sa.Integer(), nullable=True))
                batch.create_foreign_key(
                    "fk_orders_variant_id_product_variants",
                    "product_variants",
                    ["variant_id"],
                    ["id"],
                )
        else:
            op.add_column("orders", sa.Column("variant_id", sa.Integer(), nullable=True))
            op.create_foreign_key(
                "fk_orders_variant_id_product_variants",
                "orders",
                "product_variants",
                ["variant_id"],
                ["id"],
            )

    if "loyalty_entries" not in existing:
        op.create_table(
            "loyalty_entries",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("customer_id", sa.Integer(), nullable=False),
            sa.Column("order_id", sa.Integer(), nullable=False),
            sa.Column("points", sa.Integer(), nullable=False),
            sa.Column("reason", sa.String(180), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
            sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
            sa.UniqueConstraint("order_id"),
        )


def downgrade() -> None:
    # Cette migration peut adopter des tables historiques déjà remplies. Un
    # downgrade automatique risquerait donc de supprimer des comptes et des
    # commandes qui ne lui appartiennent pas. Le retour arrière reste
    # volontairement non destructif.
    pass
