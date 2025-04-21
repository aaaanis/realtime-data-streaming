"""
Pipeline guardrail — fails if the most‑recent 100 rows exceed 5 s latency.
"""

import os
import snowflake.connector

ctx = snowflake.connector.connect(
    account   = os.environ["SNOWFLAKE_ACCOUNT"],
    user      = os.environ["SNOWFLAKE_USER"],
    password  = os.environ["SNOWFLAKE_PASSWORD"],
    role      = os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
    database  = "SALES_ANALYTICS",
    schema    = "RAW",
    warehouse = "STREAM_WH",
)

def test_stream_latency():
    with ctx.cursor() as cur:
        cur.execute("""
            SELECT MAX(
                     DATEDIFF(
                         'second',
                         TO_TIMESTAMP_NTZ(DATA:event_ts_utc),
                         METADATA$INGESTION_TIME
                     )
                   ) AS max_latency
            FROM SALES_TRANSACTIONS
            ORDER BY METADATA$INGESTION_TIME DESC
            LIMIT 100
        """)
        (max_latency,) = cur.fetchone()
        assert max_latency < 5, f"Latency threshold exceeded: {max_latency}s"
