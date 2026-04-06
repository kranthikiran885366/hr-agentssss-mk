#!/bin/bash

# HR Agent System - Quick Start Script
# This script automates the initial setup process

set -e

echo "========================================="
echo "HR Agent System - Quick Start Setup"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check prerequisites
echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found: $(node --version)${NC}"

if ! command -v pnpm &> /dev/null; then
    echo -e "${BLUE}Installing pnpm...${NC}"
    npm install -g pnpm
fi
echo -e "${GREEN}✓ pnpm found: $(pnpm --version)${NC}"

# Step 2: Install dependencies
echo ""
echo -e "${BLUE}Step 2: Installing dependencies...${NC}"
pnpm install
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 3: Check for .env.local
echo ""
echo -e "${BLUE}Step 3: Checking environment configuration...${NC}"

if [ ! -f .env.local ]; then
    echo -e "${BLUE}Creating .env.local from template...${NC}"
    cat > .env.local << 'EOF'
# Database (REQUIRED - Update this!)
DATABASE_URL=postgresql://user:password@localhost:5432/hr_agents_db

# Authentication (REQUIRED)
NEXTAUTH_SECRET=$(openssl rand -base64 32)
NEXTAUTH_URL=http://localhost:5000

# API Configuration
NEXT_PUBLIC_API_BASE=http://localhost:5000
FASTAPI_BASE=http://localhost:8000
NODE_ENV=development

# Optional: AI APIs (for advanced features)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
EOF
    echo -e "${RED}⚠️  .env.local created but needs DATABASE_URL!${NC}"
    echo -e "${BLUE}Please edit .env.local and set DATABASE_URL to your PostgreSQL connection${NC}"
    exit 1
else
    # Check if DATABASE_URL is set
    if ! grep -q "DATABASE_URL=postgresql://" .env.local; then
        echo -e "${RED}✗ DATABASE_URL not configured in .env.local${NC}"
        echo -e "${BLUE}Edit .env.local and set DATABASE_URL to your PostgreSQL connection${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ .env.local configured${NC}"
fi

# Step 4: Test database connection
echo ""
echo -e "${BLUE}Step 4: Testing database connection...${NC}"

if pnpm exec prisma db execute --stdin < /dev/null 2>/dev/null; then
    echo -e "${GREEN}✓ Database connection successful${NC}"
else
    echo -e "${RED}✗ Cannot connect to database${NC}"
    echo -e "${BLUE}Troubleshooting:${NC}"
    echo "  1. Verify DATABASE_URL in .env.local"
    echo "  2. Ensure PostgreSQL is running"
    echo "  3. Check database credentials"
    exit 1
fi

# Step 5: Run migrations
echo ""
echo -e "${BLUE}Step 5: Setting up database schema...${NC}"
pnpm run db:migrate
echo -e "${GREEN}✓ Migrations completed${NC}"

# Step 6: Seed database
echo ""
echo -e "${BLUE}Step 6: Populating sample data...${NC}"
pnpm run db:seed
echo -e "${GREEN}✓ Database seeded${NC}"

# Step 7: Summary
echo ""
echo "========================================="
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Start dev server:"
echo -e "     ${BLUE}pnpm run dev${NC}"
echo ""
echo "  2. Access application:"
echo -e "     ${BLUE}http://localhost:5000${NC}"
echo ""
echo "  3. Login with test credentials:"
echo -e "     Email: ${BLUE}admin@company.com${NC}"
echo -e "     Password: ${BLUE}admin123${NC}"
echo ""
echo "  Other test users:"
echo -e "     HR: ${BLUE}hr@company.com / hr123${NC}"
echo -e "     Manager: ${BLUE}manager@company.com / manager123${NC}"
echo ""
echo "For more information, see SETUP_GUIDE.md"
echo ""
