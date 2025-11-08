"""
pulse Agent - Video Processing & Auto-Posting (formerly EngageBot)

Architecture: Expanded for shorts creation
Input: Full video file/URL after user shoots
Output: Clipped MP4s (15-60s segments) + auto-posts
Tools: FFmpeg for clipping, Tweepy for X posting
Fallback: Mock clips if no video provided
Name: pulse - the heartbeat of engagement, pushing content into the world
"""

import os
import json
import subprocess
from pathlib import Path
from typing import TypedDict, List, Dict, Any, Optional
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
import google.generativeai as genai

# Load API keys
load_dotenv()
if "GEMINI_API_KEY" not in os.environ:
    raise EnvironmentError("🚨 GEMINI_API_KEY not found. Please create a .env file with your API key.")

# Configure Google GenAI SDK
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


# --- GraphState Definition ---
class GraphState(TypedDict):
    """
    The shared state of the CreatorForge Nexus.
    """
    user_vibe: str
    niche: str
    goals: str
    topic: str
    scouted_trends: List[Dict[str, str]]
    generated_script: Dict[str, Any]
    video_path: str
    clipped_shorts: List[Dict[str, Any]]
    engage_plan: Dict[str, Any]
    deal_plan: List[Dict[str, str]]
    error: str


# --- Video Processing Functions ---
def check_ffmpeg_installed() -> bool:
    """Check if FFmpeg is installed on the system"""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_video_duration(video_path: str) -> Optional[float]:
    """Get video duration in seconds using FFmpeg"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return float(result.stdout.strip())
        return None
    except Exception as e:
        print(f"⚠️  Error getting video duration: {e}")
        return None


def clip_video_segment(
    input_path: str,
    output_path: str,
    start_time: float,
    duration: float
) -> bool:
    """
    Clip a segment from video using FFmpeg
    
    Args:
        input_path: Path to input video
        output_path: Path to save clipped video
        start_time: Start time in seconds
        duration: Duration of clip in seconds
    
    Returns:
        True if successful, False otherwise
    """
    try:
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-ss', str(start_time),
            '-t', str(duration),
            '-c:v', 'libx264',  # Re-encode with H.264
            '-c:a', 'aac',  # Re-encode audio
            '-preset', 'fast',  # Fast encoding
            '-y',  # Overwrite output file
            output_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        return result.returncode == 0 and os.path.exists(output_path)
    
    except Exception as e:
        print(f"⚠️  Error clipping video: {e}")
        return False


def auto_clip_shorts(
    video_path: str,
    output_dir: str = "shorts",
    min_duration: int = 15,
    max_duration: int = 60,
    num_clips: int = 3
) -> List[Dict[str, Any]]:
    """
    Automatically clip video into short segments
    
    Args:
        video_path: Path to full video
        output_dir: Directory to save clips
        min_duration: Minimum clip duration in seconds
        max_duration: Maximum clip duration in seconds
        num_clips: Number of clips to create
    
    Returns:
        List of clip metadata dicts
    """
    print(f"🎬 Auto-clipping video: {video_path}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get video duration
    total_duration = get_video_duration(video_path)
    
    if not total_duration:
        print("⚠️  Could not determine video duration")
        return []
    
    print(f"📹 Video duration: {total_duration:.1f} seconds")
    
    clips = []
    
    # Strategy: Create evenly spaced clips
    clip_duration = min(max_duration, total_duration / num_clips)
    
    if clip_duration < min_duration:
        print(f"⚠️  Video too short to create {num_clips} clips of {min_duration}s")
        num_clips = int(total_duration / min_duration)
        clip_duration = min_duration
    
    for i in range(num_clips):
        # Calculate start time (evenly distribute)
        start_time = i * (total_duration / num_clips)
        
        # Ensure we don't go past video end
        if start_time + clip_duration > total_duration:
            clip_duration = total_duration - start_time
        
        if clip_duration < min_duration:
            print(f"⚠️  Skipping clip {i+1} (too short)")
            continue
        
        # Output filename
        output_filename = f"short_{i+1}_{int(clip_duration)}s.mp4"
        output_path = os.path.join(output_dir, output_filename)
        
        print(f"✂️  Clipping segment {i+1}: {start_time:.1f}s - {start_time+clip_duration:.1f}s")
        
        success = clip_video_segment(
            video_path,
            output_path,
            start_time,
            clip_duration
        )
        
        if success:
            clip_metadata = {
                "clip_id": i + 1,
                "filename": output_filename,
                "path": output_path,
                "start_time": start_time,
                "duration": clip_duration,
                "size_bytes": os.path.getsize(output_path),
                "posted": False
            }
            clips.append(clip_metadata)
            print(f"✅ Created clip: {output_filename} ({clip_duration:.1f}s)")
        else:
            print(f"❌ Failed to create clip {i+1}")
    
    return clips


# --- Auto-Posting Function ---
def post_to_twitter(clip_path: str, caption: str) -> bool:
    """
    Post video clip to Twitter/X using Tweepy
    
    Args:
        clip_path: Path to video clip
        caption: Tweet caption
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check for Twitter API keys
        twitter_keys = [
            'TWITTER_API_KEY',
            'TWITTER_API_SECRET',
            'TWITTER_ACCESS_TOKEN',
            'TWITTER_ACCESS_SECRET'
        ]
        
        if not all(os.getenv(key) for key in twitter_keys):
            print("⚠️  Twitter API keys not configured - skipping post")
            return False
        
        import tweepy
        
        # Authenticate
        auth = tweepy.OAuthHandler(
            os.getenv('TWITTER_API_KEY'),
            os.getenv('TWITTER_API_SECRET')
        )
        auth.set_access_token(
            os.getenv('TWITTER_ACCESS_TOKEN'),
            os.getenv('TWITTER_ACCESS_SECRET')
        )
        
        # Create API v1.1 object for media upload
        api = tweepy.API(auth)
        
        # Upload video
        print(f"📤 Uploading video to Twitter: {clip_path}")
        media = api.media_upload(clip_path)
        
        # Create API v2 client for posting
        client = tweepy.Client(
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
        )
        
        # Post tweet with video
        response = client.create_tweet(
            text=caption,
            media_ids=[media.media_id]
        )
        
        print(f"✅ Posted to Twitter! Tweet ID: {response.data['id']}")
        return True
    
    except ImportError:
        print("⚠️  Tweepy not installed - run: pip install tweepy")
        return False
    
    except Exception as e:
        print(f"⚠️  Error posting to Twitter: {e}")
        return False


def upload_to_youtube(
    video_path: str,
    title: str,
    description: str,
    category: str = "22",  # People & Blogs
    privacy_status: str = "public"  # public, private, or unlisted
) -> Dict[str, Any]:
    """
    Upload video to YouTube using YouTube Data API v3
    
    Args:
        video_path: Path to video file
        title: Video title
        description: Video description
        category: YouTube category ID (22 = People & Blogs)
        privacy_status: Video privacy (public, private, unlisted)
    
    Returns:
        Dict with upload result {'success': bool, 'video_id': str, 'url': str}
    """
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        import pickle
        
        # Check for YouTube API credentials
        credentials_path = os.getenv('YOUTUBE_CREDENTIALS_PATH', 'youtube_credentials.json')
        token_path = 'youtube_token.pickle'
        
        if not os.path.exists(credentials_path):
            print(f"⚠️  YouTube credentials not found at {credentials_path}")
            print("💡 To enable YouTube upload:")
            print("   1. Go to https://console.cloud.google.com/")
            print("   2. Enable YouTube Data API v3")
            print("   3. Create OAuth 2.0 credentials")
            print("   4. Download credentials.json")
            print("   5. Set YOUTUBE_CREDENTIALS_PATH in .env")
            return {'success': False, 'error': 'No credentials file'}
        
        SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
        creds = None
        
        # Load saved token if exists
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next time
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        # Build YouTube service
        youtube = build('youtube', 'v3', credentials=creds)
        
        # Prepare video metadata
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': ['shorts', 'viral', 'ai-generated'],
                'categoryId': category
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Upload video
        print(f"📤 Uploading video to YouTube: {video_path}")
        print(f"   Title: {title}")
        print(f"   Privacy: {privacy_status}")
        
        media = MediaFileUpload(
            video_path,
            mimetype='video/*',
            resumable=True,
            chunksize=1024*1024  # 1MB chunks
        )
        
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"   Upload progress: {progress}%")
        
        video_id = response['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        print(f"✅ Successfully uploaded to YouTube!")
        print(f"   Video ID: {video_id}")
        print(f"   URL: {video_url}")
        
        return {
            'success': True,
            'video_id': video_id,
            'url': video_url,
            'title': title
        }
    
    except ImportError as e:
        print(f"⚠️  Missing required library: {e}")
        print("   Run: pip install google-api-python-client google-auth-oauthlib")
        return {'success': False, 'error': 'Missing libraries'}
    
    except Exception as e:
        print(f"⚠️  Error uploading to YouTube: {e}")
        return {'success': False, 'error': str(e)}


# --- pulse Agent Node ---
def run_pulse(state: GraphState) -> GraphState:
    """
    Runs the pulse agent to process video and create/post shorts.
    
    Architecture: Expanded for video processing
    Input: Full video path (after user shoots)
    Output: Clipped shorts + auto-posts to platforms
    Fallback: Mock clips if no video or FFmpeg unavailable
    
    Args:
        state: Current GraphState
    
    Returns:
        Updated state with clipped_shorts and engage_plan
    """
    print("--- � AGENT: pulse ---")
    
    # Get inputs from state
    video_path = state.get('video_path', '')
    generated_script = state.get('generated_script', {})
    topic = state.get('topic', 'Unknown topic')
    user_vibe = state.get('user_vibe', '')
    
    clipped_shorts = []
    
    # Check if video was uploaded
    if video_path and os.path.exists(video_path):
        print(f"📹 Video found: {video_path}")
        
        # Check if FFmpeg is available
        if check_ffmpeg_installed():
            print("✅ FFmpeg installed - processing video")
            
            # Auto-clip the video into shorts
            clipped_shorts = auto_clip_shorts(
                video_path,
                output_dir="shorts",
                min_duration=15,
                max_duration=60,
                num_clips=3
            )
            
            if clipped_shorts:
                print(f"✅ Created {len(clipped_shorts)} short clips")
                
                # Auto-post clips to platforms (optional - can be manual)
                for idx, clip in enumerate(clipped_shorts):
                    # Generate caption for this clip
                    caption = f"🎬 {topic} | Clip {clip['clip_id']}\n\n"
                    caption += generated_script.get('intro', '')[:200]
                    caption += f"\n\n#{topic.replace(' ', '')} #Shorts"
                    
                    # Try to post to Twitter (will skip if no API keys)
                    posted_twitter = post_to_twitter(clip['path'], caption)
                    clip['posted_twitter'] = posted_twitter
                    
                    # Try to upload to YouTube (will skip if no credentials)
                    video_title = f"{topic} - Short #{idx + 1}"
                    video_description = f"{generated_script.get('full_script', '')}\n\nGenerated with Nexus AI"
                    
                    youtube_result = upload_to_youtube(
                        video_path=clip['path'],
                        title=video_title,
                        description=video_description,
                        privacy_status='public'  # Change to 'unlisted' or 'private' if preferred
                    )
                    
                    clip['youtube_upload'] = youtube_result
                    clip['posted'] = posted_twitter or youtube_result.get('success', False)
            else:
                print("⚠️  No clips created - using fallback")
        else:
            print("⚠️  FFmpeg not installed - using mock clips")
            print("💡 Install FFmpeg: sudo apt install ffmpeg (Linux) or brew install ffmpeg (Mac)")
    else:
        print("⚠️  No video uploaded yet - creating mock clips")
    
    # Fallback: Create mock clip metadata if no real clips
    if not clipped_shorts:
        print("📦 Creating mock clip metadata...")
        clipped_shorts = [
            {
                "clip_id": 1,
                "filename": "short_1_15s.mp4",
                "path": "[MOCK] User needs to shoot video",
                "start_time": 0,
                "duration": 15,
                "size_bytes": 0,
                "posted": False,
                "is_mock": True
            },
            {
                "clip_id": 2,
                "filename": "short_2_30s.mp4",
                "path": "[MOCK] User needs to shoot video",
                "start_time": 15,
                "duration": 30,
                "size_bytes": 0,
                "posted": False,
                "is_mock": True
            },
            {
                "clip_id": 3,
                "filename": "short_3_20s.mp4",
                "path": "[MOCK] User needs to shoot video",
                "start_time": 45,
                "duration": 20,
                "size_bytes": 0,
                "posted": False,
                "is_mock": True
            }
        ]
    
    # Generate engagement plan
    engage_plan = {
        "total_clips": len(clipped_shorts),
        "clips_posted": sum(1 for c in clipped_shorts if c.get('posted', False)),
        "clips_pending": sum(1 for c in clipped_shorts if not c.get('posted', False)),
        "platforms": ["YouTube Shorts", "Twitter/X", "TikTok (manual)", "Instagram Reels (manual)"],
        "strategy": f"Distribute {len(clipped_shorts)} clips across platforms over 24 hours for maximum reach",
        "next_steps": [
            "Review clipped shorts",
            "Check YouTube uploads (auto-posted if configured)",
            "Check Twitter posts (auto-posted if configured)",
            "Post to TikTok manually (or integrate TikTok API)",
            "Post to Instagram Reels manually (or integrate Instagram API)",
            "Monitor engagement and respond to comments"
        ]
    }
    
    print(f"✅ pulse complete! {len(clipped_shorts)} shorts ready")
    
    return {
        "clipped_shorts": clipped_shorts,
        "engage_plan": engage_plan
    }


# --- Test Harness ---
if __name__ == "__main__":
    
    print("--- 🧪 TESTING pulse AGENT (Standalone) ---")
    
    # Create a mock initial state
    initial_state = GraphState(
        niche="Tech reviews",
        goals="Build audience",
        topic="AI Gadget Review",
        user_vibe="Sarcastic and honest",
        scouted_trends=[],
        generated_script={
            "intro": "Wait, I spent $500 on THIS?!",
            "body": "Let me show you why everyone's returning the AI Pin. [Hold up device] It's slower than my grandma's flip phone.",
            "outro": "Drop a 💀 if you also got scammed. Follow for real tech reviews.",
            "full_script": "Wait, I spent $500 on THIS?! Let me show you why everyone's returning the AI Pin. [Hold up device] It's slower than my grandma's flip phone. Drop a 💀 if you also got scammed. Follow for real tech reviews."
        },
        video_path="",  # No video for test (will use fallback)
        clipped_shorts=[],
        engage_plan={},
        deal_plan=[],
        error=""
    )
    
    # Run the agent
    result_state = run_pulse(initial_state)
    
    print("\n--- 🏁 RESULT ---")
    print("=" * 80)
    
    if "clipped_shorts" in result_state:
        print(f"\n📹 CLIPPED SHORTS: {len(result_state['clipped_shorts'])} clips")
        print("=" * 80)
        
        for clip in result_state['clipped_shorts']:
            print(f"\nClip #{clip['clip_id']}")
            print(f"   File: {clip['filename']}")
            print(f"   Path: {clip['path']}")
            print(f"   Duration: {clip['duration']}s")
            print(f"   Posted: {'Yes ✅' if clip.get('posted') else 'No ⏳'}")
            if clip.get('is_mock'):
                print(f"   Status: MOCK (awaiting real video)")
    
    if "engage_plan" in result_state and result_state['engage_plan']:
        plan = result_state['engage_plan']
        print(f"\n\n📊 ENGAGEMENT PLAN:")
        print("=" * 80)
        print(f"   Total Clips: {plan.get('total_clips', 0)}")
        print(f"   Posted: {plan.get('clips_posted', 0)}")
        print(f"   Pending: {plan.get('clips_pending', 0)}")
        print(f"   Strategy: {plan.get('strategy', 'N/A')}")
        print(f"\n   Next Steps:")
        for step in plan.get('next_steps', []):
            print(f"      • {step}")
    
    print("\n" + "=" * 80)
    print("\n--- ✅ SUCCESS! ---")
    print("pulse is ready. Next: User shoots video and uploads, or envoy pitches sponsors.")
