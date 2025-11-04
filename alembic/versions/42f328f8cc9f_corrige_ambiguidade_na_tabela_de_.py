"""Corrige ambiguidade na tabela de relacao de categorias de produtos.

Revision ID: 42f328f8cc9f
Revises: 4d9a55827b32
Create Date: 2025-11-04 15:30:47.344301

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42f328f8cc9f'
down_revision: Union[str, Sequence[str], None] = '4d9a55827b32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



TABLE = "produtos_categorias_relacao"
REF_TABLE = "produtos_categorias"
FK_PAI_NAME = "fk_prod_cat_rel_pai"
FK_FILHO_NAME = "fk_prod_cat_rel_filho"
UQ_FILHO_NAME = "uq_prod_cat_rel_id_categoria_filho"


def _drop_fk_if_exists(bind, table: str, fk_name: str) -> None:
    insp = sa.inspect(bind)
    for fk in insp.get_foreign_keys(table):
        if fk.get("name") == fk_name:
            op.drop_constraint(fk_name, table, type_="foreignkey")
            break


def _drop_fks_pointing_to_ref(bind) -> None:
    """
    Remove quaisquer FKs em TABLE -> REF_TABLE para as colunas alvo,
    independentemente do nome (caso já exista com nome automático).
    """
    insp = sa.inspect(bind)
    fks = insp.get_foreign_keys(TABLE)
    for fk in fks:
        if (
            fk.get("referred_table") == REF_TABLE
            and set(fk.get("constrained_columns", []))
            in ({"id_categoria_pai"}, {"id_categoria_filho"})
        ):
            if fk.get("name"):
                op.drop_constraint(fk["name"], TABLE, type_="foreignkey")


def _create_unique_if_missing(bind) -> None:
    insp = sa.inspect(bind)
    existing_uq_names = {uq.get("name") for uq in insp.get_unique_constraints(TABLE)}
    if UQ_FILHO_NAME not in existing_uq_names:
        op.create_unique_constraint(UQ_FILHO_NAME, TABLE, ["id_categoria_filho"])


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()

    # 1) Derruba FKs existentes (nomes conhecidos e/ou automáticos)
    _drop_fk_if_exists(bind, TABLE, FK_PAI_NAME)
    _drop_fk_if_exists(bind, TABLE, FK_FILHO_NAME)
    _drop_fks_pointing_to_ref(bind)

    # 2) Recria FKs com nomes explícitos
    op.create_foreign_key(
        FK_PAI_NAME,
        TABLE,
        REF_TABLE,
        ["id_categoria_pai"],
        ["id_bling"],
        onupdate=None,
        ondelete=None,
    )
    op.create_foreign_key(
        FK_FILHO_NAME,
        TABLE,
        REF_TABLE,
        ["id_categoria_filho"],
        ["id_bling"],
        onupdate=None,
        ondelete=None,
    )

    # 3) Garante UNIQUE(id_categoria_filho)
    _create_unique_if_missing(bind)


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()

    # Reverte UNIQUE
    insp = sa.inspect(bind)
    existing_uq_names = {uq.get("name") for uq in insp.get_unique_constraints(TABLE)}
    if UQ_FILHO_NAME in existing_uq_names:
        op.drop_constraint(UQ_FILHO_NAME, TABLE, type_="unique")

    # Derruba FKs nomeadas
    _drop_fk_if_exists(bind, TABLE, FK_PAI_NAME)
    _drop_fk_if_exists(bind, TABLE, FK_FILHO_NAME)

    # Opcional: recriar FKs "genéricas" (sem nome fixo) — se preferir, pode omitir
    op.create_foreign_key(
        None,  # deixa o backend/naming_convention nomear
        TABLE,
        REF_TABLE,
        ["id_categoria_pai"],
        ["id_bling"],
    )
    op.create_foreign_key(
        None,
        TABLE,
        REF_TABLE,
        ["id_categoria_filho"],
        ["id_bling"],
    )
