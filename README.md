# FastAPI Server

A scaffolding project repository for a FastAPI server-side application.

## Features

- **FastAPI Framework**: Modern, fast (high-performance), web framework for building APIs with Python 3.11+ based on standard Python type hints.
- **Configuration Management**: Environment-specific configuration with support for development, testing, and production environments.
- **Database Integration**: MySQL/PostgreSQL/SQLite database integration with Peewee ORM, connection pooling, and auto-reconnect.
- **Redis Integration**: Redis client for caching, session management, rate limiting, and token blacklisting.
- **Authentication**: JWT (HS256) based authentication with token blacklist/revocation support.
- **Encryption**: AES-256-GCM for encrypting sensitive configuration values (database passwords, JWT secrets).
- **Rate Limiting**: IP-based rate limiting on login endpoint (5 requests/60s by default).
- **Input Validation**: Pydantic request models for all API endpoints.
- **Logging**: Configurable logging system with file rotation, using proxy pattern for runtime reconfiguration.
- **CORS Support**: Cross-Origin Resource Sharing (CORS) middleware for handling cross-origin requests.
- **Background Tasks**: Thread manager with per-thread stop events for graceful shutdown.

## Project Structure

```
fastapi-server/
├── config/             # Configuration files (base, dev, testing, prod)
├── controller/         # API controllers (auth, user, mock)
├── database/           # Database proxy, base model, reconnect connectors
├── external/           # External service integrations (reserved)
├── services/           # Business logic (auth, user)
├── tests/              # Unit tests
├── thread_task/        # Background thread manager
├── utils/              # Utilities (auth, crypto, logger, redis, rate limit, captcha, password)
├── models.py           # Pydantic request validation models
├── api_server.py       # Application entry point
└── app.py              # Application initialization, middleware, routing
```

## Getting Started

### Prerequisites

- Python 3.11+
- Pipenv
- MySQL
- Redis (optional, used for rate limiting and token blacklist)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd fastapi-server
   ```

2. **Install dependencies**:
   ```bash
   pipenv install
   ```

3. **Encrypt sensitive configuration values**:
   Sensitive values (DATABASE_PASS, JWT_SECRET) must be AES-256-GCM encrypted before storing in env files. Use the encryption utility:
   ```python
   from utils.crypto_tools import AesGcm
   aes = AesGcm(b"your_config_password")
   encrypted = aes.encrypt(b"your_secret_value")
   print(encrypted)  # Store this hex string in the env file
   ```

4. **Configure environment variables**:
   - Create a `.env` file in the project root directory:
     ```
     USE_CONFIG=development
     ```
   - Create environment-specific configuration files:
     - `.env.dev` for development
     - `.env.testing` for testing
     - `.env.prod` for production

   Example `.env.dev`:
   ```
   # JWT configuration (AES-256-GCM encrypted hex string)
   JWT_SECRET=<encrypted_hex_string>

   # Database configuration
   DATABASE_USER=root
   DATABASE_PASS=<encrypted_hex_string>
   DATABASE_HOST=localhost
   DATABASE_PORT=3306
   DATABASE_NAME=dev_db
   DATABASE_CHARSET=utf8mb4
   DATABASE_POOL_SIZE=5

   # Redis configuration
   REDIS_URL=redis://localhost:6379/0

   # Log configuration
   LOG_FILE_NAME=app.log
   LOG_LEVEL=INFO
   LOG_FILE_SIZE=10485760
   LOG_BACKUP_COUNT=5
   ```

5. **Run the application**:
   ```bash
   pipenv run python api_server.py
   ```
   You will be prompted to enter the config password used to encrypt sensitive values.

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/mock/hello` | No | Mock endpoint, returns "Hello World!" |
| POST | `/api/auth/login` | No | User login, returns JWT token (rate limited: 5 req/min) |
| POST | `/api/auth/refresh` | No | Refresh JWT token, old token is revoked |
| POST | `/api/auth/logout` | Bearer | Logout, revokes current token |
| GET | `/api/users/{user_id}` | Bearer | Get user info |
| POST | `/api/users` | Bearer | Create user |
| PUT | `/api/users/{user_id}` | Bearer | Update user info |
| DELETE | `/api/users/{user_id}` | Bearer | Delete user |

### Request/Response Examples

**Login**:
```json
POST /api/auth/login
{
  "username": "admin",
  "password": "admin123"
}

Response:
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 604800
}
```

**Authenticated Request**:
```
GET /api/users/123
Authorization: Bearer eyJ...
```

## Architecture

### Middleware Stack (outer to inner)

1. **CORS Middleware** — Handles cross-origin requests
2. **Error Handler Middleware** — Catches exceptions, returns generic 500 responses (no internal details leaked)
3. **DB Session Middleware** — Manages database connections per request, rollback on error, proper pool handling

### Authentication Flow

1. Client sends username/password to `/api/auth/login`
2. Server verifies password (bcrypt), generates JWT (HS256, 7-day expiry)
3. Client includes `Authorization: Bearer <token>` in subsequent requests
4. Token verification checks both JWT signature and Redis blacklist
5. `/api/auth/logout` adds token to Redis blacklist with remaining TTL
6. `/api/auth/refresh` revokes old token and issues a new one

### Encryption

Configuration values are encrypted with AES-256-GCM using a config password provided at startup:
- 256-bit key derived via SHA-256 from the config password
- 96-bit random nonce per encryption (stored prepended to ciphertext)
- Authentication tag ensures ciphertext integrity

### Database Auto-Reconnect

Custom `ReconnectMixinNew` wraps Peewee database drivers to automatically reconnect on connection errors (MySQL/PostgreSQL/SQLite, with or without connection pooling).

### Background Threads

`ThreadManager` manages named daemon threads with per-thread `stop_event` for graceful individual shutdown, plus `Application.global_stop` for full application shutdown.

## Configuration

### Two-Level Configuration

1. **`.env`** — Contains only `USE_CONFIG` to select the environment
2. **Environment-specific** (`.env.dev` / `.env.testing` / `.env.prod`) — All business configuration

### Supported Environments

| Environment | Config File | Pool Size | Notes |
|-------------|-------------|-----------|-------|
| Development | `.env.dev` | 5 (default) | Single connection or small pool |
| Testing | `.env.testing` | 5 (default) | Isolated test database |
| Production | `.env.prod` | 20 | Large connection pool |

### Specifying Environment

```bash
USE_CONFIG=production pipenv run python api_server.py
```

## Running Tests

```bash
pipenv run python -m pytest tests/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
