from __future__ import annotations

import sqlite3
from typing import Any, Dict, List

from app.config import DB_PATH


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def initialize_database() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                sheet_name TEXT NOT NULL,
                execution_time TEXT NOT NULL,
                total_rows INTEGER NOT NULL,
                total_columns INTEGER NOT NULL,
                total_alerts INTEGER NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS columns_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                column_name TEXT NOT NULL,
                detected_type TEXT NOT NULL,
                null_count INTEGER NOT NULL,
                null_percent REAL NOT NULL,
                unique_count INTEGER NOT NULL,
                sample_values TEXT,
                FOREIGN KEY (analysis_id) REFERENCES analyses (id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                column_name TEXT,
                alert_type TEXT NOT NULL,
                description TEXT NOT NULL,
                FOREIGN KEY (analysis_id) REFERENCES analyses (id)
            )
            """
        )

        conn.commit()


def save_analysis(
    file_name: str,
    sheet_name: str,
    execution_time: str,
    dataset_profile: Dict[str, Any],
    alerts: List[Dict[str, Any]],
) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO analyses (
                file_name,
                sheet_name,
                execution_time,
                total_rows,
                total_columns,
                total_alerts
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                file_name,
                sheet_name,
                execution_time,
                dataset_profile["row_count"],
                dataset_profile["column_count"],
                len(alerts),
            ),
        )

        analysis_id = cursor.lastrowid

        for column in dataset_profile["columns"]:
            cursor.execute(
                """
                INSERT INTO columns_profile (
                    analysis_id,
                    column_name,
                    detected_type,
                    null_count,
                    null_percent,
                    unique_count,
                    sample_values
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    analysis_id,
                    column["column_name"],
                    column["detected_type"],
                    column["null_count"],
                    column["null_percent"],
                    column["unique_count"],
                    " | ".join(column["sample_values"]),
                ),
            )

        for alert in alerts:
            cursor.execute(
                """
                INSERT INTO alerts (
                    analysis_id,
                    column_name,
                    alert_type,
                    description
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    analysis_id,
                    alert.get("column"),
                    alert["type"],
                    alert["description"],
                ),
            )

        conn.commit()
        return int(analysis_id)