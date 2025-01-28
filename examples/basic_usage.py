from yt_autoresponder import BotConfig, YouTubeAutoResponder

config = BotConfig(
    
    tone="friendly and helpful",
    max_comments=50,
    max_videos=20  # Process maximum 20 videos
)

bot = YouTubeAutoResponder(config)
bot.run()