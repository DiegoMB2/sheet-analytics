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

## Project Structure

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
```

## Installation and Setup

Clone the repository, create a virtual environment, activate it, install the dependencies, and run the Streamlit app.

```bash
git clone https://github.com/DiegoMB2/sheet-analytics.git
cd sheet-analytics
python -m venv .venv
```

### Activate the virtual environment

**Windows**
```bash
.venv\Scripts\activate
```

**Linux / macOS**
```bash
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app/streamlit_app.py
```

### Alternative run command

If you have import issues, try:

```bash
python -m streamlit run app/streamlit_app.py
```

## How It Works

1. Upload a spreadsheet file
2. Select the desired sheet if needed
3. Preview the data
4. Analyze columns automatically
5. Review summaries and charts
6. Inspect inconsistencies
7. Download reports

## Example Outputs

The application can generate:

- column profile tables
- numeric summaries
- categorical summaries
- date summaries
- inconsistency alerts
- bar charts
- histograms
- time series charts
- markdown reports
- Excel reports

## Supported File Types

- Excel `.xlsx`
- Excel `.xls`
- CSV `.csv`

## Tech Stack

- Python
- Streamlit
- pandas
- openpyxl
- matplotlib
- sqlite3

## Use Cases

Sheet Analytics can be used to analyze many types of spreadsheets, including:

- financial statements
- expense logs
- customer records
- HR tables
- stock reports
- support tickets
- survey results
- public administration data

## Roadmap

Planned improvements:

- manual chart selection
- custom chart colors
- better HTML reports
- dashboard tabs
- quality score for datasets
- smarter domain-specific suggestions
- comparison between two spreadsheets
- support for larger files
- filters and interactive controls

## Contributing

Contributions are welcome.

You can contribute by:

- improving analysis logic
- adding new chart types
- improving inconsistency checks
- enhancing the UI
- writing tests
- improving documentation

## License

This project is licensed under the MIT License.