"""
RAG Preprocessor - Text Chunking Utilities
Handles final text chunking using langchain's RecursiveCharacterTextSplitter.
"""

from typing import Dict, Any, List
from langchain.text_splitter import RecursiveCharacterTextSplitter


class DocumentChunker:
    """
    Chunks documents for RAG vector embedding.
    Uses RecursiveCharacterTextSplitter with configurable parameters.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = None
    ):
        """
        Initialize chunker with configuration.

        Args:
            chunk_size: Maximum size of each chunk (default: 1000)
            chunk_overlap: Overlap between chunks (default: 200)
            separators: Custom separators for splitting
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Default separators optimized for structured content
        if separators is None:
            separators = [
                "\n\n---\n\n",  # Section breaks
                "\n\n",         # Paragraphs
                "\n",           # Lines
                ". ",           # Sentences
                ", ",           # Clauses
                " ",            # Words
                ""              # Characters
            ]

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
            is_separator_regex=False
        )

    def chunk_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk a single document into smaller pieces.

        Args:
            document: Document dict with 'content', 'source', 'filename', 'metadata'

        Returns:
            List of chunk dicts ready for vector embedding
        """
        content = document.get("content", "")

        if not content.strip():
            return []

        # Split the content
        chunks = self.splitter.split_text(content)

        # Build output with metadata
        chunked_docs = []
        for idx, chunk_text in enumerate(chunks):
            chunked_docs.append({
                "chunk_id": f"{document['filename']}_{idx}",
                "chunk_index": idx,
                "total_chunks": len(chunks),
                "content": chunk_text,
                "source": document.get("source", ""),
                "filename": document.get("filename", ""),
                "file_type": document.get("file_type", ""),
                "metadata": {
                    **document.get("metadata", {}),
                    "chunk_size": self.chunk_size,
                    "chunk_overlap": self.chunk_overlap,
                    "char_count": len(chunk_text)
                }
            })

        return chunked_docs

    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Chunk multiple documents.

        Args:
            documents: List of document dicts

        Returns:
            Flattened list of all chunks from all documents
        """
        all_chunks = []
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        return all_chunks


def create_chunker(chunk_size: int = 1000, chunk_overlap: int = 200) -> DocumentChunker:
    """
    Factory function to create a configured chunker.
    """
    return DocumentChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
