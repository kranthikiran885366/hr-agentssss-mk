import { PrismaClient } from "@prisma/client"
import { hash } from "bcryptjs"

const prisma = new PrismaClient()

async function main() {
  console.log("Seeding database with sample data...")

  try {
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

    console.log("✓ Created admin user:", adminUser.email)

    // Create HR manager
    const hrUser = await prisma.user.upsert({
      where: { email: "hr@company.com" },
      update: {},
      create: {
        name: "Sarah Johnson",
        email: "hr@company.com",
        password: await hash("hr123", 10),
        role: "HR",
        department: "Human Resources",
        position: "HR Manager",
        status: "active"
      }
    })

    console.log("✓ Created HR user:", hrUser.email)

    // Create manager users
    const managerUser = await prisma.user.upsert({
      where: { email: "manager@company.com" },
      update: {},
      create: {
        name: "Mike Chen",
        email: "manager@company.com",
        password: await hash("manager123", 10),
        role: "MANAGER",
        department: "Engineering",
        position: "Engineering Manager",
        status: "active"
      }
    })

    console.log("✓ Created manager user:", managerUser.email)

    // Create sample jobs
    const jobs = await Promise.all([
      prisma.job.upsert({
        where: { title: "Senior Software Engineer" },
        update: { status: "OPEN" },
        create: {
          title: "Senior Software Engineer",
          description: "We are looking for an experienced engineer with strong backend expertise.",
          department: "Engineering",
          salaryMin: 120000,
          salaryMax: 180000,
          status: "OPEN"
        }
      }),
      prisma.job.upsert({
        where: { title: "Product Manager" },
        update: { status: "OPEN" },
        create: {
          title: "Product Manager",
          description: "Lead product strategy and roadmap for our AI initiatives.",
          department: "Product",
          salaryMin: 100000,
          salaryMax: 160000,
          status: "OPEN"
        }
      }),
      prisma.job.upsert({
        where: { title: "Data Scientist" },
        update: { status: "OPEN" },
        create: {
          title: "Data Scientist",
          description: "Build ML models for HR analytics and insights.",
          department: "Data",
          salaryMin: 110000,
          salaryMax: 170000,
          status: "OPEN"
        }
      })
    ])

    console.log("✓ Created sample jobs")

    // Create sample candidates
    const candidates = await Promise.all([
      prisma.candidate.upsert({
        where: { email: "alice.johnson@example.com" },
        update: {},
        create: {
          name: "Alice Johnson",
          email: "alice.johnson@example.com",
          phone: "555-0001",
          status: "INTERVIEW",
          source: "LinkedIn",
          score: 87
        }
      }),
      prisma.candidate.upsert({
        where: { email: "bob.smith@example.com" },
        update: {},
        create: {
          name: "Bob Smith",
          email: "bob.smith@example.com",
          phone: "555-0002",
          status: "SCREENING",
          source: "Referral",
          score: 82
        }
      }),
      prisma.candidate.upsert({
        where: { email: "carol.davis@example.com" },
        update: {},
        create: {
          name: "Carol Davis",
          email: "carol.davis@example.com",
          phone: "555-0003",
          status: "APPLIED",
          source: "Website",
          score: 75
        }
      })
    ])

    console.log("✓ Created sample candidates")

    // Create applications
    for (const candidate of candidates) {
      for (const job of jobs) {
        await prisma.jobApplication.upsert({
          where: {
            jobId_candidateId: {
              jobId: job.id,
              candidateId: candidate.id
            }
          },
          update: {},
          create: {
            jobId: job.id,
            candidateId: candidate.id,
            status: "APPLIED"
          }
        })
      }
    }

    console.log("✓ Created job applications")

    // Create interview sessions
    for (let i = 0; i < candidates.length; i++) {
      await prisma.interviewSession.create({
        data: {
          candidateId: candidates[i].id,
          jobId: jobs[i].id,
          conductorId: hrUser.id,
          type: "SCREENING",
          status: "COMPLETED",
          score: 78 + Math.random() * 15,
          feedback: "Strong candidate. Proceed to technical round.",
          startTime: new Date(Date.now() - 86400000),
          endTime: new Date(Date.now() - 82800000)
        }
      })
    }

    console.log("✓ Created interview sessions")

    // Create performance goals
    await prisma.performanceGoal.createMany({
      data: [
        {
          userId: adminUser.id,
          title: "Implement HR Dashboard",
          description: "Build comprehensive HR analytics dashboard",
          status: "IN_PROGRESS",
          progress: 60,
          targetDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
        },
        {
          userId: hrUser.id,
          title: "Hire 5 Engineers",
          description: "Fill open engineering positions",
          status: "IN_PROGRESS",
          progress: 40,
          targetDate: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000)
        }
      ]
    })

    console.log("✓ Created performance goals")

    console.log("\n✅ Database seeding completed successfully!")
    console.log("\nTest Credentials:")
    console.log("- Admin: admin@company.com / admin123")
    console.log("- HR: hr@company.com / hr123")
    console.log("- Manager: manager@company.com / manager123")
  } catch (error) {
    console.error("Error during seeding:", error)
    throw error
  }
}

main()
  .catch((e) => {
    console.error("Fatal error:", e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })
