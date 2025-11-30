#!/usr/bin/env python3
"""
Update headers and footers across all HTML pages to match index.html
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

def extract_section(content, start_marker, end_marker):
    """Extract a section between two markers"""
    pattern = f"{re.escape(start_marker)}.*?{re.escape(end_marker)}"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(0)
    return None

def replace_section(content, new_section, start_marker, end_marker):
    """Replace a section between two markers"""
    pattern = f"{re.escape(start_marker)}.*?{re.escape(end_marker)}"
    return re.sub(pattern, new_section, content, flags=re.DOTALL)

def main():
    print("Starting header and footer updates...")

    # Read index.html as the source
    index_path = BASE_DIR / "index.html"
    if not index_path.exists():
        print(f"Error: {index_path} not found!")
        return

    index_content = read_file(index_path)

    # Extract mobile menu from index.html
    mobile_menu_start = '<!--==============================\n    Mobile Menu\n    ============================== -->'
    mobile_menu_end = '<!--==============================\n    Popup Search Box\n    ============================== -->'

    mobile_menu = extract_section(index_content, mobile_menu_start, mobile_menu_end)

    # Extract header from index.html
    header_start = '<!--==============================\n    Header Area\n    ==============================-->'
    header_end = '<!--********************************\n\t\t\tStart Main Content\n\t  ******************************** -->'

    header = extract_section(index_content, header_start, header_end)

    # Extract footer from index.html
    footer_start = '<!--==============================\n\t\t\tFooter Area\n\t==============================-->'
    footer_end = '<!-- Scroll To Top -->'

    footer = extract_section(index_content, footer_start, footer_end)

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
        backup_path = BASE_DIR / f"{page}.bak"
        page_content = read_file(page_path)
        write_file(backup_path, page_content)

        # Replace mobile menu
        if mobile_menu:
            page_content = replace_section(page_content, mobile_menu, mobile_menu_start, mobile_menu_end)

        # Replace header
        if header:
            page_content = replace_section(page_content, header, header_start, header_end)

        # Replace footer
        if footer:
            page_content = replace_section(page_content, footer, footer_start, footer_end)

        # Write updated content
        write_file(page_path, page_content)
        print(f"✓ Completed {page}")

    print("\nAll updates completed!")

if __name__ == "__main__":
    main()
