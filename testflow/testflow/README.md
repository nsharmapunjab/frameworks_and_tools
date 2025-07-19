# TestFlow - Modern Test Management Platform

🚀 **Production-ready test management tool with seamless CI/CD integration**

## Features

- **Test Case Management**: Create, organize, and execute test cases
- **Traceability Matrix**: Auto-generated relationships
- **Analytics Dashboard**: Real-time metrics and reports
- **CI/CD Integration**: Jenkins webhook support
- **Developer Tools**: CLI and VS Code extension

## Tech Stack

- **Frontend**: Next.js 14 + React 18 + TypeScript + TailwindCSS
- **Backend**: Node.js + Express + TypeScript + Prisma ORM
- **Database**: PostgreSQL
- **Infrastructure**: Docker + Docker Compose

## Quick Start

1. **Generate the project**:
   ```bash
   python3 generate_testflow.py
   cd testflow
   ```

2. **Start development environment**:
   ```bash
   docker-compose -f docker-compose.dev.yml up
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:4000

## Manual Setup

1. **Install dependencies**:
   ```bash
   cd backend && npm install && cd ..
   cd frontend && npm install && cd ..
   ```

2. **Set up environment**:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.local.example frontend/.env.local
   ```

3. **Start services**:
   ```bash
   docker-compose -f docker-compose.dev.yml up -d postgres
   cd backend && npx prisma migrate dev && npx prisma generate
   npm run dev
   ```

## Documentation

- [Getting Started](docs/getting-started.md)
- [API Documentation](docs/api.md)
- [Contributing](docs/contributing.md)

## License

MIT License - see LICENSE file for details.