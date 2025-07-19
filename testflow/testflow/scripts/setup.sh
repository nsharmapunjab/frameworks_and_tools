#!/bin/bash

echo "🚀 Setting up TestFlow..."

# Create environment files
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env"
fi

if [ ! -f frontend/.env.local ]; then
    cp frontend/.env.local.example frontend/.env.local
    echo "✅ Created frontend/.env.local"
fi

# Install dependencies
echo "📦 Installing dependencies..."
cd backend && npm install && cd ..
cd frontend && npm install && cd ..

# Start Docker services
echo "🐳 Starting Docker services..."
docker-compose -f docker-compose.dev.yml up -d postgres

# Wait and setup database
echo "⏳ Setting up database..."
sleep 10
cd backend
npx prisma generate
npx prisma migrate dev --name init
cd ..

echo "🎉 Setup complete! Run 'docker-compose -f docker-compose.dev.yml up' to start."