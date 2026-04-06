# Production Setup Guide - HR Agent System

## Overview

This guide walks you through setting up a fully functional, production-ready HR Agent System with real database, authentication, and integrations.

## Prerequisites Checklist

- [ ] Node.js 18+ installed (`node --version`)
- [ ] pnpm installed (`npm install -g pnpm`)
- [ ] PostgreSQL database (local or cloud)
- [ ] Git repository connected

## Step 1: Clone & Install

```bash
# Clone repository
git clone <your-repo-url> hr-agents
cd hr-agents

# Install all dependencies
pnpm install

# Install Prisma CLI globally (optional but recommended)
pnpm add -g prisma
```

**Expected Output:**
```
✓ Dependencies installed
✓ All 294 packages resolved
```

## Step 2: Database Setup

### Option A: Neon Cloud (Recommended)

1. Go to https://console.neon.tech
2. Create free account
3. Create new project
4. Copy connection string
5. Add to `.env.local`:
   ```
   DATABASE_URL=postgresql://user:password@ep-xxxxx.us-east-1.neon.tech/neondb?sslmode=require
   ```

### Option B: Local PostgreSQL

```bash
# macOS with Homebrew
brew install postgresql
brew services start postgresql

# Linux (Ubuntu/Debian)
sudo apt-get install postgresql
sudo systemctl start postgresql

# Create database
createdb hr_agents_db

# Get connection string
# postgresql://localhost:5432/hr_agents_db
```

### Verify Database Connection

```bash
# Test connection
pnpm prisma db execute --stdin < /dev/null

# Expected: No errors
```

## Step 3: Environment Configuration

### Create .env.local

```bash
# Copy template
cp .env.local .env.local

# Edit with your values
nano .env.local
```

### Required Variables

```bash
# Database (REQUIRED)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Authentication (REQUIRED)
NEXTAUTH_SECRET=$(openssl rand -base64 32)
NEXTAUTH_URL=http://localhost:5000

# API Configuration
NEXT_PUBLIC_API_BASE=http://localhost:5000
FASTAPI_BASE=http://localhost:8000
NODE_ENV=development

# Optional: AI APIs (for advanced features)
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Generate NEXTAUTH_SECRET

```bash
# Option 1: Using OpenSSL
openssl rand -base64 32

# Option 2: Using Node
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

## Step 4: Initialize Database

### Run Migrations

```bash
# Apply all database migrations
pnpm run db:migrate

# Expected output:
# ✓ Migrations applied successfully
# ✓ Created 15 tables
```

### Seed Sample Data

```bash
# Populate with sample data
pnpm run db:seed

# Expected output:
# ✓ Created admin user: admin@company.com
# ✓ Created HR user: hr@company.com
# ✓ Created sample jobs: 3
# ✓ Created sample candidates: 3
# ✓ Database seeding completed successfully!
```

## Step 5: Start Development Server

```bash
# Start frontend (Next.js)
pnpm run dev

# Output:
# ▲ Next.js 15.2.4
# - Local:        http://localhost:5000
# ✓ Ready in 1225ms
```

### Backend (Optional)

If using Python backend:

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Run FastAPI
python -m backend.main

# Backend runs on: http://localhost:8000
```

## Step 6: Verify Installation

### Access Application

1. **Frontend**: http://localhost:5000
2. **API Health**: http://localhost:5000/api/health

### Test Login

```bash
# Try login with seeded credentials
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@company.com","password":"admin123"}'

# Expected response:
# {
#   "success": true,
#   "user": {
#     "id": "...",
#     "email": "admin@company.com",
#     "role": "ADMIN"
#   }
# }
```

### Check Database

```bash
# Open Prisma Studio
pnpm prisma studio

# Opens http://localhost:5555
# Allows browsing all database tables
```

## Step 7: Verify All Modules

### Test Candidates API

```bash
curl -X GET http://localhost:5000/api/talent-acquisition/candidates \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Jobs API

```bash
curl -X GET http://localhost:5000/api/talent-acquisition/jobs \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Interviews API

```bash
curl -X GET http://localhost:5000/api/interviews/sessions \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Users API

```bash
curl -X GET http://localhost:5000/api/users \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Step 8: Production Deployment

### Vercel (Recommended)

```bash
# Push to GitHub
git add .
git commit -m "Production ready HR Agent System"
git push origin main

# In Vercel Dashboard:
# 1. Connect repository
# 2. Add environment variables (from .env.local)
# 3. Set NODE_ENV=production
# 4. Deploy!
```

### Environment Variables on Vercel

```
DATABASE_URL=<prod-database-url>
NEXTAUTH_SECRET=<generate-new-secret>
NEXTAUTH_URL=https://your-domain.com
NEXT_PUBLIC_API_BASE=https://your-domain.com
NODE_ENV=production
```

### Docker Deployment

```bash
# Build image
docker build -t hr-agents:latest .

# Run container
docker run -p 5000:5000 \
  -e DATABASE_URL=... \
  -e NEXTAUTH_SECRET=... \
  hr-agents:latest
```

## Troubleshooting

### Database Connection Issues

```bash
# Check connection string
echo $DATABASE_URL

# Test with psql (if PostgreSQL CLI installed)
psql $DATABASE_URL -c "SELECT 1"

# View logs
pnpm prisma studio
```

### Migration Failed

```bash
# Reset database (WARNING: deletes all data)
pnpm run db:reset

# Re-run migrations
pnpm run db:migrate
pnpm run db:seed
```

### Authentication Issues

```bash
# Verify NEXTAUTH_SECRET is set
echo $NEXTAUTH_SECRET

# Check user exists in database
pnpm prisma studio
# Navigate to users table
```

### API Returns 401

```bash
# Ensure user is authenticated
# Try login first:
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@company.com","password":"admin123"}'

# Use token from response in Authorization header
```

## Post-Setup Checklist

- [ ] Database connected and migrations applied
- [ ] Sample data seeded successfully
- [ ] Frontend loads at http://localhost:5000
- [ ] Can login with admin@company.com / admin123
- [ ] Dashboard shows real data from database
- [ ] API endpoints responding with real data
- [ ] All roles (ADMIN, HR, MANAGER) work correctly
- [ ] Candidates/Jobs/Interviews pages load real data
- [ ] No console errors in browser
- [ ] No API errors in terminal

## Common Commands Reference

```bash
# Development
pnpm dev                 # Start dev server
pnpm build               # Build for production
pnpm start               # Start production server

# Database
pnpm db:setup            # Migrate + seed
pnpm db:migrate          # Apply migrations only
pnpm db:seed             # Populate sample data
pnpm db:reset            # Full reset (⚠️ deletes data)
pnpm prisma studio      # Open database GUI
pnpm prisma:generate    # Regenerate Prisma client

# Utilities
pnpm lint                # Run linter
pnpm type-check          # Check TypeScript
```

## Next Steps

1. **Customize users**: Replace sample users with real team members
2. **Add AI integrations**: Set up OpenAI/Anthropic keys
3. **Configure email**: Set up email service for notifications
4. **Set up backup**: Enable database backups (Neon, AWS RDS)
5. **Monitor production**: Set up logging/monitoring (Sentry, LogRocket)

## Support

- Database Issues: Check Neon dashboard or PostgreSQL logs
- Frontend Issues: Check browser console (F12)
- API Issues: Check server logs in terminal
- Authentication Issues: Verify NEXTAUTH_SECRET and DATABASE_URL

## Security Notes

- ⚠️ Never commit `.env.local` to git
- ⚠️ Always use `NEXTAUTH_SECRET` in production
- ⚠️ Use strong passwords for database
- ⚠️ Enable HTTPS in production
- ⚠️ Keep credentials secure and rotated

---

✅ Setup complete! Your HR Agent System is ready for production use.
