import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const { resumeText } = await request.json()

    // Simulate AI processing time
    await new Promise((resolve) => setTimeout(resolve, 2000))

    // Extract skills using simple keyword matching (in real app, use NLP)
    const skillKeywords = [
      "JavaScript",
      "Python",
      "React",
      "Node.js",
      "Java",
      "TypeScript",
      "AWS",
      "Docker",
      "Kubernetes",
      "SQL",
      "MongoDB",
      "Git",
      "HTML",
      "CSS",
      "Vue.js",
      "Angular",
      "Express",
      "Django",
    ]

    const extractedSkills = skillKeywords.filter((skill) => resumeText.toLowerCase().includes(skill.toLowerCase()))

    // Analyze experience level
    const experienceYears = resumeText.match(/(\d+)\s*years?/gi)
    const experienceLevel =
      experienceYears && experienceYears.length > 0
        ? `${Math.max(...experienceYears.map((y) => Number.parseInt(y)))} years`
        : "2-3 years"

    // Extract education
    const educationKeywords = ["bachelor", "master", "phd", "degree", "university", "college"]
    const hasEducation = educationKeywords.some((keyword) => resumeText.toLowerCase().includes(keyword))

    const analysis = {
      score: Math.floor(Math.random() * 30) + 70, // 70-100
      skills: extractedSkills.slice(0, 8), // Top 8 skills
      experience: experienceLevel,
      education: hasEducation ? "Bachelor's in Computer Science" : "Technical background",
      strengths: [
        "Strong technical skills",
        "Good project experience",
        "Clear communication",
        "Relevant industry experience",
      ],
      recommendations: [
        "Excellent candidate for technical interview",
        "Strong match for senior developer role",
        "Consider for team lead position",
      ],
      culturalFit: Math.floor(Math.random() * 30) + 70,
      technicalFit: Math.floor(Math.random() * 30) + 70,
    }

    return NextResponse.json(analysis)
  } catch (error) {
    return NextResponse.json({ error: "Failed to analyze resume" }, { status: 500 })
  }
}
