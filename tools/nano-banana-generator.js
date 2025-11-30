#!/usr/bin/env node
/**
 * Nano Banana Image Generator for VS Code + Claude Code Workflow
 * Google Gemini Image Generation API Integration
 *
 * Usage:
 *   node nano-banana-generator.js "Your image prompt here"
 *   node nano-banana-generator.js --file prompts.json
 *   node nano-banana-generator.js --content "article text" --auto-generate
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// Configuration
const CONFIG = {
    // Model options: 'gemini-2.5-flash-preview-image-generation' (fast/cheap) or 'gemini-2.0-flash-exp'
    model: 'gemini-2.0-flash-exp',
    outputDir: './assets/img/generated',
    aspectRatio: '16:9',
    // For Pro model: '1K', '2K', '4K'
    imageSize: '1K'
};

// Load API key from environment or .env file
function getApiKey() {
    // Check environment variable first
    if (process.env.GOOGLE_AI_API_KEY) {
        return process.env.GOOGLE_AI_API_KEY;
    }

    // Check .env file
    const envPath = path.join(__dirname, '..', '.env');
    if (fs.existsSync(envPath)) {
        const envContent = fs.readFileSync(envPath, 'utf8');
        const match = envContent.match(/GOOGLE_AI_API_KEY=(.+)/);
        if (match) return match[1].trim();
    }

    // Check global config
    const globalEnvPath = path.join(process.env.HOME, '.claude', 'api-keys.env');
    if (fs.existsSync(globalEnvPath)) {
        const envContent = fs.readFileSync(globalEnvPath, 'utf8');
        const match = envContent.match(/GOOGLE_AI_API_KEY=(.+)/);
        if (match) return match[1].trim();
    }

    console.error('\n❌ ERROR: No API key found!');
    console.error('\nSetup instructions:');
    console.error('1. Go to https://aistudio.google.com/apikey');
    console.error('2. Create an API key');
    console.error('3. Add to your environment:');
    console.error('   export GOOGLE_AI_API_KEY="your-api-key-here"');
    console.error('\n   Or create a .env file in project root with:');
    console.error('   GOOGLE_AI_API_KEY=your-api-key-here\n');
    process.exit(1);
}

// Generate image using Gemini API
async function generateImage(prompt, outputFileName) {
    const apiKey = getApiKey();

    const requestBody = JSON.stringify({
        contents: [{
            parts: [{
                text: prompt
            }]
        }],
        generationConfig: {
            responseModalities: ['TEXT', 'IMAGE']
        }
    });

    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'generativelanguage.googleapis.com',
            path: `/v1beta/models/${CONFIG.model}:generateContent?key=${apiKey}`,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(requestBody)
            }
        };

        console.log(`\n🍌 Generating image with Nano Banana (${CONFIG.model})...`);
        console.log(`📝 Prompt: "${prompt.substring(0, 100)}${prompt.length > 100 ? '...' : ''}"`);

        const req = https.request(options, (res) => {
            let data = '';

            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const response = JSON.parse(data);

                    if (response.error) {
                        reject(new Error(`API Error: ${response.error.message}`));
                        return;
                    }

                    // Extract image from response
                    const candidates = response.candidates || [];
                    if (candidates.length === 0) {
                        reject(new Error('No image generated - try a different prompt'));
                        return;
                    }

                    const parts = candidates[0].content?.parts || [];
                    let imageData = null;
                    let textResponse = '';

                    for (const part of parts) {
                        if (part.inlineData) {
                            imageData = part.inlineData.data;
                        }
                        if (part.text) {
                            textResponse = part.text;
                        }
                    }

                    if (!imageData) {
                        // Model might have returned text instead of image
                        if (textResponse) {
                            console.log('\n📝 Model response:', textResponse);
                        }
                        reject(new Error('No image in response - the prompt may need adjustment'));
                        return;
                    }

                    // Save image
                    const outputDir = path.resolve(CONFIG.outputDir);
                    if (!fs.existsSync(outputDir)) {
                        fs.mkdirSync(outputDir, { recursive: true });
                    }

                    const fileName = outputFileName || `nano-banana-${Date.now()}.png`;
                    const outputPath = path.join(outputDir, fileName);

                    const imageBuffer = Buffer.from(imageData, 'base64');
                    fs.writeFileSync(outputPath, imageBuffer);

                    console.log(`\n✅ Image saved: ${outputPath}`);
                    if (textResponse) {
                        console.log(`📝 Model notes: ${textResponse}`);
                    }

                    resolve({
                        path: outputPath,
                        fileName: fileName,
                        prompt: prompt,
                        text: textResponse
                    });

                } catch (e) {
                    reject(new Error(`Failed to parse response: ${e.message}`));
                }
            });
        });

        req.on('error', reject);
        req.write(requestBody);
        req.end();
    });
}

// Generate multiple images from a JSON file
async function generateFromFile(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const prompts = JSON.parse(content);

    const results = [];
    for (const item of prompts) {
        try {
            const result = await generateImage(
                item.prompt,
                item.fileName || null
            );
            results.push(result);
            // Rate limiting - wait between requests
            await new Promise(r => setTimeout(r, 2000));
        } catch (err) {
            console.error(`❌ Failed: ${err.message}`);
            results.push({ error: err.message, prompt: item.prompt });
        }
    }

    return results;
}

// Auto-generate image prompts from content
function generatePromptsFromContent(content, topic = 'hearing care') {
    // Extract key themes from content
    const prompts = [];

    // Common hearing care image suggestions
    const imageTypes = [
        {
            keywords: ['hearing aid', 'device', 'technology'],
            prompt: `Professional photograph of modern hearing aids on a clean white surface, medical device photography, soft studio lighting, ${topic}, high quality product shot`
        },
        {
            keywords: ['audiologist', 'consultation', 'appointment'],
            prompt: `Warm photograph of an audiologist consulting with an elderly patient in a modern clinic, professional healthcare setting, natural lighting, caring atmosphere`
        },
        {
            keywords: ['ear', 'anatomy', 'hearing loss'],
            prompt: `Medical illustration of human ear anatomy, cross-section diagram, professional healthcare infographic style, clean educational design, labeled parts`
        },
        {
            keywords: ['protection', 'earplugs', 'noise'],
            prompt: `Professional product photograph of custom hearing protection earplugs, industrial and music settings, safety equipment, clean white background`
        },
        {
            keywords: ['tinnitus', 'ringing', 'sound'],
            prompt: `Abstract artistic representation of tinnitus, sound waves emanating from ear silhouette, calming blue and purple tones, medical awareness illustration`
        },
        {
            keywords: ['child', 'pediatric', 'kids'],
            prompt: `Cheerful photograph of a young child during a hearing test, friendly pediatric audiology setting, colorful environment, reassuring healthcare atmosphere`
        },
        {
            keywords: ['workplace', 'industrial', 'occupational'],
            prompt: `Industrial worker wearing proper hearing protection in a factory setting, workplace safety, professional occupational health photography`
        },
        {
            keywords: ['senior', 'elderly', 'aging'],
            prompt: `Warm portrait of happy senior couple enjoying conversation, active aging lifestyle, natural outdoor lighting, hearing health awareness`
        }
    ];

    const contentLower = content.toLowerCase();

    for (const type of imageTypes) {
        if (type.keywords.some(kw => contentLower.includes(kw))) {
            prompts.push({
                prompt: type.prompt,
                keywords: type.keywords.filter(kw => contentLower.includes(kw))
            });
        }
    }

    // Default prompt if no matches
    if (prompts.length === 0) {
        prompts.push({
            prompt: `Professional healthcare photograph related to ${topic}, modern medical clinic setting, warm and welcoming atmosphere, high quality stock photo style`,
            keywords: ['default']
        });
    }

    return prompts;
}

// Main CLI handler
async function main() {
    const args = process.argv.slice(2);

    if (args.length === 0) {
        console.log(`
🍌 Nano Banana Image Generator
================================
Google Gemini Image Generation for VS Code Workflow

Usage:
  node nano-banana-generator.js "Your detailed image prompt"
  node nano-banana-generator.js --file prompts.json
  node nano-banana-generator.js --content "article text" --auto-generate
  node nano-banana-generator.js --setup

Options:
  --file <path>       Generate images from JSON file with prompts
  --content <text>    Auto-generate prompts from content
  --output <name>     Custom output filename
  --setup             Show API key setup instructions

Examples:
  node nano-banana-generator.js "Professional photo of modern hearing aids"
  node nano-banana-generator.js --file ./image-prompts.json

Prompts JSON format:
  [
    { "prompt": "Image description", "fileName": "output-name.png" },
    { "prompt": "Another image" }
  ]
`);
        return;
    }

    // Setup instructions
    if (args.includes('--setup')) {
        console.log(`
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

3. Pricing (as of 2025):
   - Gemini 2.5 Flash Image: ~$0.039/image
   - Nano Banana Pro (4K): ~$0.24/image

4. Test your setup:
   node nano-banana-generator.js "A test image of a banana"
`);
        return;
    }

    // File-based generation
    if (args.includes('--file')) {
        const fileIndex = args.indexOf('--file') + 1;
        if (fileIndex >= args.length) {
            console.error('❌ Please specify a file path');
            process.exit(1);
        }
        const results = await generateFromFile(args[fileIndex]);
        console.log('\n📊 Generation complete:', results.length, 'images processed');
        return;
    }

    // Content-based auto-generation
    if (args.includes('--content') && args.includes('--auto-generate')) {
        const contentIndex = args.indexOf('--content') + 1;
        const content = args[contentIndex];
        const prompts = generatePromptsFromContent(content);

        console.log(`\n🔍 Found ${prompts.length} relevant image types for your content:\n`);
        prompts.forEach((p, i) => {
            console.log(`${i + 1}. Keywords: ${p.keywords.join(', ')}`);
            console.log(`   Prompt: ${p.prompt.substring(0, 80)}...`);
        });

        console.log('\n💡 To generate these images, save prompts to JSON and use --file option');

        // Save prompts to file
        const outputPath = path.join(__dirname, 'auto-prompts.json');
        fs.writeFileSync(outputPath, JSON.stringify(prompts.map((p, i) => ({
            prompt: p.prompt,
            fileName: `auto-generated-${i + 1}.png`
        })), null, 2));
        console.log(`📝 Prompts saved to: ${outputPath}`);
        return;
    }

    // Single prompt generation
    let prompt = args[0];
    let outputName = null;

    if (args.includes('--output')) {
        const outputIndex = args.indexOf('--output') + 1;
        outputName = args[outputIndex];
    }

    // If prompt starts with --, it's probably a flag error
    if (prompt.startsWith('--')) {
        console.error('❌ Invalid option. Use --help for usage.');
        process.exit(1);
    }

    try {
        await generateImage(prompt, outputName);
    } catch (err) {
        console.error(`\n❌ Error: ${err.message}`);
        process.exit(1);
    }
}

main();
