from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd

from app.config import DEFAULT_TOP_N


def analyze_dataset(df: pd.DataFrame, column_profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
    analysis: Dict[str, Any] = {
        "numeric_summary": {},
        "categorical_summary": {},
        "date_summary": {},
        "suggested_analyses": []
    }

    for profile in column_profiles:
        col = profile["column_name"]
        detected_type = profile["detected_type"]

        if detected_type == "numerica":
            numeric_series = pd.to_numeric(df[col], errors="coerce").dropna()
            if not numeric_series.empty:
                analysis["numeric_summary"][col] = {
                    "count": int(numeric_series.count()),
                    "mean": round(float(numeric_series.mean()), 2),
                    "median": round(float(numeric_series.median()), 2),
                    "min": round(float(numeric_series.min()), 2),
                    "max": round(float(numeric_series.max()), 2),
                    "std": round(float(numeric_series.std()), 2) if numeric_series.count() > 1 else 0.0,
                }
                analysis["suggested_analyses"].append(
                    f"Analisar distribuição e dispersão da coluna numérica '{col}'."
                )

        elif detected_type == "categorica":
            value_counts = df[col].astype(str).fillna("NULO").value_counts().head(DEFAULT_TOP_N)
            analysis["categorical_summary"][col] = value_counts.to_dict()
            analysis["suggested_analyses"].append(
                f"Analisar ranking das categorias mais frequentes da coluna '{col}'."
            )

        elif detected_type == "data":
            date_series = pd.to_datetime(df[col], errors="coerce").dropna()
            if not date_series.empty:
                analysis["date_summary"][col] = {
                    "min_date": str(date_series.min()),
                    "max_date": str(date_series.max()),
                    "non_null_dates": int(date_series.count()),
                }
                analysis["suggested_analyses"].append(
                    f"Construir série temporal usando a coluna de data '{col}'."
                )

    date_cols = [p["column_name"] for p in column_profiles if p["detected_type"] == "data"]
    categorical_cols = [p["column_name"] for p in column_profiles if p["detected_type"] == "categorica"]

    if date_cols and categorical_cols:
        analysis["suggested_analyses"].append(
            f"Cruzar a coluna temporal '{date_cols[0]}' com a categórica '{categorical_cols[0]}'."
        )

    return analysis