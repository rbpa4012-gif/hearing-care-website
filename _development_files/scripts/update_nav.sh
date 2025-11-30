#!/bin/bash

# List of files to update (excluding workplace-hearing-screening.html and tinnitus-management-and-treatment.html as they're already correct)
FILES=(
  "hearing-aid-fittings-and-adjustments.html"
  "hearing-aids-technology-solutions.html"
  "hearing-aid-maintenance.html"
  "custom-earplugs.html"
  "hearing-protection.html"
  "service.html"
  "about.html"
  "contact.html"
)

for file in "${FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "Updating $file..."
    # This will be done manually through Edit tool
  fi
done
