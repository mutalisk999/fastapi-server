# FastAPI Server

A scaffolding project repository for a FastAPI server-side application.

## Features

- **FastAPI Framework**: Modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.
- **Configuration Management**: Environment-specific configuration with support for development, testing, and production environments.
- **Database Integration**: MySQL database integration with Peewee ORM and connection pooling.
- **Redis Integration**: Redis client for caching and session management.
- **Authentication**: JWT-based authentication system.
- **Logging**: Configurable logging system with file rotation.
- **CORS Support**: Cross-Origin Resource Sharing (CORS) middleware for handling cross-origin requests.

## Project Structure

```
fastapi-server/
├── config/             # Configuration files
├── controller/         # API controllers
├── database/           # Database models and connector
├── external/           # External service integrations
├── thread_task/        # Background tasks
├── utils/              # Utility functions
├── .gitignore          # Git ignore file
├── LICENSE             # License file
├── Pipfile             # Pipenv dependency file
├── Pipfile.lock        # Pipenv lock file
├── README.md           # This README file
├── api_server.py       # Application entry point
└── app.py              # Application initialization
```

## Getting Started

### Prerequisites

- Python 3.11+
- Pipenv
- MySQL
- Redis (optional)

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

3. **Configure environment variables**:
   Create a `.env` file in the project root directory with the following variables:
   ```
   # Database configuration
   DATABASE_USER=your_database_user
   DATABASE_PASS=your_encrypted_database_password
   DATABASE_HOST=localhost
   DATABASE_PORT=3306
   DATABASE_NAME=your_database_name
   DATABASE_CHARSET=utf8mb4
   DATABASE_POOL_SIZE=5

   # Redis configuration
   REDIS_URL=redis://localhost:6379/0

   # JWT configuration
   JWT_SECRET=your_encrypted_jwt_secret

   # Logger configuration
   LOG_FILE_NAME=app.log
   LOG_LEVEL=INFO
   LOG_FILE_SIZE=10485760
   LOG_BACKUP_COUNT=5
   ```

4. **Run the application**:
   ```bash
   pipenv run python api_server.py
   ```
   You will be prompted to enter a config password for decrypting sensitive information.

## Usage

### API Endpoints

- **GET /api/mock/hello**: A simple mock endpoint that returns "Hello World!"

### Configuration

The application supports three environments:
- **Development**: Uses `.env.dev` file
- **Testing**: Uses `.env.testing` file
- **Production**: Uses `.env.prod` file

You can specify the environment by setting the `USE_CONFIG` environment variable:
```bash
USE_CONFIG=production pipenv run python api_server.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
