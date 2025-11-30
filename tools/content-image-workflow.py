#!/usr/bin/env python3
"""
Content + Image Generation Workflow
Automatically generates images based on content topics

Usage:
    python content-image-workflow.py --topic "hearing aids"
    python content-image-workflow.py --html page.html
    python content-image-workflow.py --interactive
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Import the nano_banana module
sys.path.insert(0, str(Path(__file__).parent))
from nano_banana import generate_image, get_api_key

# Predefined image prompts for hearing care topics
HEARING_CARE_PROMPTS = {
    'hearing aids': [
        {
            'prompt': 'Professional product photograph of modern behind-the-ear hearing aids, sleek silver design, on clean white marble surface, soft studio lighting, high-end medical device photography',
            'filename': 'hearing-aids-modern.png',
            'alt': 'Modern behind-the-ear hearing aids'
        },
        {
            'prompt': 'Close-up photograph of tiny in-ear hearing aid (ITE) being held between fingers, showing miniature technology, soft focus background, professional medical photography',
            'filename': 'hearing-aid-ite.png',
            'alt': 'In-the-ear hearing aid'
        }
    ],
    'audiologist': [
        {
            'prompt': 'Warm photograph of female audiologist in white coat consulting with senior male patient in modern hearing clinic, professional healthcare setting, natural window lighting, caring atmosphere',
            'filename': 'audiologist-consultation.png',
            'alt': 'Audiologist consulting with patient'
        },
        {
            'prompt': 'Professional audiologist performing hearing test on patient wearing headphones in soundproof booth, medical equipment visible, clinical but welcoming environment',
            'filename': 'hearing-test-booth.png',
            'alt': 'Hearing test in progress'
        }
    ],
    'hearing protection': [
        {
            'prompt': 'Array of custom hearing protection devices including musicians earplugs, industrial earmuffs, and swimming plugs, arranged on slate surface, professional product photography',
            'filename': 'hearing-protection-range.png',
            'alt': 'Range of hearing protection devices'
        },
        {
            'prompt': 'Construction worker wearing proper hearing protection earmuffs on building site, workplace safety, professional occupational health photography, Australian setting',
            'filename': 'workplace-hearing-protection.png',
            'alt': 'Worker with hearing protection'
        }
    ],
    'tinnitus': [
        {
            'prompt': 'Abstract artistic visualization of tinnitus experience, sound waves and ripples emanating from ear silhouette, calming blue and purple gradient tones, medical awareness illustration style',
            'filename': 'tinnitus-visualization.png',
            'alt': 'Artistic representation of tinnitus'
        },
        {
            'prompt': 'Person in peaceful meditation pose practicing tinnitus management techniques, serene indoor setting with plants, soft natural lighting, wellness and healthcare theme',
            'filename': 'tinnitus-management.png',
            'alt': 'Tinnitus management through relaxation'
        }
    ],
    'ear anatomy': [
        {
            'prompt': 'Detailed medical illustration of human ear cross-section showing outer ear, middle ear, and inner ear anatomy, professional educational diagram style, labeled anatomical drawing, clean white background',
            'filename': 'ear-anatomy-diagram.png',
            'alt': 'Human ear anatomy diagram'
        }
    ],
    'children hearing': [
        {
            'prompt': 'Happy young child (age 5-6) during pediatric hearing assessment, wearing child-sized headphones, colorful friendly clinic environment, reassuring female audiologist, warm cheerful atmosphere',
            'filename': 'pediatric-hearing-test.png',
            'alt': 'Child during hearing test'
        }
    ],
    'seniors': [
        {
            'prompt': 'Joyful senior couple in their 70s having conversation outdoors in Australian park setting, active aging lifestyle, natural golden hour lighting, hearing health awareness theme',
            'filename': 'seniors-conversation.png',
            'alt': 'Senior couple enjoying conversation'
        },
        {
            'prompt': 'Elderly man confidently adjusting his modern hearing aid, dignified portrait, soft natural lighting, positive aging and hearing health message',
            'filename': 'senior-hearing-aid-user.png',
            'alt': 'Senior using hearing aid'
        }
    ],
    'ear wax': [
        {
            'prompt': 'Clean professional medical photograph of ear examination with otoscope, healthcare provider examining patient ear, clinical setting, proper medical procedure documentation style',
            'filename': 'ear-examination.png',
            'alt': 'Professional ear examination'
        }
    ],
    'music hearing': [
        {
            'prompt': 'Professional musician wearing custom musicians earplugs while playing guitar, concert stage setting with dramatic lighting, hearing protection for performers',
            'filename': 'musician-hearing-protection.png',
            'alt': 'Musician with hearing protection'
        }
    ]
}


def find_matching_topics(content: str) -> list:
    """Find topics in content that match our predefined prompts."""
    content_lower = content.lower()
    matches = []

    for topic, prompts in HEARING_CARE_PROMPTS.items():
        # Check for topic keywords
        keywords = topic.split()
        if any(kw in content_lower for kw in keywords):
            matches.append(topic)

    return matches


def extract_topics_from_html(html_path: str) -> list:
    """Extract topics from HTML file content."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Basic text extraction (remove HTML tags)
    import re
    text = re.sub(r'<[^>]+>', ' ', content)
    text = re.sub(r'\s+', ' ', text)

    return find_matching_topics(text)


def generate_for_topic(topic: str, output_dir: str = None) -> list:
    """Generate all images for a specific topic."""
    if topic not in HEARING_CARE_PROMPTS:
        print(f"❌ Unknown topic: {topic}")
        print(f"Available topics: {', '.join(HEARING_CARE_PROMPTS.keys())}")
        return []

    prompts = HEARING_CARE_PROMPTS[topic]
    results = []

    print(f"\n🎨 Generating {len(prompts)} image(s) for topic: {topic}")

    for i, item in enumerate(prompts, 1):
        print(f"\n--- Image {i}/{len(prompts)} ---")

        try:
            if output_dir:
                # Create topic subfolder
                topic_dir = Path(output_dir) / topic.replace(' ', '-')
                topic_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(topic_dir / item['filename'])
            else:
                output_path = item['filename']

            result = generate_image(item['prompt'], output_path)
            result['alt'] = item.get('alt', '')
            results.append(result)

            # Rate limiting
            if i < len(prompts):
                import time
                time.sleep(2)

        except Exception as e:
            print(f"❌ Failed: {e}")
            results.append({'error': str(e), 'prompt': item['prompt']})

    return results


def interactive_mode():
    """Interactive image generation mode."""
    print("""
🍌 Nano Banana Interactive Mode
================================

Available topics:
""")
    for i, topic in enumerate(HEARING_CARE_PROMPTS.keys(), 1):
        count = len(HEARING_CARE_PROMPTS[topic])
        print(f"  {i}. {topic} ({count} images)")

    print("""
Commands:
  - Enter topic name or number to generate images
  - Enter 'custom' for custom prompt
  - Enter 'all' to generate all topics
  - Enter 'quit' to exit
""")

    topics = list(HEARING_CARE_PROMPTS.keys())

    while True:
        choice = input("\n🎨 Enter choice: ").strip().lower()

        if choice in ('quit', 'exit', 'q'):
            break

        if choice == 'all':
            for topic in topics:
                generate_for_topic(topic)
            continue

        if choice == 'custom':
            prompt = input("Enter your prompt: ").strip()
            if prompt:
                try:
                    generate_image(prompt)
                except Exception as e:
                    print(f"❌ Error: {e}")
            continue

        # Check if it's a number
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(topics):
                generate_for_topic(topics[idx])
                continue
        except ValueError:
            pass

        # Check if it's a topic name
        if choice in topics:
            generate_for_topic(choice)
        else:
            print(f"❌ Unknown option: {choice}")


def main():
    parser = argparse.ArgumentParser(
        description='🍌 Content + Image Generation Workflow'
    )
    parser.add_argument('--topic', help='Generate images for specific topic')
    parser.add_argument('--html', help='Extract topics from HTML file')
    parser.add_argument('--output', '-o', help='Output directory')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Interactive mode')
    parser.add_argument('--list', action='store_true',
                        help='List available topics')

    args = parser.parse_args()

    # Check API key
    if not get_api_key():
        print("\n❌ ERROR: No API key found!")
        print("Run: python nano_banana.py --setup")
        sys.exit(1)

    if args.list:
        print("\n📋 Available Topics:\n")
        for topic, prompts in HEARING_CARE_PROMPTS.items():
            print(f"  • {topic} ({len(prompts)} images)")
            for p in prompts:
                print(f"      - {p['filename']}")
        return

    if args.interactive:
        interactive_mode()
        return

    if args.html:
        topics = extract_topics_from_html(args.html)
        if not topics:
            print("No matching topics found in HTML")
            return

        print(f"Found topics: {', '.join(topics)}")
        for topic in topics:
            generate_for_topic(topic, args.output)
        return

    if args.topic:
        generate_for_topic(args.topic, args.output)
        return

    parser.print_help()


if __name__ == '__main__':
    main()
