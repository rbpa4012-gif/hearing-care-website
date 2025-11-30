#!/usr/bin/env python3
"""
Update headers and footers across all HTML pages to match index.html
Uses more robust regex patterns to handle variations in whitespace
"""

import re
from pathlib import Path

# Base directory
BASE_DIR = Path("/Volumes/Mac Studio 4TB/12. CLIENTS/Hearing Care version two")

# Pages to update (excluding index.html which is the source)
PAGES = [
    "about.html",
    "contact.html",
    "service.html",
    "service-details.html",
    "booking.html",
    "404.html",
    "blog.html",
    "blog-details.html",
    "portfolio.html",
    "portfolio-details.html",
    "team.html",
    "team-details.html",
]

def read_file(filepath):
    """Read file content"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    """Write content to file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    print("Starting header and footer updates...")

    # Read index.html as the source
    index_path = BASE_DIR / "index.html"
    if not index_path.exists():
        print(f"Error: {index_path} not found!")
        return

    index_content = read_file(index_path)

    # Extract mobile menu from index.html (more flexible regex)
    mobile_menu_pattern = r'(<!--={30,}\s*Mobile Menu\s*={30,}.*?-->.*?)(<!--={30,}\s*Popup Search Box\s*={30,}.*?-->)'
    mobile_menu_match = re.search(mobile_menu_pattern, index_content, re.DOTALL)
    mobile_menu = mobile_menu_match.group(0) if mobile_menu_match else None

    # Extract header from index.html
    header_pattern = r'(<!--={30,}\s*Header Area\s*={30,}.*?-->.*?)(<!--\*{30,}.*?Start Main Content.*?\*{30,}.*?-->)'
    header_match = re.search(header_pattern, index_content, re.DOTALL)
    header = header_match.group(0) if header_match else None

    # Extract footer from index.html
    footer_pattern = r'(<!--={30,}\s*Footer Area\s*={30,}.*?-->.*?)(<!-- Scroll To Top -->)'
    footer_match = re.search(footer_pattern, index_content, re.DOTALL)
    footer = footer_match.group(0) if footer_match else None

    if not mobile_menu:
        print("Warning: Could not extract mobile menu from index.html")
    if not header:
        print("Warning: Could not extract header from index.html")
    if not footer:
        print("Warning: Could not extract footer from index.html")

    # Update each page
    for page in PAGES:
        page_path = BASE_DIR / page
        if not page_path.exists():
            print(f"✗ File not found: {page}")
            continue

        print(f"Updating {page}...")

        # Create backup
        backup_path = BASE_DIR / f"{page}.bak2"
        page_content = read_file(page_path)
        write_file(backup_path, page_content)

        # Replace mobile menu
        if mobile_menu:
            page_content = re.sub(mobile_menu_pattern, mobile_menu, page_content, flags=re.DOTALL)

        # Replace header
        if header:
            page_content = re.sub(header_pattern, header, page_content, flags=re.DOTALL)

        # Replace footer
        if footer:
            page_content = re.sub(footer_pattern, footer, page_content, flags=re.DOTALL)

        # Write updated content
        write_file(page_path, page_content)
        print(f"✓ Completed {page}")

    print("\nAll updates completed!")

if __name__ == "__main__":
    main()
