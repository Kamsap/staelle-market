"""Ajoute l'administration, le catalogue et les mouvements de stock."""

from alembic import op
import sqlalchemy as sa


revision = "20260818_01"
down_revision = None
branch_labels = None
depends_on = None


def table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def column_names(table: str) -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table)}


def upgrade() -> None:
    existing = table_names()
    if "admin_users" not in existing:
        op.create_table(
            "admin_users",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("full_name", sa.String(100), nullable=False),
            sa.Column("email", sa.String(255), nullable=False),
            sa.Column("password_hash", sa.String(255), nullable=False),
            sa.Column("role", sa.String(30), nullable=False, server_default="manager"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.UniqueConstraint("email"),
        )
        op.create_index("ix_admin_users_email", "admin_users", ["email"], unique=True)

    if "products" not in existing:
        op.create_table(
            "products",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(180), nullable=False),
            sa.Column("slug", sa.String(190), nullable=False),
            sa.Column("brand", sa.String(60), nullable=False),
            sa.Column("category", sa.String(60), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("status", sa.String(20), nullable=False, server_default="active"),
            sa.Column("featured", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.UniqueConstraint("slug"),
        )
        op.create_index("ix_products_slug", "products", ["slug"], unique=True)
        op.create_index("ix_products_status", "products", ["status"])

    if "product_variants" not in existing:
        op.create_table(
            "product_variants",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("sku", sa.String(80), nullable=False),
            sa.Column("size", sa.String(60)),
            sa.Column("color", sa.String(120)),
            sa.Column("selling_price", sa.Integer(), nullable=False),
            sa.Column("compare_at_price", sa.Integer()),
            sa.Column("cost_price", sa.Integer()),
            sa.Column("stock_on_hand", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("stock_reserved", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("low_stock_threshold", sa.Integer(), nullable=False, server_default="2"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
            sa.UniqueConstraint("sku"),
        )
        op.create_index("ix_product_variants_product_id", "product_variants", ["product_id"])
        op.create_index("ix_product_variants_sku", "product_variants", ["sku"], unique=True)

    if "product_images" not in existing:
        op.create_table(
            "product_images",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("path", sa.String(500), nullable=False),
            sa.Column("alt_text", sa.String(180), nullable=False, server_default=""),
            sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
            sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        )

    if "inventory_movements" not in existing:
        op.create_table(
            "inventory_movements",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("variant_id", sa.Integer(), nullable=False),
            sa.Column("admin_user_id", sa.Integer()),
            sa.Column("kind", sa.String(30), nullable=False),
            sa.Column("quantity_delta", sa.Integer(), nullable=False),
            sa.Column("stock_after", sa.Integer(), nullable=False),
            sa.Column("note", sa.String(255), nullable=False, server_default=""),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["variant_id"], ["product_variants.id"]),
            sa.ForeignKeyConstraint(["admin_user_id"], ["admin_users.id"]),
        )
        op.create_index("ix_inventory_movements_variant_id", "inventory_movements", ["variant_id"])

    if "audit_logs" not in existing:
        op.create_table(
            "audit_logs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("admin_user_id", sa.Integer()),
            sa.Column("action", sa.String(80), nullable=False),
            sa.Column("entity_type", sa.String(50), nullable=False),
            sa.Column("entity_id", sa.Integer()),
            sa.Column("details", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["admin_user_id"], ["admin_users.id"]),
        )

    if "orders" in existing and "variant_id" not in column_names("orders"):
        if op.get_bind().dialect.name == "sqlite":
            # SQLite ne sait pas ajouter une contrainte à une table existante.
            # Le mode batch reconstruit proprement la table pour le développement local.
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


def downgrade() -> None:
    existing = table_names()
    if "orders" in existing and "variant_id" in column_names("orders"):
        if op.get_bind().dialect.name == "sqlite":
            with op.batch_alter_table("orders") as batch:
                batch.drop_constraint("fk_orders_variant_id_product_variants", type_="foreignkey")
                batch.drop_column("variant_id")
        else:
            op.drop_constraint("fk_orders_variant_id_product_variants", "orders", type_="foreignkey")
            op.drop_column("orders", "variant_id")
    for table in ["audit_logs", "inventory_movements", "product_images", "product_variants", "products", "admin_users"]:
        if table in table_names():
            op.drop_table(table)
