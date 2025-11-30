"""
RAG Preprocessor - Markdown Driver
Parses Markdown files with header-based splitting and custom metadata extraction.
"""

import re
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from langchain_text_splitters import MarkdownHeaderTextSplitter


class MarkdownDriver:
    """
    Markdown processing driver for RAG preprocessing.
    - Uses langchain MarkdownHeaderTextSplitter for header-based splitting
    - Extracts custom **METADATA:** JSON blocks
    - Splits by # and ### headers
    """

    # Headers to split on
    HEADERS_TO_SPLIT = [
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
    ]

    # Pattern to match **METADATA:** blocks
    METADATA_PATTERN = r'\*\*METADATA:\*\*\s*```json\s*([\s\S]*?)\s*```'

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.filename = self.file_path.name

    def extract(self) -> Dict[str, Any]:
        """
        Main extraction method.
        Returns structured document with split content and metadata.
        """
        # Read the markdown file
        with open(self.file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        # Extract and remove custom metadata block
        custom_metadata, clean_content = self._extract_metadata_block(raw_content)

        # Split by headers using langchain
        header_splits = self._split_by_headers(clean_content)

        # Build structured content
        structured_content = self._build_structured_content(header_splits)

        return {
            "source": str(self.file_path),
            "filename": self.filename,
            "file_type": "markdown",
            "content": structured_content,
            "metadata": {
                "custom_metadata": custom_metadata,
                "section_count": len(header_splits),
                "extraction_method": "langchain MarkdownHeaderTextSplitter"
            }
        }

    def _extract_metadata_block(self, content: str) -> tuple[Optional[Dict], str]:
        """
        Extract **METADATA:** JSON block from content.
        Returns (metadata_dict, content_without_metadata).
        """
        custom_metadata = None

        match = re.search(self.METADATA_PATTERN, content, re.MULTILINE)
        if match:
            try:
                json_str = match.group(1).strip()
                custom_metadata = json.loads(json_str)
            except json.JSONDecodeError:
                # If JSON is invalid, keep it as raw string
                custom_metadata = {"raw": match.group(1).strip()}

            # Remove the metadata block from content
            content = re.sub(self.METADATA_PATTERN, '', content, flags=re.MULTILINE)

        return custom_metadata, content.strip()

    def _split_by_headers(self, content: str) -> List[Dict[str, Any]]:
        """
        Split markdown content by headers using langchain.
        """
        splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.HEADERS_TO_SPLIT,
            strip_headers=False  # Keep headers in content for context
        )

        splits = splitter.split_text(content)

        # Convert to list of dicts with content and metadata
        result = []
        for doc in splits:
            result.append({
                "content": doc.page_content,
                "headers": doc.metadata
            })

        return result

    def _build_structured_content(self, splits: List[Dict[str, Any]]) -> str:
        """
        Build structured content string from splits.
        Preserves header hierarchy information.
        """
        content_parts = []

        for idx, split in enumerate(splits):
            section_content = split["content"].strip()
            headers = split.get("headers", {})

            if not section_content:
                continue

            # Build section with header context
            header_context = []
            for level in ['h1', 'h2', 'h3']:
                if level in headers:
                    header_context.append(headers[level])

            if header_context:
                context_str = " > ".join(header_context)
                content_parts.append(f"[Section: {context_str}]\n{section_content}")
            else:
                content_parts.append(section_content)

        return "\n\n---\n\n".join(content_parts)


def process_markdown(file_path: str) -> Dict[str, Any]:
    """
    Convenience function to process a Markdown file.
    """
    driver = MarkdownDriver(file_path)
    return driver.extract()
