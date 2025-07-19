@echo off
echo Setting up TestFlow...

if not exist backend\.env copy backend\.env.example backend\.env
if not exist frontend\.env.local copy frontend\.env.local.example frontend\.env.local

cd backend && npm install && cd ..
cd frontend && npm install && cd ..

docker-compose -f docker-compose.dev.yml up -d postgres
timeout /t 10

cd backend
npx prisma generate
npx prisma migrate dev --name init
cd ..

echo Setup complete!
pause