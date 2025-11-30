# Generate Image with Nano Banana

Generate an image using Google's Nano Banana (Gemini) image generation API.

## Instructions

When the user provides an image description or prompt, use the Nano Banana generator to create the image.

**Step 1:** Check if the API key is configured by running:
```bash
python3 tools/nano_banana.py --setup
```

**Step 2:** Generate the image with the user's prompt:
```bash
python3 tools/nano_banana.py "$ARGUMENTS"
```

**Step 3:** Report the output path and any model notes to the user.

## Prompt Tips for Best Results

- Describe the scene narratively, don't just list keywords
- Include lighting details (soft, natural, studio, etc.)
- Specify style (photorealistic, illustration, medical, etc.)
- For hearing care content, include professional/healthcare context

## Example Prompts

- "Professional photograph of modern hearing aids on a clean white surface, soft studio lighting"
- "Warm photo of audiologist consulting with elderly patient in modern clinic"
- "Medical illustration of human ear anatomy, educational diagram style"
