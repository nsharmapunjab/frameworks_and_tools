# TestFlow Setup Instructions

## Quick Start

1. **Navigate to project:**
   ```bash
   cd testflow
   ```

2. **Run setup (if dependencies installed automatically):**
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   docker-compose -f docker-compose.dev.yml up
   ```

3. **Manual setup (if dependencies need manual installation):**
   ```bash
   # Install dependencies
   cd backend && npm install && cd ..
   cd frontend && npm install && cd ..
   
   # Setup environment
   cp backend/.env.example backend/.env
   cp frontend/.env.local.example frontend/.env.local
   
   # Start database
   docker-compose -f docker-compose.dev.yml up -d postgres
   
   # Setup database (wait 10 seconds first)
   sleep 10
   cd backend && npx prisma generate && npx prisma migrate dev --name init && cd ..
   
   # Start all services
   docker-compose -f docker-compose.dev.yml up
   ```

## Access Points

- Frontend: http://localhost:3000
- Backend: http://localhost:4000
- Database: localhost:5432

## Troubleshooting

- If ports are in use, change them in docker-compose.dev.yml
- If npm install fails, try: npm cache clean --force
- If Docker fails, ensure Docker Desktop is running

## Next Steps

1. Create an account at http://localhost:3000
2. Create your first project
3. Add test cases and start testing!

For more help, see README.md and docs/ folder.