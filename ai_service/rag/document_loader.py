from pathlib import Path
from typing import List

import pandas as pd


SUPPORTED_DOCUMENT_EXTENSIONS = {".xls", ".xlsx", ".md", ".txt"}


def load_excel_documents(file_path: str) -> List[str]:
    excel_path = Path(file_path)

    engine = "xlrd" if excel_path.suffix.lower() == ".xls" else "openpyxl"
    sheets = pd.read_excel(excel_path, sheet_name=None, engine=engine)

    chunks = []

    for sheet_name, dataframe in sheets.items():
        dataframe = dataframe.fillna("")

        for row_index, row in dataframe.iterrows():
            row_parts = []

            for column_name, value in row.items():
                if value == "":
                    continue

                row_parts.append(f"{column_name}: {value}")

            if not row_parts:
                continue

            chunk = (
                f"Sheet: {sheet_name}\n"
                f"Row: {row_index + 1}\n"
                + "\n".join(row_parts)
            )

            chunks.append(chunk)

    return chunks


def load_text_document(file_path: str) -> List[str]:
    text_path = Path(file_path)
    content = text_path.read_text(encoding="utf-8").strip()

    if not content:
        return []

    return [
        f"File: {text_path.name}\n{content}"
    ]


def load_document(file_path: str) -> List[str]:
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension in {".xls", ".xlsx"}:
        return load_excel_documents(str(path))

    if extension in {".md", ".txt"}:
        return load_text_document(str(path))

    return []


def load_documents(documents_dir: str = "documents") -> List[str]:
    base_dir = Path(documents_dir)

    if not base_dir.exists():
        return []

    chunks: List[str] = []
    for path in sorted(base_dir.iterdir()):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_DOCUMENT_EXTENSIONS:
            continue

        chunks.extend(load_document(str(path)))

    return chunks
