# FastAPI Server

A scaffolding project repository for a FastAPI server-side application with authentication, database integration, and background task support.

## Features

- **FastAPI Framework**: Modern, fast (high-performance), web framework for building APIs with Python 3.11+
- **Configuration Management**: Environment-specific configuration (development, testing, production) with encrypted secrets
- **Database Integration**: MySQL database integration with Peewee ORM and auto-reconnect connection pooling
- **Redis Integration**: Redis client wrapper for caching and session management
- **Authentication**: JWT-based authentication system with password hashing (bcrypt)
- **Request Validation**: Pydantic models for request validation
- **Logging**: Configurable logging system with file rotation
- **CORS Support**: Configurable Cross-Origin Resource Sharing (CORS) middleware
- **Background Tasks**: Thread manager for handling background tasks with graceful shutdown

## Project Structure

```
fastapi-server/
├── config/             # Configuration files (base, dev, testing, prod)
├── controller/         # API controllers (auth, user)
├── database/           # Database connector with auto-reconnect
├── external/           # External service integrations
├── services/           # Business logic services (auth, user)
├── thread_task/        # Background task management
├── tests/              # Unit tests
├── utils/              # Utility functions (auth, crypto, logger, redis, etc.)
├── logs/               # Application logs (auto-created)
├── .env                # Environment selector (USE_CONFIG)
├── .env.dev            # Development environment variables
├── .env.testing        # Testing environment variables
├── .env.prod           # Production environment variables
├── requirements.txt    # Python dependencies
├── README.md           # This README file
├── api_server.py       # Application entry point
└── app.py              # Application initialization
```

## Getting Started

### Prerequisites

- Python 3.11+
- MySQL 5.7+
- Redis (optional)

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

3. **Configure environment variables**:

   Create a `.env` file in the project root:
   ```env
   # Environment selector: development, testing, or production
   USE_CONFIG=development
   ```

   Create environment-specific configuration files:

   **`.env.dev`** (Development):
   ```env
   # JWT configuration (encrypted with config password)
   JWT_SECRET=<encrypted_jwt_secret>

   # Database configuration
   DATABASE_USER=root
   DATABASE_PASS=<encrypted_database_password>
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

4. **Run the application**:
   ```bash
   python api_server.py
   ```

   You will be prompted to enter a config password for decrypting sensitive information (JWT_SECRET, DATABASE_PASS).

## API Endpoints

### Mock Endpoints

- **GET /api/mock/hello**: Returns "Hello World!" message

### Authentication Endpoints

- **POST /api/auth/login**: User login
  ```json
  {
    "username": "admin",
    "password": "admin123"
  }
  ```
  Response:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 604800
  }
  ```

- **POST /api/auth/refresh**: Refresh access token
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIs..."
  }
  ```

### User Endpoints (Require Authentication)

All user endpoints require a Bearer token in the Authorization header.

- **GET /api/users/{user_id}**: Get user information
- **POST /api/users**: Create a new user
  ```json
  {
    "username": "newuser",
    "email": "user@example.com"
  }
  ```
- **PUT /api/users/{user_id}**: Update user information
  ```json
  {
    "username": "updated_user",
    "email": "updated@example.com"
  }
  ```
- **DELETE /api/users/{user_id}**: Delete a user

## Configuration Encryption

Sensitive configuration values (JWT_SECRET, DATABASE_PASS) are encrypted using AES-128-CBC. To encrypt a value:

```python
from utils.crypto_tools import Aes128Cbc

# Use your config password to create the cipher
aes = Aes128Cbc(b"your_config_password")

# Encrypt a value
encrypted = aes.aes128_cbc_encrypt(b"my_secret_value")
print(encrypted)  # Put this in your .env file

# Decrypt a value
decrypted = aes.aes128_cbc_decrypt(encrypted)
print(decrypted)  # Outputs: my_secret_value
```

## Environment Configuration

### Supported Environments

- **development**: Uses `.env.dev` file
- **testing**: Uses `.env.testing` file
- **production**: Uses `.env.prod` file
- **default**: Falls back to development

### Configuration Reference

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

## Background Tasks

The application includes a thread manager for handling background tasks:

```python
from thread_task import thread_manager

def my_task(args):
    while not Application.global_stop:
        # Do work here
        pass

# Start a thread
thread_manager.start_thread(
    thread_id="my_task",
    name="My Background Task",
    function=my_task,
    args=None
)

# Stop a specific thread
thread_manager.stop_thread("my_task")

# Stop all threads
thread_manager.stop_all_threads()
```

## Testing

Run unit tests:

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_auth_service
python -m unittest tests.test_password_tools
python -m unittest tests.test_user_service
```

## Security Considerations

- All sensitive configuration values should be encrypted before storing in `.env` files
- The config password is entered at runtime and never stored
- JWT tokens expire after 7 days by default
- Passwords are hashed using bcrypt before storage
- CORS origins should be restricted in production

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
