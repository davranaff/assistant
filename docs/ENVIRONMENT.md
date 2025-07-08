# Environment Variables Setup

This document describes how to configure environment variables for the AutoPoster Bot application.

## Quick Start

1. Copy the template file:
   ```bash
   cp env.template .env
   ```

2. Edit `.env` file with your actual values:
   ```bash
   nano .env
   ```

## Required Variables

### Database Configuration
- `DATABASE_URL`: PostgreSQL connection string
  - Format: `postgresql+asyncpg://username:password@host:port/database`
  - Example: `postgresql+asyncpg://user:password@localhost:5432/autopost_db`

### Telegram Bot Configuration
- `TELEGRAM_BOT_TOKEN`: Token from [@BotFather](https://t.me/BotFather)
  - Required for bot functionality
  - Format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

- `WEBHOOK_BASE_URL`: Your server's public URL
  - Required for webhook mode
  - Example: `https://your-domain.com`
  - For local development: `http://localhost:8000`

### OpenAI Configuration
- `OPENAI_API_KEY`: OpenAI API key for content generation
  - Required for AI-powered article creation
  - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
  - Format: `sk-...`

## Optional Variables

### Publishers API Keys
Configure these if you want to publish to specific platforms:

- `MEDIUM_API_KEY`: Medium API token
  - Get from [Medium Settings](https://medium.com/me/settings)
  - Under "Integration tokens"

- `DEV_TO_API_KEY`: Dev.to API key
  - Get from [Dev.to Settings](https://dev.to/settings/account)
  - Under "DEV Community API Keys"

### Reddit API Configuration
Required for Reddit publishing:

- `REDDIT_CLIENT_ID`: Reddit app client ID
- `REDDIT_CLIENT_SECRET`: Reddit app client secret
- `REDDIT_USERNAME`: Your Reddit username
- `REDDIT_PASSWORD`: Your Reddit password

Get credentials from [Reddit Apps](https://www.reddit.com/prefs/apps)

### Application Configuration
- `SECRET_KEY`: JWT secret key (change in production!)
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration (default: 30)
- `APP_NAME`: Application name (default: AutoPoster Bot)
- `DEBUG`: Debug mode (default: false)

## Environment Files

- `.env` - Main environment file (not committed to git)
- `env.template` - Template with example values (committed to git)
- `.env.local` - Local development overrides
- `.env.production` - Production environment
- `.env.staging` - Staging environment
- `.env.development` - Development environment

## Security Notes

1. Never commit `.env` files to version control
2. Use strong, unique values for `SECRET_KEY` in production
3. Regularly rotate API keys
4. Use environment-specific configurations for different deployments

## Development Setup

For local development, minimal configuration:

```bash
# Required
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/autopost_db
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_key_here

# Optional for local development
WEBHOOK_BASE_URL=http://localhost:8000
DEBUG=true
```

## Production Checklist

- [ ] Strong `SECRET_KEY` generated
- [ ] All required API keys configured
- [ ] Database URL points to production database
- [ ] `DEBUG=false`
- [ ] HTTPS webhook URL configured
- [ ] Environment variables secured (e.g., using secrets manager)
