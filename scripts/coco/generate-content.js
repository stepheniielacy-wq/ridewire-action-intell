#!/usr/bin/env node

/**
 * COCO AI Influencer - Content Generation Orchestrator
 *
 * Generates automotive diagnostic video content using a fully free,
 * open-source stack (no paid API keys or billing accounts required):
 * - Ollama (local open-source LLM): Script writing
 * - Piper TTS (local open-source neural voice): Voiceover
 * - ffmpeg (open-source): Assembles narration + a generated background
 *   into a real, uploadable MP4 video
 *
 * Falls back to a simple templated script / silent video if any of these
 * local tools are unavailable (e.g. running outside CI), so the pipeline
 * never crashes.
 *
 * DISCLAIMER: This tool generates AI-powered educational content.
 * All automotive information should be verified by qualified mechanics.
 * RideWire does not replace professional automotive repair services.
 */

require('dotenv').config();
const fs = require('fs').promises;
const path = require('path');
const { execFile } = require('child_process');
const { promisify } = require('util');
const execFileAsync = promisify(execFile);

const OLLAMA_URL = process.env.OLLAMA_URL || 'http://127.0.0.1:11434';
const OLLAMA_MODEL = process.env.OLLAMA_MODEL || 'llama3.2:1b';
const PIPER_MODEL_PATH = process.env.PIPER_MODEL_PATH || path.join(__dirname, '../../assets/voices/en_US-amy-medium.onnx');

class COCOContentGenerator {
  constructor() {
    this.outputDir = path.join(__dirname, '../../output/coco-videos');
  }

  /**
   * Generate video script using a local open-source LLM (Ollama).
   * Falls back to a plain templated script if Ollama isn't reachable.
   */
  async generateScript(topic, targetLength = 3) {
    console.log(`📝 Generating script for: ${topic}`);

    const prompt = `Create a ${targetLength}-minute YouTube video script about: "${topic}"

Requirements:
- Target audience: Car enthusiasts and DIY mechanics
- Tone: Professional but friendly, educational
- Include: Clear explanation, step-by-step guidance, safety warnings
- Always end with this exact disclaimer sentence: "This is educational content only. Always consult a qualified mechanic for vehicle repairs. RideWire does not replace professional automotive services."

Respond ONLY with strict JSON, no markdown, in this exact shape:
{"intro": "...", "mainContent": "...", "callToAction": "..."}`;

    try {
      const text = await this.callOllama(prompt);
      const parsed = this.extractJson(text);

      const script = {
        title: topic,
        intro: parsed.intro || `Today we're tackling: ${topic}`,
        mainContent: parsed.mainContent || 'Detailed explanation with step-by-step guidance.',
        callToAction: parsed.callToAction || 'Subscribe for more automotive AI tips. Visit RideWire AI Hub for diagnostic tools.',
        disclaimer: 'This is educational content only. Always consult a qualified mechanic for vehicle repairs. RideWire does not replace professional automotive services.',
        estimatedDuration: `${targetLength} minutes`,
        keywords: this.extractKeywords(topic),
        generatedBy: 'ollama:' + OLLAMA_MODEL
      };

      console.log('✅ Script generated successfully (open-source LLM)');
      return script;
    } catch (error) {
      console.warn(`⚠️  Local AI writer unavailable (${error.message}), using templated fallback script`);
      return {
        title: topic,
        intro: `Today we're looking at ${topic}.`,
        mainContent: `Here's what you need to know about ${topic}, step by step.`,
        callToAction: 'Subscribe for more automotive AI tips. Visit RideWire AI Hub for diagnostic tools.',
        disclaimer: 'This is educational content only. Always consult a qualified mechanic for vehicle repairs. RideWire does not replace professional automotive services.',
        estimatedDuration: `${targetLength} minutes`,
        keywords: this.extractKeywords(topic),
        generatedBy: 'template-fallback'
      };
    }
  }

  /**
   * Call a local Ollama server running an open-source model.
   */
  async callOllama(prompt) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 90000);
    try {
      const res = await fetch(`${OLLAMA_URL}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: OLLAMA_MODEL, prompt, stream: false }),
        signal: controller.signal
      });
      if (!res.ok) {
        throw new Error(`Ollama returned HTTP ${res.status}`);
      }
      const data = await res.json();
      return data.response || '';
    } finally {
      clearTimeout(timeout);
    }
  }

  /**
   * Best-effort extraction of a JSON object from an LLM response
   * (small local models sometimes wrap JSON in extra text).
   */
  extractJson(text) {
    try {
      return JSON.parse(text);
    } catch (_) {
      const match = text.match(/\{[\s\S]*\}/);
      if (match) {
        try {
          return JSON.parse(match[0]);
        } catch (_) { /* fall through */ }
      }
      return {};
    }
  }

  /**
   * Generate voiceover using the local, open-source Piper TTS engine.
   * Falls back to no audio (silent track) if Piper/the voice model isn't available.
   */
  async generateVoiceover(script, outputPath) {
    console.log('🎙️  Generating voiceover (open-source Piper TTS)...');

    const narrationText = [script.intro, script.mainContent, script.callToAction, script.disclaimer]
      .filter(Boolean)
      .join('\n\n');

    try {
      await fs.access(PIPER_MODEL_PATH);

      const wavPath = outputPath.replace(/\.mp3$/i, '.wav');
      await execFileAsync('python3', [
        '-m', 'piper',
        '-m', PIPER_MODEL_PATH,
        '-f', wavPath
      ], { input: narrationText, timeout: 120000 }).catch(async (err) => {
        // Some environments need stdin piped explicitly.
        const { spawnSync } = require('child_process');
        const result = spawnSync('python3', ['-m', 'piper', '-m', PIPER_MODEL_PATH, '-f', wavPath], {
          input: narrationText,
          timeout: 120000
        });
        if (result.status !== 0) {
          throw err;
        }
      });

      console.log('✅ Voiceover generated (open-source Piper TTS)');
      return wavPath;
    } catch (error) {
      console.warn(`⚠️  Piper TTS unavailable (${error.message}), skipping real voiceover`);
      return null;
    }
  }

  /**
   * Assemble the final video locally with ffmpeg: a generated background
   * with the video title, plus the narration audio track. No paid avatar
   * API required.
   */
  async generateVideo(audioPath, scriptData, outputPath) {
    console.log('🎬 Assembling video with ffmpeg...');

    try {
      let duration = 15;
      if (audioPath) {
        const { stdout } = await execFileAsync('ffprobe', [
          '-v', 'error', '-show_entries', 'format=duration',
          '-of', 'default=noprint_wrappers=1:nokey=1', audioPath
        ]);
        duration = Math.ceil(parseFloat(stdout.trim())) + 1;
      }

      const title = (scriptData.title || 'RideWire AI Hub').replace(/'/g, "\\'").replace(/:/g, '\\:');
      const fontPath = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf';
      const drawText = `drawtext=fontfile=${fontPath}:text='${title}':fontcolor=white:fontsize=54:x=(w-text_w)/2:y=(h-text_h)/2-40:box=1:boxcolor=0x1b263b@0.8:boxborderw=30,drawtext=fontfile=${fontPath}:text='RideWire AI Hub':fontcolor=0x8ecae6:fontsize=32:x=(w-text_w)/2:y=(h-text_h)/2+60`;

      const args = [
        '-y',
        '-f', 'lavfi', '-i', `color=c=0x0d1b2a:s=1280x720:d=${duration}`
      ];
      if (audioPath) {
        args.push('-i', audioPath);
      }
      args.push('-vf', drawText, '-c:v', 'libx264', '-pix_fmt', 'yuv420p');
      if (audioPath) {
        args.push('-c:a', 'aac', '-shortest');
      }
      args.push(outputPath);

      await execFileAsync('ffmpeg', args, { timeout: 180000 });

      console.log('✅ Video assembled (ffmpeg, open-source)');
      return outputPath;
    } catch (error) {
      console.error('❌ Video generation failed:', error.message);
      throw error;
    }
  }

  /**
   * Extract keywords for SEO
   */
  extractKeywords(topic) {
    const keywords = [
      'automotive diagnostics',
      'car repair',
      'DIY mechanic',
      'check engine light',
      'OBD-II',
      'vehicle maintenance',
      'AI diagnostics'
    ];

    keywords.push(...topic.toLowerCase().split(' ').filter(w => w.length > 3));

    return [...new Set(keywords)];
  }

  /**
   * Generate complete video content
   */
  async generateContent(topic, options = {}) {
    console.log(`\n🚀 Starting COCO content generation for: "${topic}"\n`);

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const videoId = `coco-${timestamp}`;

    try {
      await fs.mkdir(this.outputDir, { recursive: true });

      const script = await this.generateScript(topic, options.targetLength || 3);

      const audioPath = path.join(this.outputDir, `${videoId}-audio.mp3`);
      const realAudioPath = await this.generateVoiceover(script, audioPath);

      const videoPath = path.join(this.outputDir, `${videoId}-video.mp4`);
      await this.generateVideo(realAudioPath, script, videoPath);

      const metadata = {
        videoId,
        topic,
        title: script.title,
        keywords: script.keywords,
        script,
        generatedAt: new Date().toISOString(),
        status: 'ready_for_upload',
        simulated: false,
        paths: {
          audio: realAudioPath,
          video: videoPath
        }
      };

      const metadataPath = path.join(this.outputDir, `${videoId}-metadata.json`);
      await fs.writeFile(metadataPath, JSON.stringify(metadata, null, 2));

      console.log('\n✅ Content generation complete!');
      console.log(`📁 Output directory: ${this.outputDir}`);
      console.log(`🎬 Video ID: ${videoId}`);

      return metadata;

    } catch (error) {
      console.error('\n❌ Content generation failed:', error.message);
      throw error;
    }
  }
}

// CLI interface
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log(`
COCO AI Influencer - Content Generator (free, open-source stack)

Usage: node generate-content.js "Video Topic" [duration]

Examples:
  node generate-content.js "Check Engine Light Quick Fix P0300"
  node generate-content.js "Harley Davidson Diagnostic Codes Explained" 5
  node generate-content.js "AI Multi-Agent Consensus for Brake Problems" 3

Options:
  duration: Target video length in minutes (default: 3)

Uses local, open-source tools only (no paid API keys required):
  Ollama (OLLAMA_MODEL, default llama3.2:1b) for script writing
  Piper TTS (PIPER_MODEL_PATH) for voiceover
  ffmpeg for final video assembly
    `);
    process.exit(1);
  }

  const topic = args[0];
  const duration = parseInt(args[1]) || 3;

  const generator = new COCOContentGenerator();

  generator.generateContent(topic, { targetLength: duration })
    .then(metadata => {
      console.log('\n📊 Generation Summary:');
      console.log(JSON.stringify(metadata, null, 2));
      process.exit(0);
    })
    .catch(error => {
      console.error('\n💥 Fatal error:', error);
      process.exit(1);
    });
}

module.exports = COCOContentGenerator;
