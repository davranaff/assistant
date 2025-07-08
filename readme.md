# 🤖 AutoPostAI Bot

**Telegram Bot for AI Content Generation & Auto Publishing**

A Telegram bot that uses ChatGPT to generate blog posts and auto-publish them to platforms like Medium, Reddit, Dev.to, and more.

## 🚀 Features

✍️ **Generate blog content using OpenAI GPT**
- AI-powered article generation based on topics
- Professional, engaging content creation
- Customizable content style and length

✅ **Confirm, regenerate, or delete drafts via Telegram**
- Interactive approval workflow
- Easy content review and editing
- One-click regeneration with new AI content

🌍 **Auto-publish posts to multiple platforms via APIs**
- Medium integration
- Dev.to publishing
- Reddit posting
- Extensible for new platforms

📊 **Track post status and publication results**
- Real-time publication status
- Success/failure notifications
- Links to published articles

🔧 **Manage everything directly from Telegram**
- Simple command-based interface
- Intuitive inline keyboards
- User-friendly workflow

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.9+
- **Database**: PostgreSQL with SQLAlchemy
- **Bot Framework**: aiogram 3.x
- **AI**: OpenAI GPT-4o-mini
- **Architecture**: Clean Architecture + DDD
- **Deployment**: Docker, Webhook-based

## 📋 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment
```bash
cp env.template .env
nano .env  # Add your API keys
```

### 3. Initialize Database
```bash
python create_tables.py
```

### 4. Run Application
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. Set Webhook
```bash
curl -X POST "http://localhost:8000/api/v1/telegram/set_webhook"
```

## 🎯 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start working with the bot |
| `/new_post` | Create new article |
| `/my_posts` | View your articles |
| `/help` | Show help message |

## 📝 Article Creation Workflow

1. **User**: `/new_post`
2. **Bot**: "Please enter the topic for your article:"
3. **User**: "Artificial Intelligence in Healthcare"
4. **Bot**: Generates content using OpenAI → shows preview
5. **User**: ✅ Confirm / ♻️ Regenerate / ❌ Delete
6. **Bot**: 🚀 Publish → publishes to selected platforms
7. **Bot**: Shows publication results with links

## 🏗️ Architecture

Built with **Clean Architecture** and **Domain-Driven Design** principles:

```
app/
├── api/                    # FastAPI REST API
├── domain/                 # Business logic and rules
├── application/            # Use cases and workflows
├── infrastructure/         # External integrations
└── core/                   # Shared infrastructure
```

## 🔐 Required Configuration

### Essential API Keys:
- `TELEGRAM_BOT_TOKEN` - from @BotFather
- `OPENAI_API_KEY` - from OpenAI Platform
- `DATABASE_URL` - PostgreSQL connection

### Optional Publishing APIs:
- `MEDIUM_API_KEY` - for Medium publishing
- `DEV_TO_API_KEY` - for Dev.to publishing
- `REDDIT_*` - for Reddit publishing

## 🌟 Key Features

- **AI-Powered Content**: Advanced GPT-4 content generation
- **Multi-Platform Publishing**: Publish to multiple platforms simultaneously
- **Clean Architecture**: Maintainable, testable, scalable codebase
- **Webhook Support**: Efficient real-time message handling
- **Type Safety**: Full TypeScript-style type hints
- **Async Operations**: High-performance async/await throughout
- **Environment Management**: Secure configuration handling

## 📚 Documentation

- **[Environment Setup](docs/ENVIRONMENT.md)** - Complete guide to environment variables and configuration
- **[Architecture Guide](docs/ARCHITECTURE.md)** - Detailed architecture documentation and design decisions
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when running)

## 🔧 Development

### Local Development
```bash
# Copy development template
cp env.development .env

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Useful Commands
```bash
# Check webhook status
curl "http://localhost:8000/api/v1/telegram/webhook/info"

# Health check
curl "http://localhost:8000/health"

# Bot information
curl "http://localhost:8000/api/v1/telegram/me"
```

## 🚀 Production Deployment

1. Set up PostgreSQL database
2. Configure environment variables
3. Set webhook URL to your domain
4. Deploy with Docker or cloud platform
5. Monitor logs and performance

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Follow Clean Architecture principles
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

🚀 **Ready to automate your content creation!** Generate, review, and publish articles with AI assistance directly from Telegram.
