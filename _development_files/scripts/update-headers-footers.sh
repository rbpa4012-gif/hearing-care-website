#!/bin/bash

# Script to update headers and footers across all HTML pages

# Define the pages to update (excluding index.html which is the source)
PAGES=(
    "contact.html"
    "service.html"
    "service-details.html"
    "booking.html"
    "404.html"
    "blog.html"
    "blog-details.html"
    "portfolio.html"
    "portfolio-details.html"
    "team.html"
    "team-details.html"
)

# Base directory
BASE_DIR="/Volumes/Mac Studio 4TB/12. CLIENTS/Hearing Care version two"

echo "Starting header and footer updates..."

for page in "${PAGES[@]}"; do
    if [ -f "$BASE_DIR/$page" ]; then
        echo "Updating $page..."

        # Create backup
        cp "$BASE_DIR/$page" "$BASE_DIR/${page}.bak"

        # Update mobile menu logo
        sed -i '' 's|<a href="index.html"><img src="assets/img/logo-dark.svg" alt="[^"]*">|<a href="index.html"><img src="assets/img/hearing-care-logo-header.svg" alt="Hearing Care">|g' "$BASE_DIR/$page"

        # Update footer logo
        sed -i '' 's|<a href="index.html"><img src="assets/img/logo.svg" alt="[^"]*">|<a href="index.html"><img src="assets/img/hearing-care-logo-white.svg" alt="Hearing Care">|g' "$BASE_DIR/$page"

        # Update copyright background color
        sed -i '' 's|<div class="copyright-wrap" style="background-color: #36556C;">|<div class="copyright-wrap" style="background-color: #E4F25A;">|g' "$BASE_DIR/$page"

        # Update copyright text color
        sed -i '' 's|<p class="copyright-text"><i class="fal fa-copyright"></i> Copyright 2025 - <a href="index.html">Hearing Care</a> All rights reserved.</p>|<p class="copyright-text" style="color: #36556C;"><i class="fal fa-copyright"></i> Copyright 2025 - <a href="index.html" style="color: #36556C;">Hearing Care</a> All rights reserved.</p>|g' "$BASE_DIR/$page"

        echo "✓ Completed $page"
    else
        echo "✗ File not found: $page"
    fi
done

echo "All updates completed!"
