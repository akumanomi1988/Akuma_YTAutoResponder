# YouTube AutoResponder 🚀

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


The bot will automatically:
1. Detect your YouTube channel
2. Find all your recent videos
3. Process unanswered comments in all videos

```python
from yt_autoresponder import BotConfig, YouTubeAutoResponder

# Minimal configuration example
config = BotConfig(
    max_comments=100,  # Daily comment limit
    max_videos=20      # Maximum videos to check
)

bot = YouTubeAutoResponder(config)
bot.run()
```
## Features:

🔄 Automatic channel detection

📅 Processes most recent videos first

⚖️ Configurable daily limits

⏳ Intelligent rate limiting

🔍 Error recovery and continuation

## Installation 📦

```bash
pip install yt-autoresponder
```
## Quick Start 🚀

1. **Set up Google Cloud credentials**:
   - Create a project in [Google Cloud Console](https://console.cloud.google.com/)
   - Enable YouTube Data API v3
   - Create OAuth 2.0 Client ID (Desktop App type)
   - Download credentials as `client_secrets.json`

2. **Basic usage example**:
```python
from yt_autoresponder import BotConfig, YouTubeAutoResponder

config = BotConfig(
    client_secrets_file="path/to/your/client_secrets.json",  # Required
    tone="friendly",
    max_comments=50,
    max_videos=20
)

bot = YouTubeAutoResponder(config)
bot.run()
```

## Configuration ⚙️

### BotConfig Options:
```python
@dataclass
class BotConfig:
    video_id: str                   # YouTube video ID
    client_secrets_file: str = 'client_secrets.json'  # OAuth2 credentials
    tone: str = "professional"      # Response tone/style
    max_comments: int = 30          # Max comments to process daily
    request_delay: float = 1.5      # Delay between API requests
    max_retries: int = 3            # API error retry attempts
```

## Advanced Usage 🔧

### Scheduled Daily Execution
Use cron (Linux/macOS) or Task Scheduler (Windows) to run daily:
```bash
# Example cron job (runs daily at 8am)
0 8 * * * /path/to/python /path/to/your_script.py
```

### Custom Response Templates
Extend the `generate_response` method to implement custom templates:
```python
class CustomResponder(YouTubeAutoResponder):
    def generate_response(self, comment: str, context: str) -> str:
        # Implement custom logic here
        return super().generate_response(comment, context)
```

## Contributing 🤝

Contributions are welcome! Please read our [contribution guidelines](CONTRIBUTING.md) before submitting PRs.

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
