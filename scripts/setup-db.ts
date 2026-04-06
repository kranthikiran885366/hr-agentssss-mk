import { PrismaClient } from "@prisma/client"
import { hash } from "bcryptjs"

const prisma = new PrismaClient()

async function main() {
  console.log("Setting up database...")

  // Create admin user
  const adminUser = await prisma.user.upsert({
    where: { email: "admin@company.com" },
    update: {},
    create: {
      name: "Admin User",
      email: "admin@company.com",
      password: await hash("admin123", 10),
      role: "ADMIN",
      department: "Human Resources",
      position: "HR Administrator",
      status: "active"
    }
  })

  console.log("Created admin user:", adminUser.email)

  // Create sample HR user
  const hrUser = await prisma.user.upsert({
    where: { email: "hr@company.com" },
    update: {},
    create: {
      name: "HR Manager",
      email: "hr@company.com",
      password: await hash("hr123", 10),
      role: "HR",
      department: "Human Resources",
      position: "HR Manager",
      status: "active"
    }
  })

  console.log("Created HR user:", hrUser.email)

  // Create sample jobs
  const jobTitles = ["Senior Software Engineer", "Product Manager", "UX Designer", "Data Scientist", "DevOps Engineer"]
  const departments = ["Engineering", "Product", "Design", "Data", "Infrastructure"]

  for (let i = 0; i < jobTitles.length; i++) {
    await prisma.job.upsert({
      where: { title: jobTitles[i] },
      update: {},
      create: {
        title: jobTitles[i],
        description: `We are looking for a talented ${jobTitles[i]} to join our team.`,
        department: departments[i],
        salaryMin: 80000,
        salaryMax: 150000,
        status: "OPEN"
      }
    })
  }

  console.log("Created sample jobs")

  // Create sample candidates
  const candidateNames = ["Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", "Emma Brown"]
  const candidateEmails = ["alice@example.com", "bob@example.com", "carol@example.com", "david@example.com", "emma@example.com"]

  for (let i = 0; i < candidateNames.length; i++) {
    await prisma.candidate.upsert({
      where: { email: candidateEmails[i] },
      update: {},
      create: {
        name: candidateNames[i],
        email: candidateEmails[i],
        phone: `555-000${i}`,
        status: "APPLIED",
        source: "LinkedIn",
        score: 75 + Math.random() * 20
      }
    })
  }

  console.log("Created sample candidates")

  // Create interview sessions
  const candidates = await prisma.candidate.findMany({ take: 3 })
  const jobs = await prisma.job.findMany({ take: 3 })

  for (let i = 0; i < candidates.length; i++) {
    await prisma.interviewSession.create({
      data: {
        candidateId: candidates[i].id,
        jobId: jobs[i]?.id,
        conductorId: hrUser.id,
        type: "SCREENING",
        status: "COMPLETED",
        score: 78 + Math.random() * 15,
        feedback: "Great candidate with strong technical skills."
      }
    })
  }

  console.log("Created sample interview sessions")

  console.log("Database setup complete!")
}

main()
  .catch((e) => {
    console.error("Error setting up database:", e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })
