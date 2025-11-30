# Task Management System

A comprehensive enterprise-grade Task Management System built with FastAPI (Python) and React (TypeScript). Features include JWT authentication with role-based access, task management with categories/priorities, real-time notifications, advanced search/filtering, data export, analytics dashboard, file attachments, and team collaboration.

## 🚀 Features

### Authentication & Authorization
- JWT-based authentication with access and refresh tokens
- Role-based access control (Admin, Manager, Member, Viewer)
- Secure password hashing with bcrypt

### Task Management
- Complete CRUD operations for tasks
- Task categories (Bug, Feature, Improvement, Documentation, etc.)
- Priority levels (Low, Medium, High, Urgent)
- Status tracking (Todo, In Progress, In Review, Completed, Archived)
- Subtasks support
- Due date management with overdue detection

### Team Collaboration
- Create and manage teams
- Team roles (Owner, Admin, Member, Viewer)
- Assign tasks to team members
- Team-based task filtering

### Real-time Notifications
- WebSocket-based real-time notifications
- Notification types for task assignment, updates, completion, etc.
- Mark as read functionality

### Analytics & Reporting
- Task completion statistics
- Status and priority breakdowns
- Team performance metrics
- User activity analytics

### Data Export
- Export tasks to CSV or JSON format
- Filtered exports based on status and team

### File Attachments
- Upload files to tasks
- Supported formats: PDF, DOC, DOCX, XLS, XLSX, images, etc.
- File size limits and validation

## 🏗️ Architecture

The project follows clean architecture principles:

```
task-management-system/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   │   └── v1/         # API version 1
│   │   ├── core/           # Core configurations
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── tests/              # Test suite
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── store/          # Redux store
│   │   └── utils/          # Utilities
│   └── Dockerfile
├── docker-compose.yml      # Container orchestration
└── docs/                   # Documentation
```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: SQLAlchemy with async support (SQLite/PostgreSQL)
- **Authentication**: JWT (python-jose)
- **Validation**: Pydantic
- **Testing**: pytest with pytest-asyncio

### Frontend
- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI (MUI)
- **State Management**: Redux Toolkit
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Charts**: Chart.js with react-chartjs-2

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **CI/CD**: GitHub Actions

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker and Docker Compose (optional)

### Backend Setup

```bash
# Navigate to backend directory
cd task-management-system/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run the application
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

### Frontend Setup

```bash
# Navigate to frontend directory
cd task-management-system/frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will be available at `http://localhost:3000`

### Docker Setup

```bash
# Navigate to project root
cd task-management-system

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📖 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login (form data) |
| POST | `/api/v1/auth/login/json` | Login (JSON) |
| POST | `/api/v1/auth/refresh` | Refresh access token |

### User Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/me` | Get current user |
| PATCH | `/api/v1/users/me` | Update current user |
| GET | `/api/v1/users` | List users (admin) |
| GET | `/api/v1/users/{id}` | Get user by ID |

### Task Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/tasks` | Create task |
| GET | `/api/v1/tasks` | List/search tasks |
| GET | `/api/v1/tasks/{id}` | Get task |
| PATCH | `/api/v1/tasks/{id}` | Update task |
| DELETE | `/api/v1/tasks/{id}` | Delete task |
| POST | `/api/v1/tasks/{id}/attachments` | Upload attachment |
| GET | `/api/v1/tasks/{id}/attachments` | List attachments |

### Team Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/teams` | Create team |
| GET | `/api/v1/teams` | List teams |
| GET | `/api/v1/teams/{id}` | Get team |
| PATCH | `/api/v1/teams/{id}` | Update team |
| DELETE | `/api/v1/teams/{id}` | Delete team |
| POST | `/api/v1/teams/{id}/members` | Add member |
| DELETE | `/api/v1/teams/{id}/members/{user_id}` | Remove member |

### Analytics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/tasks` | Task analytics |
| GET | `/api/v1/analytics/teams/{id}` | Team analytics |
| GET | `/api/v1/analytics/users/me` | User analytics |

### Export Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/export/tasks` | Export tasks (CSV/JSON) |

## 🧪 Testing

### Backend Tests

```bash
cd task-management-system/backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_auth.py
```

### Frontend Tests

```bash
cd task-management-system/frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

## 📝 Environment Variables

### Backend

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT secret key | Generated |
| `DATABASE_URL` | Database connection URL | SQLite |
| `REDIS_URL` | Redis URL (optional) | None |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | 30 |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | localhost |

## 🔒 Security

- Passwords hashed with bcrypt
- JWT tokens with expiration
- Role-based access control
- Input validation with Pydantic
- SQL injection protection via SQLAlchemy ORM
- CORS protection
- Rate limiting (configurable)

## 📈 Performance

- Async database operations
- Connection pooling
- Response compression
- Static asset caching
- Database indexes for common queries

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
