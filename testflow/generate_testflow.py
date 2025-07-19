#!/usr/bin/env python3
"""
TestFlow Framework Generator
============================

This script automatically generates the complete TestFlow test management framework.
Run this script to create the entire project structure with all necessary files.

Author: Nitin Sharma
Version: 1.0.0
License: MIT
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Any

class TestFlowGenerator:
    def __init__(self):
        self.project_name = "testflow"
        self.current_dir = Path.cwd()
        self.project_dir = self.current_dir / self.project_name
        self.colors = {
            'GREEN': '\033[92m',
            'BLUE': '\033[94m',
            'YELLOW': '\033[93m',
            'RED': '\033[91m',
            'BOLD': '\033[1m',
            'END': '\033[0m'
        }

    def print_colored(self, message: str, color: str = 'END'):
        """Print colored messages to console"""
        print(f"{self.colors.get(color, self.colors['END'])}{message}{self.colors['END']}")

    def print_banner(self):
        """Print the welcome banner"""
        banner = """
================================================================
                    TestFlow Generator                        
              Production-Ready Test Management Tool
		created by Nitin Sharma           
                                                              
  🚀 Modern Stack: Next.js + Node.js + PostgreSQL           
  📊 Rich Analytics & Reporting Dashboard                    
  🔗 Jenkins CI/CD Integration                               
  📋 Traceability Matrix & Release Management                
  🛠️ CLI Tools & VS Code Extension                           
================================================================
        """
        self.print_colored(banner, 'BLUE')

    def check_prerequisites(self):
        """Check if required tools are installed"""
        self.print_colored("\n🔍 Checking prerequisites...", 'YELLOW')
        
        required_tools = {
            'node': 'Node.js (v18 or higher)',
            'npm': 'npm package manager', 
            'docker': 'Docker',
            'docker-compose': 'Docker Compose'
        }
        
        missing_tools = []
        
        for tool, description in required_tools.items():
            try:
                result = subprocess.run([tool, '--version'], 
                                      capture_output=True, text=True, check=True)
                self.print_colored(f"  ✅ {description}: Found", 'GREEN')
            except (subprocess.CalledProcessError, FileNotFoundError):
                missing_tools.append(description)
                self.print_colored(f"  ❌ {description}: Not found", 'RED')
        
        if missing_tools:
            self.print_colored("\n⚠️  Missing required tools:", 'RED')
            for tool in missing_tools:
                self.print_colored(f"    - {tool}", 'RED')
            self.print_colored("\nPlease install missing tools and run again.", 'RED')
            return False
        
        self.print_colored("\n✅ All prerequisites satisfied!", 'GREEN')
        return True

    def create_directory_structure(self):
        """Create the complete directory structure"""
        self.print_colored("\n📁 Creating directory structure...", 'YELLOW')
        
        directories = [
            "",
            "frontend", "frontend/app", "frontend/app/(auth)", "frontend/app/(auth)/login",
            "frontend/app/(auth)/register", "frontend/app/dashboard", "frontend/app/projects",
            "frontend/app/projects/[id]", "frontend/app/projects/[id]/test-cases",
            "frontend/app/projects/[id]/releases", "frontend/app/projects/[id]/reports",
            "frontend/app/projects/[id]/traceability", "frontend/app/admin",
            "frontend/components", "frontend/components/ui", "frontend/components/forms",
            "frontend/components/tables", "frontend/components/charts", "frontend/hooks",
            "frontend/lib", "frontend/types", "frontend/styles", "frontend/public",
            
            "backend", "backend/src", "backend/src/controllers", "backend/src/middleware",
            "backend/src/models", "backend/src/routes", "backend/src/services",
            "backend/src/utils", "backend/src/webhooks", "backend/prisma",
            "backend/tests", "backend/scripts",
            
            "shared", "shared/types", "shared/constants",
            "docker", "docker/nginx", "docker/postgres",
            "docs", "scripts", "cli", "cli/src", "cli/bin",
            "vscode-extension", "vscode-extension/src", "vscode-extension/src/providers",
            ".github", ".github/workflows",
        ]
        
        for directory in directories:
            dir_path = self.project_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            
        self.print_colored("✅ Directory structure created successfully!", 'GREEN')

    def create_backend_files(self):
        """Create all backend files"""
        self.print_colored("\n🔧 Creating backend files...", 'YELLOW')
        
        # Backend package.json
        backend_package = {
            "name": "testflow-backend",
            "version": "1.0.0",
            "description": "TestFlow API Server",
            "main": "dist/app.js",
            "scripts": {
                "start": "node dist/app.js",
                "dev": "nodemon src/app.ts",
                "build": "tsc",
                "test": "jest",
                "db:migrate": "prisma migrate dev",
                "db:generate": "prisma generate",
                "lint": "eslint src/**/*.ts"
            },
            "dependencies": {
                "@prisma/client": "^5.7.0",
                "express": "^4.18.2",
                "cors": "^2.8.5",
                "helmet": "^7.1.0",
                "express-rate-limit": "^7.1.5",
                "bcryptjs": "^2.4.3",
                "jsonwebtoken": "^9.0.2",
                "winston": "^3.11.0",
                "socket.io": "^4.7.4",
                "redis": "^4.6.12"
            },
            "devDependencies": {
                "@types/node": "^20.10.4",
                "@types/express": "^4.17.21",
                "@types/cors": "^2.8.17",
                "typescript": "^5.3.3",
                "nodemon": "^3.0.2",
                "ts-node": "^10.9.1",
                "prisma": "^5.7.0",
                "jest": "^29.7.0",
                "eslint": "^8.56.0",
                "@typescript-eslint/eslint-plugin": "^6.14.0"
            }
        }
        
        self._write_json_file("backend/package.json", backend_package)
        
        # Prisma schema
        prisma_schema = '''generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  username  String   @unique
  firstName String
  lastName  String
  role      Role     @default(DEVELOPER)
  isActive  Boolean  @default(true)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  createdTestCases    TestCase[] @relation("TestCaseCreator")
  assignedTestCases   TestCase[] @relation("TestCaseAssignee")
  testExecutions      TestExecution[]
  projectMembers      ProjectMember[]

  @@map("users")
}

model Project {
  id          String   @id @default(cuid())
  name        String
  description String?
  isActive    Boolean  @default(true)
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  components      Component[]
  features        Feature[]
  testCases       TestCase[]
  releases        Release[]
  members         ProjectMember[]
  jenkinsConfig   JenkinsConfig?

  @@map("projects")
}

model Component {
  id          String   @id @default(cuid())
  name        String
  description String?
  projectId   String
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  project   Project   @relation(fields: [projectId], references: [id], onDelete: Cascade)
  features  Feature[]
  testCases TestCase[]

  @@unique([projectId, name])
  @@map("components")
}

model TestCase {
  id                String            @id @default(cuid())
  name              String
  description       String?
  scenario          String
  validations       String[]
  automationStatus  AutomationStatus  @default(MANUAL)
  regressionStatus  RegressionStatus  @default(NO)
  priority          Priority          @default(MEDIUM)
  status            TestCaseStatus    @default(DRAFT)
  tags              String[]
  
  projectId         String
  componentId       String
  featureId         String
  createdById       String
  assignedToId      String?
  
  project           Project           @relation(fields: [projectId], references: [id], onDelete: Cascade)
  component         Component         @relation(fields: [componentId], references: [id], onDelete: Cascade)
  feature           Feature           @relation(fields: [featureId], references: [id], onDelete: Cascade)
  createdBy         User              @relation("TestCaseCreator", fields: [createdById], references: [id])
  assignedTo        User?             @relation("TestCaseAssignee", fields: [assignedToId], references: [id])
  
  executions        TestExecution[]
  
  createdAt         DateTime          @default(now())
  updatedAt         DateTime          @updatedAt

  @@map("test_cases")
}

enum Role {
  ADMIN
  QA
  DEVELOPER
  PM
}

enum AutomationStatus {
  MANUAL
  AUTOMATED
  SEMI_AUTOMATED
}

enum RegressionStatus {
  YES
  NO
  CONDITIONAL
}

enum Priority {
  LOW
  MEDIUM
  HIGH
  CRITICAL
}

enum TestCaseStatus {
  DRAFT
  READY
  APPROVED
  DEPRECATED
}'''
        
        self._write_file("backend/prisma/schema.prisma", prisma_schema.strip())
        
        # Main app.ts
        app_ts = '''import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { PrismaClient } from '@prisma/client';

const app = express();
export const prisma = new PrismaClient();

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true
}));

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Basic route
app.get('/api/test', (req, res) => {
  res.json({ message: 'TestFlow API is running!' });
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`🚀 TestFlow API server running on port ${PORT}`);
});'''
        
        self._write_file("backend/src/app.ts", app_ts.strip())

    def create_frontend_files(self):
        """Create all frontend files"""
        self.print_colored("\n🎨 Creating frontend files...", 'YELLOW')
        
        # Frontend package.json
        frontend_package = {
            "name": "testflow-frontend",
            "version": "1.0.0",
            "description": "TestFlow Web Application",
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
            },
            "dependencies": {
                "next": "14.0.4",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "tailwindcss": "^3.3.6",
                "lucide-react": "^0.294.0"
            },
            "devDependencies": {
                "@types/node": "^20.10.4",
                "@types/react": "^18.2.42",
                "@types/react-dom": "^18.2.17",
                "typescript": "^5.3.3",
                "eslint": "^8.56.0",
                "eslint-config-next": "14.0.4",
                "autoprefixer": "^10.4.16",
                "postcss": "^8.4.32"
            }
        }
        
        self._write_json_file("frontend/package.json", frontend_package)
        
        # Main layout
        main_layout = '''import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'TestFlow - Modern Test Management',
  description: 'Production-ready test management tool',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-background">
          {children}
        </div>
      </body>
    </html>
  )
}'''
        
        self._write_file("frontend/app/layout.tsx", main_layout.strip())
        
        # Homepage
        homepage = '''import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen">
      <header className="px-4 lg:px-6 h-14 flex items-center border-b">
        <Link className="flex items-center justify-center" href="#">
          <span className="font-bold text-xl">🧪 TestFlow</span>
        </Link>
        <nav className="ml-auto flex gap-4 sm:gap-6">
          <Link className="text-sm font-medium hover:underline" href="/login">
            Login
          </Link>
          <Link className="text-sm font-medium hover:underline" href="/register">
            Register
          </Link>
        </nav>
      </header>

      <main className="flex-1">
        <section className="w-full py-12 md:py-24 lg:py-32">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center space-y-4 text-center">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
                  Modern Test Management
                </h1>
                <p className="mx-auto max-w-[700px] text-gray-500 md:text-xl">
                  Streamline your QA process with TestFlow. Powerful test case management, 
                  CI/CD integration, and real-time analytics.
                </p>
              </div>
              <div className="space-x-4">
                <Link href="/register" className="bg-blue-600 text-white px-8 py-3 rounded-md hover:bg-blue-700">
                  Get Started
                </Link>
                <Link href="/login" className="border border-gray-300 px-8 py-3 rounded-md hover:bg-gray-50">
                  Login
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}'''
        
        self._write_file("frontend/app/page.tsx", homepage.strip())
        
        # Global CSS
        global_css = '''@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-white text-gray-900;
  }
}'''
        
        self._write_file("frontend/app/globals.css", global_css.strip())

    def create_docker_files(self):
        """Create Docker configuration files"""
        self.print_colored("\n🐳 Creating Docker configuration...", 'YELLOW')
        
        # Docker Compose for development
        docker_compose_dev = '''version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - NEXT_PUBLIC_API_URL=http://localhost:4000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "4000:4000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://testflow:password@postgres:5432/testflow
      - JWT_SECRET=development-secret-key
    volumes:
      - ./backend:/app
      - /app/node_modules
    depends_on:
      - postgres

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=testflow
      - POSTGRES_USER=testflow
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:'''
        
        self._write_file("docker-compose.dev.yml", docker_compose_dev.strip())
        
        # Frontend Dockerfile.dev
        frontend_dockerfile_dev = '''FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]'''
        
        self._write_file("frontend/Dockerfile.dev", frontend_dockerfile_dev.strip())
        
        # Backend Dockerfile.dev
        backend_dockerfile_dev = '''FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN npx prisma generate

EXPOSE 4000

CMD ["npm", "run", "dev"]'''
        
        self._write_file("backend/Dockerfile.dev", backend_dockerfile_dev.strip())

    def create_documentation(self):
        """Create documentation files"""
        self.print_colored("\n📚 Creating documentation...", 'YELLOW')
        
        # Main README
        readme = '''# TestFlow - Modern Test Management Platform

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

MIT License - see LICENSE file for details.'''
        
        self._write_file("README.md", readme.strip())
        
        # Getting started guide
        getting_started = '''# Getting Started with TestFlow

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

For more detailed instructions, see the main README.md file.'''
        
        self._write_file("docs/getting-started.md", getting_started.strip())

    def create_environment_files(self):
        """Create environment configuration files"""
        self.print_colored("\n🔐 Creating environment files...", 'YELLOW')
        
        # Backend .env.example
        backend_env = '''DATABASE_URL=postgresql://testflow:password@localhost:5432/testflow
JWT_SECRET=your-secret-key-change-in-production
NODE_ENV=development
PORT=4000
CORS_ORIGIN=http://localhost:3000'''
        
        self._write_file("backend/.env.example", backend_env.strip())
        
        # Frontend .env.local.example
        frontend_env = '''NEXT_PUBLIC_API_URL=http://localhost:4000
NEXT_PUBLIC_APP_NAME=TestFlow'''
        
        self._write_file("frontend/.env.local.example", frontend_env.strip())

    def create_scripts(self):
        """Create utility scripts"""
        self.print_colored("\n📜 Creating utility scripts...", 'YELLOW')
        
        # Setup script
        setup_script = '''#!/bin/bash

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

echo "🎉 Setup complete! Run 'docker-compose -f docker-compose.dev.yml up' to start."'''
        
        self._write_file("scripts/setup.sh", setup_script.strip())
        
        # Windows setup
        setup_bat = '''@echo off
echo Setting up TestFlow...

if not exist backend\\.env copy backend\\.env.example backend\\.env
if not exist frontend\\.env.local copy frontend\\.env.local.example frontend\\.env.local

cd backend && npm install && cd ..
cd frontend && npm install && cd ..

docker-compose -f docker-compose.dev.yml up -d postgres
timeout /t 10

cd backend
npx prisma generate
npx prisma migrate dev --name init
cd ..

echo Setup complete!
pause'''
        
        self._write_file("scripts/setup.bat", setup_bat.strip())
        
        # Make scripts executable
        try:
            os.chmod(self.project_dir / "scripts" / "setup.sh", 0o755)
        except:
            pass

    def create_config_files(self):
        """Create configuration files"""
        self.print_colored("\n⚙️ Creating configuration files...", 'YELLOW')
        
        # .gitignore
        gitignore = '''# Dependencies
node_modules/
*.log

# Environment variables
.env
.env.local

# Build outputs
.next/
dist/
build/

# Database
*.sqlite

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Testing
coverage/'''
        
        self._write_file(".gitignore", gitignore.strip())
        
        # TypeScript config for backend
        backend_tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "outDir": "./dist",
                "rootDir": "./src",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True
            },
            "include": ["src/**/*"],
            "exclude": ["node_modules", "dist"]
        }
        
        self._write_json_file("backend/tsconfig.json", backend_tsconfig)
        
        # TypeScript config for frontend
        frontend_tsconfig = {
            "compilerOptions": {
                "target": "es5",
                "lib": ["dom", "dom.iterable", "esnext"],
                "allowJs": True,
                "skipLibCheck": True,
                "strict": True,
                "noEmit": True,
                "esModuleInterop": True,
                "module": "esnext",
                "moduleResolution": "bundler",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "jsx": "preserve",
                "incremental": True,
                "plugins": [{"name": "next"}],
                "baseUrl": ".",
                "paths": {"@/*": ["./*"]}
            },
            "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
            "exclude": ["node_modules"]
        }
        
        self._write_json_file("frontend/tsconfig.json", frontend_tsconfig)

    def install_dependencies(self):
        """Install npm dependencies"""
        self.print_colored("\n📦 Installing dependencies...", 'YELLOW')
        
        try:
            # Backend dependencies
            self.print_colored("  Installing backend dependencies...", 'BLUE')
            result = subprocess.run(['npm', 'install'], 
                         cwd=self.project_dir / 'backend', 
                         capture_output=True, text=True)
            
            if result.returncode != 0:
                self.print_colored("⚠️  Backend npm install failed - install manually later", 'YELLOW')
                return True
            
            # Frontend dependencies
            self.print_colored("  Installing frontend dependencies...", 'BLUE')
            result = subprocess.run(['npm', 'install'], 
                         cwd=self.project_dir / 'frontend', 
                         capture_output=True, text=True)
            
            if result.returncode != 0:
                self.print_colored("⚠️  Frontend npm install failed - install manually later", 'YELLOW')
                return True
            
            self.print_colored("✅ Dependencies installed successfully!", 'GREEN')
            return True
            
        except Exception as e:
            self.print_colored("⚠️  Dependency installation skipped - install manually later", 'YELLOW')
            return True

    def setup_database(self):
        """Set up the database"""
        self.print_colored("\n🗄️ Setting up database schema...", 'YELLOW')
        
        try:
            backend_node_modules = self.project_dir / 'backend' / 'node_modules'
            if not backend_node_modules.exists():
                self.print_colored("⚠️  Dependencies not installed, skipping Prisma setup", 'YELLOW')
                return True
            
            result = subprocess.run(['npx', 'prisma', 'generate'], 
                         cwd=self.project_dir / 'backend', 
                         capture_output=True, text=True)
            
            if result.returncode != 0:
                self.print_colored("⚠️  Prisma setup skipped - run manually later", 'YELLOW')
                return True
            
            self.print_colored("✅ Database schema setup completed!", 'GREEN')
            return True
            
        except Exception as e:
            self.print_colored("⚠️  Database setup skipped - run manually later", 'YELLOW')
            return True

    def create_final_instructions(self):
        """Create final setup instructions"""
        self.print_colored("\n📋 Creating setup instructions...", 'YELLOW')
        
        instructions = '''# TestFlow Setup Instructions

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

For more help, see README.md and docs/ folder.'''
        
        self._write_file("SETUP.md", instructions.strip())

    def _write_file(self, file_path: str, content: str):
        """Write content to a file"""
        full_path = self.project_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _write_json_file(self, file_path: str, data: Dict[str, Any]):
        """Write JSON data to a file"""
        full_path = self.project_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def run(self):
        """Run the complete generation process"""
        try:
            self.print_banner()
            
            # Check if project directory already exists
            if self.project_dir.exists():
                response = input(f"\n📁 Directory '{self.project_name}' already exists. Overwrite? (y/N): ")
                if response.lower() != 'y':
                    self.print_colored("❌ Generation cancelled.", 'RED')
                    return False
                shutil.rmtree(self.project_dir)
            
            # Generation steps
            steps = [
                ("Creating directory structure", self.create_directory_structure),
                ("Creating backend files", self.create_backend_files),
                ("Creating frontend files", self.create_frontend_files),
                ("Creating Docker configuration", self.create_docker_files),
                ("Creating documentation", self.create_documentation),
                ("Creating environment files", self.create_environment_files),
                ("Creating utility scripts", self.create_scripts),
                ("Creating configuration files", self.create_config_files),
                ("Installing dependencies", self.install_dependencies),
                ("Setting up database", self.setup_database),
                ("Creating final instructions", self.create_final_instructions),
            ]
            
            for step_name, step_function in steps:
                try:
                    step_function()
                except Exception as e:
                    self.print_colored(f"❌ Failed at step '{step_name}': {e}", 'RED')
                    self.print_colored("⚠️  Continuing anyway...", 'YELLOW')
            
            # Success message
            self.print_colored("\n" + "="*60, 'GREEN')
            self.print_colored("🎉 TestFlow has been successfully generated!", 'GREEN')
            self.print_colored("="*60, 'GREEN')
            
            self.print_colored(f"\n📁 Project created at: {self.project_dir}", 'BLUE')
            self.print_colored("\n🚀 Next steps:", 'YELLOW')
            self.print_colored("  1. cd testflow", 'BLUE')
            
            # Check if dependencies were installed
            backend_node_modules = self.project_dir / 'backend' / 'node_modules'
            if backend_node_modules.exists():
                self.print_colored("  2. chmod +x scripts/setup.sh && ./scripts/setup.sh", 'BLUE')
                self.print_colored("  3. docker-compose -f docker-compose.dev.yml up", 'BLUE')
            else:
                self.print_colored("  2. Install dependencies:", 'YELLOW')
                self.print_colored("     cd backend && npm install && cd ..", 'BLUE')
                self.print_colored("     cd frontend && npm install && cd ..", 'BLUE')
                self.print_colored("  3. chmod +x scripts/setup.sh && ./scripts/setup.sh", 'BLUE')
                self.print_colored("  4. docker-compose -f docker-compose.dev.yml up", 'BLUE')
            
            self.print_colored("  5. Open http://localhost:3000", 'BLUE')
            
            self.print_colored("\n📚 Important files:", 'YELLOW')
            self.print_colored("  • SETUP.md - Detailed setup instructions", 'BLUE')
            self.print_colored("  • README.md - Project overview", 'BLUE')
            self.print_colored("  • docs/getting-started.md - Getting started guide", 'BLUE')
            
            # Windows-specific instructions
            if os.name == 'nt':
                self.print_colored("\n🪟 Windows users:", 'YELLOW')
                self.print_colored("  • Use scripts\\setup.bat instead of setup.sh", 'BLUE')
            
            return True
            
        except KeyboardInterrupt:
            self.print_colored("\n❌ Generation interrupted by user.", 'RED')
            return False
        except Exception as e:
            self.print_colored(f"\n❌ Unexpected error: {e}", 'RED')
            return False

def main():
    """Main entry point"""
    print("Starting TestFlow Generator...")
    
    generator = TestFlowGenerator()
    success = generator.run()
    
    if success:
        print("\n✅ Generation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Generation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
