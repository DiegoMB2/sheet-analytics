from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from app.config import REPORTS_DIR
from app.utils import sanitize_filename, timestamp_str


def export_reports(
    file_name: str,
    sheet_name: str,
    dataset_profile: Dict[str, Any],
    analysis: Dict[str, Any],
    alerts: List[Dict[str, Any]],
    generated_charts: List[str],
) -> Dict[str, str]:
    base_name = f"{sanitize_filename(Path(file_name).stem)}_{sanitize_filename(sheet_name)}_{timestamp_str()}"

    md_path = REPORTS_DIR / f"{base_name}.md"
    xlsx_path = REPORTS_DIR / f"{base_name}.xlsx"

    _export_markdown(md_path, file_name, sheet_name, dataset_profile, analysis, alerts, generated_charts)
    _export_excel(xlsx_path, dataset_profile, analysis, alerts, generated_charts)

    return {
        "markdown_report": str(md_path),
        "excel_report": str(xlsx_path),
    }


def _export_markdown(
    output_path: Path,
    file_name: str,
    sheet_name: str,
    dataset_profile: Dict[str, Any],
    analysis: Dict[str, Any],
    alerts: List[Dict[str, Any]],
    generated_charts: List[str],
) -> None:
    lines: List[str] = []

    lines.append(f"# Relatório de Análise - {sheet_name}")
    lines.append("")
    lines.append(f"**Arquivo:** {file_name}")
    lines.append(f"**Aba:** {sheet_name}")
    lines.append(f"**Total de linhas:** {dataset_profile['row_count']}")
    lines.append(f"**Total de colunas:** {dataset_profile['column_count']}")
    lines.append("")

    lines.append("## Perfil das colunas")
    lines.append("")

    for column in dataset_profile["columns"]:
        lines.append(f"### {column['column_name']}")
        lines.append(f"- Tipo detectado: {column['detected_type']}")
        lines.append(f"- Nulos: {column['null_count']} ({column['null_percent']}%)")
        lines.append(f"- Valores únicos: {column['unique_count']}")
        lines.append(f"- Amostras: {', '.join(column['sample_values']) if column['sample_values'] else 'Sem amostras'}")
        lines.append("")

    lines.append("## Resumos analíticos")
    lines.append("")

    if analysis["numeric_summary"]:
        lines.append("### Colunas numéricas")
        for col, stats in analysis["numeric_summary"].items():
            lines.append(f"- **{col}**: média={stats['mean']}, mediana={stats['median']}, min={stats['min']}, max={stats['max']}")
        lines.append("")

    if analysis["categorical_summary"]:
        lines.append("### Colunas categóricas")
        for col, values in analysis["categorical_summary"].items():
            lines.append(f"- **{col}**: {values}")
        lines.append("")

    if analysis["date_summary"]:
        lines.append("### Colunas de data")
        for col, stats in analysis["date_summary"].items():
            lines.append(f"- **{col}**: início={stats['min_date']}, fim={stats['max_date']}, válidas={stats['non_null_dates']}")
        lines.append("")

    lines.append("## Sugestões automáticas")
    lines.append("")
    for suggestion in analysis["suggested_analyses"]:
        lines.append(f"- {suggestion}")
    lines.append("")

    lines.append("## Alertas de inconsistência")
    lines.append("")
    if alerts:
        for alert in alerts:
            lines.append(f"- [{alert['type']}] {alert['description']}")
    else:
        lines.append("- Nenhuma inconsistência relevante encontrada.")
    lines.append("")

    lines.append("## Gráficos gerados")
    lines.append("")
    if generated_charts:
        for chart in generated_charts:
            lines.append(f"- {chart}")
    else:
        lines.append("- Nenhum gráfico foi gerado.")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def _export_excel(
    output_path: Path,
    dataset_profile: Dict[str, Any],
    analysis: Dict[str, Any],
    alerts: List[Dict[str, Any]],
    generated_charts: List[str],
) -> None:
    columns_df = pd.DataFrame(dataset_profile["columns"])
    alerts_df = pd.DataFrame(alerts) if alerts else pd.DataFrame(columns=["column", "type", "description"])

    numeric_rows = []
    for col, stats in analysis["numeric_summary"].items():
        row = {"column_name": col}
        row.update(stats)
        numeric_rows.append(row)
    numeric_df = pd.DataFrame(numeric_rows)

    categorical_rows = []
    for col, values in analysis["categorical_summary"].items():
        for category, qty in values.items():
            categorical_rows.append(
                {
                    "column_name": col,
                    "category": category,
                    "count": qty,
                }
            )
    categorical_df = pd.DataFrame(categorical_rows)

    date_rows = []
    for col, stats in analysis["date_summary"].items():
        row = {"column_name": col}
        row.update(stats)
        date_rows.append(row)
    date_df = pd.DataFrame(date_rows)

    suggestions_df = pd.DataFrame(
        {"suggestion": analysis["suggested_analyses"]}
    ) if analysis["suggested_analyses"] else pd.DataFrame(columns=["suggestion"])

    charts_df = pd.DataFrame({"chart_path": generated_charts}) if generated_charts else pd.DataFrame(columns=["chart_path"])

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        columns_df.to_excel(writer, sheet_name="perfil_colunas", index=False)
        alerts_df.to_excel(writer, sheet_name="alertas", index=False)
        numeric_df.to_excel(writer, sheet_name="resumo_numerico", index=False)
        categorical_df.to_excel(writer, sheet_name="resumo_categorico", index=False)
        date_df.to_excel(writer, sheet_name="resumo_datas", index=False)
        suggestions_df.to_excel(writer, sheet_name="sugestoes", index=False)
        charts_df.to_excel(writer, sheet_name="graficos", index=False)