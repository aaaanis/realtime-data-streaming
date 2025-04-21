CREATE OR REPLACE SCHEMA UTIL;

CREATE OR REPLACE FUNCTION UTIL.ADD_MISSING_COLUMNS(
    db      STRING,
    sch     STRING,
    tbl     STRING,
    record  VARIANT
)
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('snowflake-snowpark-python')
HANDLER = 'add_missing_columns'
AS
$$
from typing import Dict
import json
from snowflake.snowpark import Session

def add_missing_columns(db: str, sch: str, tbl: str, record) -> str:
    session: Session = Session.builder.getOrCreate()
    full = f'"{db}"."{sch}"."{tbl}"'

    existing = {r["column_name"].upper() for r in session.sql(f"SHOW COLUMNS IN {full}").collect()}
    payload: Dict = json.loads(record)
    added = []

    for key, val in payload.items():
        col = key.upper()
        if col in existing:
            continue
        if isinstance(val, str):
            dtype = "STRING"
        elif isinstance(val, bool):
            dtype = "BOOLEAN"
        elif isinstance(val, int):
            dtype = "NUMBER"
        elif isinstance(val, float):
            dtype = "FLOAT"
        else:
            dtype = "VARIANT"

        session.sql(f'ALTER TABLE {full} ADD COLUMN IF NOT EXISTS "{col}" {dtype}').collect()
        added.append(col)

    return ",".join(added) if added else "NONE"
$$;
