from typing import Dict
import json
from snowflake.snowpark import Session

def add_missing_columns(session: Session,
                        database: str,
                        schema: str,
                        table: str,
                        record: str) -> str:
    full_name = f'"{database}"."{schema}"."{table}"'
    existing = {r["column_name"].upper() for r in session.sql(f"SHOW COLUMNS IN {full_name}").collect()}
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
        session.sql(f'ALTER TABLE {full_name} ADD COLUMN IF NOT EXISTS "{col}" {dtype}').collect()
        added.append(col)

    return ",".join(added) if added else "NONE"
