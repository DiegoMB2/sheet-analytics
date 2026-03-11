from __future__ import annotations

from pathlib import Path

from app.analyzer import analyze_dataset
from app.chart_generator import generate_charts
from app.inconsistency_detector import detect_inconsistencies
from app.profiler import build_dataset_profile, list_sheets, load_sheet
from app.report_builder import export_reports
from app.sqlite_store import initialize_database, save_analysis
from app.utils import timestamp_str


def choose_sheet(file_path: str) -> str:
    sheets = list_sheets(file_path)

    print("\nAbas encontradas:")
    for idx, sheet in enumerate(sheets, start=1):
        print(f"{idx}. {sheet}")

    while True:
        choice = input("\nDigite o número da aba que deseja analisar: ").strip()

        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(sheets):
                return sheets[index]

        print("Opção inválida. Tente novamente.")


def main() -> None:
    print("=" * 60)
    print("Sheet Sage - Agente de Análise de Planilhas")
    print("=" * 60)

    initialize_database()

    file_path = input("\nInforme o caminho do arquivo Excel (.xlsx): ").strip().strip('"')

    if not file_path:
        print("Nenhum arquivo informado.")
        return

    path_obj = Path(file_path)
    if not path_obj.exists():
        print("Arquivo não encontrado.")
        return

    try:
        sheet_name = choose_sheet(file_path)
        df = load_sheet(file_path, sheet_name)

        dataset_profile = build_dataset_profile(df, sheet_name)
        alerts = detect_inconsistencies(df)
        analysis = analyze_dataset(df, dataset_profile["columns"])
        generated_charts = generate_charts(df, dataset_profile["columns"])

        reports = export_reports(
            file_name=path_obj.name,
            sheet_name=sheet_name,
            dataset_profile=dataset_profile,
            analysis=analysis,
            alerts=alerts,
            generated_charts=generated_charts,
        )

        analysis_id = save_analysis(
            file_name=path_obj.name,
            sheet_name=sheet_name,
            execution_time=timestamp_str(),
            dataset_profile=dataset_profile,
            alerts=alerts,
        )

        print("\nResumo da análise")
        print("-" * 60)
        print(f"Aba analisada: {sheet_name}")
        print(f"Total de linhas: {dataset_profile['row_count']}")
        print(f"Total de colunas: {dataset_profile['column_count']}")
        print(f"Total de alertas: {len(alerts)}")
        print(f"Análise registrada no SQLite com ID: {analysis_id}")

        print("\nColunas detectadas:")
        for col in dataset_profile["columns"]:
            print(
                f"- {col['column_name']} -> {col['detected_type']} "
                f"(nulos: {col['null_count']}, únicos: {col['unique_count']})"
            )

        print("\nArquivos gerados:")
        print(f"- Relatório Markdown: {reports['markdown_report']}")
        print(f"- Relatório Excel: {reports['excel_report']}")

        if generated_charts:
            print("- Gráficos:")
            for chart in generated_charts:
                print(f"  - {chart}")
        else:
            print("- Nenhum gráfico foi gerado.")

        if alerts:
            print("\nPrincipais alertas:")
            for alert in alerts[:10]:
                print(f"- [{alert['type']}] {alert['description']}")
        else:
            print("\nNenhuma inconsistência relevante encontrada.")

    except Exception as exc:
        print(f"\nErro durante a análise: {exc}")


if __name__ == "__main__":
    main()