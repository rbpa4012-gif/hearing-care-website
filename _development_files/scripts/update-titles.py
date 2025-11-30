#!/usr/bin/env python3
"""
Update page titles and meta tags across all HTML pages
"""

import re
from pathlib import Path

# Base directory
BASE_DIR = Path("/Volumes/Mac Studio 4TB/12. CLIENTS/Hearing Care version two")

# Page title updates
TITLE_UPDATES = {
    "service.html": {
        "title": "Hearing Services - Hearing Care | Caloundra Audiologist",
        "description": "Comprehensive hearing services including hearing assessments, hearing aid fittings, tinnitus management, and custom ear protection. Professional audiology care in Caloundra.",
        "keywords": "hearing services, hearing assessment, hearing aid fitting, tinnitus management, custom earplugs, audiometry"
    },
    "service-details.html": {
        "title": "Hearing Service Details - Hearing Care | Expert Audiology",
        "description": "Detailed information about our hearing services. Professional hearing care tailored to your needs in Caloundra, QLD.",
        "keywords": "hearing service details, audiology services, hearing care Caloundra"
    },
    "booking.html": {
        "title": "Book Appointment - Hearing Care | Schedule Your Visit",
        "description": "Book your hearing assessment appointment with Hearing Care in Caloundra. Call (07) 5223 4444 or book online today.",
        "keywords": "book hearing appointment, hearing assessment booking, audiologist Caloundra"
    },
    "404.html": {
        "title": "Page Not Found - Hearing Care",
        "description": "The page you're looking for cannot be found. Return to Hearing Care homepage.",
        "keywords": "404, page not found"
    },
    "blog.html": {
        "title": "Blog - Hearing Care | Hearing Health Tips & News",
        "description": "Read the latest hearing health tips, news, and information from Hearing Care experts.",
        "keywords": "hearing health blog, audiology news, hearing care tips"
    },
    "blog-details.html": {
        "title": "Blog Article - Hearing Care | Hearing Health Information",
        "description": "Read detailed articles about hearing health and audiology from Hearing Care.",
        "keywords": "hearing health article, audiology information"
    },
    "portfolio.html": {
        "title": "Our Work - Hearing Care | Success Stories",
        "description": "See how Hearing Care has helped improve the lives of our clients in Caloundra.",
        "keywords": "hearing care success stories, client testimonials"
    },
    "portfolio-details.html": {
        "title": "Success Story - Hearing Care | Client Experience",
        "description": "Read about successful hearing care outcomes from our Caloundra clinic.",
        "keywords": "hearing care success, client story"
    },
    "team.html": {
        "title": "Our Team - Hearing Care | Meet Linda Whittaker",
        "description": "Meet the professional team at Hearing Care, led by qualified audiometrist Linda Whittaker.",
        "keywords": "hearing care team, Linda Whittaker, audiometrist Caloundra"
    },
    "team-details.html": {
        "title": "Team Member - Hearing Care | Our Professionals",
        "description": "Learn more about our hearing care professionals dedicated to your hearing health.",
        "keywords": "audiometrist, hearing care professional"
    }
}

def update_meta_tags(content, title, description, keywords):
    """Update title and meta tags in HTML content"""

    # Update title
    content = re.sub(
        r'<title>.*?</title>',
        f'<title>{title}</title>',
        content,
        flags=re.DOTALL
    )

    # Update author
    content = re.sub(
        r'<meta name="author" content="[^"]*">',
        '<meta name="author" content="Hearing Care">',
        content
    )

    # Update description
    content = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{description}">',
        content
    )

    # Update keywords
    content = re.sub(
        r'<meta name="keywords" content="[^"]*">',
        f'<meta name="keywords" content="{keywords}">',
        content
    )

    return content

def main():
    print("Updating page titles and meta tags...")

    for page, meta_data in TITLE_UPDATES.items():
        page_path = BASE_DIR / page
        if not page_path.exists():
            print(f"✗ File not found: {page}")
            continue

        print(f"Updating {page}...")

        # Read the file
        with open(page_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update meta tags
        updated_content = update_meta_tags(
            content,
            meta_data["title"],
            meta_data["description"],
            meta_data["keywords"]
        )

        # Write back
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        print(f"✓ Completed {page}")

    print("\nAll page titles and meta tags updated!")

if __name__ == "__main__":
    main()
