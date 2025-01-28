"""
Complete configuration example with custom paths
"""
from yt_autoresponder import BotConfig, YouTubeAutoResponder

def main():
    config = BotConfig(
        client_secrets_file="/etc/youtube_credentials/client_secrets.json",
        tone="professional with occasional humor",
        max_comments=100,
        max_videos=50,
        request_delay=2.0,
        max_retries=5
    )
    
    bot = YouTubeAutoResponder(config)
    
    try:
        bot.run()
    except Exception as e:
        print(f"Error during execution: {str(e)}")

if __name__ == "__main__":
    main()