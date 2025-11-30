"""
RAG Preprocessor - Excel Driver
Linearizes Excel data into natural language sentences for RAG ingestion.
"""

import pandas as pd
from typing import Dict, Any, List
from pathlib import Path


class ExcelDriver:
    """
    Excel processing driver for RAG preprocessing.
    - Uses pandas for Excel parsing
    - Linearizes each row into natural language sentences
    - Uses column headers as context keys
    """

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.filename = self.file_path.name

    def extract(self) -> Dict[str, Any]:
        """
        Main extraction method.
        Returns structured document with linearized content and metadata.
        """
        # Read all sheets from Excel file
        excel_file = pd.ExcelFile(self.file_path)
        sheet_names = excel_file.sheet_names

        all_content = []
        total_rows = 0

        for sheet_name in sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)

            if df.empty:
                continue

            # Clean column names
            df.columns = [str(col).strip() for col in df.columns]

            # Linearize the sheet
            linearized = self._linearize_dataframe(df, sheet_name)
            if linearized:
                all_content.append(f"## Sheet: {sheet_name}\n\n{linearized}")
                total_rows += len(df)

        full_content = "\n\n".join(all_content)

        return {
            "source": str(self.file_path),
            "filename": self.filename,
            "file_type": "excel",
            "content": full_content,
            "metadata": {
                "sheet_count": len(sheet_names),
                "sheet_names": sheet_names,
                "total_rows": total_rows,
                "extraction_method": "pandas linearization"
            }
        }

    def _linearize_dataframe(self, df: pd.DataFrame, sheet_name: str) -> str:
        """
        Convert each row into a natural language sentence.
        Example: "The Revenue for Q1 was 500k"
        """
        linearized_rows = []
        columns = df.columns.tolist()

        for idx, row in df.iterrows():
            sentences = self._row_to_sentences(row, columns, idx)
            if sentences:
                linearized_rows.append(sentences)

        return "\n\n".join(linearized_rows)

    def _row_to_sentences(self, row: pd.Series, columns: List[str], row_idx: int) -> str:
        """
        Convert a single row into natural language sentences.
        Handles different data patterns intelligently.
        """
        sentences = []

        # Check if there's a primary identifier column (first non-null meaningful column)
        primary_key = None
        primary_value = None

        # Common identifier column patterns
        id_patterns = ['name', 'id', 'title', 'item', 'product', 'category', 'date', 'period']

        for col in columns:
            col_lower = col.lower()
            if any(pattern in col_lower for pattern in id_patterns):
                val = row[col]
                if pd.notna(val) and str(val).strip():
                    primary_key = col
                    primary_value = self._format_value(val)
                    break

        # If no identifier found, use row number
        if primary_key is None:
            primary_key = "Row"
            primary_value = str(row_idx + 1)

        # Build sentences for each column
        for col in columns:
            if col == primary_key:
                continue

            val = row[col]

            if pd.isna(val) or str(val).strip() == "":
                continue

            formatted_val = self._format_value(val)
            sentence = self._construct_sentence(primary_key, primary_value, col, formatted_val)
            sentences.append(sentence)

        if sentences:
            # Add context header
            header = f"**{primary_key}: {primary_value}**"
            return header + "\n" + "\n".join(f"- {s}" for s in sentences)

        return ""

    def _format_value(self, value: Any) -> str:
        """
        Format a cell value for natural language output.
        """
        if pd.isna(value):
            return "N/A"

        # Handle numeric values
        if isinstance(value, (int, float)):
            if isinstance(value, float) and value.is_integer():
                return f"{int(value):,}"
            elif isinstance(value, float):
                return f"{value:,.2f}"
            else:
                return f"{value:,}"

        # Handle datetime
        if hasattr(value, 'strftime'):
            return value.strftime('%Y-%m-%d')

        return str(value).strip()

    def _construct_sentence(self, primary_key: str, primary_value: str,
                            col: str, value: str) -> str:
        """
        Construct a natural language sentence from column and value.
        """
        # Clean column name for readability
        col_clean = col.replace('_', ' ').replace('-', ' ')

        # Determine appropriate sentence structure based on column type
        col_lower = col.lower()

        # Amount/Value patterns
        if any(word in col_lower for word in ['amount', 'total', 'sum', 'revenue', 'cost', 'price', 'value']):
            return f"The {col_clean} is {value}"

        # Count/Quantity patterns
        if any(word in col_lower for word in ['count', 'quantity', 'qty', 'number', 'num']):
            return f"The {col_clean} is {value}"

        # Status patterns
        if any(word in col_lower for word in ['status', 'state', 'condition']):
            return f"The {col_clean} is {value}"

        # Date patterns
        if any(word in col_lower for word in ['date', 'time', 'created', 'updated', 'modified']):
            return f"The {col_clean} is {value}"

        # Percentage patterns
        if any(word in col_lower for word in ['percent', 'rate', 'ratio', '%']):
            return f"The {col_clean} is {value}"

        # Description patterns
        if any(word in col_lower for word in ['description', 'desc', 'note', 'comment', 'remarks']):
            return f"{col_clean}: {value}"

        # Default pattern
        return f"The {col_clean} is {value}"


def process_excel(file_path: str) -> Dict[str, Any]:
    """
    Convenience function to process an Excel file.
    """
    driver = ExcelDriver(file_path)
    return driver.extract()
