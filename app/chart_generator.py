from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd

from app.config import CHARTS_DIR, DEFAULT_TOP_N
from app.utils import sanitize_filename


def generate_charts(df: pd.DataFrame, column_profiles: List[Dict]) -> List[str]:
    generated_files: List[str] = []

    for profile in column_profiles:
        col = profile["column_name"]
        detected_type = profile["detected_type"]

        try:
            if detected_type == "categorica":
                file_path = _generate_bar_chart(df, col)
                if file_path:
                    generated_files.append(file_path)

            elif detected_type == "numerica":
                file_path = _generate_histogram(df, col)
                if file_path:
                    generated_files.append(file_path)

            elif detected_type == "data":
                file_path = _generate_time_series(df, col)
                if file_path:
                    generated_files.append(file_path)

        except Exception as exc:
            print(f"[AVISO] Não foi possível gerar gráfico para '{col}': {exc}")

    return generated_files


def _generate_bar_chart(df: pd.DataFrame, col: str) -> str | None:
    counts = df[col].fillna("NULO").astype(str).value_counts().head(DEFAULT_TOP_N)
    if counts.empty:
        return None

    plt.figure(figsize=(10, 6))
    counts.sort_values().plot(kind="barh")
    plt.title(f"Top categorias - {col}")
    plt.xlabel("Quantidade")
    plt.ylabel(col)
    plt.tight_layout()

    filename = f"bar_{sanitize_filename(col)}.png"
    output_path = CHARTS_DIR / filename
    plt.savefig(output_path, dpi=150)
    plt.close()

    return str(output_path)


def _generate_histogram(df: pd.DataFrame, col: str) -> str | None:
    series = pd.to_numeric(df[col], errors="coerce").dropna()
    if series.empty:
        return None

    plt.figure(figsize=(10, 6))
    plt.hist(series, bins=20)
    plt.title(f"Distribuição - {col}")
    plt.xlabel(col)
    plt.ylabel("Frequência")
    plt.tight_layout()

    filename = f"hist_{sanitize_filename(col)}.png"
    output_path = CHARTS_DIR / filename
    plt.savefig(output_path, dpi=150)
    plt.close()

    return str(output_path)


def _generate_time_series(df: pd.DataFrame, col: str) -> str | None:
    date_series = pd.to_datetime(df[col], errors="coerce").dropna()
    if date_series.empty:
        return None

    counts = date_series.dt.to_period("M").astype(str).value_counts().sort_index()
    if counts.empty:
        return None

    plt.figure(figsize=(11, 6))
    counts.plot(kind="line", marker="o")
    plt.title(f"Série temporal mensal - {col}")
    plt.xlabel("Período")
    plt.ylabel("Quantidade")
    plt.xticks(rotation=45)
    plt.tight_layout()

    filename = f"line_{sanitize_filename(col)}.png"
    output_path = CHARTS_DIR / filename
    plt.savefig(output_path, dpi=150)
    plt.close()

    return str(output_path)