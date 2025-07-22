"""
Real Data Generator for HR System
Generates comprehensive, realistic datasets using multiple AI models
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import uuid
import random
from faker import Faker
import openai
import google.generativeai as genai
import anthropic
from concurrent.futures import ThreadPoolExecutor
import aiofiles
import os

logger = logging.getLogger(__name__)

class RealDataGenerator:
    def __init__(self):
        self.fake = Faker()
        self.executor = ThreadPoolExecutor(max_workers=20)
        
        # Initialize AI clients
        self.openai_client = openai
        self.gemini_client = None
        self.claude_client = None
        
        # Data generation templates
        self.job_categories = [
            "Software Engineer", "Data Scientist", "Product Manager", "UX Designer",
            "DevOps Engineer", "Marketing Manager", "Sales Representative", "HR Manager",
            "Financial Analyst", "Business Analyst", "Project Manager", "Quality Assurance",
            "Customer Success", "Operations Manager", "Research Scientist", "Consultant"
        ]
        
        self.skill_database = {
            "Software Engineer": {
                "technical": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Git", "SQL", "MongoDB", "Redis"],
                "soft": ["Problem Solving", "Team Collaboration", "Code Review", "Agile Development", "Technical Communication"]
            },
            "Data Scientist": {
                "technical": ["Python", "R", "SQL", "Machine Learning", "TensorFlow", "PyTorch", "Pandas", "NumPy", "Jupyter", "Tableau"],
                "soft": ["Statistical Analysis", "Data Storytelling", "Business Acumen", "Research Skills", "Presentation Skills"]
            },
            "Product Manager": {
                "technical": ["Analytics", "SQL", "A/B Testing", "Wireframing", "API Understanding", "Data Analysis"],
                "soft": ["Strategic Thinking", "Stakeholder Management", "User Empathy", "Decision Making", "Communication"]
            },
            "UX Designer": {
                "technical": ["Figma", "Sketch", "Adobe Creative Suite", "Prototyping", "User Research", "Usability Testing"],
                "soft": ["Empathy", "Creative Thinking", "Problem Solving", "Collaboration", "Visual Communication"]
            },
            "DevOps Engineer": {
                "technical": ["Kubernetes", "Docker", "AWS", "Terraform", "Jenkins", "Monitoring", "Linux", "Bash", "Ansible"],
                "soft": ["System Thinking", "Automation Mindset", "Troubleshooting", "Collaboration", "Continuous Learning"]
            }
        }

    async def initialize(self):
        """Initialize data generator with AI clients"""
        try:
            logger.info("Initializing Real Data Generator...")
            
            # Initialize OpenAI
            openai.api_key = os.getenv("OPENAI_API_KEY")
            
            # Initialize Gemini
            genai.configure(api_key=os.getenv("GOOGLE_AI_API_KEY"))
            self.gemini_client = genai.GenerativeModel('gemini-pro')
            
            # Initialize Claude
            self.claude_client = anthropic.Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
            
            logger.info("Real Data Generator initialized successfully")
            
        except Exception as e:
            logger.error(f"Data generator initialization error: {str(e)}")
            raise

    async def generate_comprehensive_datasets(self) -> Dict[str, pd.DataFrame]:
        """Generate all HR datasets"""
        try:
            logger.info("Starting comprehensive dataset generation...")
            
            datasets = {}
            
            # Generate datasets in parallel
            tasks = [
                ("resumes", self.generate_resume_dataset(10000)),
                ("interviews", self.generate_interview_dataset(8000)),
                ("performance_reviews", self.generate_performance_dataset(6000)),
                ("workplace_communications", self.generate_communication_dataset(15000)),
                ("conflict_cases", self.generate_conflict_dataset(3000)),
                ("training_records", self.generate_training_dataset(12000)),
                ("employee_profiles", self.generate_employee_dataset(5000)),
                ("job_descriptions", self.generate_job_dataset(2000)),
                ("feedback_data", self.generate_feedback_dataset(20000)),
                ("leave_requests", self.generate_leave_dataset(8000))
            ]
            
            # Execute all generation tasks
            results = await asyncio.gather(*[task[1] for task in tasks])
            
            # Map results to dataset names
            for i, (name, _) in enumerate(tasks):
                datasets[name] = results[i]
                logger.info(f"Generated {name} dataset with {len(results[i])} records")
            
            # Save datasets
            await self.save_datasets(datasets)
            
            logger.info("Comprehensive dataset generation completed")
            return datasets
            
        except Exception as e:
            logger.error(f"Dataset generation error: {str(e)}")
            raise

    async def generate_resume_dataset(self, count: int) -> pd.DataFrame:
        """Generate realistic resume dataset"""
        try:
            logger.info(f"Generating {count} resumes...")
            
            resumes = []
            batch_size = 50
            
            for i in range(0, count, batch_size):
                batch_end = min(i + batch_size, count)
                batch_size_actual = batch_end - i
                
                # Generate batch of resumes
                batch_tasks = []
                for j in range(batch_size_actual):
                    category = random.choice(self.job_categories)
                    experience_years = np.random.randint(0, 20)
                    education_level = random.choice(["High School", "Associate", "Bachelor's", "Master's", "PhD"])
                    
                    task = self._generate_single_resume(category, experience_years, education_level)
                    batch_tasks.append(task)
                
                batch_results = await asyncio.gather(*batch_tasks)
                resumes.extend(batch_results)
                
                logger.info(f"Generated {len(resumes)}/{count} resumes")
            
            return pd.DataFrame(resumes)
            
        except Exception as e:
            logger.error(f"Resume dataset generation error: {str(e)}")
            raise

    async def _generate_single_resume(self, category: str, experience_years: int, education_level: str) -> Dict[str, Any]:
        """Generate a single realistic resume"""
        try:
            # Get skills for category
            skills = self.skill_database.get(category, {})
            technical_skills = random.sample(skills.get("technical", []), k=min(len(skills.get("technical", [])), random.randint(3, 8)))
            soft_skills = random.sample(skills.get("soft", []), k=min(len(skills.get("soft", [])), random.randint(2, 5)))
            
            # Generate personal info
            name = self.fake.name()
            email = self.fake.email()
            phone = self.fake.phone_number()
            location = f"{self.fake.city()}, {self.fake.state()}"
            
            # Generate resume text using AI
            prompt = f"""
            Generate a realistic resume for:
            Name: {name}
            Position: {category}
            Experience: {experience_years} years
            Education: {education_level}
            Technical Skills: {', '.join(technical_skills)}
            Soft Skills: {', '.join(soft_skills)}
            
            Include:
            - Professional summary (2-3 sentences)
            - Work experience with specific achievements
            - Education details
            - Skills section
            - Notable projects or accomplishments
            
            Make it realistic and detailed (400-600 words).
            """
            
            response = await self.openai_client.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert resume writer creating realistic professional resumes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.8
            )
            
            resume_text = response.choices[0].message.content.strip()
            
            # Calculate quality score
            quality_score = self._calculate_resume_quality(resume_text, experience_years, education_level, technical_skills)
            
            return {
                "id": str(uuid.uuid4()),
                "name": name,
                "email": email,
                "phone": phone,
                "location": location,
                "category": category,
                "experience_years": experience_years,
                "education_level": education_level,
                "technical_skills": technical_skills,
                "soft_skills": soft_skills,
                "resume_text": resume_text,
                "quality_score": quality_score,
                "created_at": datetime.utcnow().isoformat(),
                "word_count": len(resume_text.split()),
                "has_achievements": "achievement" in resume_text.lower() or "accomplished" in resume_text.lower(),
                "has_metrics": any(char.isdigit() for char in resume_text),
                "label": self.job_categories.index(category)
            }
            
        except Exception as e:
            logger.error(f"Single resume generation error: {str(e)}")
            return self._generate_fallback_resume(category, experience_years, education_level)

    async def generate_interview_dataset(self, count: int) -> pd.DataFrame:
        """Generate realistic interview dataset"""
        try:
            logger.info(f"Generating {count} interview conversations...")
            
            interviews = []
            interview_types = ["technical", "behavioral", "cultural", "case_study", "system_design"]
            difficulty_levels = ["junior", "mid", "senior", "principal"]
            
            batch_size = 40
            
            for i in range(0, count, batch_size):
                batch_end = min(i + batch_size, count)
                batch_size_actual = batch_end - i
                
                batch_tasks = []
                for j in range(batch_size_actual):
                    interview_type = random.choice(interview_types)
                    difficulty = random.choice(difficulty_levels)
                    position = random.choice(self.job_categories)
                    
                    task = self._generate_single_interview(interview_type, difficulty, position)
                    batch_tasks.append(task)
                
                batch_results = await asyncio.gather(*batch_tasks)
                interviews.extend(batch_results)
                
                logger.info(f"Generated {len(interviews)}/{count} interviews")
            
            return pd.DataFrame(interviews)
            
        except Exception as e:
            logger.error(f"Interview dataset generation error: {str(e)}")
            raise

    async def _generate_single_interview(self, interview_type: str, difficulty: str, position: str) -> Dict[str, Any]:
        """Generate a single realistic interview conversation"""
        try:
            prompt = f"""
            Generate a realistic {interview_type} interview conversation for a {difficulty} level {position} position.
            
            Include:
            - 6-10 questions and detailed candidate responses
            - Natural conversation flow with follow-up questions
            - Realistic technical depth for {difficulty} level
            - Candidate showing both strengths and areas for improvement
            - Interviewer providing clarifications and probing deeper
            
            Format as:
            Interviewer: [question]
            Candidate: [response]
            
            Make it authentic and detailed (800-1200 words).
            """
            
            response = await self.openai_client.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are creating realistic interview conversations for HR training."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.8
            )
            
            conversation = response.choices[0].message.content.strip()
            
            # Generate evaluation scores
            scores = self._generate_interview_scores(difficulty, interview_type)
            
            return {
                "id": str(uuid.uuid4()),
                "interview_type": interview_type,
                "difficulty": difficulty,
                "position": position,
                "conversation": conversation,
                "technical_score": scores["technical"],
                "communication_score": scores["communication"],
                "problem_solving_score": scores["problem_solving"],
                "cultural_fit_score": scores["cultural_fit"],
                "overall_score": scores["overall"],
                "recommendation": scores["recommendation"],
                "feedback": scores["feedback"],
                "duration_minutes": random.randint(30, 90),
                "question_count": conversation.count("Interviewer:"),
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Single interview generation error: {str(e)}")
            return self._generate_fallback_interview(interview_type, difficulty, position)

    async def generate_performance_dataset(self, count: int) -> pd.DataFrame:
        """Generate realistic performance review dataset"""
        try:
            logger.info(f"Generating {count} performance reviews...")
            
            reviews = []
            performance_levels = ["exceptional", "exceeds", "meets", "below", "unsatisfactory"]
            
            batch_size = 30
            
            for i in range(0, count, batch_size):
                batch_end = min(i + batch_size, count)
                batch_size_actual = batch_end - i
                
                batch_tasks = []
                for j in range(batch_size_actual):
                    level = random.choice(performance_levels)
                    position = random.choice(self.job_categories)
                    employee_name = self.fake.name()
                    
                    task = self._generate_single_performance_review(level, position, employee_name)
                    batch_tasks.append(task)
                
                batch_results = await asyncio.gather(*batch_tasks)
                reviews.extend(batch_results)
                
                logger.info(f"Generated {len(reviews)}/{count} performance reviews")
            
            return pd.DataFrame(reviews)
            
        except Exception as e:
            logger.error(f"Performance dataset generation error: {str(e)}")
            raise

    async def _generate_single_performance_review(self, level: str, position: str, employee_name: str) -> Dict[str, Any]:
        """Generate a single realistic performance review"""
        try:
            level_descriptions = {
                "exceptional": "outstanding performance, consistently exceeds all expectations",
                "exceeds": "consistently exceeds expectations and delivers excellent results",
                "meets": "meets expectations and performs well in their role",
                "below": "below expectations, needs improvement in several areas",
                "unsatisfactory": "unsatisfactory performance, significant concerns"
            }
            
            prompt = f"""
            Write a detailed performance review for {employee_name}, a {position} with {level_descriptions[level]}.
            
            Include:
            - Overall performance summary
            - Specific achievements and accomplishments
            - Areas of strength
            - Areas for improvement
            - Goal achievement analysis
            - Collaboration and teamwork assessment
            - Professional development recommendations
            - Specific examples and metrics where possible
            
            Make it professional, constructive, and detailed (300-500 words).
            """
            
            response = await self.openai_client.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an experienced HR manager writing detailed performance reviews."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=700,
                temperature=0.7
            )
            
            review_text = response.choices[0].message.content.strip()
            
            # Generate metrics
            metrics = self._generate_performance_metrics(level)
            
            return {
                "id": str(uuid.uuid4()),
                "employee_name": employee_name,
                "position": position,
                "performance_level": level,
                "review_text": review_text,
                "overall_score": metrics["overall_score"],
                "goal_achievement": metrics["goal_achievement"],
                "quality_score": metrics["quality_score"],
                "collaboration_score": metrics["collaboration_score"],
                "innovation_score": metrics["innovation_score"],
                "leadership_score": metrics["leadership_score"],
                "review_period": f"{datetime.now().year}-Q{random.randint(1, 4)}",
                "reviewer": self.fake.name(),
                "created_at": datetime.utcnow().isoformat(),
                "label": ["exceptional", "exceeds", "meets", "below", "unsatisfactory"].index(level)
            }
            
        except Exception as e:
            logger.error(f"Single performance review generation error: {str(e)}")
            return self._generate_fallback_performance_review(level, position, employee_name)

    async def generate_communication_dataset(self, count: int) -> pd.DataFrame:
        """Generate workplace communication dataset"""
        try:
            logger.info(f"Generating {count} workplace communications...")
            
            communications = []
            sentiments = ["positive", "negative", "neutral", "frustrated", "excited", "concerned", "satisfied"]
            comm_types = ["email", "slack_message", "meeting_notes", "feedback", "review", "complaint", "praise"]
            
            batch_size = 60
            
            for i in range(0, count, batch_size):
                batch_end = min(i + batch_size, count)
                batch_size_actual = batch_end - i
                
                batch_tasks = []
                for j in range(batch_size_actual):
                    sentiment = random.choice(sentiments)
                    comm_type = random.choice(comm_types)
                    
                    task = self._generate_single_communication(sentiment, comm_type)
                    batch_tasks.append(task)
                
                batch_results = await asyncio.gather(*batch_tasks)
                communications.extend(batch_results)
                
                logger.info(f"Generated {len(communications)}/{count} communications")
            
            return pd.DataFrame(communications)
            
        except Exception as e:
            logger.error(f"Communication dataset generation error: {str(e)}")
            raise

    async def _generate_single_communication(self, sentiment: str, comm_type: str) -> Dict[str, Any]:
        """Generate a single workplace communication"""
        try:
            sentiment_prompts = {
                "positive": "enthusiastic, optimistic, and encouraging",
                "negative": "frustrated, disappointed, or critical",
                "neutral": "factual, professional, and balanced",
                "frustrated": "showing clear frustration or annoyance",
                "excited": "showing enthusiasm and energy",
                "concerned": "expressing worry or concern",
                "satisfied": "showing contentment and approval"
            }
            
            prompt = f"""
            Write a realistic workplace {comm_type} that is {sentiment_prompts[sentiment]}.
            
            Make it:
            - Authentic and professional
            - 50-200 words
            - Include specific workplace context
            - Show realistic workplace scenarios
            - Appropriate for the sentiment and communication type
            
            Examples of context: project updates, team meetings, performance feedback, 
            deadline discussions, collaboration issues, achievements, concerns, etc.
            """
            
            response = await self.openai_client.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are writing realistic workplace communications."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.8
            )
            
            text = response.choices[0].message.content.strip()
            
            # Analyze sentiment intensity
            intensity = self._calculate_sentiment_intensity(text, sentiment)
            
            return {
                "id": str(uuid.uuid4()),
                "text": text,
                "sentiment": sentiment,
                "communication_type": comm_type,
                "intensity": intensity,
                "word_count": len(text.split()),
                "has_urgency": any(word in text.lower() for word in ["urgent", "asap", "immediately", "deadline"]),
                "has_emotion": any(word in text.lower() for word in ["excited", "frustrated", "concerned", "happy", "disappointed"]),
                "professional_tone": self._assess_professional_tone(text),
                "created_at": datetime.utcnow().isoformat(),
                "label": ["positive", "negative", "neutral", "frustrated", "excited", "concerned", "satisfied"].index(sentiment)
            }
            
        except Exception as e:
            logger.error(f"Single communication generation error: {str(e)}")
            return self._generate_fallback_communication(sentiment, comm_type)

    async def generate_conflict_dataset(self, count: int) -> pd.DataFrame:
        """Generate conflict resolution dataset"""
        try:
            logger.info(f"Generating {count} conflict cases...")
            
            conflicts = []
            conflict_types = ["interpersonal", "work_related", "communication", "resource", "policy", "performance"]
            severity_levels = [1, 2, 3, 4, 5]
            
            batch_size = 25
            
            for i in range(0, count, batch_size):
                batch_end = min(i + batch_size, count)
                batch_size_actual = batch_end - i
                
                batch_tasks = []
                for j in range(batch_size_actual):
                    conflict_type = random.choice(conflict_types)
                    severity = random.choice(severity_levels)
                    
                    task = self._generate_single_conflict(conflict_type, severity)
                    batch_tasks.append(task)
                
                batch_results = await asyncio.gather(*batch_tasks)
                conflicts.extend(batch_results)
                
                logger.info(f"Generated {len(conflicts)}/{count} conflict cases")
            
            return pd.DataFrame(conflicts)
            
        except Exception as e:
            logger.error(f"Conflict dataset generation error: {str(e)}")
            raise

    async def _generate_single_conflict(self, conflict_type: str, severity: int) -> Dict[str, Any]:
        """Generate a single conflict case"""
        try:
            severity_descriptions = {
                1: "minor disagreement, easily resolvable",
                2: "moderate conflict, requires some intervention",
                3: "significant conflict, needs formal mediation",
                4: "serious conflict, affecting team productivity",
                5: "severe conflict, requiring immediate HR intervention"
            }
            
            prompt = f"""
            Generate a realistic workplace conflict case:
            
            Type: {conflict_type}
            Severity: {severity}/5 ({severity_descriptions[severity]})
            
            Include:
            - Detailed description of the conflict situation
            - Parties involved (anonymized as Person A, Person B, etc.)
            - Root causes and contributing factors
            - Impact on work and team
            - Timeline of events
            - Any previous attempts at resolution
            
            Make it realistic and detailed (200-400 words).
            """
            
            response = await self.openai_client.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an HR professional documenting workplace conflicts."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            description = response.choices[0].message.content.strip()
            
            # Generate resolution data
            resolution_data = self._generate_conflict_resolution_data(conflict_type, severity)
            
            return {
                "id": str(uuid.uuid4()),
                "conflict_type": conflict_type,
                "severity_level": severity,
                "description": description,
                "parties_involved": random.randint(2, 5),
                "resolution_approach": resolution_data["approach"],
                "resolution_time_days": resolution_data["time_days"],
                "resolution_success": resolution_data["success"],
                "mediator_assigned": resolution_data["mediator_assigned"],
                "escalated": severity >= 4,
                "department": random.choice(["Engineering", "Sales", "Marketing", "HR", "Operations", "Finance"]),
                "reported_date": (datetime.utcnow() - timedelta(days=random.randint(1, 365))).isoformat(),
                "status": random.choice(["open", "in_progress", "resolved", "escalated"]),
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Single conflict generation error: {str(e)}")
            return self._generate_fallback_conflict(conflict_type, severity)

    async def generate_training_dataset(self, count: int) -> pd.DataFrame:
        """Generate training records dataset"""
        try:
            logger.info(f"Generating {count} training records...")
            
            training_records = []
            training_types = ["technical", "soft_skills", "compliance", "leadership", "safety", "product"]
            completion_statuses = ["completed", "in_progress", "not_started", "dropped"]
            
            batch_size = 50
            
            for i in range(0, count, batch_size):
                batch_end = min(i + batch_size, count)
                batch_size_actual = batch_end - i
                
                batch_tasks = []
                for j in range(batch_size_actual):
                    training_type = random.choice(training_types)
                    status = random.choice(completion_statuses)
                    
                    task = self._generate_single_training_record(training_type, status)
                    batch_tasks.append(task)
                
                batch_results = await asyncio.gather(*batch_tasks)
                training_records.extend(batch_results)
                
                logger.info(f"Generated {len(training_records)}/{count} training records")
            
            return pd.DataFrame(training_records)
            
        except Exception as e:
            logger.error(f"Training dataset generation error: {str(e)}")
            raise

    async def _generate_single_training_record(self, training_type: str, status: str) -> Dict[str, Any]:
        """Generate a single training record"""
        try:
            employee_name = self.fake.name()
            course_name = self._generate_course_name(training_type)
            
            # Generate completion data based on status
            completion_data = self._generate_training_completion_data(status)
            
            return {
                "id": str(uuid.uuid4()),
                "employee_name": employee_name,
                "employee_id": str(uuid.uuid4()),
                "course_name": course_name,
                "training_type": training_type,
                "status": status,
                "progress_percentage": completion_data["progress"],
                "completion_score": completion_data["score"],
                "time_spent_hours": completion_data["time_spent"],
                "start_date": completion_data["start_date"],
                "completion_date": completion_data["completion_date"],
                "instructor": self.fake.name(),
                "department": random.choice(["Engineering", "Sales", "Marketing", "HR", "Operations", "Finance"]),
                "cost": random.randint(100, 2000),
                "certification_earned": completion_data["certification"],
                "feedback_score": random.randint(1, 5) if status == "completed" else None,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Single training record generation error: {str(e)}")
            return self._generate_fallback_training_record(training_type, status)

    async def save_datasets(self, datasets: Dict[str, pd.DataFrame]):
        """Save all generated datasets"""
        try:
            logger.info("Saving generated datasets...")
            
            # Create data directory
            os.makedirs("data/generated", exist_ok=True)
            
            for name, df in datasets.items():
                # Save as CSV
                csv_path = f"data/generated/{name}.csv"
                df.to_csv(csv_path, index=False)
                
                # Save as JSON for complex data
                json_path = f"data/generated/{name}.json"
                df.to_json(json_path, orient="records", indent=2)
                
                # Save metadata
                metadata = {
                    "dataset_name": name,
                    "record_count": len(df),
                    "columns": list(df.columns),
                    "generated_at": datetime.utcnow().isoformat(),
                    "file_size_mb": round(os.path.getsize(csv_path) / (1024 * 1024), 2)
                }
                
                metadata_path = f"data/generated/{name}_metadata.json"
                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=2)
                
                logger.info(f"Saved {name} dataset: {len(df)} records")
            
            # Create summary
            summary = {
                "total_datasets": len(datasets),
                "total_records": sum(len(df) for df in datasets.values()),
                "datasets": {name: len(df) for name, df in datasets.items()},
                "generated_at": datetime.utcnow().isoformat()
            }
            
            with open("data/generated/summary.json", "w") as f:
                json.dump(summary, f, indent=2)
            
            logger.info("All datasets saved successfully")
            
        except Exception as e:
            logger.error(f"Dataset saving error: {str(e)}")
            raise

    # Helper methods for data generation
    def _calculate_resume_quality(self, text: str, experience: int, education: str, skills: List[str]) -> float:
        """Calculate resume quality score"""
        score = 50  # Base score
        
        # Experience factor
        score += min(experience * 2, 20)
        
        # Education factor
        education_scores = {"PhD": 20, "Master's": 15, "Bachelor's": 10, "Associate": 5, "High School": 0}
        score += education_scores.get(education, 0)
        
        # Skills factor
        score += min(len(skills) * 2, 15)
        
        # Text quality factors
        if len(text.split()) > 300:
            score += 5
        if "achievement" in text.lower() or "accomplished" in text.lower():
            score += 5
        if any(char.isdigit() for char in text):
            score += 5
        
        return min(score, 100)

    def _generate_interview_scores(self, difficulty: str, interview_type: str) -> Dict[str, Any]:
        """Generate realistic interview scores"""
        base_scores = {
            "junior": {"min": 50, "max": 80},
            "mid": {"min": 60, "max": 85},
            "senior": {"min": 70, "max": 95},
            "principal": {"min": 75, "max": 98}
        }
        
        score_range = base_scores[difficulty]
        
        technical = random.randint(score_range["min"], score_range["max"])
        communication = random.randint(score_range["min"] + 5, score_range["max"])
        problem_solving = random.randint(score_range["min"], score_range["max"])
        cultural_fit = random.randint(score_range["min"] + 10, min(score_range["max"] + 5, 100))
        
        overall = (technical + communication + problem_solving + cultural_fit) / 4
        
        if overall >= 80:
            recommendation = "hire"
        elif overall >= 65:
            recommendation = "maybe"
        else:
            recommendation = "no_hire"
        
        feedback = f"Candidate demonstrated {difficulty}-level competency in {interview_type} interview."
        
        return {
            "technical": technical,
            "communication": communication,
            "problem_solving": problem_solving,
            "cultural_fit": cultural_fit,
            "overall": overall,
            "recommendation": recommendation,
            "feedback": feedback
        }

    def _generate_performance_metrics(self, level: str) -> Dict[str, float]:
        """Generate performance metrics based on level"""
        level_ranges = {
            "exceptional": {"min": 90, "max": 100},
            "exceeds": {"min": 80, "max": 95},
            "meets": {"min": 70, "max": 85},
            "below": {"min": 50, "max": 75},
            "unsatisfactory": {"min": 20, "max": 60}
        }
        
        score_range = level_ranges[level]
        
        return {
            "overall_score": random.randint(score_range["min"], score_range["max"]),
            "goal_achievement": random.randint(score_range["min"], score_range["max"]),
            "quality_score": random.randint(score_range["min"], score_range["max"]),
            "collaboration_score": random.randint(score_range["min"], score_range["max"]),
            "innovation_score": random.randint(score_range["min"], score_range["max"]),
            "leadership_score": random.randint(score_range["min"], score_range["max"])
        }

    def _calculate_sentiment_intensity(self, text: str, sentiment: str) -> float:
        """Calculate sentiment intensity"""
        # Simple intensity calculation based on keywords
        intensity_words = {
            "high": ["extremely", "absolutely", "completely", "totally", "incredibly"],
            "medium": ["very", "quite", "really", "significantly", "considerably"],
            "low": ["somewhat", "slightly", "a bit", "rather", "fairly"]
        }
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in intensity_words["high"]):
            return random.uniform(0.8, 1.0)
        elif any(word in text_lower for word in intensity_words["medium"]):
            return random.uniform(0.5, 0.8)
        else:
            return random.uniform(0.3, 0.6)

    def _assess_professional_tone(self, text: str) -> float:
        """Assess professional tone of communication"""
        # Simple professional tone assessment
        unprofessional_words = ["hate", "stupid", "ridiculous", "awful", "terrible"]
        professional_words = ["please", "thank you", "appreciate", "consider", "recommend"]
        
        text_lower = text.lower()
        
        unprofessional_count = sum(1 for word in unprofessional_words if word in text_lower)
        professional_count = sum(1 for word in professional_words if word in text_lower)
        
        if unprofessional_count > 0:
            return max(0.3, 0.8 - (unprofessional_count * 0.2))
        else:
            return min(1.0, 0.7 + (professional_count * 0.1))

    def _generate_conflict_resolution_data(self, conflict_type: str, severity: int) -> Dict[str, Any]:
        """Generate conflict resolution data"""
        resolution_approaches = {
            "interpersonal": "mediation",
            "work_related": "collaborative",
            "communication": "clarification",
            "resource": "negotiation",
            "policy": "clarification",
            "performance": "coaching"
        }
        
        base_time = {1: 2, 2: 5, 3: 10, 4: 20, 5: 30}
        time_days = base_time[severity] + random.randint(-2, 5)
        
        success_rates = {1: 0.95, 2: 0.90, 3: 0.80, 4: 0.70, 5: 0.60}
        success = random.random() < success_rates[severity]
        
        return {
            "approach": resolution_approaches.get(conflict_type, "mediation"),
            "time_days": max(1, time_days),
            "success": success,
            "mediator_assigned": severity >= 3
        }

    def _generate_course_name(self, training_type: str) -> str:
        """Generate realistic course names"""
        course_templates = {
            "technical": [
                "Advanced Python Programming", "Cloud Architecture Fundamentals", "Data Science with Machine Learning",
                "Cybersecurity Best Practices", "API Design and Development", "DevOps and CI/CD"
            ],
            "soft_skills": [
                "Effective Communication", "Leadership Development", "Time Management Mastery",
                "Conflict Resolution", "Team Building", "Presentation Skills"
            ],
            "compliance": [
                "Data Privacy and GDPR", "Workplace Safety Training", "Anti-Harassment Policy",
                "Financial Compliance", "Code of Conduct", "Information Security"
            ],
            "leadership": [
                "Strategic Leadership", "Managing Remote Teams", "Performance Management",
                "Change Management", "Executive Presence", "Decision Making"
            ],
            "safety": [
                "Workplace Safety Fundamentals", "Emergency Response", "Ergonomics Training",
                "Chemical Safety", "Fire Safety", "First Aid Certification"
            ],
            "product": [
                "Product Strategy", "User Experience Design", "Market Research", 
                "Product Analytics", "Agile Product Management", "Customer Discovery"
            ]
        }
        
        return random.choice(course_templates.get(training_type, ["General Training"]))

    def _generate_training_completion_data(self, status: str) -> Dict[str, Any]:
        """Generate training completion data based on status"""
        start_date = datetime.utcnow() - timedelta(days=random.randint(1, 180))
        
        if status == "completed":
            progress = 100
            score = random.randint(70, 100)
            time_spent = random.randint(10, 80)
            completion_date = start_date + timedelta(days=random.randint(1, 30))
            certification = random.choice([True, False])
        elif status == "in_progress":
            progress = random.randint(20, 90)
            score = None
            time_spent = random.randint(5, 40)
            completion_date = None
            certification = False
        elif status == "dropped":
            progress = random.randint(5, 50)
            score = None
            time_spent = random.randint(1, 20)
            completion_date = None
            certification = False
        else:  # not_started
            progress = 0
            score = None
            time_spent = 0
            completion_date = None
            certification = False
        
        return {
            "progress": progress,
            "score": score,
            "time_spent": time_spent,
            "start_date": start_date.isoformat(),
            "completion_date": completion_date.isoformat() if completion_date else None,
            "certification": certification
        }

    # Fallback methods for error cases
    def _generate_fallback_resume(self, category: str, experience: int, education: str) -> Dict[str, Any]:
        """Generate fallback resume when AI generation fails"""
        return {
            "id": str(uuid.uuid4()),
            "name": self.fake.name(),
            "email": self.fake.email(),
            "phone": self.fake.phone_number(),
            "location": f"{self.fake.city()}, {self.fake.state()}",
            "category": category,
            "experience_years": experience,
            "education_level": education,
            "technical_skills": ["General Skills"],
            "soft_skills": ["Communication"],
            "resume_text": f"Professional {category} with {experience} years of experience and {education} education.",
            "quality_score": 60,
            "created_at": datetime.utcnow().isoformat(),
            "word_count": 15,
            "has_achievements": False,
            "has_metrics": False,
            "label": self.job_categories.index(category) if category in self.job_categories else 0
        }

    def _generate_fallback_interview(self, interview_type: str, difficulty: str, position: str) -> Dict[str, Any]:
        """Generate fallback interview when AI generation fails"""
        return {
            "id": str(uuid.uuid4()),
            "interview_type": interview_type,
            "difficulty": difficulty,
            "position": position,
            "conversation": f"Sample {interview_type} interview conversation for {difficulty} {position}.",
            "technical_score": 70,
            "communication_score": 75,
            "problem_solving_score": 70,
            "cultural_fit_score": 80,
            "overall_score": 73.75,
            "recommendation": "maybe",
            "feedback": f"Standard {interview_type} interview performance.",
            "duration_minutes": 45,
            "question_count": 5,
            "created_at": datetime.utcnow().isoformat()
        }

    def _generate_fallback_performance_review(self, level: str, position: str, employee_name: str) -> Dict[str, Any]:
        """Generate fallback performance review when AI generation fails"""
        return {
            "id": str(uuid.uuid4()),
            "employee_name": employee_name,
            "position": position,
            "performance_level": level,
            "review_text": f"Performance review for {employee_name} showing {level} performance.",
            "overall_score": 75,
            "goal_achievement": 80,
            "quality_score": 75,
            "collaboration_score": 80,
            "innovation_score": 70,
            "leadership_score": 75,
            "review_period": f"{datetime.now().year}-Q{random.randint(1, 4)}",
            "reviewer": self.fake.name(),
            "created_at": datetime.utcnow().isoformat(),
            "label": ["exceptional", "exceeds", "meets", "below", "unsatisfactory"].index(level)
        }

    def _generate_fallback_communication(self, sentiment: str, comm_type: str) -> Dict[str, Any]:
        """Generate fallback communication when AI generation fails"""
        return {
            "id": str(uuid.uuid4()),
            "text": f"Sample {comm_type} with {sentiment} sentiment.",
            "sentiment": sentiment,
            "communication_type": comm_type,
            "intensity": 0.5,
            "word_count": 6,
            "has_urgency": False,
            "has_emotion": False,
            "professional_tone": 0.8,
            "created_at": datetime.utcnow().isoformat(),
            "label": ["positive", "negative", "neutral", "frustrated", "excited", "concerned", "satisfied"].index(sentiment)
        }

    def _generate_fallback_conflict(self, conflict_type: str, severity: int) -> Dict[str, Any]:
        """Generate fallback conflict when AI generation fails"""
        return {
            "id": str(uuid.uuid4()),
            "conflict_type": conflict_type,
            "severity_level": severity,
            "description": f"Sample {conflict_type} conflict with severity level {severity}.",
            "parties_involved": 2,
            "resolution_approach": "mediation",
            "resolution_time_days": 7,
            "resolution_success": True,
            "mediator_assigned": severity >= 3,
            "escalated": severity >= 4,
            "department": "General",
            "reported_date": datetime.utcnow().isoformat(),
            "status": "open",
            "created_at": datetime.utcnow().isoformat()
        }

    def _generate_fallback_training_record(self, training_type: str, status: str) -> Dict[str, Any]:
        """Generate fallback training record when AI generation fails"""
        return {
            "id": str(uuid.uuid4()),
            "employee_name": self.fake.name(),
            "employee_id": str(uuid.uuid4()),
            "course_name": f"Sample {training_type} Course",
            "training_type": training_type,
            "status": status,
            "progress_percentage": 50 if status == "in_progress" else (100 if status == "completed" else 0),
            "completion_score": 80 if status == "completed" else None,
            "time_spent_hours": 20,
            "start_date": datetime.utcnow().isoformat(),
            "completion_date": datetime.utcnow().isoformat() if status == "completed" else None,
            "instructor": self.fake.name(),
            "department": "General",
            "cost": 500,
            "certification_earned": status == "completed",
            "feedback_score": 4 if status == "completed" else None,
            "created_at": datetime.utcnow().isoformat()
        }

    async def generate_employee_dataset(self, count: int) -> pd.DataFrame:
        """Generate employee profiles dataset"""
        try:
            logger.info(f"Generating {count} employee profiles...")
            
            employees = []
            
            for i in range(count):
                employee = {
                    "id": str(uuid.uuid4()),
                    "name": self.fake.name(),
                    "email": self.fake.email(),
                    "phone": self.fake.phone_number(),
                    "position": random.choice(self.job_categories),
                    "department": random.choice(["Engineering", "Sales", "Marketing", "HR", "Operations", "Finance"]),
                    "hire_date": self.fake.date_between(start_date="-5y", end_date="today").isoformat(),
                    "salary": random.randint(40000, 200000),
                    "manager_id": str(uuid.uuid4()) if random.random() > 0.1 else None,
                    "location": f"{self.fake.city()}, {self.fake.state()}",
                    "employment_type": random.choice(["full_time", "part_time", "contract"]),
                    "status": random.choice(["active", "inactive", "terminated"]),
                    "performance_rating": random.choice(["exceptional", "exceeds", "meets", "below", "unsatisfactory"]),
                    "created_at": datetime.utcnow().isoformat()
                }
                employees.append(employee)
            
            return pd.DataFrame(employees)
            
        except Exception as e:
            logger.error(f"Employee dataset generation error: {str(e)}")
            raise

    async def generate_job_dataset(self, count: int) -> pd.DataFrame:
        """Generate job descriptions dataset"""
        try:
            logger.info(f"Generating {count} job descriptions...")
            
            jobs = []
            
            for i in range(count):
                category = random.choice(self.job_categories)
                job = {
                    "id": str(uuid.uuid4()),
                    "title": category,
                    "department": random.choice(["Engineering", "Sales", "Marketing", "HR", "Operations", "Finance"]),
                    "location": f"{self.fake.city()}, {self.fake.state()}",
                    "employment_type": random.choice(["full_time", "part_time", "contract"]),
                    "salary_min": random.randint(40000, 120000),
                    "salary_max": random.randint(120000, 250000),
                    "experience_required": random.randint(0, 10),
                    "education_required": random.choice(["High School", "Bachelor's", "Master's", "PhD"]),
                    "remote_allowed": random.choice([True, False]),
                    "status": random.choice(["open", "closed", "draft"]),
                    "posted_date": self.fake.date_between(start_date="-1y", end_date="today").isoformat(),
                    "created_at": datetime.utcnow().isoformat()
                }
                jobs.append(job)
            
            return pd.DataFrame(jobs)
            
        except Exception as e:
            logger.error(f"Job dataset generation error: {str(e)}")
            raise

    async def generate_feedback_dataset(self, count: int) -> pd.DataFrame:
        """Generate feedback dataset"""
        try:
            logger.info(f"Generating {count} feedback records...")
            
            feedback_records = []
            feedback_types = ["peer", "manager", "subordinate", "self", "360"]
            
            for i in range(count):
                feedback = {
                    "id": str(uuid.uuid4()),
                    "employee_id": str(uuid.uuid4()),
                    "reviewer_id": str(uuid.uuid4()),
                    "feedback_type": random.choice(feedback_types),
                    "rating": random.randint(1, 5),
                    "comments": f"Sample feedback comment {i}",
                    "category": random.choice(["performance", "collaboration", "leadership", "communication"]),
                    "quarter": f"{datetime.now().year}-Q{random.randint(1, 4)}",
                    "created_at": datetime.utcnow().isoformat()
                }
                feedback_records.append(feedback)
            
            return pd.DataFrame(feedback_records)
            
        except Exception as e:
            logger.error(f"Feedback dataset generation error: {str(e)}")
            raise

    async def generate_leave_dataset(self, count: int) -> pd.DataFrame:
        """Generate leave requests dataset"""
        try:
            logger.info(f"Generating {count} leave requests...")
            
            leave_requests = []
            leave_types = ["annual", "sick", "maternity", "paternity", "emergency", "bereavement"]
            statuses = ["pending", "approved", "rejected", "cancelled"]
            
            for i in range(count):
                start_date = self.fake.date_between(start_date="-1y", end_date="+6m")
                end_date = start_date + timedelta(days=random.randint(1, 14))
                
                leave_request = {
                    "id": str(uuid.uuid4()),
                    "employee_id": str(uuid.uuid4()),
                    "leave_type": random.choice(leave_types),
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days_requested": (end_date - start_date).days + 1,
                    "reason": f"Sample leave reason {i}",
                    "status": random.choice(statuses),
                    "approved_by": str(uuid.uuid4()) if random.random() > 0.3 else None,
                    "submitted_date": (start_date - timedelta(days=random.randint(1, 30))).isoformat(),
                    "created_at": datetime.utcnow().isoformat()
                }
                leave_requests.append(leave_request)
            
            return pd.DataFrame(leave_requests)
            
        except Exception as e:
            logger.error(f"Leave dataset generation error: {str(e)}")
            raise
