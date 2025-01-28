"""
Main client class for YouTube AutoResponder
"""
import time
import logging
from typing import List, Tuple
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import GoogleAuthError
from google_auth_oauthlib.flow import InstalledAppFlow
import g4f

from .models import BotConfig
from .exceptions import AuthenticationError, APIQuotaExceeded

logger = logging.getLogger(__name__)

class YouTubeAutoResponder:
    """Main class for handling YouTube comment responses"""
    
    def __init__(self, config: BotConfig):
        self.config = config
        self.youtube = self._authenticate()
        self.processed_comments = 0

    def _authenticate(self):
        """Authenticate with YouTube API"""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.config.client_secrets_file,
                self.config.scopes
            )
            credentials = flow.run_local_server(port=0)
            return build(
                self.config.api_name,
                self.config.api_version,
                credentials=credentials
            )
        except (GoogleAuthError, FileNotFoundError) as e:
            logger.error(f"Authentication error: {str(e)}")
            raise AuthenticationError("Failed to authenticate with YouTube API") from e

    def _handle_api_errors(func):
        """Decorator for handling API errors"""
        def wrapper(self, *args, **kwargs):
            for attempt in range(self.config.max_retries):
                try:
                    return func(self, *args, **kwargs)
                except HttpError as e:
                    if e.resp.status == 403 and 'quotaExceeded' in str(e):
                        raise APIQuotaExceeded("API quota exceeded") from e
                    logger.error(f"HTTP Error {e.resp.status}: {e._get_reason()}")
                    if attempt == self.config.max_retries - 1:
                        raise
                    time.sleep(2 ** attempt)
                except Exception as e:
                    logger.error(f"Unexpected error: {str(e)}")
                    raise
            return None
        return wrapper
        
    @_handle_api_errors
    def get_channel_videos(self) -> List[str]:
        """Get all videos from authenticated user's channel"""
        try:
            # Get channel ID
            channels = self.youtube.channels().list(
                part="snippet,contentDetails",
                mine=True
            ).execute()
            
            channel_id = channels['items'][0]['id']
            
            # Get uploads playlist ID
            playlists = self.youtube.channels().list(
                part="contentDetails",
                id=channel_id
            ).execute()
            
            uploads_playlist_id = playlists['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get all videos from uploads playlist
            video_ids = []
            request = self.youtube.playlistItems().list(
                part="contentDetails",
                playlistId=uploads_playlist_id,
                maxResults=50
            )
            
            while request and len(video_ids) < self.config.max_videos:
                response = request.execute()
                for item in response.get('items', []):
                    video_ids.append(item['contentDetails']['videoId'])
                
                request = self.youtube.playlistItems().list_next(request, response)
                time.sleep(self.config.request_delay)
            
            return video_ids[:self.config.max_videos]
        
        except IndexError:
            logger.error("No channel found for authenticated user")
            return []

    def process_all_videos(self):
        """Main processing loop for all videos"""
        try:
            logger.info("Starting processing for all channel videos")
            video_ids = self.get_channel_videos()
            
            if not video_ids:
                logger.warning("No videos found in channel")
                return
                
            logger.info(f"Found {len(video_ids)} videos to process")
            
            for video_id in video_ids:
                if self.processed_comments >= self.config.max_comments:
                    break
                    
                try:
                    self.process_video(video_id)
                except Exception as e:
                    logger.error(f"Error processing video {video_id}: {str(e)}")
                    continue
                
            logger.info(f"Total processed comments: {self.processed_comments}")
            
        except Exception as e:
            logger.error(f"Critical error in processing: {str(e)}")
            raise

    def process_video(self, video_id: str):
        """Process a single video"""
        logger.info(f"Processing video ID: {video_id}")
        
        context = self.get_video_summary(video_id)
        comments = self.get_unanswered_comments(video_id)
        
        if not comments:
            logger.info("No unanswered comments in this video")
            return
            
        logger.info(f"Found {len(comments)} unanswered comments")
        
        for comment_id, comment_text in comments:
            if self.processed_comments >= self.config.max_comments:
                break
                
            response_text = self.generate_response(comment_text, context)
            if response_text:
                self.post_reply(comment_id, response_text)
                self.processed_comments += 1
                time.sleep(self.config.request_delay)
    @_handle_api_errors
    def get_video_summary(self) -> str:
        """Get video description as context"""
        request = self.youtube.videos().list(
            part="snippet",
            id=self.config.video_id
        )
        response = request.execute()
        return response['items'][0]['snippet']['description'][:1000] if response['items'] else ""

    @_handle_api_errors
    def get_unanswered_comments(self) -> List[Tuple[str, str]]:
        """Retrieve comments without replies"""
        comments = []
        request = self.youtube.commentThreads().list(
            part="snippet,replies",
            videoId=self.config.video_id,
            moderationStatus="published",
            textFormat="plainText",
            maxResults=100
        )

        while request and self.processed_comments < self.config.max_comments:
            time.sleep(self.config.request_delay)
            response = request.execute()
            
            for item in response.get('items', []):
                if not item.get('replies'):
                    comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                    comment_id = item['snippet']['topLevelComment']['id']
                    comments.append((comment_id, comment))
                    self.processed_comments += 1
                    
                    if self.processed_comments >= self.config.max_comments:
                        return comments
            
            request = self.youtube.commentThreads().list_next(request, response)
        
        return comments

    def generate_response(self, comment: str, context: str) -> str:
        """Generate AI response using LLM"""
        try:
            prompt = (
                f"Respond to this YouTube comment in a {self.config.tone} tone. "
                f"Video context: {context[:2000]}\n\n"
                f"Comment: {comment[:500]}\n\n"
                "Response:"
            )
            
            response = g4f.ChatCompletion.create(
                model=g4f.models.gpt_4,
                messages=[{"role": "user", "content": prompt}],
            )
            
            return response.strip()[:500]
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            return ""

    @_handle_api_errors
    def post_reply(self, comment_id: str, text: str) -> bool:
        """Post reply to a comment"""
        if not text:
            return False
            
        self.youtube.comments().insert(
            part="snippet",
            body={
                "snippet": {
                    "parentId": comment_id,
                    "textOriginal": text
                }
            }
        ).execute()
        logger.info(f"Posted reply to comment {comment_id}")
        return True

    def run(self):
        """Execute the comment response workflow"""
        try:
            logger.info("Starting comment response process...")
            context = self.get_video_summary()
            comments = self.get_unanswered_comments()
            
            for comment_id, comment_text in comments:
                if self.processed_comments >= self.config.max_comments:
                    break
                
                response_text = self.generate_response(comment_text, context)
                if response_text:
                    self.post_reply(comment_id, response_text)
                    time.sleep(self.config.request_delay)
            
            logger.info(f"Processed {self.processed_comments} comments successfully")
            
        except APIQuotaExceeded as e:
            logger.error("Stopping due to API quota limits")
            raise
        except Exception as e:
            logger.error(f"Critical error: {str(e)}")
            raise