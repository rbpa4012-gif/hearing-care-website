#!/usr/bin/env python3
"""
Nano Banana Image Generator - Python Version
Google Gemini Image Generation for VS Code + Claude Code Workflow

Usage:
    python nano_banana.py "Your image prompt"
    python nano_banana.py --batch prompts.json
    python nano_banana.py --setup
"""

import os
import sys
import json
import base64
import argparse
from pathlib import Path
from datetime import datetime

try:
    from google import genai
    from google.genai import types
    HAS_SDK = True
except ImportError:
    HAS_SDK = False
    import urllib.request
    import urllib.error

# Configuration
CONFIG = {
    'model': 'gemini-2.0-flash-exp',  # or 'gemini-2.5-flash-preview-image-generation'
    'output_dir': './assets/img/generated',
    'aspect_ratio': '16:9',
}


def get_api_key():
    """Load API key from environment or config files."""
    # Check environment variable
    if os.environ.get('GOOGLE_AI_API_KEY'):
        return os.environ['GOOGLE_AI_API_KEY']

    # Check project .env
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        content = env_path.read_text()
        for line in content.splitlines():
            if line.startswith('GOOGLE_AI_API_KEY='):
                return line.split('=', 1)[1].strip().strip('"\'')

    # Check global config
    global_env = Path.home() / '.claude' / 'api-keys.env'
    if global_env.exists():
        content = global_env.read_text()
        for line in content.splitlines():
            if line.startswith('GOOGLE_AI_API_KEY='):
                return line.split('=', 1)[1].strip().strip('"\'')

    return None


def generate_with_sdk(prompt: str, output_name: str = None) -> dict:
    """Generate image using official Google Gen AI SDK."""
    api_key = get_api_key()
    if not api_key:
        raise ValueError("No API key found")

    client = genai.Client(api_key=api_key)

    print(f"\n🍌 Generating with Nano Banana ({CONFIG['model']})...")
    print(f"📝 Prompt: \"{prompt[:100]}{'...' if len(prompt) > 100 else ''}\"")

    response = client.models.generate_content(
        model=CONFIG['model'],
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
        )
    )

    # Extract image and text from response
    image_data = None
    text_response = ""

    for part in response.candidates[0].content.parts:
        if hasattr(part, 'inline_data') and part.inline_data:
            image_data = part.inline_data.data
        if hasattr(part, 'text') and part.text:
            text_response = part.text

    if not image_data:
        if text_response:
            print(f"\n📝 Model response: {text_response}")
        raise ValueError("No image in response - try adjusting your prompt")

    # Save image
    output_dir = Path(CONFIG['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = output_name or f"nano-banana-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
    output_path = output_dir / filename

    image_bytes = base64.b64decode(image_data) if isinstance(image_data, str) else image_data
    output_path.write_bytes(image_bytes)

    print(f"\n✅ Image saved: {output_path}")
    if text_response:
        print(f"📝 Model notes: {text_response}")

    return {
        'path': str(output_path),
        'filename': filename,
        'prompt': prompt,
        'text': text_response
    }


def generate_with_rest(prompt: str, output_name: str = None) -> dict:
    """Generate image using REST API (no SDK required)."""
    api_key = get_api_key()
    if not api_key:
        raise ValueError("No API key found")

    print(f"\n🍌 Generating with Nano Banana ({CONFIG['model']})...")
    print(f"📝 Prompt: \"{prompt[:100]}{'...' if len(prompt) > 100 else ''}\"")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{CONFIG['model']}:generateContent?key={api_key}"

    payload = json.dumps({
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"]
        }
    }).encode('utf-8')

    req = urllib.request.Request(
        url,
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            data = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        try:
            error_data = json.loads(error_body)
            raise ValueError(f"API Error: {error_data.get('error', {}).get('message', error_body)}")
        except json.JSONDecodeError:
            raise ValueError(f"API Error ({e.code}): {error_body}")

    # Extract image
    candidates = data.get('candidates', [])
    if not candidates:
        raise ValueError("No response from API")

    parts = candidates[0].get('content', {}).get('parts', [])
    image_data = None
    text_response = ""

    for part in parts:
        if 'inlineData' in part:
            image_data = part['inlineData']['data']
        if 'text' in part:
            text_response = part['text']

    if not image_data:
        if text_response:
            print(f"\n📝 Model response: {text_response}")
        raise ValueError("No image in response")

    # Save image
    output_dir = Path(CONFIG['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = output_name or f"nano-banana-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
    output_path = output_dir / filename

    image_bytes = base64.b64decode(image_data)
    output_path.write_bytes(image_bytes)

    print(f"\n✅ Image saved: {output_path}")
    if text_response:
        print(f"📝 Model notes: {text_response}")

    return {
        'path': str(output_path),
        'filename': filename,
        'prompt': prompt,
        'text': text_response
    }


def generate_image(prompt: str, output_name: str = None) -> dict:
    """Generate image using best available method."""
    if HAS_SDK:
        return generate_with_sdk(prompt, output_name)
    else:
        return generate_with_rest(prompt, output_name)


def batch_generate(prompts_file: str) -> list:
    """Generate multiple images from a JSON file."""
    with open(prompts_file) as f:
        prompts = json.load(f)

    results = []
    for i, item in enumerate(prompts, 1):
        prompt = item.get('prompt') or item
        filename = item.get('fileName') or item.get('filename')

        print(f"\n{'='*50}")
        print(f"Image {i}/{len(prompts)}")

        try:
            result = generate_image(prompt, filename)
            results.append(result)
        except Exception as e:
            print(f"❌ Failed: {e}")
            results.append({'error': str(e), 'prompt': prompt})

        # Rate limiting
        if i < len(prompts):
            import time
            time.sleep(2)

    return results


def show_setup():
    """Display setup instructions."""
    print("""
🍌 Nano Banana Setup Instructions
==================================

1. Get your API Key:
   → Go to https://aistudio.google.com/apikey
   → Click "Create API Key"
   → Select or create a Google Cloud project

2. Configure the API Key (choose one method):

   Method A - Environment Variable (recommended):
   export GOOGLE_AI_API_KEY="your-api-key-here"

   Method B - Project .env file:
   Create .env in project root with:
   GOOGLE_AI_API_KEY=your-api-key-here

   Method C - Global config:
   Create ~/.claude/api-keys.env with:
   GOOGLE_AI_API_KEY=your-api-key-here

3. Install SDK (optional, for better performance):
   pip install google-genai

4. Pricing (as of 2025):
   - Gemini 2.5 Flash Image: ~$0.039/image
   - Nano Banana Pro (4K): ~$0.24/image

5. Test your setup:
   python nano_banana.py "A test image of a banana"
""")


def main():
    parser = argparse.ArgumentParser(
        description='🍌 Nano Banana Image Generator - Google Gemini for VS Code'
    )
    parser.add_argument('prompt', nargs='?', help='Image generation prompt')
    parser.add_argument('--batch', metavar='FILE', help='Generate from JSON prompts file')
    parser.add_argument('--output', '-o', metavar='NAME', help='Output filename')
    parser.add_argument('--setup', action='store_true', help='Show setup instructions')

    args = parser.parse_args()

    if args.setup:
        show_setup()
        return

    # Check API key
    if not get_api_key():
        print("\n❌ ERROR: No API key found!")
        print("Run with --setup for configuration instructions")
        sys.exit(1)

    if args.batch:
        results = batch_generate(args.batch)
        print(f"\n📊 Batch complete: {len([r for r in results if 'error' not in r])}/{len(results)} successful")
        return

    if not args.prompt:
        parser.print_help()
        return

    try:
        generate_image(args.prompt, args.output)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
