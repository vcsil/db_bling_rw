#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 19 14:53:59 2025.

@author: vcsil

gera_modelos.py
Executa o dump SQL e extrai classes ORM (SQLAlchemy ≥2.0).

pip install sqlalchemy psycopg[binary]
"""

from __future__ import annotations

import re
from pathlib import Path
from sqlalchemy import create_engine, text, inspect, MetaData, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.exc import ProgrammingError
from urllib.parse import quote_plus

# 1. CONFIGURAÇÕES ---------------------------------------------------------
raw_pwd = 'mi%40Senha%3A123'          # exemplo contendo @ e :
safe_pwd = quote_plus(raw_pwd)    # → 'mi%40Senha%3A123'

DB_URL = f"postgresql+psycopg://postgres:{safe_pwd}@127.0.0.1:5432/meu_db"
SQL_FILE = Path("drawSQL-pgsql-export-2023-12-03.sql")
OUT_FILE = Path("models.py")

# 2. EXECUTA O DUMP (idempotente) -----------------------------------------
engine = create_engine(DB_URL, echo=False, future=True)
sql = SQL_FILE.read_text(encoding="utf-8")

with engine.begin() as conn:
    try:
        conn.execute(text(sql))
    except ProgrammingError as e:          # já tinha rodado?
        if "already exists" not in str(e):
            raise

# 3. REFLETE O ESQUEMA -----------------------------------------------------
insp = inspect(engine)
metadata = MetaData()
metadata.reflect(bind=engine)

# 4. GERA CÓDIGO -----------------------------------------------------------
header = """\
from __future__ import annotations
from typing import Optional, List

from sqlalchemy import (
    Boolean, Date, DateTime, Float, Integer, BigInteger, SmallInteger,
    Numeric, String, Text, ForeignKey, CHAR
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    \"\"\"Classe-base declarativa, usada por todas as entidades.\"\"\"
    pass

"""
classes = []

def camel(name: str) -> str:
    return "".join(p.title() for p in re.split(r"[_\W]+", name))

for tbl in metadata.sorted_tables:
    cls_name = camel(tbl.name)
    lines: list[str] = [f"class {cls_name}(Base):", f"    __tablename__ = \"{tbl.name}\"", ""]
    insp_tbl = insp.get_columns(tbl.name)

    for col in insp_tbl:
        py_typ = col["type"].python_type.__name__.capitalize()  # ex.: 'int' -> 'Int'
        sa_typ = col["type"]                                    # já instanciado
        args = [repr(sa_typ)]
        if col["foreign_keys"]:
            fk = next(iter(col["foreign_keys"]))
            args.append(f"ForeignKey(\"{fk.column.table.name}.{fk.column.name}\")")

        kwargs = []
        if col["primary_key"]:
            kwargs.append("primary_key=True")
        if col["nullable"] is False:
            kwargs.append("nullable=False")
        if col.get("unique"):
            kwargs.append("unique=True")

        args_kwargs = ", ".join(args + kwargs)
        lines.append(f"    {col['name']}: Mapped[{py_typ}] = mapped_column({args_kwargs})")

    lines.append("")  # linha em branco depois da classe
    classes.append("\n".join(lines))

OUT_FILE.write_text(header + "\n\n".join(classes), encoding="utf-8")
print(f"✅ Modelos gerados em {OUT_FILE.resolve()}")
