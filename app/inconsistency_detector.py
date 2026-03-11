from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd

from app.config import HIGH_NULL_ALERT_THRESHOLD
from app.profiler import detect_column_type
from app.utils import is_probable_date_column, is_probable_id_column


def detect_inconsistencies(df: pd.DataFrame) -> List[Dict[str, Any]]:
    alerts: List[Dict[str, Any]] = []

    total_rows = len(df)

    if total_rows == 0:
        alerts.append({
            "column": None,
            "type": "base_vazia",
            "description": "A planilha está vazia."
        })
        return alerts

    fully_duplicated = int(df.duplicated().sum())
    if fully_duplicated > 0:
        alerts.append({
            "column": None,
            "type": "linhas_duplicadas",
            "description": f"Foram encontradas {fully_duplicated} linhas totalmente duplicadas."
        })

    for col in df.columns:
        series = df[col]
        detected_type = detect_column_type(series, col)
        null_count = int(series.isna().sum())
        null_ratio = null_count / total_rows if total_rows else 0

        if null_ratio >= HIGH_NULL_ALERT_THRESHOLD:
            alerts.append({
                "column": col,
                "type": "muitos_nulos",
                "description": f"A coluna '{col}' possui {null_count} valores nulos ({null_ratio:.1%})."
            })

        if detected_type == "vazia":
            alerts.append({
                "column": col,
                "type": "coluna_vazia",
                "description": f"A coluna '{col}' está totalmente vazia."
            })

        if is_probable_id_column(col):
            duplicates = int(series.dropna().astype(str).duplicated().sum())
            if duplicates > 0:
                alerts.append({
                    "column": col,
                    "type": "duplicidade_chave",
                    "description": f"A coluna '{col}' possui {duplicates} valores duplicados e parece ser identificadora."
                })

        if detected_type == "data" or is_probable_date_column(col):
            non_null = series.dropna()
            if not non_null.empty:
                converted = pd.to_datetime(non_null, errors="coerce")
                invalid_dates = int(converted.isna().sum())
                if invalid_dates > 0:
                    alerts.append({
                        "column": col,
                        "type": "datas_invalidas",
                        "description": f"A coluna '{col}' possui {invalid_dates} valores com possível data inválida."
                    })

        if detected_type in ("categorica", "texto"):
            non_null = series.dropna().astype(str)
            leading_trailing_spaces = int((non_null != non_null.str.strip()).sum())
            if leading_trailing_spaces > 0:
                alerts.append({
                    "column": col,
                    "type": "espacos_extras",
                    "description": f"A coluna '{col}' possui {leading_trailing_spaces} valores com espaços extras no início/fim."
                })

    return alerts