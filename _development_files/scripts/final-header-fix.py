#!/usr/bin/env python3
"""
Final fix for navigation menus across all pages
"""

import re
from pathlib import Path

# Base directory
BASE_DIR = Path("/Volumes/Mac Studio 4TB/12. CLIENTS/Hearing Care version two")

# Pages to update (excluding index.html)
PAGES = [
    "about.html",
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

# The correct navigation menu HTML
CORRECT_NAV = '''                            <div class="col">
                                <nav class="main-menu menu-style1 d-none d-lg-block">
                                    <ul>
                                        <li>
                                            <a href="index.html">Home</a>
                                        </li>
                                        <li>
                                            <a href="about.html">About Us</a>
                                        </li>
                                        <li class="menu-item-has-children">
                                            <a href="service.html">Hearing Services</a>
                                            <ul class="sub-menu">
                                                <li><a href="service.html">All Services</a></li>
                                                <li><a href="service-details.html">Hearing Aid Fittings and Adjustments</a></li>
                                                <li><a href="service-details.html">Hearing Protection</a></li>
                                                <li><a href="service-details.html">Tinnitus Management</a></li>
                                                <li><a href="service-details.html">Comprehensive Hearing Assessments for Adults</a></li>
                                                <li><a href="service-details.html">Screening Tests</a></li>
                                                <li><a href="service-details.html">Hearing Aid Repairs and Maintenance</a></li>
                                                <li><a href="service-details.html">Custom Earplugs</a></li>
                                                <li><a href="service-details.html">Workplace Hearing Tests</a></li>
                                            </ul>
                                        </li>
                                        <li>
                                            <a href="contact.html">Contact</a>
                                        </li>
                                        <li>
                                            <a href="booking.html">Book an Appointment</a>
                                        </li>
                                    </ul>
                                </nav>
                            </div>'''

def main():
    print("Fixing navigation menus...")

    for page in PAGES:
        page_path = BASE_DIR / page
        if not page_path.exists():
            print(f"✗ File not found: {page}")
            continue

        print(f"Updating {page}...")

        # Read the file
        with open(page_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find and replace the navigation section
        # Pattern to match the nav section
        pattern = r'<div class="col">\s*<nav class="main-menu menu-style1 d-none d-lg-block">.*?</nav>\s*</div>'

        # Replace with correct navigation
        updated_content = re.sub(pattern, CORRECT_NAV, content, flags=re.DOTALL)

        # Write back
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        print(f"✓ Completed {page}")

    print("\nAll navigation menus fixed!")

if __name__ == "__main__":
    main()
