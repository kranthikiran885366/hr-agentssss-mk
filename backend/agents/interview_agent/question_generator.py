"""
Question Generator - AI-powered interview question generation
Creates personalized questions based on job requirements and candidate background
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import openai
import json
import random
from datetime import datetime

from backend.utils.config import settings

logger = logging.getLogger(__name__)

class QuestionGenerator:
    def __init__(self):
        self.is_initialized = False
        self.question_templates = {}
        self.difficulty_levels = ["entry", "intermediate", "senior", "expert"]
        
    async def initialize(self):
        """Initialize question generator"""
        try:
            logger.info("Initializing Question Generator...")
            
            # Load question templates
            await self._load_question_templates()
            
            self.is_initialized = True
            logger.info("Question Generator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Question Generator: {str(e)}")
            raise

    async def _load_question_templates(self):
        """Load question templates by category and difficulty"""
        self.question_templates = {
            "technical": {
                "entry": [
                    {
                        "text": "Explain the difference between a list and a tuple in Python.",
                        "category": "technical",
                        "subcategory": "data_structures",
                        "expected_duration": 120,
                        "keywords": ["list", "tuple", "mutable", "immutable"],
                        "follow_up_questions": [
                            "When would you use a tuple instead of a list?",
                            "Can you give an example of each?"
                        ]
                    },
                    {
                        "text": "What is the purpose of version control systems like Git?",
                        "category": "technical",
                        "subcategory": "tools",
                        "expected_duration": 150,
                        "keywords": ["git", "version control", "collaboration"],
                        "follow_up_questions": [
                            "What is the difference between git merge and git rebase?",
                            "How do you resolve merge conflicts?"
                        ]
                    }
                ],
                "intermediate": [
                    {
                        "text": "Explain the concept of database indexing and its impact on query performance.",
                        "category": "technical",
                        "subcategory": "database",
                        "expected_duration": 180,
                        "keywords": ["index", "performance", "query", "optimization"],
                        "follow_up_questions": [
                            "What are the trade-offs of having too many indexes?",
                            "How would you identify which columns to index?"
                        ]
                    },
                    {
                        "text": "Describe the differences between REST and GraphQL APIs.",
                        "category": "technical",
                        "subcategory": "api_design",
                        "expected_duration": 200,
                        "keywords": ["REST", "GraphQL", "API", "endpoints"],
                        "follow_up_questions": [
                            "When would you choose GraphQL over REST?",
                            "How do you handle authentication in both approaches?"
                        ]
                    }
                ],
                "senior": [
                    {
                        "text": "Design a scalable architecture for a real-time chat application that can handle millions of users.",
                        "category": "technical",
                        "subcategory": "system_design",
                        "expected_duration": 300,
                        "keywords": ["scalability", "real-time", "architecture", "websockets"],
                        "follow_up_questions": [
                            "How would you handle message persistence?",
                            "What about handling user presence and status?"
                        ]
                    }
                ]
            },
            "behavioral": {
                "entry": [
                    {
                        "text": "Tell me about a time when you had to learn a new technology quickly.",
                        "category": "behavioral",
                        "subcategory": "adaptability",
                        "expected_duration": 180,
                        "keywords": ["learning", "adaptation", "technology"],
                        "follow_up_questions": [
                            "What resources did you use to learn?",
                            "How did you apply this new knowledge?"
                        ]
                    }
                ],
                "intermediate": [
                    {
                        "text": "Describe a situation where you had to work with a difficult team member.",
                        "category": "behavioral",
                        "subcategory": "teamwork",
                        "expected_duration": 200,
                        "keywords": ["teamwork", "conflict", "communication"],
                        "follow_up_questions": [
                            "What was the outcome?",
                            "What would you do differently?"
                        ]
                    }
                ],
                "senior": [
                    {
                        "text": "Tell me about a time when you had to make a difficult technical decision that affected the entire team.",
                        "category": "behavioral",
                        "subcategory": "leadership",
                        "expected_duration": 250,
                        "keywords": ["leadership", "decision", "impact"],
                        "follow_up_questions": [
                            "How did you communicate this decision to stakeholders?",
                            "What was the long-term impact?"
                        ]
                    }
                ]
            },
            "problem_solving": {
                "entry": [
                    {
                        "text": "How would you debug a web application that is loading slowly?",
                        "category": "problem_solving",
                        "subcategory": "debugging",
                        "expected_duration": 200,
                        "keywords": ["debugging", "performance", "web"],
                        "follow_up_questions": [
                            "What tools would you use?",
                            "How would you prioritize the issues you find?"
                        ]
                    }
                ],
                "intermediate": [
                    {
                        "text": "You notice that your application's database queries are getting slower over time. How would you investigate and solve this?",
                        "category": "problem_solving",
                        "subcategory": "performance",
                        "expected_duration": 250,
                        "keywords": ["database", "performance", "optimization"],
                        "follow_up_questions": [
                            "What metrics would you monitor?",
                            "How would you prevent this in the future?"
                        ]
                    }
                ]
            },
            "cultural_fit": [
                {
                    "text": "What motivates you in your work?",
                    "category": "cultural_fit",
                    "subcategory": "motivation",
                    "expected_duration": 120,
                    "keywords": ["motivation", "values", "goals"],
                    "follow_up_questions": [
                        "How do you stay motivated during challenging projects?",
                        "What type of work environment helps you thrive?"
                    ]
                },
                {
                    "text": "How do you handle work-life balance?",
                    "category": "cultural_fit",
                    "subcategory": "balance",
                    "expected_duration": 150,
                    "keywords": ["balance", "stress", "priorities"],
                    "follow_up_questions": [
                        "What do you do when work becomes overwhelming?",
                        "How do you prioritize competing demands?"
                    ]
                }
            ]
        }

    async def generate_questions(self, interview_type: str, job_description: str = "", 
                               candidate_background: str = "", difficulty_level: str = "intermediate") -> List[Dict[str, Any]]:
        """Generate personalized interview questions"""
        try:
            questions = []
            
            if interview_type == "technical":
                questions = await self._generate_technical_questions(job_description, difficulty_level)
            elif interview_type == "behavioral":
                questions = await self._generate_behavioral_questions(candidate_background, difficulty_level)
            elif interview_type == "comprehensive":
                questions = await self._generate_comprehensive_questions(job_description, candidate_background, difficulty_level)
            elif interview_type == "screening":
                questions = await self._generate_screening_questions(job_description)
            else:
                questions = await self._generate_default_questions()
            
            # Add AI-generated questions if needed
            if len(questions) < 8:  # Ensure minimum question count
                ai_questions = await self._generate_ai_questions(interview_type, job_description, len(questions))
                questions.extend(ai_questions)
            
            # Add unique IDs and metadata
            for i, question in enumerate(questions):
                question["id"] = f"q_{i+1}_{interview_type}"
                question["order"] = i + 1
                question["generated_at"] = datetime.utcnow().isoformat()
            
            return questions
            
        except Exception as e:
            logger.error(f"Question generation error: {str(e)}")
            return await self._generate_default_questions()

    async def _generate_technical_questions(self, job_description: str, difficulty_level: str) -> List[Dict[str, Any]]:
        """Generate technical questions based on job description"""
        try:
            questions = []
            
            # Get base technical questions for difficulty level
            base_questions = self.question_templates.get("technical", {}).get(difficulty_level, [])
            questions.extend(base_questions[:4])  # Take first 4 base questions
            
            # Extract technologies from job description
            technologies = await self._extract_technologies_from_job(job_description)
            
            # Generate technology-specific questions
            for tech in technologies[:3]:  # Limit to 3 technologies
                tech_question = await self._generate_technology_question(tech, difficulty_level)
                if tech_question:
                    questions.append(tech_question)
            
            # Add system design question for senior level
            if difficulty_level in ["senior", "expert"]:
                system_design_question = await self._generate_system_design_question(job_description)
                questions.append(system_design_question)
            
            return questions
            
        except Exception as e:
            logger.error(f"Technical question generation error: {str(e)}")
            return self.question_templates.get("technical", {}).get("intermediate", [])[:5]

    async def _generate_behavioral_questions(self, candidate_background: str, difficulty_level: str) -> List[Dict[str, Any]]:
        """Generate behavioral questions based on candidate background"""
        try:
            questions = []
            
            # Get base behavioral questions
            base_questions = self.question_templates.get("behavioral", {}).get(difficulty_level, [])
            questions.extend(base_questions[:3])
            
            # Add cultural fit questions
            cultural_questions = self.question_templates.get("cultural_fit", [])
            questions.extend(cultural_questions[:2])
            
            # Generate experience-specific questions
            if "manager" in candidate_background.lower() or "lead" in candidate_background.lower():
                leadership_question = {
                    "text": "Tell me about a time when you had to lead a team through a challenging project.",
                    "category": "behavioral",
                    "subcategory": "leadership",
                    "expected_duration": 240,
                    "keywords": ["leadership", "team", "challenge"],
                    "follow_up_questions": [
                        "How did you motivate your team?",
                        "What obstacles did you face and how did you overcome them?"
                    ]
                }
                questions.append(leadership_question)
            
            return questions
            
        except Exception as e:
            logger.error(f"Behavioral question generation error: {str(e)}")
            return self.question_templates.get("behavioral", {}).get("intermediate", [])[:4]

    async def _generate_comprehensive_questions(self, job_description: str, candidate_background: str, difficulty_level: str) -> List[Dict[str, Any]]:
        """Generate comprehensive questions covering all aspects"""
        try:
            questions = []
            
            # Technical questions (40%)
            technical_questions = await self._generate_technical_questions(job_description, difficulty_level)
            questions.extend(technical_questions[:5])
            
            # Behavioral questions (40%)
            behavioral_questions = await self._generate_behavioral_questions(candidate_background, difficulty_level)
            questions.extend(behavioral_questions[:4])
            
            # Problem-solving questions (20%)
            problem_solving_questions = self.question_templates.get("problem_solving", {}).get(difficulty_level, [])
            questions.extend(problem_solving_questions[:2])
            
            return questions
            
        except Exception as e:
            logger.error(f"Comprehensive question generation error: {str(e)}")
            return await self._generate_default_questions()

    async def _generate_screening_questions(self, job_description: str) -> List[Dict[str, Any]]:
        """Generate quick screening questions"""
        try:
            screening_questions = [
                {
                    "text": "Can you briefly walk me through your relevant experience for this role?",
                    "category": "screening",
                    "subcategory": "experience",
                    "expected_duration": 120,
                    "keywords": ["experience", "background", "relevant"],
                    "follow_up_questions": [
                        "What interests you most about this position?",
                        "What are your salary expectations?"
                    ]
                },
                {
                    "text": "What is your availability to start if selected?",
                    "category": "screening",
                    "subcategory": "logistics",
                    "expected_duration": 60,
                    "keywords": ["availability", "start date", "notice"],
                    "follow_up_questions": [
                        "Do you have any upcoming commitments that might affect your availability?"
                    ]
                },
                {
                    "text": "Are you comfortable with the job requirements and responsibilities as described?",
                    "category": "screening",
                    "subcategory": "fit",
                    "expected_duration": 90,
                    "keywords": ["requirements", "responsibilities", "comfortable"],
                    "follow_up_questions": [
                        "Is there anything about the role you'd like clarification on?"
                    ]
                }
            ]
            
            # Add one technical screening question
            basic_tech_question = await self._generate_basic_technical_question(job_description)
            screening_questions.append(basic_tech_question)
            
            return screening_questions
            
        except Exception as e:
            logger.error(f"Screening question generation error: {str(e)}")
            return await self._generate_default_questions()[:4]

    async def _extract_technologies_from_job(self, job_description: str) -> List[str]:
        """Extract technologies mentioned in job description"""
        try:
            # Common technology keywords
            tech_keywords = [
                "python", "java", "javascript", "typescript", "react", "angular", "vue",
                "node.js", "express", "django", "flask", "spring", "laravel",
                "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
                "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
                "git", "jenkins", "gitlab", "github", "jira", "confluence"
            ]
            
            job_lower = job_description.lower()
            found_technologies = []
            
            for tech in tech_keywords:
                if tech in job_lower:
                    found_technologies.append(tech)
            
            return found_technologies[:5]  # Return top 5 technologies
            
        except Exception as e:
            logger.error(f"Technology extraction error: {str(e)}")
            return ["python", "javascript", "sql"]  # Default technologies

    async def _generate_technology_question(self, technology: str, difficulty_level: str) -> Dict[str, Any]:
        """Generate question specific to a technology"""
        try:
            tech_questions = {
                "python": {
                    "entry": "What are the main differences between Python 2 and Python 3?",
                    "intermediate": "Explain Python's GIL (Global Interpreter Lock) and its implications.",
                    "senior": "How would you optimize Python code for better performance in a high-traffic web application?"
                },
                "javascript": {
                    "entry": "What is the difference between let, const, and var in JavaScript?",
                    "intermediate": "Explain event delegation and how it works in JavaScript.",
                    "senior": "How would you implement a custom Promise from scratch?"
                },
                "react": {
                    "entry": "What are React components and how do they differ from regular HTML elements?",
                    "intermediate": "Explain the React component lifecycle and when you would use each method.",
                    "senior": "How would you optimize a React application for better performance?"
                },
                "sql": {
                    "entry": "What is the difference between INNER JOIN and LEFT JOIN?",
                    "intermediate": "Explain database normalization and its benefits.",
                    "senior": "How would you optimize a complex SQL query that's running slowly?"
                },
                "aws": {
                    "entry": "What are the main services offered by AWS?",
                    "intermediate": "Explain the difference between EC2, ECS, and Lambda.",
                    "senior": "How would you design a fault-tolerant architecture on AWS?"
                }
            }
            
            question_text = tech_questions.get(technology, {}).get(difficulty_level, 
                f"Tell me about your experience with {technology}.")
            
            return {
                "text": question_text,
                "category": "technical",
                "subcategory": f"technology_{technology}",
                "expected_duration": 180,
                "keywords": [technology, "experience", "knowledge"],
                "follow_up_questions": [
                    f"Can you give me a specific example of how you've used {technology}?",
                    f"What challenges have you faced while working with {technology}?"
                ]
            }
            
        except Exception as e:
            logger.error(f"Technology question generation error: {str(e)}")
            return {
                "text": f"Tell me about your experience with {technology}.",
                "category": "technical",
                "subcategory": "technology",
                "expected_duration": 120,
                "keywords": [technology],
                "follow_up_questions": []
            }

    async def _generate_system_design_question(self, job_description: str) -> Dict[str, Any]:
        """Generate system design question based on job context"""
        try:
            # Extract domain from job description
            domain_keywords = {
                "e-commerce": "Design a scalable e-commerce platform that can handle Black Friday traffic.",
                "social": "Design a social media feed system that can handle millions of users.",
                "messaging": "Design a real-time messaging system like WhatsApp.",
                "video": "Design a video streaming platform like YouTube.",
                "finance": "Design a payment processing system that ensures data consistency.",
                "gaming": "Design a multiplayer game backend that can handle real-time interactions."
            }
            
            job_lower = job_description.lower()
            for domain, question in domain_keywords.items():
                if domain in job_lower:
                    return {
                        "text": question,
                        "category": "technical",
                        "subcategory": "system_design",
                        "expected_duration": 600,  # 10 minutes
                        "keywords": ["system design", "scalability", "architecture"],
                        "follow_up_questions": [
                            "How would you handle data consistency?",
                            "What about caching strategies?",
                            "How would you monitor and debug this system?"
                        ]
                    }
            
            # Default system design question
            return {
                "text": "Design a URL shortening service like bit.ly that can handle millions of requests per day.",
                "category": "technical",
                "subcategory": "system_design",
                "expected_duration": 600,
                "keywords": ["system design", "scalability", "url shortening"],
                "follow_up_questions": [
                    "How would you handle analytics and click tracking?",
                    "What about custom URLs and expiration?",
                    "How would you scale this globally?"
                ]
            }
            
        except Exception as e:
            logger.error(f"System design question generation error: {str(e)}")
            return {
                "text": "Design a simple web application architecture.",
                "category": "technical",
                "subcategory": "system_design",
                "expected_duration": 300,
                "keywords": ["architecture", "design"],
                "follow_up_questions": []
            }

    async def _generate_basic_technical_question(self, job_description: str) -> Dict[str, Any]:
        """Generate basic technical question for screening"""
        try:
            basic_questions = [
                "What programming languages are you most comfortable with?",
                "Can you explain what an API is and how you've used them?",
                "What is your experience with databases?",
                "How do you typically approach debugging a problem?",
                "What development tools do you use regularly?"
            ]
            
            selected_question = random.choice(basic_questions)
            
            return {
                "text": selected_question,
                "category": "technical",
                "subcategory": "basic",
                "expected_duration": 120,
                "keywords": ["basic", "technical", "experience"],
                "follow_up_questions": [
                    "Can you give me a specific example?",
                    "What challenges have you faced in this area?"
                ]
            }
            
        except Exception as e:
            logger.error(f"Basic technical question generation error: {str(e)}")
            return {
                "text": "What programming languages are you most comfortable with?",
                "category": "technical",
                "subcategory": "basic",
                "expected_duration": 120,
                "keywords": ["programming", "languages"],
                "follow_up_questions": []
            }

    async def _generate_ai_questions(self, interview_type: str, job_description: str, current_count: int) -> List[Dict[str, Any]]:
        """Generate additional questions using AI"""
        try:
            needed_questions = max(8 - current_count, 0)
            if needed_questions == 0:
                return []
            
            prompt = f"""
            Generate {needed_questions} interview questions for a {interview_type} interview.
            
            Job Description: {job_description[:500]}
            
            Requirements:
            1. Questions should be relevant to the role
            2. Mix of difficulty levels
            3. Include follow-up questions
            4. Specify expected duration in seconds
            
            Return as JSON array with format:
            {{
                "text": "question text",
                "category": "{interview_type}",
                "subcategory": "specific area",
                "expected_duration": 180,
                "keywords": ["keyword1", "keyword2"],
                "follow_up_questions": ["follow up 1", "follow up 2"]
            }}
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert interviewer creating relevant interview questions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            try:
                ai_questions = json.loads(response.choices[0].message.content)
                return ai_questions if isinstance(ai_questions, list) else []
            except json.JSONDecodeError:
                logger.warning("Failed to parse AI-generated questions")
                return []
            
        except Exception as e:
            logger.error(f"AI question generation error: {str(e)}")
            return []

    async def _generate_default_questions(self) -> List[Dict[str, Any]]:
        """Generate default questions as fallback"""
        try:
            default_questions = [
                {
                    "text": "Tell me about yourself and your background.",
                    "category": "general",
                    "subcategory": "introduction",
                    "expected_duration": 120,
                    "keywords": ["background", "experience"],
                    "follow_up_questions": [
                        "What interests you about this role?",
                        "What are your career goals?"
                    ]
                },
                {
                    "text": "What are your greatest strengths?",
                    "category": "general",
                    "subcategory": "strengths",
                    "expected_duration": 90,
                    "keywords": ["strengths", "skills"],
                    "follow_up_questions": [
                        "Can you give me an example of how you've used this strength?"
                    ]
                },
                {
                    "text": "Describe a challenging project you've worked on.",
                    "category": "behavioral",
                    "subcategory": "challenges",
                    "expected_duration": 180,
                    "keywords": ["challenge", "project", "problem-solving"],
                    "follow_up_questions": [
                        "What made it challenging?",
                        "How did you overcome the obstacles?"
                    ]
                },
                {
                    "text": "Where do you see yourself in 5 years?",
                    "category": "general",
                    "subcategory": "goals",
                    "expected_duration": 120,
                    "keywords": ["goals", "future", "career"],
                    "follow_up_questions": [
                        "How does this role fit into your career plans?"
                    ]
                }
            ]
            
            return default_questions
            
        except Exception as e:
            logger.error(f"Default question generation error: {str(e)}")
            return []

    async def generate_follow_up_question(self, original_question: Dict[str, Any], 
                                        candidate_response: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dynamic follow-up question based on candidate response"""
        try:
            # Check if predefined follow-ups exist
            predefined_followups = original_question.get("follow_up_questions", [])
            
            # If response quality is low, use predefined follow-ups
            response_score = analysis.get("overall_score", 0)
            if response_score < 60 and predefined_followups:
                return {
                    "text": predefined_followups[0],
                    "category": original_question.get("category"),
                    "subcategory": "follow_up",
                    "expected_duration": 120,
                    "keywords": original_question.get("keywords", []),
                    "follow_up_questions": []
                }
            
            # Generate AI-powered follow-up
            ai_followup = await self._generate_ai_followup(original_question, candidate_response, analysis)
            return ai_followup
            
        except Exception as e:
            logger.error(f"Follow-up question generation error: {str(e)}")
            return {
                "text": "Can you elaborate on that point?",
                "category": original_question.get("category", "general"),
                "subcategory": "follow_up",
                "expected_duration": 120,
                "keywords": [],
                "follow_up_questions": []
            }

    async def _generate_ai_followup(self, original_question: Dict[str, Any], 
                                  candidate_response: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered follow-up question"""
        try:
            prompt = f"""
            Generate a relevant follow-up question based on:
            
            Original Question: {original_question.get('text')}
            Candidate Response: {candidate_response[:300]}
            Response Quality: {analysis.get('overall_score', 0)}/100
            
            The follow-up should:
            1. Dig deeper into their response
            2. Clarify any unclear points
            3. Explore specific examples or details
            4. Be natural and conversational
            
            Return only the follow-up question text.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert interviewer creating insightful follow-up questions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            followup_text = response.choices[0].message.content.strip()
            
            return {
                "text": followup_text,
                "category": original_question.get("category"),
                "subcategory": "ai_followup",
                "expected_duration": 120,
                "keywords": original_question.get("keywords", []),
                "follow_up_questions": []
            }
            
        except Exception as e:
            logger.error(f"AI follow-up generation error: {str(e)}")
            return {
                "text": "Can you provide more details about that?",
                "category": original_question.get("category", "general"),
                "subcategory": "followup",
                "expected_duration": 120,
                "keywords": [],
                "follow_up_questions": []
            }

    async def customize_questions_for_role(self, questions: List[Dict[str, Any]], 
                                         job_title: str, company_culture: str = "") -> List[Dict[str, Any]]:
        """Customize questions based on specific role and company culture"""
        try:
            customized_questions = []
            
            for question in questions:
                # Add role-specific context
                if job_title.lower() in question["text"].lower():
                    # Question already mentions the role
                    customized_questions.append(question)
                else:
                    # Customize question for the role
                    customized_question = question.copy()
                    
                    # Add role context to behavioral questions
                    if question["category"] == "behavioral":
                        role_context = f" in your experience as a {job_title}"
                        if not customized_question["text"].endswith("?"):
                            customized_question["text"] += role_context + "?"
                        else:
                            customized_question["text"] = customized_question["text"][:-1] + role_context + "?"
                    
                    customized_questions.append(customized_question)
            
            # Add company culture questions if provided
            if company_culture:
                culture_question = await self._generate_culture_question(company_culture)
                customized_questions.append(culture_question)
            
            return customized_questions
            
        except Exception as e:
            logger.error(f"Question customization error: {str(e)}")
            return questions

    async def _generate_culture_question(self, company_culture: str) -> Dict[str, Any]:
        """Generate question based on company culture"""
        try:
            culture_keywords = {
                "innovation": "How do you stay current with new technologies and industry trends?",
                "collaboration": "Describe your ideal team environment and how you contribute to team success.",
                "fast-paced": "How do you handle working in a fast-paced, rapidly changing environment?",
                "remote": "What strategies do you use to stay productive and connected while working remotely?",
                "startup": "What attracts you to working in a startup environment?",
                "enterprise": "How do you approach working within established processes and procedures?"
            }
            
            culture_lower = company_culture.lower()
            for keyword, question_text in culture_keywords.items():
                if keyword in culture_lower:
                    return {
                        "text": question_text,
                        "category": "cultural_fit",
                        "subcategory": f"culture_{keyword}",
                        "expected_duration": 150,
                        "keywords": ["culture", keyword, "fit"],
                        "follow_up_questions": [
                            "Can you give me a specific example?",
                            "How has this worked for you in the past?"
                        ]
                    }
            
            # Default culture question
            return {
                "text": "What type of work environment helps you do your best work?",
                "category": "cultural_fit",
                "subcategory": "environment",
                "expected_duration": 120,
                "keywords": ["environment", "culture", "work"],
                "follow_up_questions": [
                    "What aspects of our company culture appeal to you?"
                ]
            }
            
        except Exception as e:
            logger.error(f"Culture question generation error: {str(e)}")
            return {
                "text": "What values are important to you in a workplace?",
                "category": "cultural_fit",
                "subcategory": "values",
                "expected_duration": 120,
                "keywords": ["values", "workplace"],
                "follow_up_questions": []
            }

    def get_question_statistics(self) -> Dict[str, Any]:
        """Get statistics about available questions"""
        try:
            stats = {
                "total_questions": 0,
                "by_category": {},
                "by_difficulty": {},
                "average_duration": 0
            }
            
            total_duration = 0
            question_count = 0
            
            for category, difficulty_levels in self.question_templates.items():
                if isinstance(difficulty_levels, dict):
                    stats["by_category"][category] = 0
                    for difficulty, questions in difficulty_levels.items():
                        if difficulty not in stats["by_difficulty"]:
                            stats["by_difficulty"][difficulty] = 0
                        
                        question_count += len(questions)
                        stats["by_category"][category] += len(questions)
                        stats["by_difficulty"][difficulty] += len(questions)
                        
                        for question in questions:
                            total_duration += question.get("expected_duration", 120)
                else:
                    # Handle categories without difficulty levels
                    stats["by_category"][category] = len(difficulty_levels)
                    question_count += len(difficulty_levels)
                    
                    for question in difficulty_levels:
                        total_duration += question.get("expected_duration", 120)
            
            stats["total_questions"] = question_count
            stats["average_duration"] = total_duration / max(question_count, 1)
            
            return stats
            
        except Exception as e:
            logger.error(f"Question statistics error: {str(e)}")
            return {"total_questions": 0, "error": str(e)}
