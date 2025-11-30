"""
RAG Preprocessor - PDF Driver
Extracts text and tables from PDF files with header/footer stripping.
"""

import fitz  # PyMuPDF
import pdfplumber
from typing import List, Dict, Any
from pathlib import Path


class PDFDriver:
    """
    PDF processing driver for RAG preprocessing.
    - Uses PyMuPDF (fitz) for fast text extraction
    - Uses pdfplumber for table extraction (converted to Markdown)
    - Strips headers/footers (top/bottom 50px noise zones)
    """

    HEADER_FOOTER_MARGIN = 50  # pixels to strip from top/bottom

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.filename = self.file_path.name

    def extract(self) -> Dict[str, Any]:
        """
        Main extraction method.
        Returns structured document with text content and metadata.
        """
        text_content = self._extract_text_with_pymupdf()
        tables_markdown = self._extract_tables_with_pdfplumber()

        # Combine text and tables
        full_content = text_content
        if tables_markdown:
            full_content += "\n\n## Extracted Tables\n\n" + tables_markdown

        return {
            "source": str(self.file_path),
            "filename": self.filename,
            "file_type": "pdf",
            "content": full_content,
            "metadata": {
                "page_count": self._get_page_count(),
                "has_tables": bool(tables_markdown),
                "extraction_method": "PyMuPDF + pdfplumber"
            }
        }

    def _extract_text_with_pymupdf(self) -> str:
        """
        Extract text using PyMuPDF with header/footer stripping.
        """
        extracted_pages = []

        with fitz.open(self.file_path) as doc:
            for page_num, page in enumerate(doc):
                # Get page dimensions
                page_rect = page.rect
                page_height = page_rect.height

                # Define content area (exclude header/footer zones)
                content_rect = fitz.Rect(
                    page_rect.x0,
                    page_rect.y0 + self.HEADER_FOOTER_MARGIN,  # Skip header
                    page_rect.x1,
                    page_height - self.HEADER_FOOTER_MARGIN    # Skip footer
                )

                # Extract text only from content area
                text = page.get_text("text", clip=content_rect)

                if text.strip():
                    extracted_pages.append(f"--- Page {page_num + 1} ---\n{text.strip()}")

        return "\n\n".join(extracted_pages)

    def _extract_tables_with_pdfplumber(self) -> str:
        """
        Extract tables using pdfplumber and convert to Markdown format.
        """
        all_tables_md = []

        with pdfplumber.open(self.file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Get page dimensions for header/footer filtering
                page_height = page.height

                # Define content bounding box (exclude header/footer)
                content_bbox = (
                    0,
                    self.HEADER_FOOTER_MARGIN,
                    page.width,
                    page_height - self.HEADER_FOOTER_MARGIN
                )

                # Crop page to content area
                cropped_page = page.within_bbox(content_bbox)

                # Extract tables from cropped area
                tables = cropped_page.extract_tables()

                for table_idx, table in enumerate(tables):
                    if table and len(table) > 0:
                        md_table = self._table_to_markdown(table)
                        if md_table:
                            all_tables_md.append(
                                f"### Table {table_idx + 1} (Page {page_num + 1})\n\n{md_table}"
                            )

        return "\n\n".join(all_tables_md)

    def _table_to_markdown(self, table: List[List[str]]) -> str:
        """
        Convert a table (list of rows) to Markdown format.
        """
        if not table or len(table) < 1:
            return ""

        # Clean cells - replace None with empty string, strip whitespace
        cleaned_table = []
        for row in table:
            cleaned_row = [
                str(cell).strip() if cell is not None else ""
                for cell in row
            ]
            cleaned_table.append(cleaned_row)

        # Skip empty tables
        if all(all(cell == "" for cell in row) for row in cleaned_table):
            return ""

        # Build Markdown table
        md_lines = []

        # Header row
        header = cleaned_table[0]
        md_lines.append("| " + " | ".join(header) + " |")

        # Separator row
        md_lines.append("| " + " | ".join(["---"] * len(header)) + " |")

        # Data rows
        for row in cleaned_table[1:]:
            # Ensure row has same number of columns as header
            while len(row) < len(header):
                row.append("")
            md_lines.append("| " + " | ".join(row[:len(header)]) + " |")

        return "\n".join(md_lines)

    def _get_page_count(self) -> int:
        """Get total page count of the PDF."""
        with fitz.open(self.file_path) as doc:
            return len(doc)


def process_pdf(file_path: str) -> Dict[str, Any]:
    """
    Convenience function to process a PDF file.
    """
    driver = PDFDriver(file_path)
    return driver.extract()
