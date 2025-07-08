# AutoPoster Bot - Architecture

## Overview

The project is built on **Clean Architecture** and **Domain-Driven Design (DDD)** principles with clear layer separation and Dependency Injection.

## Architectural Principles

- **Inversion of Control** - dependencies inverted through interfaces
- **Dependency Injection** - dependency management through DI container
- **Single Responsibility** - each class has one responsibility
- **Open/Closed** - easily extended with new functionality
- **Interface Segregation** - narrow, specialized interfaces

## Layer Structure

### 1. Domain Layer (`app/domain/`)
**Core layer** - contains business logic and rules

```
domain/
├── models/              # Domain models with business logic
│   └── post.py         # Post, PostContent, PublicationResult
├── repositories/        # Repository interfaces
│   └── post_repository.py
└── services/           # Domain service interfaces
    ├── content_generator.py
    └── publisher.py
```

**Principles:**
- Independent of external layers
- Contains core business logic
- Defines interfaces for external dependencies

### 2. Application Layer (`app/application/`)
**Orchestration** - use cases and application services

```
application/
└── use_cases/          # Use case scenarios
    ├── create_post.py
    ├── confirm_post.py
    ├── publish_post.py
    └── regenerate_content.py
```

**Principles:**
- Coordinates business operation execution
- Depends only on Domain Layer
- Contains application-specific logic

### 3. Infrastructure Layer (`app/infrastructure/`)
**External integrations** - interface implementations

```
infrastructure/
├── repositories/       # Repository implementations
│   └── sqlalchemy_post_repository.py
└── services/          # External service implementations
    ├── openai_content_generator.py
    ├── multi_platform_publisher.py
    └── platform_publishers.py
```

**Principles:**
- Implements interfaces from Domain Layer
- Integrates with external systems (DB, APIs)
- Contains technical details

### 4. Presentation Layer (`app/presentation/`)
**Entry points** - controllers and handlers

```
presentation/
├── api/               # REST API controllers
│   └── telegram_controller.py
└── telegram/          # Telegram bot handlers
    └── bot_handlers.py
```

**Principles:**
- Handles incoming requests
- Calls Application Layer use cases
- Formats responses

### 5. Core Layer (`app/core/`)
**Shared Kernel** - shared infrastructure

```
core/
├── config.py          # Application configuration
├── container.py       # DI container
├── logging.py         # Logging setup
└── bootstrap.py       # Application initialization
```

## Data Flow

```
Telegram → Presentation → Application → Domain → Infrastructure
    ↓           ↓            ↓          ↓           ↓
 Webhook → Controller → Use Case → Model → Repository → Database
```

## Dependency Injection

All dependencies are managed through DI container:

```python
# Registration in bootstrap.py
register_service(PostRepository, SqlAlchemyPostRepository)
register_service(ContentGenerator, OpenAIContentGenerator)

# Usage in use case
post_repository = resolve_service(PostRepository)
```

## Telegram Bot Flow

1. **Webhook** → `TelegramController.webhook()`
2. **Handler** → `BotHandlers.handle_*`
3. **Use Case** → Application Layer
4. **Response** → Telegram API

## Extensibility

### Adding new publishing platform:

1. Create publisher in `infrastructure/services/`
2. Register in `MultiPlatformPublisher`
3. Add to `Platform` enum

### Adding new use case:

1. Create in `application/use_cases/`
2. Register in DI container
3. Use in controller

### Adding new domain model:

1. Create in `domain/models/`
2. Create repository interface
3. Implement in Infrastructure Layer

## Testing

Architecture facilitates testing:

- **Unit tests** - isolated domain model tests
- **Integration tests** - use case tests with mocks
- **E2E tests** - API endpoint tests

## Architecture Benefits

✅ **Readability** - clear separation of concerns
✅ **Testability** - easy to mock dependencies
✅ **Extensibility** - simple addition of new features
✅ **Maintainability** - changes are localized
✅ **Scalability** - ready for growth

## Disadvantages

❌ **Complexity** - requires understanding of patterns
❌ **Overhead** - more files and abstractions
❌ **Learning Curve** - need to learn principles

---

*Architecture designed for long-term development and project scaling.*
