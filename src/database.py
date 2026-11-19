import sqlite3
from contextlib import closing
from datetime import datetime, timezone


def init_db(db_path: str) -> None:
    """Cria a tabela de registos se ainda não existir."""
    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    latency_ms REAL,
                    checked_at TEXT NOT NULL
                )
                """
            )


def save_check(
    db_path: str,
    target: str,
    port: int,
    status: str,
    latency_ms: float | None,
) -> None:
    """Guarda o resultado de uma verificação."""
    now = datetime.now(timezone.utc).isoformat()
    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            conn.execute(
                """
                INSERT INTO checks (target, port, status, latency_ms, checked_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (target, port, status, latency_ms, now),
            )


def get_summary(db_path: str) -> list[tuple]:
    """Calcula total de testes, disponibilidade (%) e latências por alvo."""
    with closing(sqlite3.connect(db_path)) as conn:
        cursor = conn.execute(
            """
            SELECT
                target,
                port,
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'ONLINE' THEN 1 ELSE 0 END) AS online_count,
                ROUND(AVG(latency_ms), 2) AS avg_ms,
                ROUND(MIN(latency_ms), 2) AS min_ms,
                ROUND(MAX(latency_ms), 2) AS max_ms
            FROM checks
            GROUP BY target, port
            ORDER BY target
            """
        )
        return cursor.fetchall()