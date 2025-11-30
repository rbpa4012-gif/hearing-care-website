#!/usr/bin/env python3
"""
RAG Preprocessor - Main Entry Point
ETL Pipeline for preprocessing documents for RAG vector embedding.

Usage:
    python main.py                    # Process all files in data/raw/
    python main.py --input ./docs     # Process files from custom directory
    python main.py --output ./out     # Output to custom directory

Author: RAG Preprocessor System
Version: 1.0.0
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from tqdm import tqdm

# Import drivers
from src.drivers.pdf_driver import process_pdf
from src.drivers.excel_driver import process_excel
from src.drivers.markdown_driver import process_markdown

# Import utilities
from src.utils.chunker import create_chunker
from src.utils.file_detector import (
    detect_file_type,
    get_files_from_directory,
    get_supported_extensions
)


# Configuration
DEFAULT_INPUT_DIR = "./data/raw"
DEFAULT_OUTPUT_DIR = "./data/processed"
OUTPUT_FILENAME = "knowledge_base.json"

# Chunking configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def get_driver(file_type: str):
    """
    Get the appropriate driver function for a file type.
    """
    drivers = {
        'pdf': process_pdf,
        'excel': process_excel,
        'markdown': process_markdown,
    }
    return drivers.get(file_type)


def process_file(file_path: str) -> Dict[str, Any]:
    """
    Process a single file using the appropriate driver.

    Args:
        file_path: Path to the file

    Returns:
        Processed document dict or None if processing failed
    """
    file_type = detect_file_type(file_path)

    if not file_type:
        print(f"  ⚠️  Unsupported file type: {file_path}")
        return None

    driver = get_driver(file_type)

    if not driver:
        print(f"  ⚠️  No driver found for: {file_type}")
        return None

    try:
        document = driver(file_path)
        return document
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {str(e)}")
        return None


def run_pipeline(input_dir: str, output_dir: str, recursive: bool = True) -> Dict[str, Any]:
    """
    Run the complete ETL pipeline.

    Args:
        input_dir: Directory containing raw files
        output_dir: Directory for processed output
        recursive: Whether to search subdirectories

    Returns:
        Pipeline results summary
    """
    print("\n" + "=" * 60)
    print("🚀 RAG PREPROCESSOR - ETL Pipeline")
    print("=" * 60)

    # Validate directories
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not input_path.exists():
        print(f"\n❌ Input directory not found: {input_dir}")
        print(f"   Creating directory: {input_dir}")
        input_path.mkdir(parents=True, exist_ok=True)
        return {"status": "error", "message": "Input directory was empty"}

    output_path.mkdir(parents=True, exist_ok=True)

    # Discover files
    print(f"\n📁 Input Directory:  {input_dir}")
    print(f"📁 Output Directory: {output_dir}")
    print(f"📄 Supported Types:  {', '.join(get_supported_extensions())}")

    files = get_files_from_directory(input_dir, recursive=recursive)

    if not files:
        print(f"\n⚠️  No supported files found in {input_dir}")
        return {"status": "warning", "message": "No files to process"}

    print(f"\n📊 Found {len(files)} file(s) to process")
    print("-" * 60)

    # Initialize chunker
    chunker = create_chunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

    # Process files with progress bar
    all_chunks = []
    processed_count = 0
    error_count = 0
    file_summaries = []

    for file_path in tqdm(files, desc="Processing files", unit="file"):
        filename = Path(file_path).name
        tqdm.write(f"  📄 Processing: {filename}")

        document = process_file(file_path)

        if document:
            # Chunk the document
            chunks = chunker.chunk_document(document)
            all_chunks.extend(chunks)

            file_summaries.append({
                "filename": filename,
                "file_type": document.get("file_type", "unknown"),
                "chunks_created": len(chunks),
                "status": "success"
            })
            processed_count += 1
            tqdm.write(f"      ✅ Created {len(chunks)} chunks")
        else:
            file_summaries.append({
                "filename": filename,
                "status": "error"
            })
            error_count += 1

    # Build output
    print("\n" + "-" * 60)
    print("📦 Building knowledge base...")

    knowledge_base = {
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "pipeline_version": "1.0.0",
            "source_directory": str(input_dir),
            "chunk_config": {
                "chunk_size": CHUNK_SIZE,
                "chunk_overlap": CHUNK_OVERLAP
            },
            "statistics": {
                "total_files_found": len(files),
                "files_processed": processed_count,
                "files_errored": error_count,
                "total_chunks": len(all_chunks)
            },
            "file_summaries": file_summaries
        },
        "chunks": all_chunks
    }

    # Save output
    output_file = output_path / OUTPUT_FILENAME
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(knowledge_base, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n" + "=" * 60)
    print("✅ PIPELINE COMPLETE")
    print("=" * 60)
    print(f"\n📊 Results Summary:")
    print(f"   • Files processed:  {processed_count}/{len(files)}")
    print(f"   • Errors:           {error_count}")
    print(f"   • Total chunks:     {len(all_chunks)}")
    print(f"\n📁 Output saved to: {output_file}")
    print(f"   File size: {output_file.stat().st_size / 1024:.1f} KB")
    print("\n" + "=" * 60 + "\n")

    return {
        "status": "success",
        "output_file": str(output_file),
        "files_processed": processed_count,
        "total_chunks": len(all_chunks)
    }


def main():
    """
    Main entry point with CLI argument parsing.
    """
    parser = argparse.ArgumentParser(
        description="RAG Preprocessor - ETL Pipeline for document preprocessing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           Process files from ./data/raw/
  python main.py --input ./documents       Process from custom directory
  python main.py --output ./processed      Output to custom directory
  python main.py --no-recursive            Don't search subdirectories
        """
    )

    parser.add_argument(
        "--input", "-i",
        type=str,
        default=DEFAULT_INPUT_DIR,
        help=f"Input directory containing raw files (default: {DEFAULT_INPUT_DIR})"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for processed files (default: {DEFAULT_OUTPUT_DIR})"
    )

    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Don't search subdirectories"
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=CHUNK_SIZE,
        help=f"Maximum chunk size in characters (default: {CHUNK_SIZE})"
    )

    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=CHUNK_OVERLAP,
        help=f"Overlap between chunks (default: {CHUNK_OVERLAP})"
    )

    args = parser.parse_args()

    # Update global config if custom values provided
    global CHUNK_SIZE, CHUNK_OVERLAP
    CHUNK_SIZE = args.chunk_size
    CHUNK_OVERLAP = args.chunk_overlap

    # Run pipeline
    result = run_pipeline(
        input_dir=args.input,
        output_dir=args.output,
        recursive=not args.no_recursive
    )

    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    exit(main())
