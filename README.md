# HR Agent System

A comprehensive AI-powered HR automation platform with interview, onboarding, and performance management capabilities.

## Features

- AI-powered interviews (chat, voice, video)
- Automated onboarding process
- Resume analysis and candidate matching
- Performance management and analytics
- Voice and communication automation

## Getting Started

### Prerequisites

- Node.js 18+ and npm/pnpm
- Python 3.9+
- MongoDB
- SQL Database (PostgreSQL recommended)

### Installation

1. Clone the repository
2. Install frontend dependencies:
   ```
   pnpm install
   ```
3. Install backend dependencies:
   ```
   pip install -r backend/requirements.txt
   ```

### Configuration

1. Create a `.env.local` file in the root directory with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   MONGODB_URI=your_mongodb_uri
   DATABASE_URL=your_sql_database_url
   NEXTAUTH_SECRET=your_nextauth_secret
   NEXTAUTH_URL=http://localhost:3000
   ```

### Running the Application

To run both frontend and backend simultaneously:

```
pnpm run dev:all
```

To run only the frontend:

```
pnpm run dev
```

To run only the backend:

```
python -m backend.main
```

## Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Project Structure

- `/app` - Next.js app router pages
- `/components` - React components
- `/backend` - Python backend with AI agents
- `/public` - Static assets
- `/lib` - Utility functions and shared code