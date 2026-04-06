# HR Agent System — Production-Ready

A comprehensive, fully integrated AI-powered HR automation platform with real-time interview management, intelligent candidate pipeline, performance analytics, and complete employee lifecycle automation.

## 🚀 Key Features

### Talent Acquisition
- Real-time candidate pipeline management
- AI-powered resume analysis with skill matching
- Automated candidate screening and ranking
- Job requisition and approval workflow
- Candidate communication tracking

### Interview Management
- Live AI-powered interviews (streaming support)
- Real-time conversation analysis
- Performance scoring and feedback generation
- Interview transcription and recording
- Multi-format interviews (chat, video, voice)

### Onboarding & Lifecycle
- Automated multi-step onboarding workflows
- Task assignment and progress tracking
- Document verification and E-signing
- Equipment provisioning
- Training assignment and tracking

### Performance Management
- Real-time performance tracking
- Goal setting and progress monitoring
- Review scheduling and management
- Analytics and insights
- Team performance comparisons

### Dashboard & Analytics
- Real-time HR metrics and KPIs
- Agent activity monitoring
- Pipeline analytics
- Audit logs and compliance tracking

## 🏗️ Architecture

### Tech Stack
- **Frontend**: Next.js 15 with TypeScript, React 19
- **Backend**: Python FastAPI with async support
- **Database**: PostgreSQL (Neon) with Prisma ORM
- **Authentication**: NextAuth.js with bcrypt password hashing
- **UI Components**: Radix UI + Tailwind CSS
- **Real-time**: WebSocket support
- **AI/ML**: OpenAI, Anthropic Claude, and custom models

## ⚡ Quick Start

### 1. Prerequisites
```bash
Node.js 18+, pnpm/npm, PostgreSQL (or use Neon cloud)
```

### 2. Clone & Install
```bash
git clone <repo>
cd hr-agents
pnpm install
```

### 3. Configure Environment
Copy `.env.local` and update with your actual values:
```bash
cp .env.local.example .env.local
# Edit .env.local with real database URL and API keys
```

**Key Environment Variables:**
- `DATABASE_URL` - PostgreSQL connection string (required)
- `NEXTAUTH_SECRET` - Generate with `openssl rand -base64 32`
- `NEXTAUTH_URL` - Application URL (default: http://localhost:5000)
- AI API Keys: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` (optional, for AI features)

### 4. Database Setup
```bash
# Run migrations and seed with sample data
pnpm run db:setup

# Or step by step:
pnpm run db:migrate  # Apply migrations
pnpm run db:seed     # Populate sample data
```

### 5. Start Development Server
```bash
pnpm run dev
# Starts on http://localhost:5000
```

## 📋 Default Test Users

After running `db:seed`, use these credentials:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@company.com | admin123 |
| HR Manager | hr@company.com | hr123 |
| Manager | manager@company.com | manager123 |

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/login` - Login with email/password
- `GET /api/auth/[...nextauth]` - NextAuth routes

### Candidates & Jobs
- `GET /api/talent-acquisition/candidates` - List candidates
- `POST /api/talent-acquisition/candidates` - Create candidate
- `GET /api/talent-acquisition/jobs` - List jobs
- `POST /api/talent-acquisition/jobs` - Create job posting

### Interviews
- `GET /api/interviews/sessions` - List interview sessions
- `POST /api/interviews/sessions` - Create new interview
- `POST /api/interviews/[sessionId]/message` - Send interview message
- `GET /api/interviews/[sessionId]/evaluation` - Get evaluation

### Users & Teams
- `GET /api/users` - List all users (admin only)
- `POST /api/users` - Create new user (admin only)
- `GET /api/users/[id]` - Get user details

## 🗄️ Database Schema

### Core Models
- **users** - Employee and HR personnel accounts
- **candidates** - Job applicants
- **jobs** - Open positions
- **job_applications** - Candidate applications to jobs
- **interview_sessions** - Interview records
- **interview_messages** - Conversation history
- **resumes** - Candidate resumes with analysis
- **performance_reviews** - Employee reviews
- **performance_goals** - OKR tracking
- **onboarding_tasks** - New hire checklists
- **audit_logs** - Compliance tracking

All models include proper timestamps, relationships, and indexing for production use.

## 🔐 Security Features

- ✅ Password hashing with bcrypt (10 rounds)
- ✅ JWT-based session management
- ✅ Role-based access control (RBAC)
- ✅ SQL injection prevention (Prisma parameterization)
- ✅ Input validation with Zod
- ✅ CORS protection
- ✅ Audit logging for all actions
- ✅ Encrypted password storage

## 📊 Real Data Integration

❌ **NO MOCK DATA** - Everything is database-backed:
- ✅ All interview sessions stored in PostgreSQL
- ✅ Real candidate profiles with resumes
- ✅ Actual job postings and applications
- ✅ Live performance data
- ✅ Complete audit trail

## 🚢 Production Deployment

### Vercel (Recommended)
1. Connect GitHub repo to Vercel
2. Set environment variables in Vercel dashboard
3. Automatic deployments on push

### Docker
```bash
docker build -t hr-agents .
docker run -p 5000:5000 --env-file .env.local hr-agents
```

### Traditional Server
```bash
pnpm build
pnpm start
```

## 📖 Project Structure

```
/app                    # Next.js app router
  /api                  # API routes
  /dashboard            # Admin dashboard
  /interviews           # Interview pages
  /onboarding           # Onboarding flow
/components             # React components
/lib                    # Utilities (auth, db, types)
/prisma                 # Database schema & migrations
/backend                # Python FastAPI backend (optional)
/public                 # Static assets
/types                  # TypeScript types
```

## 🛠️ Development Commands

```bash
pnpm dev              # Start dev server
pnpm build            # Production build
pnpm start            # Start production server
pnpm lint             # Run linter
pnpm db:migrate       # Apply DB migrations
pnpm db:seed          # Populate sample data
pnpm db:reset         # Full database reset
pnpm prisma:generate  # Regenerate Prisma client
```

## 📝 Important Notes

- Database migrations are managed by Prisma (no SQL scripts to run manually)
- All authentication is done through NextAuth.js + Prisma
- No localStorage - all data persists in PostgreSQL
- Real-time updates use API polling (WebSocket optional)
- AI features require API keys (OpenAI, Anthropic)

## 🤝 Contributing

Follow the established patterns:
- Use Prisma for database queries
- Add types to `/types` directory
- Keep API routes focused on single responsibility
- Always require authentication check in protected routes

## 📞 Support

Check logs with:
```bash
# Frontend logs in browser console
# Backend API errors: Vercel deployment logs or server console
# Database issues: Check Neon dashboard
```

## 📄 License

© 2026 HR Agent Systems. All rights reserved.
