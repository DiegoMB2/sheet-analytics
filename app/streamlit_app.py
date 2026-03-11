from __future__ import annotations

from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd
import streamlit as st

from app.analyzer import analyze_dataset
from app.chart_generator import generate_charts
from app.inconsistency_detector import detect_inconsistencies
from app.profiler import build_dataset_profile, list_sheets, load_sheet
from app.report_builder import export_reports
from app.sqlite_store import initialize_database, save_analysis
from app.utils import timestamp_str


st.set_page_config(
    page_title="Sheet Analytics",
    page_icon="📊",
    layout="wide",
)


def load_uploaded_dataframe(uploaded_file, selected_sheet: str | None = None) -> tuple[pd.DataFrame, str]:
    suffix = Path(uploaded_file.name).suffix.lower()

    if suffix == ".csv":
        df = pd.read_csv(uploaded_file)
        df.columns = [str(col).strip() for col in df.columns]
        return df, "CSV"

    if suffix in [".xlsx", ".xls"]:
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name

        if selected_sheet:
            df = load_sheet(tmp_path, selected_sheet)
            return df, selected_sheet

        sheets = list_sheets(tmp_path)
        df = load_sheet(tmp_path, sheets[0])
        return df, sheets[0]

    raise ValueError("Formato não suportado. Envie um arquivo .xlsx, .xls ou .csv.")


def get_excel_sheets(uploaded_file) -> list[str]:
    suffix = Path(uploaded_file.name).suffix.lower()

    if suffix not in [".xlsx", ".xls"]:
        return []

    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = tmp.name

    return list_sheets(tmp_path)


def dataframe_to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output.read()


def render_summary_cards(dataset_profile: dict, alerts: list[dict]) -> None:
    c1, c2, c3 = st.columns(3)
    c1.metric("Linhas", dataset_profile["row_count"])
    c2.metric("Colunas", dataset_profile["column_count"])
    c3.metric("Alertas", len(alerts))


def render_column_profile_table(dataset_profile: dict) -> pd.DataFrame:
    rows = []
    for col in dataset_profile["columns"]:
        rows.append(
            {
                "Coluna": col["column_name"],
                "Tipo detectado": col["detected_type"],
                "Nulos": col["null_count"],
                "% Nulos": col["null_percent"],
                "Únicos": col["unique_count"],
                "Amostras": " | ".join(col["sample_values"]) if col["sample_values"] else "",
            }
        )

    profile_df = pd.DataFrame(rows)
    st.dataframe(profile_df, use_container_width=True)
    return profile_df


def render_analysis_sections(analysis: dict) -> None:
    st.subheader("Sugestões automáticas de análise")
    if analysis["suggested_analyses"]:
        for item in analysis["suggested_analyses"]:
            st.markdown(f"- {item}")
    else:
        st.info("Nenhuma sugestão automática foi gerada.")

    st.subheader("Resumo numérico")
    if analysis["numeric_summary"]:
        numeric_rows = []
        for col, stats in analysis["numeric_summary"].items():
            row = {"Coluna": col}
            row.update(stats)
            numeric_rows.append(row)
        st.dataframe(pd.DataFrame(numeric_rows), use_container_width=True)
    else:
        st.info("Nenhuma coluna numérica identificada.")

    st.subheader("Resumo categórico")
    if analysis["categorical_summary"]:
        cat_rows = []
        for col, values in analysis["categorical_summary"].items():
            for category, count in values.items():
                cat_rows.append(
                    {
                        "Coluna": col,
                        "Categoria": category,
                        "Quantidade": count,
                    }
                )
        st.dataframe(pd.DataFrame(cat_rows), use_container_width=True)
    else:
        st.info("Nenhuma coluna categórica identificada.")

    st.subheader("Resumo temporal")
    if analysis["date_summary"]:
        date_rows = []
        for col, stats in analysis["date_summary"].items():
            row = {"Coluna": col}
            row.update(stats)
            date_rows.append(row)
        st.dataframe(pd.DataFrame(date_rows), use_container_width=True)
    else:
        st.info("Nenhuma coluna de data identificada.")


def render_alerts(alerts: list[dict]) -> pd.DataFrame:
    st.subheader("Inconsistências detectadas")

    if not alerts:
        st.success("Nenhuma inconsistência relevante encontrada.")
        return pd.DataFrame(columns=["Coluna", "Tipo", "Descrição"])

    alert_rows = []
    for alert in alerts:
        alert_rows.append(
            {
                "Coluna": alert.get("column", ""),
                "Tipo": alert["type"],
                "Descrição": alert["description"],
            }
        )

    alerts_df = pd.DataFrame(alert_rows)
    st.dataframe(alerts_df, use_container_width=True)
    return alerts_df


def render_charts(chart_paths: list[str]) -> None:
    st.subheader("Gráficos gerados")

    if not chart_paths:
        st.info("Nenhum gráfico foi gerado automaticamente.")
        return

    for chart in chart_paths:
        st.image(chart, use_container_width=True, caption=Path(chart).name)


def build_markdown_download(dataset_profile: dict, analysis: dict, alerts: list[dict], file_name: str, sheet_name: str) -> str:
    lines = []
    lines.append(f"# Relatório de análise - {sheet_name}")
    lines.append("")
    lines.append(f"**Arquivo:** {file_name}")
    lines.append(f"**Linhas:** {dataset_profile['row_count']}")
    lines.append(f"**Colunas:** {dataset_profile['column_count']}")
    lines.append("")
    lines.append("## Colunas")
    lines.append("")

    for col in dataset_profile["columns"]:
        lines.append(f"### {col['column_name']}")
        lines.append(f"- Tipo: {col['detected_type']}")
        lines.append(f"- Nulos: {col['null_count']} ({col['null_percent']}%)")
        lines.append(f"- Únicos: {col['unique_count']}")
        lines.append("")

    lines.append("## Sugestões")
    lines.append("")
    for suggestion in analysis["suggested_analyses"]:
        lines.append(f"- {suggestion}")

    lines.append("")
    lines.append("## Alertas")
    lines.append("")
    if alerts:
        for alert in alerts:
            lines.append(f"- [{alert['type']}] {alert['description']}")
    else:
        lines.append("- Nenhum alerta relevante encontrado.")

    return "\n".join(lines)


def main() -> None:
    initialize_database()

    st.title("📊 Sheet Analytics")
    st.caption("Análise visual de planilhas Excel e CSV com detecção automática de colunas, gráficos e inconsistências.")

    with st.sidebar:
        st.header("Configurações")
        uploaded_file = st.file_uploader(
            "Envie sua planilha",
            type=["xlsx", "xls", "csv"],
            help="Você pode enviar qualquer planilha Excel ou CSV.",
        )

    if not uploaded_file:
        st.info("Envie uma planilha para começar.")
        return

    suffix = Path(uploaded_file.name).suffix.lower()
    selected_sheet = None

    if suffix in [".xlsx", ".xls"]:
        sheets = get_excel_sheets(uploaded_file)
        selected_sheet = st.sidebar.selectbox("Escolha a aba", sheets)

    try:
        df, sheet_name = load_uploaded_dataframe(uploaded_file, selected_sheet)

        st.subheader("Pré-visualização da planilha")
        st.dataframe(df.head(20), use_container_width=True)

        dataset_profile = build_dataset_profile(df, sheet_name)
        alerts = detect_inconsistencies(df)
        analysis = analyze_dataset(df, dataset_profile["columns"])
        chart_paths = generate_charts(df, dataset_profile["columns"])

        save_analysis(
            file_name=uploaded_file.name,
            sheet_name=sheet_name,
            execution_time=timestamp_str(),
            dataset_profile=dataset_profile,
            alerts=alerts,
        )

        st.subheader("Resumo geral")
        render_summary_cards(dataset_profile, alerts)

        st.subheader("Perfil das colunas")
        profile_df = render_column_profile_table(dataset_profile)

        render_analysis_sections(analysis)
        alerts_df = render_alerts(alerts)
        render_charts(chart_paths)

        st.subheader("Downloads")
        markdown_report = build_markdown_download(
            dataset_profile=dataset_profile,
            analysis=analysis,
            alerts=alerts,
            file_name=uploaded_file.name,
            sheet_name=sheet_name,
        )

        st.download_button(
            label="Baixar perfil das colunas em Excel",
            data=dataframe_to_excel_bytes(profile_df),
            file_name="perfil_colunas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        st.download_button(
            label="Baixar alertas em Excel",
            data=dataframe_to_excel_bytes(alerts_df),
            file_name="alertas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        st.download_button(
            label="Baixar relatório em Markdown",
            data=markdown_report.encode("utf-8"),
            file_name="relatorio_analise.md",
            mime="text/markdown",
        )

    except Exception as exc:
        st.error(f"Erro ao processar a planilha: {exc}")


if __name__ == "__main__":
    main()