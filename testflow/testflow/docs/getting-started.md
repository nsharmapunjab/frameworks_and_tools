# Getting Started with TestFlow

## Prerequisites

- Node.js 18+
- Docker and Docker Compose
- npm or yarn

## Installation Steps

1. **Generate project** using the Python script
2. **Install dependencies** in backend and frontend
3. **Start Docker services** for database
4. **Run database migrations**
5. **Start development servers**

## First Steps

1. Navigate to http://localhost:3000
2. Register a new account
3. Create your first project
4. Add test cases and execute them

## Development Commands

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up

# Stop services
docker-compose -f docker-compose.dev.yml down

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

For more detailed instructions, see the main README.md file.