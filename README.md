# FastAPI Server

A scaffolding project repository for a FastAPI server-side application with authentication, database integration, and background task support.

## Features

- **FastAPI Framework**: Modern, fast (high-performance), web framework for building APIs with Python 3.11+ based on standard Python type hints.
- **Configuration Management**: Environment-specific configuration (development, testing, production) with encrypted secrets.
- **Database Integration**: MySQL/PostgreSQL/SQLite database integration with Peewee ORM, connection pooling, and auto-reconnect.
- **Redis Integration**: Redis client for caching, session management, rate limiting, and token blacklisting.
- **Authentication**: JWT (HS256) based authentication with bcrypt password hashing and token blacklist/revocation support.
- **Encryption**: AES-256-GCM for encrypting sensitive configuration values (database passwords, JWT secrets).
- **Rate Limiting**: IP-based rate limiting on login endpoint (5 requests/60s by default).
- **Request Validation**: Pydantic models for request validation.
- **Logging**: Configurable logging system with file rotation, using proxy pattern for runtime reconfiguration.
- **CORS Support**: Configurable Cross-Origin Resource Sharing (CORS) middleware.
- **Background Tasks**: Thread manager for handling background tasks with per-thread graceful shutdown.

## Project Structure

```
fastapi-server/
├── config/             # Configuration files (base, dev, testing, prod)
├── controller/         # API controllers (auth, user, mock)
├── database/           # Database proxy, base model, reconnect connectors
├── external/           # External service integrations (reserved)
├── services/           # Business logic services (auth, user)
├── tests/              # Unit tests
├── thread_task/        # Background task management
├── utils/              # Utility functions (auth, crypto, logger, redis, rate limit, captcha, password, schemas)
├── logs/               # Application logs (auto-created)
├── .env                # Environment selector (USE_CONFIG)
├── .env.dev            # Development environment variables
├── .env.testing        # Testing environment variables
├── .env.prod           # Production environment variables
├── requirements.txt    # Python dependencies
├── api_server.py       # Application entry point
└── app.py              # Application initialization, middleware, routing
```

## Getting Started

### Prerequisites

- Python 3.11+
- MySQL 5.7+
- Redis (optional, used for rate limiting and token blacklist)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd fastapi-server
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Encrypt sensitive configuration values**:
   Sensitive values (DATABASE_PASS, JWT_SECRET) must be AES-256-GCM encrypted before storing in env files:
   ```python
   from utils.crypto_tools import AesGcm
   aes = AesGcm(b"your_config_password")
   encrypted = aes.encrypt(b"your_secret_value")
   print(encrypted)  # Store this hex string in the env file
   ```

4. **Configure environment variables**:

   Create a `.env` file in the project root:
   ```env
   USE_CONFIG=development
   ```

   Create environment-specific configuration files:

   **`.env.dev`** (Development):
   ```env
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

   # CORS configuration
   CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]

   # Server configuration
   SERVER_HOST=0.0.0.0
   SERVER_PORT=7788

   # Log configuration
   LOG_FILE_NAME=app.log
   LOG_LEVEL=INFO
   LOG_FILE_SIZE=10485760
   LOG_BACKUP_COUNT=5
   ```

5. **Run the application**:
   ```bash
   python api_server.py
   ```
   You will be prompted to enter the config password for decrypting sensitive information (JWT_SECRET, DATABASE_PASS).

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/mock/hello` | No | Returns "Hello World!" message |
| POST | `/api/auth/login` | No | User login, returns JWT token (rate limited: 5 req/min) |
| POST | `/api/auth/refresh` | No | Refresh JWT token, old token is revoked |
| POST | `/api/auth/logout` | Bearer | Logout, revokes current token |
| GET | `/api/users/{user_id}` | Bearer | Get user information |
| POST | `/api/users` | Bearer | Create a new user |
| PUT | `/api/users/{user_id}` | Bearer | Update user information |
| DELETE | `/api/users/{user_id}` | Bearer | Delete a user |

### Request/Response Examples

**Login**:
```json
POST /api/auth/login
{
  "username": "admin",
  "password": "admin123"
}
```
> **Note**: `admin/admin123` is a **development-only** mock credential. It is
> accepted only while `MOCK_AUTH_ENABLED=true` (the default in dev/testing).
> The production config forces `MOCK_AUTH_ENABLED=false`, which rejects all
> logins until a real user store is wired in.

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 604800
}
```

**Authenticated Request**:
```
GET /api/users/123
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

## Architecture

### Middleware Stack (outer to inner)

1. **CORS Middleware** — Handles cross-origin requests
2. **Error Handler Middleware** — Catches exceptions, returns generic 500 responses (no internal details leaked)
3. **DB Session Middleware** — Manages database transactions per request, commit on success, rollback on error, proper pool handling

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

`ThreadManager` manages named daemon threads with per-thread `_stop_flag` for graceful individual shutdown, plus `Application.global_stop` for full application shutdown.

## Configuration Reference

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| JWT_SECRET | string | - | JWT signing secret (encrypted) |
| DATABASE_USER | string | - | Database username |
| DATABASE_PASS | string | - | Database password (encrypted) |
| DATABASE_HOST | string | localhost | Database host |
| DATABASE_PORT | int | 3306 | Database port |
| DATABASE_NAME | string | - | Database name |
| DATABASE_CHARSET | string | utf8mb4 | Database charset |
| DATABASE_POOL_SIZE | int | 5 | Database connection pool size |
| REDIS_URL | string | redis://localhost:6379/0 | Redis connection URL |
| CORS_ORIGINS | list | ["http://localhost:3000"] | Allowed CORS origins |
| SERVER_HOST | string | 0.0.0.0 | Server bind address |
| SERVER_PORT | int | 7788 | Server port |
| LOG_FILE_NAME | string | app.log | Log file name |
| LOG_LEVEL | string | INFO | Log level (DEBUG, INFO, WARNING, ERROR) |
| LOG_FILE_SIZE | int | 10485760 | Max log file size in bytes |
| LOG_BACKUP_COUNT | int | 5 | Number of log backup files |

### Supported Environments

| Environment | Config File | Pool Size | Notes |
|-------------|-------------|-----------|-------|
| Development | `.env.dev` | 5 (default) | Single connection or small pool |
| Testing | `.env.testing` | 5 (default) | Isolated test database |
| Production | `.env.prod` | 20 | Large connection pool |

### Specifying Environment

```bash
USE_CONFIG=production python api_server.py
```

## Security Considerations

- The `admin/admin123` login is a **dev-only mock**; production sets `MOCK_AUTH_ENABLED=false` and rejects all logins until a real user store exists
- All sensitive configuration values should be encrypted before storing in `.env` files
- The config password is entered at runtime and never stored
- JWT tokens expire after 7 days by default
- Tokens can be revoked via Redis blacklist on logout
- Passwords are hashed using bcrypt before storage
- Login endpoint is rate-limited to prevent brute force attacks
- CORS origins should be restricted in production
- Error responses never leak internal exception details

## Testing

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_auth_service
python -m unittest tests.test_password_tools
python -m unittest tests.test_user_service
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
