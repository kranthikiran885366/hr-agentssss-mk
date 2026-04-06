-- CreateEnum
CREATE TYPE "UserRole" AS ENUM ('ADMIN', 'HR', 'MANAGER', 'USER');
CREATE TYPE "TrainingNeedsStatus" AS ENUM ('DRAFT', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');
CREATE TYPE "TrainingPriority" AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
CREATE TYPE "JobStatus" AS ENUM ('OPEN', 'CLOSED', 'ON_HOLD');
CREATE TYPE "CandidateStatus" AS ENUM ('APPLIED', 'SCREENING', 'INTERVIEW', 'OFFER', 'HIRED', 'REJECTED');
CREATE TYPE "ApplicationStatus" AS ENUM ('APPLIED', 'SCREENING', 'INTERVIEW', 'OFFER', 'ACCEPTED', 'REJECTED');
CREATE TYPE "InterviewType" AS ENUM ('SCREENING', 'TECHNICAL', 'BEHAVIORAL', 'FINAL');
CREATE TYPE "InterviewStatus" AS ENUM ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');
CREATE TYPE "GoalStatus" AS ENUM ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'FAILED');
CREATE TYPE "OnboardingStatus" AS ENUM ('PENDING', 'IN_PROGRESS', 'COMPLETED');

-- CreateTable
CREATE TABLE "users" (
    "id" TEXT NOT NULL,
    "name" TEXT,
    "email" TEXT NOT NULL,
    "password" TEXT,
    "email_verified" TIMESTAMP(3),
    "image" TEXT,
    "role" "UserRole" NOT NULL DEFAULT 'USER',
    "department" TEXT,
    "position" TEXT,
    "phone" TEXT,
    "bio" TEXT,
    "status" TEXT NOT NULL DEFAULT 'active',
    "last_active_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX "users_email_key" ON "users"("email");

-- CreateTable
CREATE TABLE "team_members" (
    "id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "manager_id" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "team_members_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX "team_members_user_id_manager_id_key" ON "team_members"("user_id", "manager_id");

-- CreateTable
CREATE TABLE "skills" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "category" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "skills_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX "skills_name_key" ON "skills"("name");

-- CreateTable
CREATE TABLE "training_needs_analyses" (
    "id" TEXT NOT NULL,
    "employee_id" TEXT NOT NULL,
    "created_by_id" TEXT NOT NULL,
    "status" "TrainingNeedsStatus" NOT NULL DEFAULT 'DRAFT',
    "deadline" TIMESTAMP(3),
    "notes" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "training_needs_analyses_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "training_needs_skills" (
    "id" TEXT NOT NULL,
    "training_needs_id" TEXT NOT NULL,
    "skill_id" TEXT NOT NULL,
    "current_level" INTEGER NOT NULL DEFAULT 1,
    "target_level" INTEGER NOT NULL,
    "priority" "TrainingPriority" NOT NULL DEFAULT 'MEDIUM',
    "gap" INTEGER NOT NULL DEFAULT 0,
    "recommended_training" TEXT,
    "notes" TEXT,
    CONSTRAINT "training_needs_skills_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX "training_needs_skills_training_needs_id_skill_id_key" ON "training_needs_skills"("training_needs_id", "skill_id");

-- CreateTable
CREATE TABLE "jobs" (
    "id" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "department" TEXT NOT NULL,
    "salaryMin" INTEGER,
    "salaryMax" INTEGER,
    "status" "JobStatus" NOT NULL DEFAULT 'OPEN',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "jobs_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "candidates" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "phone" TEXT,
    "status" "CandidateStatus" NOT NULL DEFAULT 'APPLIED',
    "source" TEXT,
    "score" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "candidates_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX "candidates_email_key" ON "candidates"("email");

-- CreateTable
CREATE TABLE "resumes" (
    "id" TEXT NOT NULL,
    "candidate_id" TEXT NOT NULL,
    "user_id" TEXT,
    "content" TEXT NOT NULL,
    "analysis" JSONB,
    "score" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "uploaded_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "resumes_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX "resumes_candidate_id_key" ON "resumes"("candidate_id");

-- CreateTable
CREATE TABLE "job_applications" (
    "id" TEXT NOT NULL,
    "job_id" TEXT NOT NULL,
    "candidate_id" TEXT NOT NULL,
    "status" "ApplicationStatus" NOT NULL DEFAULT 'APPLIED',
    "applied_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "job_applications_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX "job_applications_job_id_candidate_id_key" ON "job_applications"("job_id", "candidate_id");

-- CreateTable
CREATE TABLE "interview_sessions" (
    "id" TEXT NOT NULL,
    "candidate_id" TEXT NOT NULL,
    "conductor_id" TEXT,
    "job_id" TEXT,
    "type" "InterviewType" NOT NULL,
    "status" "InterviewStatus" NOT NULL DEFAULT 'SCHEDULED',
    "startTime" TIMESTAMP(3),
    "endTime" TIMESTAMP(3),
    "score" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "feedback" TEXT,
    "recording" TEXT,
    "transcript" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "interview_sessions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "interview_messages" (
    "id" TEXT NOT NULL,
    "session_id" TEXT NOT NULL,
    "role" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "interview_messages_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "performance_reviews" (
    "id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "reviewPeriod" TEXT NOT NULL,
    "rating" DOUBLE PRECISION NOT NULL,
    "feedback" TEXT,
    "goals" TEXT,
    "nextSteps" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "performance_reviews_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "performance_goals" (
    "id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "description" TEXT,
    "status" "GoalStatus" NOT NULL DEFAULT 'IN_PROGRESS',
    "targetDate" TIMESTAMP(3),
    "progress" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "performance_goals_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "onboarding_tasks" (
    "id" TEXT NOT NULL,
    "employee_id" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "description" TEXT,
    "status" "OnboardingStatus" NOT NULL DEFAULT 'PENDING',
    "dueDate" TIMESTAMP(3),
    "completedAt" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "onboarding_tasks_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "audit_logs" (
    "id" TEXT NOT NULL,
    "action" TEXT NOT NULL,
    "entity" TEXT NOT NULL,
    "entity_id" TEXT NOT NULL,
    "user_id" TEXT,
    "changes" JSONB,
    "timestamp" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "audit_logs_pkey" PRIMARY KEY ("id")
);

-- AddForeignKey
ALTER TABLE "team_members" ADD CONSTRAINT "team_members_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "team_members" ADD CONSTRAINT "team_members_manager_id_fkey" FOREIGN KEY ("manager_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "training_needs_analyses" ADD CONSTRAINT "training_needs_analyses_employee_id_fkey" FOREIGN KEY ("employee_id") REFERENCES "users"("id") ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "training_needs_analyses" ADD CONSTRAINT "training_needs_analyses_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "users"("id") ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "training_needs_skills" ADD CONSTRAINT "training_needs_skills_training_needs_id_fkey" FOREIGN KEY ("training_needs_id") REFERENCES "training_needs_analyses"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "training_needs_skills" ADD CONSTRAINT "training_needs_skills_skill_id_fkey" FOREIGN KEY ("skill_id") REFERENCES "skills"("id") ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "resumes" ADD CONSTRAINT "resumes_candidate_id_fkey" FOREIGN KEY ("candidate_id") REFERENCES "candidates"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "resumes" ADD CONSTRAINT "resumes_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "job_applications" ADD CONSTRAINT "job_applications_job_id_fkey" FOREIGN KEY ("job_id") REFERENCES "jobs"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "job_applications" ADD CONSTRAINT "job_applications_candidate_id_fkey" FOREIGN KEY ("candidate_id") REFERENCES "candidates"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "interview_sessions" ADD CONSTRAINT "interview_sessions_candidate_id_fkey" FOREIGN KEY ("candidate_id") REFERENCES "candidates"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "interview_sessions" ADD CONSTRAINT "interview_sessions_conductor_id_fkey" FOREIGN KEY ("conductor_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "interview_messages" ADD CONSTRAINT "interview_messages_session_id_fkey" FOREIGN KEY ("session_id") REFERENCES "interview_sessions"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "performance_reviews" ADD CONSTRAINT "performance_reviews_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "performance_goals" ADD CONSTRAINT "performance_goals_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
