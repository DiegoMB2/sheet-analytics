from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd

from app.utils import is_probable_date_column, is_probable_id_column


def list_sheets(file_path: str) -> List[str]:
    xls = pd.ExcelFile(file_path)
    return xls.sheet_names


def load_sheet(file_path: str, sheet_name: str | None = None) -> pd.DataFrame:
    if sheet_name:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    else:
        df = pd.read_excel(file_path)

    df.columns = [str(col).strip() for col in df.columns]
    return df


def detect_column_type(series: pd.Series, column_name: str) -> str:
    non_null = series.dropna()

    if non_null.empty:
        return "vazia"

    if pd.api.types.is_datetime64_any_dtype(series):
        return "data"

    if pd.api.types.is_numeric_dtype(series):
        if is_probable_id_column(column_name):
            return "identificador"
        return "numerica"

    if is_probable_date_column(column_name):
        converted = pd.to_datetime(non_null, errors="coerce")
        if converted.notna().mean() >= 0.7:
            return "data"

    as_numeric = pd.to_numeric(non_null.astype(str).str.replace(",", ".", regex=False), errors="coerce")
    if as_numeric.notna().mean() >= 0.8:
        if is_probable_id_column(column_name):
            return "identificador"
        return "numerica"

    nunique = non_null.astype(str).nunique(dropna=True)

    if is_probable_id_column(column_name):
        uniqueness_ratio = nunique / max(len(non_null), 1)
        if uniqueness_ratio >= 0.8:
            return "identificador"

    if nunique <= 30:
        return "categorica"

    return "texto"


def build_column_profile(df: pd.DataFrame) -> List[Dict[str, Any]]:
    profiles: List[Dict[str, Any]] = []

    for col in df.columns:
        series = df[col]
        total = len(series)
        nulls = int(series.isna().sum())
        non_null = series.dropna()
        unique_count = int(non_null.astype(str).nunique()) if not non_null.empty else 0
        sample_values = non_null.astype(str).head(3).tolist()

        profile = {
            "column_name": col,
            "detected_type": detect_column_type(series, col),
            "total_rows": total,
            "null_count": nulls,
            "null_percent": round((nulls / total) * 100, 2) if total else 0,
            "unique_count": unique_count,
            "sample_values": sample_values,
        }
        profiles.append(profile)

    return profiles


def build_dataset_profile(df: pd.DataFrame, sheet_name: str) -> Dict[str, Any]:
    column_profiles = build_column_profile(df)

    return {
        "sheet_name": sheet_name,
        "row_count": int(df.shape[0]),
        "column_count": int(df.shape[1]),
        "columns": column_profiles,
    }