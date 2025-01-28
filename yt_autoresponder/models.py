@dataclass
class BotConfig:
    """
    Configuration model for the responder bot
    
    Args:
        client_secrets_file (str): Path to Google API OAuth2 client secrets JSON file
        tone (str): Desired tone for responses (e.g., "friendly", "professional")
        max_comments (int): Maximum comments to process daily
        max_videos (int): Maximum videos to check per execution
        request_delay (float): Delay between API requests in seconds
        max_retries (int): Maximum retry attempts for API calls
    """
    client_secrets_file: str = 'client_secrets.json'
    api_name: str = 'youtube'
    api_version: str = 'v3'
    scopes: List[str] = None
    tone: str = "friendly and professional"
    max_retries: int = 3
    request_delay: float = 1.5
    max_comments: int = 30
    max_videos: int = 10  # New parameter

    def __post_init__(self):
        if self.scopes is None:
            self.scopes = [
                'https://www.googleapis.com/auth/youtube.force-ssl',
                'https://www.googleapis.com/auth/youtube.readonly'
            ]