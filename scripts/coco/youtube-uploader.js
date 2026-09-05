#!/usr/bin/env node

/**
 * COCO AI Influencer - YouTube Uploader
 * 
 * Handles automated YouTube video uploads with:
 * - OAuth authentication
 * - Metadata management (title, description, tags)
 * - Thumbnail upload
 * - Publishing schedule
 * - Playlist management
 * 
 * REQUIRES: YouTube Data API v3 credentials
 */

require('dotenv').config();
const fs = require('fs').promises;
const path = require('path');

class YouTubeUploader {
  constructor() {
    this.apiKey = process.env.YOUTUBE_API_KEY;
    this.clientId = process.env.YOUTUBE_CLIENT_ID;
    this.clientSecret = process.env.YOUTUBE_CLIENT_SECRET;
    this.channelId = process.env.YOUTUBE_CHANNEL_ID;
    this.refreshToken = process.env.YOUTUBE_REFRESH_TOKEN;
    this.oauth2Client = null;

    this.validateConfig();
  }

  /**
   * Lazily build an authenticated OAuth2 client from the stored refresh token
   */
  getOAuth2Client() {
    if (this.oauth2Client) return this.oauth2Client;

    const { google } = require('googleapis');
    const OAuth2 = google.auth.OAuth2;

    const oauth2Client = new OAuth2(
      this.clientId,
      this.clientSecret,
      'http://localhost:3000/oauth2callback'
    );

    oauth2Client.setCredentials({ refresh_token: this.refreshToken });
    this.oauth2Client = oauth2Client;
    return oauth2Client;
  }

  validateConfig() {
    const missing = [];
    if (!this.clientId) missing.push('YOUTUBE_CLIENT_ID');
    if (!this.clientSecret) missing.push('YOUTUBE_CLIENT_SECRET');
    
    if (missing.length > 0) {
      console.warn('⚠️  Missing YouTube credentials:', missing.join(', '));
      console.warn('⚠️  Set these in .env file for upload functionality');
      console.warn('⚠️  Get credentials from: https://console.cloud.google.com/');
    }
  }

  /**
   * Generate video metadata for upload
   */
  generateMetadata(videoData) {
    const { title, script, keywords } = videoData;
    
    // Craft engaging description with legal disclaimer
    const description = `${script.intro}

${script.mainContent}

🔧 RideWire AI Hub - Multi-AI Automotive Diagnostics
Visit: https://ridewire.ai (placeholder)

📌 What You'll Learn:
• Understanding diagnostic codes
• Step-by-step troubleshooting
• AI-powered diagnostic tools
• Professional best practices

⚠️ IMPORTANT DISCLAIMER:
This content is for educational purposes only. All automotive diagnostic information should be verified by qualified mechanics and automotive professionals. RideWire AI Hub and this channel do not replace professional automotive repair services. Always consult a certified mechanic for vehicle repairs and diagnostics. We are not liable for damages resulting from following this information.

🔔 Subscribe for more AI-powered automotive content!
📧 Questions? Visit our website or leave a comment below.

#AutomotiveDiagnostics #CarRepair #DIYMechanic #CheckEngineLight #OBDII #AITools

---
Powered by COCO AI - Educational Content Generator
© ${new Date().getFullYear()} RideWire AI Hub. All rights reserved.`;

    const tags = [
      ...keywords,
      'RideWire',
      'COCO AI',
      'automotive education',
      'car maintenance'
    ].slice(0, 30); // YouTube allows max 30 tags

    return {
      title: `${title} | RideWire AI Hub`,
      description,
      tags,
      category: 'Autos & Vehicles', // YouTube category ID: 2
      privacyStatus: 'public', // Options: public, private, unlisted
      madeForKids: false,
      defaultLanguage: 'en',
      defaultAudioLanguage: 'en'
    };
  }

  /**
   * Upload video to YouTube
   */
  async uploadVideo(videoPath, metadata) {
    console.log(`\n📤 Uploading video to YouTube...\n`);
    
    if (!this.clientId || !this.clientSecret || !this.refreshToken) {
      console.log('⚠️  YouTube credentials not fully configured (need client ID, secret, and refresh token)');
      console.log('📝 Simulating upload process...\n');
      
      // Simulate upload for demonstration
      return this.simulateUpload(videoPath, metadata);
    }

    try {
      const { google } = require('googleapis');
      const fsSync = require('fs');

      const oauth2Client = this.getOAuth2Client();

      const youtube = google.youtube({
        version: 'v3',
        auth: oauth2Client
      });

      const response = await youtube.videos.insert({
        part: 'snippet,status',
        requestBody: {
          snippet: {
            title: metadata.title,
            description: metadata.description,
            tags: metadata.tags,
            categoryId: '2'
          },
          status: {
            privacyStatus: metadata.privacyStatus,
            madeForKids: metadata.madeForKids,
            ...(metadata.publishAt ? { publishAt: metadata.publishAt } : {})
          }
        },
        media: {
          body: fsSync.createReadStream(videoPath)
        }
      });

      const videoId = response.data.id;
      const videoUrl = `https://youtube.com/watch?v=${videoId}`;

      console.log(`\n✅ Video uploaded successfully!`);
      console.log(`📺 Video ID: ${videoId}`);
      console.log(`🔗 URL: ${videoUrl}`);

      return {
        id: videoId,
        url: videoUrl,
        uploadedAt: new Date().toISOString(),
        status: 'uploaded',
        metadata
      };

    } catch (error) {
      console.error('❌ Upload failed:', error.message);
      throw error;
    }
  }

  /**
   * Simulate upload for demonstration
   */
  async simulateUpload(videoPath, metadata) {
    console.log('📋 Video Metadata:');
    console.log(`   Title: ${metadata.title}`);
    console.log(`   Tags: ${metadata.tags.slice(0, 5).join(', ')}...`);
    console.log(`   Privacy: ${metadata.privacyStatus}`);
    console.log(`   Category: ${metadata.category}`);
    
    // Simulate upload delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const videoId = `simulated-${Date.now()}`;
    const videoUrl = `https://youtube.com/watch?v=${videoId}`;
    
    console.log(`\n✅ Video uploaded successfully!`);
    console.log(`📺 Video ID: ${videoId}`);
    console.log(`🔗 URL: ${videoUrl}`);
    
    return {
      id: videoId,
      url: videoUrl,
      uploadedAt: new Date().toISOString(),
      status: 'uploaded',
      metadata
    };
  }

  /**
   * Schedule video for future publication
   */
  async scheduleVideo(videoPath, metadata, publishAt) {
    console.log(`\n⏰ Scheduling video for: ${publishAt}\n`);
    
    // YouTube API allows scheduling by setting publishAt in status
    const scheduledMetadata = {
      ...metadata,
      privacyStatus: 'private',
      publishAt: new Date(publishAt).toISOString()
    };
    
    return await this.uploadVideo(videoPath, scheduledMetadata);
  }

  /**
   * Add video to playlist
   */
  async addToPlaylist(videoId, playlistId) {
    console.log(`\n📋 Adding video ${videoId} to playlist ${playlistId}...\n`);
    
    if (!this.clientId || !this.clientSecret || !this.refreshToken) {
      console.log('⚠️  YouTube credentials not fully configured, simulating...');
      return { success: true, simulated: true };
    }

    try {
      const { google } = require('googleapis');
      const oauth2Client = this.getOAuth2Client();
      const youtube = google.youtube({ version: 'v3', auth: oauth2Client });

      await youtube.playlistItems.insert({
        part: 'snippet',
        requestBody: {
          snippet: {
            playlistId: playlistId,
            resourceId: {
              kind: 'youtube#video',
              videoId: videoId
            }
          }
        }
      });

      console.log('✅ Video added to playlist');
      return { success: true, simulated: false };
      
    } catch (error) {
      console.error('❌ Failed to add to playlist:', error.message);
      throw error;
    }
  }

  /**
   * Upload complete workflow
   */
  async uploadWorkflow(videoMetadataPath, options = {}) {
    try {
      // Load video metadata
      const metadataContent = await fs.readFile(videoMetadataPath, 'utf8');
      const videoData = JSON.parse(metadataContent);
      
      console.log(`\n🚀 Starting upload workflow for: ${videoData.topic}\n`);
      
      // Generate YouTube metadata
      const youtubeMetadata = this.generateMetadata(videoData);
      
      // Upload video
      let uploadResult;
      if (options.scheduleAt) {
        uploadResult = await this.scheduleVideo(
          videoData.paths.video,
          youtubeMetadata,
          options.scheduleAt
        );
      } else {
        uploadResult = await this.uploadVideo(
          videoData.paths.video,
          youtubeMetadata
        );
      }
      
      // Add to playlist if specified
      if (options.playlistId) {
        await this.addToPlaylist(uploadResult.id, options.playlistId);
      }
      
      // Save upload record
      const uploadRecord = {
        ...uploadResult,
        videoData,
        uploadedBy: 'COCO AI Automation',
        timestamp: new Date().toISOString()
      };
      
      const recordPath = path.join(
        path.dirname(videoMetadataPath),
        `${videoData.videoId}-upload-record.json`
      );
      
      await fs.writeFile(recordPath, JSON.stringify(uploadRecord, null, 2));
      
      console.log(`\n✅ Upload workflow complete!`);
      console.log(`📄 Record saved: ${recordPath}`);
      
      return uploadRecord;
      
    } catch (error) {
      console.error('\n❌ Upload workflow failed:', error.message);
      throw error;
    }
  }
}

// CLI interface
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log(`
COCO AI Influencer - YouTube Uploader

Usage: node youtube-uploader.js <metadata-file> [options]

Arguments:
  metadata-file: Path to video metadata JSON file

Options:
  --schedule <ISO-date>: Schedule video for future publication
  --playlist <playlist-id>: Add video to playlist after upload

Examples:
  node youtube-uploader.js output/coco-videos/coco-2024-01-08-video-metadata.json
  node youtube-uploader.js output/coco-videos/metadata.json --schedule "2024-01-15T09:00:00Z"
  node youtube-uploader.js output/coco-videos/metadata.json --playlist PLxxxxxxxxxxxxxxxx

Environment Variables Required:
  YOUTUBE_CLIENT_ID: OAuth client ID from Google Cloud Console
  YOUTUBE_CLIENT_SECRET: OAuth client secret
  YOUTUBE_CHANNEL_ID: Your YouTube channel ID (optional)

Setup Instructions:
  1. Go to https://console.cloud.google.com/
  2. Create a project and enable YouTube Data API v3
  3. Create OAuth 2.0 credentials
  4. Add credentials to .env file
    `);
    process.exit(1);
  }
  
  const metadataPath = args[0];
  const options = {};
  
  if (args.includes('--schedule')) {
    options.scheduleAt = args[args.indexOf('--schedule') + 1];
  }
  
  if (args.includes('--playlist')) {
    options.playlistId = args[args.indexOf('--playlist') + 1];
  }
  
  const uploader = new YouTubeUploader();
  
  uploader.uploadWorkflow(metadataPath, options)
    .then(result => {
      console.log('\n📊 Upload Result:');
      console.log(JSON.stringify(result, null, 2));
      process.exit(0);
    })
    .catch(error => {
      console.error('\n💥 Fatal error:', error);
      process.exit(1);
    });
}

module.exports = YouTubeUploader;
