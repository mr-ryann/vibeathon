"""
VibeOS - External API Integration Tools
Handles all third-party API interactions: trends, social posting, email, analytics
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

import tweepy
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

from utils import get_api_key, retry_with_exponential_backoff, validate_email


# ==================== TREND HUNTING TOOLS ====================

class TrendHunter:
    """Discovers viral trends using Google Serper and X API"""
    
    def __init__(self):
        self.serper_key = get_api_key('serper')
        self.serper_url = "https://google.serper.dev/search"
    
    def search_trending_topics(self, niche: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search Google for trending topics in user's niche
        Returns list of trending topics with relevance scores
        """
        
        # Build search query focused on recent viral content
        query = f"{niche} viral trending 2024 2025"
        
        payload = {
            "q": query,
            "num": num_results,
            "gl": "us",
            "hl": "en",
            "tbs": "qdr:w"  # Past week only
        }
        
        headers = {
            "X-API-KEY": self.serper_key,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self.serper_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            trends = []
            for result in data.get('organic', [])[:num_results]:
                trends.append({
                    "title": result.get('title', ''),
                    "snippet": result.get('snippet', ''),
                    "link": result.get('link', ''),
                    "relevance_score": self._calculate_relevance(result, niche),
                    "source": "Google Serper"
                })
            
            return sorted(trends, key=lambda x: x['relevance_score'], reverse=True)
        
        except Exception as e:
            print(f"Error fetching trends from Serper: {e}")
            return []
    
    def _calculate_relevance(self, result: Dict, niche: str) -> float:
        """Calculate trend relevance score (0-10)"""
        score = 5.0
        
        text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
        niche_lower = niche.lower()
        
        # Boost score if niche keywords appear
        if niche_lower in text:
            score += 2.0
        
        # Boost for viral indicators
        viral_keywords = ['viral', 'trending', 'blowing up', 'everyone is', 'millions']
        for keyword in viral_keywords:
            if keyword in text:
                score += 0.5
        
        # Boost for recent dates
        current_year = str(datetime.now().year)
        if current_year in text:
            score += 1.0
        
        return min(score, 10.0)
    
    def get_twitter_trends(self, niche: str) -> List[Dict[str, Any]]:
        """
        Fetch trending topics from X/Twitter
        Note: Requires Twitter API credentials
        """
        try:
            twitter_token = os.getenv('TWITTER_BEARER_TOKEN')
            if not twitter_token:
                return []
            
            # Initialize Twitter client
            client = tweepy.Client(bearer_token=twitter_token)
            
            # Search recent tweets in niche
            query = f"{niche} -is:retweet lang:en"
            tweets = client.search_recent_tweets(
                query=query,
                max_results=20,
                tweet_fields=['public_metrics', 'created_at']
            )
            
            if not tweets.data:
                return []
            
            trends = []
            for tweet in tweets.data:
                metrics = tweet.public_metrics
                engagement = metrics['like_count'] + metrics['retweet_count'] * 2
                
                if engagement > 100:  # Only high-engagement tweets
                    trends.append({
                        "text": tweet.text[:200],
                        "engagement": engagement,
                        "likes": metrics['like_count'],
                        "retweets": metrics['retweet_count'],
                        "created_at": str(tweet.created_at),
                        "source": "Twitter",
                        "relevance_score": min(engagement / 1000, 10.0)
                    })
            
            return sorted(trends, key=lambda x: x['relevance_score'], reverse=True)[:5]
        
        except Exception as e:
            print(f"Error fetching Twitter trends: {e}")
            return []
    
    def get_best_trends(self, niche: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Combine trends from multiple sources and return top trends
        """
        all_trends = []
        
        # Get Google trends
        google_trends = self.search_trending_topics(niche, num_results=10)
        all_trends.extend(google_trends)
        
        # Get Twitter trends
        twitter_trends = self.get_twitter_trends(niche)
        all_trends.extend(twitter_trends)
        
        # Sort by relevance and return top results
        all_trends.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        return all_trends[:limit]


# ==================== SOCIAL MEDIA POSTING TOOLS ====================

class SocialMediaPoster:
    """Handles posting to X/Twitter, TikTok, Instagram"""
    
    def __init__(self):
        self.twitter_client = self._init_twitter()
    
    def _init_twitter(self):
        """Initialize Twitter API client"""
        try:
            api_key = os.getenv('TWITTER_API_KEY')
            api_secret = os.getenv('TWITTER_API_SECRET')
            access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            access_secret = os.getenv('TWITTER_ACCESS_SECRET')
            
            if all([api_key, api_secret, access_token, access_secret]):
                client = tweepy.Client(
                    consumer_key=api_key,
                    consumer_secret=api_secret,
                    access_token=access_token,
                    access_token_secret=access_secret
                )
                return client
        except Exception as e:
            print(f"Twitter init failed: {e}")
        
        return None
    
    def post_to_twitter(self, content: str) -> Dict[str, Any]:
        """
        Post content to Twitter/X
        Returns post ID and status
        """
        if not self.twitter_client:
            return {"status": "error", "message": "Twitter client not configured"}
        
        try:
            # Ensure content fits Twitter's limit
            if len(content) > 280:
                content = content[:277] + "..."
            
            response = self.twitter_client.create_tweet(text=content)
            
            return {
                "status": "success",
                "platform": "Twitter",
                "post_id": response.data['id'],
                "url": f"https://twitter.com/user/status/{response.data['id']}",
                "posted_at": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "status": "error",
                "platform": "Twitter",
                "message": str(e)
            }
    
    def post_to_tiktok(self, video_path: str, caption: str, hashtags: List[str]) -> Dict[str, Any]:
        """
        Post video to TikTok (placeholder - requires TikTok API access)
        In production, use TikTok Content Posting API
        """
        # Note: TikTok API requires business account and approval
        # This is a placeholder for the MVP
        
        return {
            "status": "simulated",
            "platform": "TikTok",
            "message": "TikTok posting requires business API access (in development)",
            "caption": caption,
            "hashtags": hashtags
        }
    
    def post_to_instagram(self, image_path: str, caption: str) -> Dict[str, Any]:
        """
        Post to Instagram (placeholder - requires Instagram Graph API)
        In production, use Instagram Graph API with business account
        """
        return {
            "status": "simulated",
            "platform": "Instagram",
            "message": "Instagram posting via Graph API (in development)",
            "caption": caption
        }


# ==================== AUTO-REPLY TOOLS ====================

class AutoReplyEngine:
    """Automatically replies to comments in user's voice"""
    
    def __init__(self, vibe_profile: Dict[str, Any]):
        self.vibe_profile = vibe_profile
        self.twitter_client = None
        
        try:
            bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            if bearer_token:
                self.twitter_client = tweepy.Client(bearer_token=bearer_token)
        except Exception as e:
            print(f"AutoReply init failed: {e}")
    
    def get_recent_comments(self, post_id: str, platform: str = "twitter") -> List[Dict[str, Any]]:
        """Fetch recent comments/replies on a post"""
        
        if platform == "twitter" and self.twitter_client:
            try:
                # Get replies to the tweet
                # Note: This is a simplified version; production would use conversation_id
                return []  # Placeholder
            except Exception as e:
                print(f"Error fetching comments: {e}")
        
        return []
    
    def generate_reply(self, comment_text: str, ai_model) -> str:
        """
        Generate contextual reply in user's voice
        Uses AI model passed from agents.py
        """
        # Build prompt based on vibe profile
        tone = self.vibe_profile.get('tone', 'friendly')
        
        reply_prompt = f"""Generate a short, authentic reply to this comment in a {tone} tone.
        
Comment: "{comment_text}"

Requirements:
- Keep it under 100 characters
- Sound like a real person, not a brand
- Match the {tone} vibe
- Be engaging but natural

Reply:"""
        
        # This would call the AI model (passed from agents.py)
        # For now, return a template
        return f"Thanks for the comment! 🙏"
    
    def auto_reply_to_post(self, post_id: str, platform: str, max_replies: int = 10):
        """
        Automatically reply to first N comments on a post
        """
        comments = self.get_recent_comments(post_id, platform)
        replies_sent = 0
        
        for comment in comments[:max_replies]:
            try:
                # Generate reply (would use AI in production)
                reply = self.generate_reply(comment['text'], None)
                
                # Post reply
                # (Implementation depends on platform API)
                replies_sent += 1
                
            except Exception as e:
                print(f"Error replying to comment: {e}")
        
        return replies_sent


# ==================== SPONSOR OUTREACH TOOLS ====================

class SponsorFinder:
    """Finds and contacts potential sponsors"""
    
    def __init__(self):
        self.serper_key = get_api_key('serper')
    
    def find_sponsors(self, niche: str, num_sponsors: int = 3) -> List[Dict[str, Any]]:
        """
        Find brands relevant to user's niche
        Uses Google search to find brands actively sponsoring creators
        """
        
        query = f"{niche} brand sponsor influencer partnership collaboration"
        
        payload = {
            "q": query,
            "num": num_sponsors * 3,  # Get extra for filtering
            "gl": "us"
        }
        
        headers = {
            "X-API-KEY": self.serper_key,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post("https://google.serper.dev/search", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            sponsors = []
            for result in data.get('organic', []):
                # Extract potential sponsor info
                brand_name = self._extract_brand_name(result['title'])
                website = result.get('link', '')
                
                if brand_name and website:
                    # Extract category from snippet
                    category = self._extract_category(result.get('snippet', ''), niche)
                    
                    # Find contact email for this brand
                    email = self._find_brand_email(brand_name, website)
                    
                    sponsors.append({
                        "name": brand_name,  # Changed from brand_name to name
                        "website": website,
                        "description": result.get('snippet', ''),
                        "category": category,
                        "email": email,
                        "relevance": self._calculate_brand_relevance(result, niche)
                    })
            
            # Sort by relevance and return top N
            sponsors.sort(key=lambda x: x['relevance'], reverse=True)
            return sponsors[:num_sponsors]
        
        except Exception as e:
            print(f"Error finding sponsors: {e}")
            return []
    
    def _extract_brand_name(self, title: str) -> Optional[str]:
        """Extract brand name from search result title"""
        # Remove common suffixes
        title = title.split('|')[0].split('-')[0].strip()
        return title if len(title) < 50 else None
    
    def _calculate_brand_relevance(self, result: Dict, niche: str) -> float:
        """Calculate how relevant a brand is to the niche"""
        score = 5.0
        
        text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
        
        # Boost if niche appears
        if niche.lower() in text:
            score += 2.0
        
        # Boost if partnership-related keywords appear
        partnership_keywords = ['sponsor', 'partnership', 'influencer', 'brand deal', 'collaboration']
        for keyword in partnership_keywords:
            if keyword in text:
                score += 1.0
        
        return min(score, 10.0)
    
    def _extract_category(self, snippet: str, niche: str) -> str:
        """Extract business category from search snippet"""
        snippet_lower = snippet.lower()
        
        # Common category keywords
        categories = {
            'tech': ['technology', 'software', 'app', 'saas', 'digital', 'ai', 'tech'],
            'fitness': ['fitness', 'health', 'wellness', 'workout', 'gym', 'nutrition'],
            'beauty': ['beauty', 'cosmetic', 'skincare', 'makeup', 'personal care'],
            'fashion': ['fashion', 'clothing', 'apparel', 'style', 'wear'],
            'food': ['food', 'restaurant', 'meal', 'snack', 'beverage', 'drink'],
            'gaming': ['gaming', 'game', 'esports', 'stream', 'player'],
            'education': ['education', 'learning', 'course', 'tutorial', 'training'],
            'finance': ['finance', 'investing', 'money', 'banking', 'payment'],
        }
        
        for category, keywords in categories.items():
            if any(keyword in snippet_lower for keyword in keywords):
                return category.capitalize()
        
        # Default to niche-based category
        return niche.split()[0].capitalize()
    
    def _find_brand_email(self, brand_name: str, website: str) -> str:
        """
        Find contact email using Serper API search
        """
        domain = website.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
        
        # Search for contact email
        email_query = f"{brand_name} partnerships email contact sponsorship"
        
        try:
            payload = {
                "q": email_query,
                "num": 5,
                "gl": "us"
            }
            
            headers = {
                "X-API-KEY": self.serper_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post("https://google.serper.dev/search", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Look for email patterns in results
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            
            for result in data.get('organic', [])[:5]:
                snippet = result.get('snippet', '')
                emails = re.findall(email_pattern, snippet)
                
                # Prioritize partnership/marketing emails
                for email in emails:
                    email_lower = email.lower()
                    if any(keyword in email_lower for keyword in ['partner', 'sponsor', 'marketing', 'collab', 'business']):
                        return email
                
                # Return first valid email if no partnership email found
                if emails:
                    return emails[0]
            
        except Exception as e:
            print(f"Error finding email for {brand_name}: {e}")
        
        # Fallback to common partnership email format
        return f"partnerships@{domain}"
    
    def find_contact_email(self, brand_website: str) -> Optional[str]:
        """
        Extract contact email from brand website
        In production, would use Hunter.io API or web scraping
        """
        # Placeholder - in production, use Hunter.io or scraping
        return f"partnerships@{brand_website.replace('https://', '').replace('www.', '').split('/')[0]}"


class EmailSender:
    """Sends sponsor pitch emails via Gmail API"""
    
    def __init__(self):
        self.gmail_service = self._init_gmail()
    
    def _init_gmail(self):
        """Initialize Gmail API service"""
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        creds = None
        
        # Token file stores user's access and refresh tokens
        token_path = 'token.pickle'
        
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
                if os.path.exists(credentials_path):
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    return None
            
            # Save credentials for next run
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        try:
            service = build('gmail', 'v1', credentials=creds)
            return service
        except Exception as e:
            print(f"Gmail service init failed: {e}")
            return None
    
    def send_pitch_email(self, to_email: str, subject: str, body: str, user_email: str) -> Dict[str, Any]:
        """
        Send sponsor pitch email via Gmail API
        """
        if not self.gmail_service:
            return {"status": "error", "message": "Gmail service not initialized"}
        
        try:
            from email.mime.text import MIMEText
            import base64
            
            message = MIMEText(body)
            message['to'] = to_email
            message['subject'] = subject
            message['from'] = user_email
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            send_message = self.gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                "status": "success",
                "message_id": send_message['id'],
                "to": to_email,
                "sent_at": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


# ==================== ANALYTICS TRACKING TOOLS ====================

class AnalyticsTracker:
    """Tracks social media performance and engagement"""
    
    def __init__(self):
        self.twitter_client = None
        
        try:
            bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            if bearer_token:
                self.twitter_client = tweepy.Client(bearer_token=bearer_token)
        except Exception as e:
            print(f"Analytics tracker init failed: {e}")
    
    def get_twitter_analytics(self, user_id: str = "me") -> Dict[str, Any]:
        """
        Fetch Twitter account analytics
        """
        if not self.twitter_client:
            return {}
        
        try:
            # Get user info
            user = self.twitter_client.get_user(id=user_id, user_fields=['public_metrics'])
            
            if user.data:
                metrics = user.data.public_metrics
                return {
                    "followers": metrics['followers_count'],
                    "following": metrics['following_count'],
                    "tweets": metrics['tweet_count'],
                    "platform": "Twitter"
                }
        
        except Exception as e:
            print(f"Error fetching Twitter analytics: {e}")
        
        return {}
    
    def track_post_performance(self, post_id: str, platform: str) -> Dict[str, Any]:
        """
        Track individual post performance
        """
        if platform == "twitter" and self.twitter_client:
            try:
                tweet = self.twitter_client.get_tweet(
                    id=post_id,
                    tweet_fields=['public_metrics']
                )
                
                if tweet.data:
                    metrics = tweet.data.public_metrics
                    return {
                        "likes": metrics['like_count'],
                        "retweets": metrics['retweet_count'],
                        "replies": metrics['reply_count'],
                        "impressions": metrics.get('impression_count', 0),
                        "platform": "Twitter"
                    }
            
            except Exception as e:
                print(f"Error tracking post: {e}")
        
        return {}


# ==================== TESTING ====================

if __name__ == "__main__":
    # Test trend hunting
    print("Testing Trend Hunter...")
    hunter = TrendHunter()
    trends = hunter.search_trending_topics("fitness memes", num_results=5)
    
    for i, trend in enumerate(trends, 1):
        print(f"\n{i}. {trend['title']}")
        print(f"   Relevance: {trend['relevance_score']}/10")
        print(f"   Snippet: {trend['snippet'][:100]}...")
    
    # Test sponsor finder
    print("\n" + "="*50)
    print("Testing Sponsor Finder...")
    finder = SponsorFinder()
    sponsors = finder.find_sponsors("fitness", num_sponsors=3)
    
    for sponsor in sponsors:
        print(f"\n- {sponsor['brand_name']}")
        print(f"  Relevance: {sponsor['relevance']}/10")
        print(f"  Website: {sponsor['website']}")
