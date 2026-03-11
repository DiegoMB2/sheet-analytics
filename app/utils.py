import re
from datetime import datetime


def sanitize_filename(name: str) -> str:
    name = re.sub(r"[^\w\-. ]", "_", name, flags=re.UNICODE)
    name = re.sub(r"\s+", "_", name.strip())
    return name


def timestamp_str() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_str(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def is_probable_id_column(column_name: str) -> bool:
    name = column_name.lower()
    keywords = [
        "id", "codigo", "código", "numero", "número", "protocolo",
        "matricula", "matrícula", "cpf", "cnpj", "chave"
    ]
    return any(word in name for word in keywords)


def is_probable_date_column(column_name: str) -> bool:
    name = column_name.lower()
    keywords = ["data", "dt_", "dt", "date", "prazo", "deadline"]
    return any(word in name for word in keywords)