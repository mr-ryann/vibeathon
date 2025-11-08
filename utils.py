"""
VibeOS - Utility Functions
Core helper functions for content analysis, API handling, and data processing
"""

import re
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import hashlib
from collections import Counter
import sqlite3
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# ==================== DATABASE UTILITIES ====================

class VibeDatabase:
    """SQLite database manager for user data, content history, and analytics"""
    
    def __init__(self, db_path: str = "vibe_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                niche TEXT,
                goal TEXT,
                vibe_profile TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP
            )
        """)
        
        # Content samples table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_samples (
                sample_id TEXT PRIMARY KEY,
                user_id TEXT,
                content_text TEXT,
                content_type TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Generated content table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generated_content (
                content_id TEXT PRIMARY KEY,
                user_id TEXT,
                platform TEXT,
                script TEXT,
                caption TEXT,
                hashtags TEXT,
                trend_source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                posted_at TIMESTAMP,
                engagement_rate REAL,
                likes INTEGER,
                comments INTEGER,
                shares INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Sponsor outreach table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sponsors (
                outreach_id TEXT PRIMARY KEY,
                user_id TEXT,
                brand_name TEXT,
                brand_email TEXT,
                pitch_subject TEXT,
                pitch_body TEXT,
                sent_at TIMESTAMP,
                opened BOOLEAN DEFAULT 0,
                replied BOOLEAN DEFAULT 0,
                deal_closed BOOLEAN DEFAULT 0,
                deal_value REAL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                metric_id TEXT PRIMARY KEY,
                user_id TEXT,
                metric_date DATE,
                followers_count INTEGER,
                engagement_rate REAL,
                content_posted INTEGER,
                revenue REAL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_user_profile(self, user_id: str, niche: str, goal: str, vibe_profile: Dict):
        """Save user profile and vibe analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO users (user_id, niche, goal, vibe_profile, last_active)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, niche, goal, json.dumps(vibe_profile), datetime.now()))
        conn.commit()
        conn.close()
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Retrieve user profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "user_id": row[0],
                "niche": row[1],
                "goal": row[2],
                "vibe_profile": json.loads(row[3]) if row[3] else {},
                "created_at": row[4],
                "last_active": row[5]
            }
        return None
    
    def save_generated_content(self, user_id: str, platform: str, content_data: Dict):
        """Save AI-generated content"""
        content_id = hashlib.md5(f"{user_id}{datetime.now()}".encode()).hexdigest()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO generated_content 
            (content_id, user_id, platform, script, caption, hashtags, trend_source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            content_id, user_id, platform,
            content_data.get('script', ''),
            content_data.get('caption', ''),
            json.dumps(content_data.get('hashtags', [])),
            content_data.get('trend_source', '')
        ))
        conn.commit()
        conn.close()
        return content_id

    def get_recent_scripts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch recently generated scripts with engagement metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
                SELECT content_id, user_id, platform, script, caption, hashtags,
                       trend_source, created_at, posted_at, engagement_rate,
                       likes, comments, shares
                FROM generated_content
                ORDER BY datetime(created_at) DESC
                LIMIT ?
            """,
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()

        recent_scripts: List[Dict[str, Any]] = []
        for row in rows:
            hashtags_raw = row[5]
            try:
                hashtags = json.loads(hashtags_raw) if hashtags_raw else []
            except json.JSONDecodeError:
                hashtags = []

            recent_scripts.append({
                "content_id": row[0],
                "user_id": row[1],
                "platform": row[2],
                "script": row[3],
                "caption": row[4],
                "hashtags": hashtags,
                "trend_source": row[6],
                "created_at": row[7],
                "posted_at": row[8],
                "engagement_rate": row[9] or 0,
                "likes": row[10] or 0,
                "comments": row[11] or 0,
                "shares": row[12] or 0
            })

        return recent_scripts
    
    def get_user_analytics(self, user_id: str, days: int = 30) -> pd.DataFrame:
        """Get user analytics for dashboard"""
        conn = sqlite3.connect(self.db_path)
        
        # Get content performance
        query = f"""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as posts,
                AVG(engagement_rate) as avg_engagement,
                SUM(likes) as total_likes
            FROM generated_content
            WHERE user_id = ? 
            AND created_at >= date('now', '-{days} days')
            GROUP BY DATE(created_at)
            ORDER BY date
        """
        df = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()
        return df


# ==================== VIBE ANALYSIS UTILITIES ====================

def extract_vibe_markers(content_samples: List[str]) -> Dict[str, Any]:
    """
    Analyze content samples to extract unique vibe markers
    Returns tone, vocabulary patterns, humor style, and formatting preferences
    """
    
    all_text = " ".join(content_samples)
    
    # Tone detection patterns
    tone_markers = {
        "sarcastic": len(re.findall(r'yeah right|sure thing|oh great|totally|obviously', all_text, re.I)),
        "wholesome": len(re.findall(r'love|heart|blessed|grateful|amazing|beautiful', all_text, re.I)),
        "edgy": len(re.findall(r'fuck|shit|damn|hell|wtf|bruh', all_text, re.I)),
        "professional": len(re.findall(r'leverage|optimize|strategy|data-driven|ROI', all_text, re.I)),
        "casual": len(re.findall(r"gonna|wanna|gotta|kinda|sorta|lol|lmao", all_text, re.I))
    }
    
    # Emoji usage patterns
    emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+')
    emoji_usage = len(emoji_pattern.findall(all_text))
    
    # Punctuation style
    exclamation_count = all_text.count('!')
    question_count = all_text.count('?')
    ellipsis_count = all_text.count('...')
    
    # Sentence length (complexity indicator)
    sentences = re.split(r'[.!?]+', all_text)
    avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len([s for s in sentences if s.strip()]), 1)
    
    # Vocabulary extraction
    words = re.findall(r'\b\w+\b', all_text.lower())
    word_freq = Counter(words)
    
    # Remove common stop words
    stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'it', 'that', 'this'])
    unique_vocab = [word for word, count in word_freq.most_common(30) if word not in stop_words and len(word) > 3]
    
    # Determine dominant tone
    dominant_tone = max(tone_markers, key=tone_markers.get) if max(tone_markers.values()) > 0 else "neutral"
    
    return {
        "tone": dominant_tone,
        "tone_scores": tone_markers,
        "emoji_density": emoji_usage / max(len(all_text), 1) * 100,
        "punctuation_style": {
            "exclamation_ratio": exclamation_count / max(len(sentences), 1),
            "question_ratio": question_count / max(len(sentences), 1),
            "uses_ellipsis": ellipsis_count > 2
        },
        "avg_sentence_length": round(avg_sentence_length, 1),
        "signature_words": unique_vocab[:15],
        "complexity": "simple" if avg_sentence_length < 12 else "moderate" if avg_sentence_length < 20 else "complex"
    }


def build_vibe_prompt(vibe_profile: Dict[str, Any]) -> str:
    """
    Convert vibe profile into a system prompt for content generation
    """
    tone = vibe_profile.get('tone', 'casual')
    emoji_density = vibe_profile.get('emoji_density', 0)
    punctuation = vibe_profile.get('punctuation_style', {})
    signature_words = vibe_profile.get('signature_words', [])
    
    prompt = f"""You are writing content that matches this EXACT vibe profile:

TONE: {tone} - embody this tone in every sentence
EMOJI USAGE: {"Heavy (use 3-5 per post)" if emoji_density > 2 else "Moderate (1-2 per post)" if emoji_density > 0.5 else "Minimal (0-1 per post)"}
PUNCTUATION STYLE: {"Uses lots of exclamation points!" if punctuation.get('exclamation_ratio', 0) > 0.2 else "Calm punctuation."} {"Asks rhetorical questions?" if punctuation.get('question_ratio', 0) > 0.1 else ""} {"Uses ellipsis for dramatic pauses..." if punctuation.get('uses_ellipsis') else ""}
SIGNATURE VOCABULARY: Naturally incorporate these words when relevant: {', '.join(signature_words[:10])}
SENTENCE STYLE: {"Short punchy sentences." if vibe_profile.get('complexity') == 'simple' else "Mix of short and medium sentences." if vibe_profile.get('complexity') == 'moderate' else "Can use complex sentences."}

CRITICAL: This is not generic AI content. Write like the REAL PERSON who created the sample content. Match their energy, humor, and voice exactly."""

    return prompt


# ==================== CONTENT UTILITIES ====================

def clean_content_text(text: str) -> str:
    """Clean and normalize content text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)
    # Remove mentions (but keep the context)
    text = re.sub(r'@\w+', '', text)
    return text


def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from content"""
    return re.findall(r'#(\w+)', text)


def format_caption_with_hashtags(caption: str, hashtags: List[str], max_length: int = 150) -> str:
    """Format caption with hashtags, respecting platform limits"""
    # Ensure caption doesn't exceed limit
    if len(caption) > max_length - 50:  # Leave room for hashtags
        caption = caption[:max_length - 53] + "..."
    
    # Add hashtags
    hashtag_str = " ".join([f"#{tag}" for tag in hashtags[:10]])
    full_caption = f"{caption}\n\n{hashtag_str}"
    
    return full_caption


def calculate_engagement_rate(likes: int, comments: int, shares: int, followers: int) -> float:
    """Calculate engagement rate"""
    if followers == 0:
        return 0.0
    total_engagement = likes + (comments * 2) + (shares * 3)  # Weighted
    return round((total_engagement / followers) * 100, 2)


# ==================== API UTILITIES ====================

def get_api_key(service: str) -> str:
    """Safely retrieve API keys from environment"""
    key_mapping = {
        'groq': 'GROQ_API_KEY',
        'anthropic': 'ANTHROPIC_API_KEY',
        'serper': 'SERPER_API_KEY',
        'twitter': 'TWITTER_BEARER_TOKEN',
        'gmail': 'GMAIL_CREDENTIALS_PATH',
        'gemini': 'GEMINI_API_KEY'
    }
    
    env_var = key_mapping.get(service.lower())
    if not env_var:
        raise ValueError(f"Unknown service: {service}")
    
    api_key = os.getenv(env_var)
    if not api_key:
        raise ValueError(f"Missing {env_var} in environment variables")
    
    return api_key


def retry_with_exponential_backoff(func, max_retries: int = 3, base_delay: int = 2):
    """Retry function with exponential backoff for API calls"""
    from time import sleep
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            delay = base_delay ** attempt
            print(f"Retry {attempt + 1}/{max_retries} after {delay}s due to: {str(e)}")
            sleep(delay)


# ==================== VALIDATION UTILITIES ====================

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_url(url: str) -> bool:
    """Validate URL format"""
    pattern = r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)$'
    return re.match(pattern, url) is not None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Limit length
    return filename[:200]


# ==================== DATETIME UTILITIES ====================

def get_optimal_posting_times() -> List[str]:
    """Return optimal posting times based on research"""
    return [
        "09:00",  # Morning commute
        "12:00",  # Lunch break
        "17:00",  # Evening commute
        "20:00"   # Prime time
    ]


def get_next_posting_time() -> datetime:
    """Calculate next optimal posting time"""
    now = datetime.now()
    optimal_times = get_optimal_posting_times()
    
    for time_str in optimal_times:
        hour, minute = map(int, time_str.split(':'))
        posting_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if posting_time > now:
            return posting_time
    
    # If all times passed, return first time tomorrow
    tomorrow = now + timedelta(days=1)
    hour, minute = map(int, optimal_times[0].split(':'))
    return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)


# ==================== EXPORT UTILITIES ====================

def export_analytics_csv(user_id: str, output_path: str = "analytics_export.csv"):
    """Export user analytics to CSV"""
    db = VibeDatabase()
    df = db.get_user_analytics(user_id, days=90)
    df.to_csv(output_path, index=False)
    return output_path


def generate_media_kit(user_data: Dict) -> str:
    """Generate markdown media kit for sponsor pitches"""
    media_kit = f"""# {user_data.get('name', 'Creator')} - Media Kit

## Overview
**Niche:** {user_data.get('niche', 'N/A')}  
**Followers:** {user_data.get('followers', 0):,}  
**Avg Engagement Rate:** {user_data.get('engagement_rate', 0)}%  
**Content Style:** {user_data.get('vibe_tone', 'Authentic & Engaging')}

## Audience Demographics
- **Primary Age:** 18-34 (72%)
- **Gender:** Mixed audience
- **Top Locations:** United States, Canada, UK

## Recent Performance
- **30-Day Reach:** {user_data.get('reach_30d', 0):,}
- **Best Performing Post:** {user_data.get('best_post_likes', 0):,} likes
- **Engagement Trend:** ↑ {user_data.get('growth_rate', 0)}% growth

## Partnership Opportunities
✅ Sponsored posts  
✅ Product reviews  
✅ Affiliate partnerships  
✅ Long-term brand ambassadorships

**Contact:** {user_data.get('email', 'contact@example.com')}
"""
    return media_kit


# ==================== TESTING UTILITIES ====================

def generate_sample_user_id() -> str:
    """Generate random user ID for testing"""
    import uuid
    return f"user_{uuid.uuid4().hex[:8]}"


if __name__ == "__main__":
    # Test vibe extraction
    samples = [
        "bruh this is absolutely wild lmao 😂 can't believe this actually works",
        "okay so here's the thing... nobody talks about this but it's literally game-changing",
        "POV: you just discovered the secret that influencers don't want you to know 👀"
    ]
    
    vibe = extract_vibe_markers(samples)
    print("Extracted Vibe Profile:")
    print(json.dumps(vibe, indent=2))
    
    print("\n" + "="*50)
    print("Generated Vibe Prompt:")
    print(build_vibe_prompt(vibe))
