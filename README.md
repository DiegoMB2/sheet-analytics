# Sheet Analytics

Visual spreadsheet analysis with automatic profiling, charts, inconsistency detection, and report export using Python and Streamlit.

## Overview

Sheet Analytics is an open source Python project designed to help users explore and understand spreadsheet data in a simple and visual way.

Upload an Excel or CSV file and the app will:

- detect columns and data types automatically
- generate descriptive summaries
- suggest useful analyses
- create charts
- detect inconsistencies
- export reports

The tool is generic and works for many use cases, such as:

- finance
- sales
- HR
- inventory
- operations
- customer service
- research datasets
- public sector spreadsheets

## Features

- Upload `.xlsx`, `.xls`, and `.csv` files
- Select Excel sheets visually
- Automatic column profiling
- Data type detection
- Numeric, categorical, and date summaries
- Automatic chart generation
- Inconsistency detection
- Exportable reports
- Streamlit visual interface
- SQLite analysis history

## Project structure

```text
sheet-analytics/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── profiler.py
│   ├── analyzer.py
│   ├── chart_generator.py
│   ├── inconsistency_detector.py
│   ├── report_builder.py
│   ├── sqlite_store.py
│   ├── utils.py
│   └── streamlit_app.py
├── outputs/
│   ├── charts/
│   ├── reports/
│   └── database/
├── requirements.txt
└── README.md