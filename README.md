# AI Chat API

A Flask-based REST API that provides a secure chat interface with AI, featuring user authentication, request quota management, and detailed logging.

## Features

- 🔐 JWT-based Authentication
- 📝 MongoDB Integration
- 🤖 AI Chat Interface with Ollama
- ⚡ Rate Limiting (15 requests per day per user)
- 📨 Email Support (Password Reset & Notifications)
- 🔍 Detailed Logging System
- 🌐 CORS Support
- 🔑 Google OAuth Integration

## Tech Stack

- **Backend Framework**: Flask
- **Database**: MongoDB with MongoEngine ODM
- **Authentication**: JWT (JSON Web Tokens)
- **AI Model**: Ollama (llama3.2)
- **Email**: Flask-Mail
- **Documentation**: OpenAPI/Swagger

## Prerequisites

- Python 3.9+
- MongoDB
- Ollama (running locally)
- SMTP server access (for email functionality)
- Google OAuth credentials (for social login)

## Ollama Setup

1. **Install Ollama**
   ```bash
   # For macOS or Linux
   curl -fsSL https://ollama.com/install.sh | sh
   
   # For Windows
   # Download from https://ollama.com/download/windows
   ```

2. **Start Ollama Server**
   ```bash
   ollama serve
   ```

3. **Pull the LLaMA Model**
   ```bash
   ollama pull llama3.2
   ```

4. **Test Ollama**
   ```bash
   # In a new terminal
   curl http://localhost:11434/api/generate -d '{
     "model": "llama3.2",
     "prompt": "Hello, how are you?"
   }'
   ```

5. **Verify API Access**
   - Ensure Ollama is running on `http://localhost:11434`
   - The Flask app will communicate with this endpoint
   - Default model used: `llama3.2`

## Quick Start

1. **Clone the repository**
bash
git clone <repository-url>
cd <project-directory>

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
Create a `.env` file in the root directory:
```env
# Flask Configuration
SECRET_KEY=your_secret_key
FLASK_DEBUG=1
FLASK_APP=run.py

# MongoDB Configuration
MONGODB_URI=your_mongodb_connection_string

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password

# Web Client URL
WEB_CLIENT_URL=http://localhost:3000

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Logging Configuration
LOG_LEVEL=DEBUG
LOG_TO_CONSOLE=True
LOG_TO_FILE=True
LOG_FILE=logs/app.log
```

5. **Start the application**
```bash
flask run
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/google` - Google OAuth login
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password

### User Management
- `GET /api/users/profile` - Get user profile
- `GET /api/users/quota` - Get remaining request quota

### Chat
- `POST /api/chat/send` - Send message to AI
  ```json
  {
    "message": "Your message here",
    "context_id": "optional_context_id"
  }
  ```

## Request Quota System

Each user is limited to 15 requests per day:
- Quota resets at midnight UTC
- Remaining quota returned in response headers (`X-RateLimit-Remaining`)
- Quota information included in chat responses:
  ```json
  {
    "response": "AI response",
    "context_id": "uuid",
    "success": true,
    "quota": {
      "remaining_requests": 14,
      "max_requests": 15,
      "reset_time": "midnight UTC"
    }
  }
  ```

## Logging System

The application uses a comprehensive logging system:
- Console and/or file logging (configurable via environment variables)
- Rotating file logs with configurable size and backup count
- Detailed log format including:
  - Timestamp
  - Module name
  - Log level
  - File name and line number
  - Message

## Development

### VS Code Configuration
Launch configuration is provided in `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debugger: Flask",
            "type": "debugpy",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "run.py",
                "FLASK_DEBUG": "1"
            },
            "args": [
                "run",
                "--no-debugger"
            ],
            "jinja": true,
            "autoStartBrowser": false
        }
    ]
}
```

### Project Structure
```
.
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models/
│   ├── routes/
│   └── utils/
├── logs/
├── .env
├── requirements.txt
└── run.py
```

## Security Features

- JWT-based authentication
- Password hashing
- Rate limiting
- CORS protection
- Environment variable configuration
- Secure password reset flow
- OAuth 2.0 integration

## Error Handling

Standard HTTP status codes are used:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 429: Too Many Requests (quota exceeded)
- 500: Internal Server Error

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

