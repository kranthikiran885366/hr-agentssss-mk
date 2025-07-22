"""
Resume Agent - AI-powered resume analysis and processing
Uses real NLP models and ML algorithms
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import spacy
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics.pairwise import cosine_similarity
import re
import json
from datetime import datetime
import PyPDF2
import docx
from io import BytesIO
import openai
from transformers import pipeline, AutoTokenizer, AutoModel
import torch

from backend.database.sql_database import SessionLocal
from backend.database.mongo_database import get_mongo_client
from backend.models.sql_models import Resume, Candidate, Job
from backend.utils.config import settings

logger = logging.getLogger(__name__)

class ResumeAgent:
    def __init__(self):
        self.nlp = None
        self.skill_extractor = None
        self.experience_classifier = None
        self.vectorizer = None
        self.embedding_model = None
        self.tokenizer = None
        self.is_initialized = False
        
        # Skill categories
        self.skill_categories = {
            'programming': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php',
                'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab'
            ],
            'web_development': [
                'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express',
                'django', 'flask', 'spring', 'laravel', 'rails', 'nextjs'
            ],
            'databases': [
                'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
                'oracle', 'sqlite', 'cassandra', 'dynamodb', 'neo4j'
            ],
            'cloud_devops': [
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
                'jenkins', 'gitlab', 'ansible', 'chef', 'puppet'
            ],
            'data_science': [
                'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch',
                'matplotlib', 'seaborn', 'jupyter', 'spark', 'hadoop'
            ],
            'mobile': [
                'android', 'ios', 'react native', 'flutter', 'xamarin',
                'swift', 'kotlin', 'objective-c'
            ]
        }

    async def initialize(self):
        """Initialize AI models and components"""
        try:
            logger.info("Initializing Resume Agent...")
            
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            
            # Initialize OpenAI
            openai.api_key = settings.OPENAI_API_KEY
            
            # Load transformer model for embeddings
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.embedding_model = AutoModel.from_pretrained(model_name)
            
            # Initialize skill extraction pipeline
            self.skill_extractor = pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                tokenizer="dbmdz/bert-large-cased-finetuned-conll03-english"
            )
            
            # Initialize vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            # Initialize experience classifier
            self.experience_classifier = RandomForestClassifier(
                n_estimators=100,
                random_state=42
            )
            
            self.is_initialized = True
            logger.info("Resume Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Resume Agent: {str(e)}")
            raise

    def is_ready(self) -> bool:
        """Check if agent is ready"""
        return self.is_initialized

    async def extract_text_from_file(self, content: bytes, filename: str) -> str:
        """Extract text from uploaded file"""
        try:
            file_extension = filename.lower().split('.')[-1]
            
            if file_extension == 'pdf':
                return await self._extract_from_pdf(content)
            elif file_extension in ['doc', 'docx']:
                return await self._extract_from_docx(content)
            elif file_extension == 'txt':
                return content.decode('utf-8')
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            logger.error(f"Text extraction error: {str(e)}")
            raise

    async def _extract_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF"""
        try:
            pdf_file = BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}")
            raise

    async def _extract_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX"""
        try:
            doc_file = BytesIO(content)
            doc = docx.Document(doc_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"DOCX extraction error: {str(e)}")
            raise

    async def analyze_resume(self, content: bytes, filename: str, job_id: Optional[str] = None, user_id: str = None) -> Dict[str, Any]:
        """Comprehensive resume analysis using AI"""
        try:
            # Extract text
            text = await self.extract_text_from_file(content, filename)
            
            # Parallel processing of different analysis components
            tasks = [
                self._extract_contact_info(text),
                self._extract_skills(text),
                self._extract_experience(text),
                self._extract_education(text),
                self._calculate_overall_score(text, job_id),
                self._generate_ai_summary(text),
                self._extract_projects(text),
                self._analyze_achievements(text)
            ]
            
            results = await asyncio.gather(*tasks)
            
            contact_info, skills, experience, education, scores, ai_summary, projects, achievements = results
            
            # Combine all analysis results
            analysis = {
                "id": f"resume_{datetime.utcnow().timestamp()}",
                "filename": filename,
                "contact_info": contact_info,
                "skills": skills,
                "experience": experience,
                "education": education,
                "projects": projects,
                "achievements": achievements,
                "scores": scores,
                "ai_summary": ai_summary,
                "raw_text": text,
                "analyzed_at": datetime.utcnow().isoformat(),
                "job_id": job_id,
                "user_id": user_id
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Resume analysis error: {str(e)}")
            raise

    async def _extract_contact_info(self, text: str) -> Dict[str, Any]:
        """Extract contact information using NLP"""
        try:
            doc = self.nlp(text)
            contact_info = {
                "name": None,
                "email": None,
                "phone": None,
                "linkedin": None,
                "github": None,
                "location": None
            }
            
            # Extract email
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            if emails:
                contact_info["email"] = emails[0]
            
            # Extract phone
            phone_patterns = [
                r'(\+\d{1,3}[-.\s]?)?($$?\d{3}$$?[-.\s]?\d{3}[-.\s]?\d{4})',
                r'(\+\d{1,3}[-.\s]?)?\d{10}',
                r'(\+\d{1,3}[-.\s]?)?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'
            ]
            
            for pattern in phone_patterns:
                phones = re.findall(pattern, text)
                if phones:
                    contact_info["phone"] = ''.join(phones[0]) if isinstance(phones[0], tuple) else phones[0]
                    break
            
            # Extract name using NER
            for ent in doc.ents:
                if ent.label_ == "PERSON" and not contact_info["name"]:
                    contact_info["name"] = ent.text
                elif ent.label_ in ["GPE", "LOC"] and not contact_info["location"]:
                    contact_info["location"] = ent.text
            
            # Extract LinkedIn
            linkedin_pattern = r'linkedin\.com/in/[\w-]+'
            linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
            if linkedin_matches:
                contact_info["linkedin"] = linkedin_matches[0]
            
            # Extract GitHub
            github_pattern = r'github\.com/[\w-]+'
            github_matches = re.findall(github_pattern, text, re.IGNORECASE)
            if github_matches:
                contact_info["github"] = github_matches[0]
            
            return contact_info
            
        except Exception as e:
            logger.error(f"Contact extraction error: {str(e)}")
            return {}

    async def _extract_skills(self, text: str) -> Dict[str, Any]:
        """Extract and categorize skills using AI"""
        try:
            text_lower = text.lower()
            extracted_skills = {}
            
            # Extract skills by category
            for category, skills in self.skill_categories.items():
                found_skills = []
                for skill in skills:
                    pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                    if re.search(pattern, text_lower):
                        found_skills.append(skill)
                extracted_skills[category] = found_skills
            
            # Use NER to find additional technical terms
            ner_results = self.skill_extractor(text)
            technical_terms = []
            
            for result in ner_results:
                if result['entity'].startswith('B-') or result['entity'].startswith('I-'):
                    technical_terms.append(result['word'])
            
            # Calculate skill scores
            skill_scores = {}
            for category, skills in extracted_skills.items():
                skill_scores[category] = len(skills)
            
            return {
                "skills_by_category": extracted_skills,
                "technical_terms": list(set(technical_terms)),
                "skill_scores": skill_scores,
                "total_skills": sum(len(skills) for skills in extracted_skills.values())
            }
            
        except Exception as e:
            logger.error(f"Skill extraction error: {str(e)}")
            return {}

    async def _extract_experience(self, text: str) -> Dict[str, Any]:
        """Extract work experience using NLP"""
        try:
            doc = self.nlp(text)
            experience_data = {
                "positions": [],
                "total_years": 0,
                "level": "entry",
                "companies": [],
                "industries": []
            }
            
            # Extract years of experience
            year_patterns = [
                r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
                r'experience\s*:?\s*(\d+)\+?\s*years?',
                r'(\d+)\+?\s*yrs?\s*(?:of\s*)?experience'
            ]
            
            years_found = []
            for pattern in year_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                years_found.extend([int(match) for match in matches])
            
            if years_found:
                experience_data["total_years"] = max(years_found)
            
            # Determine experience level
            if experience_data["total_years"] >= 10:
                experience_data["level"] = "senior"
            elif experience_data["total_years"] >= 5:
                experience_data["level"] = "mid"
            elif experience_data["total_years"] >= 2:
                experience_data["level"] = "junior"
            
            # Extract organizations using NER
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    experience_data["companies"].append(ent.text)
            
            # Extract job titles and positions
            job_title_patterns = [
                r'(software engineer|developer|manager|analyst|specialist|coordinator|director|lead|architect|consultant)',
                r'(senior|junior|lead|principal|staff)\s+(engineer|developer|analyst)',
                r'(project manager|product manager|engineering manager)'
            ]
            
            positions = []
            for pattern in job_title_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                positions.extend([' '.join(match) if isinstance(match, tuple) else match for match in matches])
            
            experience_data["positions"] = list(set(positions))
            
            return experience_data
            
        except Exception as e:
            logger.error(f"Experience extraction error: {str(e)}")
            return {}

    async def _extract_education(self, text: str) -> Dict[str, Any]:
        """Extract education information"""
        try:
            education_data = {
                "degrees": [],
                "institutions": [],
                "level": "none",
                "fields_of_study": [],
                "gpa": None
            }
            
            # Degree patterns
            degree_patterns = [
                r'\b(bachelor|master|phd|doctorate|associate)\s+(?:of\s+)?(?:science|arts|engineering|business|computer science)\b',
                r'\b(ba|bs|ms|ma|mba|phd|btech|mtech|be|me)\b',
                r'\b(degree|diploma|certificate)\s+in\s+[\w\s]+',
            ]
            
            degrees_found = []
            for pattern in degree_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                degrees_found.extend(matches)
            
            education_data["degrees"] = list(set([deg if isinstance(deg, str) else ' '.join(deg) for deg in degrees_found]))
            
            # Extract institutions
            institution_patterns = [
                r'(university|college|institute|school)\s+of\s+[\w\s]+',
                r'[\w\s]+\s+(university|college|institute)',
                r'\b[A-Z][a-z]+\s+(University|College|Institute)\b'
            ]
            
            institutions = []
            for pattern in institution_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                institutions.extend(matches)
            
            education_data["institutions"] = list(set([inst if isinstance(inst, str) else ' '.join(inst) for inst in institutions]))
            
            # Extract GPA
            gpa_pattern = r'gpa\s*:?\s*(\d+\.?\d*)'
            gpa_matches = re.findall(gpa_pattern, text, re.IGNORECASE)
            if gpa_matches:
                education_data["gpa"] = float(gpa_matches[0])
            
            # Determine education level
            if any('phd' in deg.lower() or 'doctorate' in deg.lower() for deg in education_data["degrees"]):
                education_data["level"] = "doctorate"
            elif any('master' in deg.lower() or 'ms' in deg.lower() or 'ma' in deg.lower() or 'mba' in deg.lower() for deg in education_data["degrees"]):
                education_data["level"] = "masters"
            elif any('bachelor' in deg.lower() or 'bs' in deg.lower() or 'ba' in deg.lower() for deg in education_data["degrees"]):
                education_data["level"] = "bachelors"
            elif education_data["degrees"]:
                education_data["level"] = "other"
            
            return education_data
            
        except Exception as e:
            logger.error(f"Education extraction error: {str(e)}")
            return {}

    async def _extract_projects(self, text: str) -> List[Dict[str, Any]]:
        """Extract project information"""
        try:
            projects = []
            
            # Look for project sections
            project_patterns = [
                r'projects?\s*:?\s*(.*?)(?=\n\s*\n|\n[A-Z]|\Z)',
                r'personal projects?\s*:?\s*(.*?)(?=\n\s*\n|\n[A-Z]|\Z)',
                r'key projects?\s*:?\s*(.*?)(?=\n\s*\n|\n[A-Z]|\Z)'
            ]
            
            for pattern in project_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    # Extract individual projects
                    project_lines = match.split('\n')
                    for line in project_lines:
                        line = line.strip()
                        if line and len(line) > 20:  # Filter out short lines
                            projects.append({
                                "description": line,
                                "technologies": self._extract_technologies_from_text(line)
                            })
            
            return projects[:5]  # Return top 5 projects
            
        except Exception as e:
            logger.error(f"Project extraction error: {str(e)}")
            return []

    async def _analyze_achievements(self, text: str) -> List[str]:
        """Extract achievements and accomplishments"""
        try:
            achievements = []
            
            # Look for achievement indicators
            achievement_patterns = [
                r'(increased|improved|reduced|achieved|delivered|led|managed|developed|built|created|designed|implemented)\s+[^.]*\d+[%\w\s]*',
                r'(award|recognition|certification|achievement|accomplishment)\s*:?\s*[^.\n]*',
                r'(successfully|effectively|efficiently)\s+[^.]*'
            ]
            
            for pattern in achievement_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                achievements.extend([match if isinstance(match, str) else ' '.join(match) for match in matches])
            
            return list(set(achievements))[:10]  # Return top 10 achievements
            
        except Exception as e:
            logger.error(f"Achievement extraction error: {str(e)}")
            return []

    def _extract_technologies_from_text(self, text: str) -> List[str]:
        """Extract technologies from a text snippet"""
        technologies = []
        text_lower = text.lower()
        
        all_skills = []
        for skills in self.skill_categories.values():
            all_skills.extend(skills)
        
        for skill in all_skills:
            if skill.lower() in text_lower:
                technologies.append(skill)
        
        return technologies

    async def _calculate_overall_score(self, text: str, job_id: Optional[str] = None) -> Dict[str, float]:
        """Calculate comprehensive scoring"""
        try:
            scores = {
                "overall_score": 0.0,
                "technical_score": 0.0,
                "experience_score": 0.0,
                "education_score": 0.0,
                "communication_score": 0.0,
                "cultural_fit_score": 0.0
            }
            
            # Technical score based on skills
            skills_data = await self._extract_skills(text)
            total_skills = skills_data.get("total_skills", 0)
            scores["technical_score"] = min(total_skills * 5, 100)  # Cap at 100
            
            # Experience score
            experience_data = await self._extract_experience(text)
            years = experience_data.get("total_years", 0)
            scores["experience_score"] = min(years * 10, 100)  # Cap at 100
            
            # Education score
            education_data = await self._extract_education(text)
            education_level = education_data.get("level", "none")
            education_scores = {
                "doctorate": 100,
                "masters": 85,
                "bachelors": 70,
                "other": 50,
                "none": 20
            }
            scores["education_score"] = education_scores.get(education_level, 20)
            
            # Communication score (based on text quality)
            word_count = len(text.split())
            sentence_count = len(text.split('.'))
            avg_sentence_length = word_count / max(sentence_count, 1)
            scores["communication_score"] = min(avg_sentence_length * 3, 100)
            
            # Cultural fit score (placeholder - would use job description matching)
            scores["cultural_fit_score"] = 75.0  # Default score
            
            # Overall score (weighted average)
            weights = {
                "technical_score": 0.3,
                "experience_score": 0.25,
                "education_score": 0.2,
                "communication_score": 0.15,
                "cultural_fit_score": 0.1
            }
            
            scores["overall_score"] = sum(
                scores[key] * weight for key, weight in weights.items()
            )
            
            return scores
            
        except Exception as e:
            logger.error(f"Scoring error: {str(e)}")
            return {"overall_score": 0.0}

    async def _generate_ai_summary(self, text: str) -> Dict[str, str]:
        """Generate AI-powered summary and recommendations"""
        try:
            # Use OpenAI to generate summary
            prompt = f"""
            Analyze this resume and provide:
            1. A brief professional summary (2-3 sentences)
            2. Key strengths (3-4 points)
            3. Areas for improvement (2-3 points)
            4. Hiring recommendation (hire/maybe/no with reasoning)
            
            Resume text:
            {text[:2000]}  # Limit text to avoid token limits
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert HR professional analyzing resumes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content
            
            # Parse the response (simplified parsing)
            return {
                "summary": ai_response,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI summary generation error: {str(e)}")
            return {
                "summary": "AI summary generation failed",
                "generated_at": datetime.utcnow().isoformat()
            }

    async def store_resume(self, analysis: Dict[str, Any], db_session, mongo_db) -> Resume:
        """Store resume analysis in both SQL and MongoDB"""
        try:
            # Store in SQL database
            resume_record = Resume(
                id=analysis["id"],
                filename=analysis["filename"],
                overall_score=analysis["scores"]["overall_score"],
                technical_score=analysis["scores"]["technical_score"],
                experience_score=analysis["scores"]["experience_score"],
                education_score=analysis["scores"]["education_score"],
                job_id=analysis.get("job_id"),
                user_id=analysis.get("user_id"),
                analyzed_at=datetime.fromisoformat(analysis["analyzed_at"])
            )
            
            db_session.add(resume_record)
            db_session.commit()
            
            # Store detailed analysis in MongoDB
            mongo_collection = mongo_db.resume_analyses
            await mongo_collection.insert_one(analysis)
            
            logger.info(f"Resume {analysis['id']} stored successfully")
            return resume_record
            
        except Exception as e:
            logger.error(f"Resume storage error: {str(e)}")
            db_session.rollback()
            raise

    async def get_analysis(self, resume_id: str, db_session) -> Optional[Dict[str, Any]]:
        """Get resume analysis by ID"""
        try:
            # Get from SQL first
            resume_record = db_session.query(Resume).filter(Resume.id == resume_id).first()
            if not resume_record:
                return None
            
            # Get detailed analysis from MongoDB
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            mongo_collection = mongo_db.resume_analyses
            
            analysis = await mongo_collection.find_one({"id": resume_id})
            return analysis
            
        except Exception as e:
            logger.error(f"Resume retrieval error: {str(e)}")
            return None

    async def match_with_job(self, resume_id: str, job_id: str, db_session) -> Dict[str, Any]:
        """Match resume with specific job requirements"""
        try:
            # Get resume analysis
            analysis = await self.get_analysis(resume_id, db_session)
            if not analysis:
                raise ValueError("Resume not found")
            
            # Get job requirements
            job = db_session.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError("Job not found")
            
            # Calculate match score
            match_score = await self._calculate_job_match_score(analysis, job)
            
            return {
                "resume_id": resume_id,
                "job_id": job_id,
                "match_score": match_score,
                "recommendations": await self._generate_match_recommendations(analysis, job),
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Job matching error: {str(e)}")
            raise

    async def _calculate_job_match_score(self, analysis: Dict[str, Any], job) -> float:
        """Calculate how well resume matches job requirements"""
        try:
            # Extract required skills from job description
            job_skills = self._extract_technologies_from_text(job.description)
            resume_skills = []
            
            for category_skills in analysis["skills"]["skills_by_category"].values():
                resume_skills.extend(category_skills)
            
            # Calculate skill overlap
            common_skills = set(job_skills) & set(resume_skills)
            skill_match_score = len(common_skills) / max(len(job_skills), 1) * 100
            
            # Factor in experience level
            required_experience = self._extract_required_experience(job.description)
            candidate_experience = analysis["experience"]["total_years"]
            
            experience_match = min(candidate_experience / max(required_experience, 1), 1.0) * 100
            
            # Weighted average
            match_score = (skill_match_score * 0.6) + (experience_match * 0.4)
            
            return min(match_score, 100.0)
            
        except Exception as e:
            logger.error(f"Match score calculation error: {str(e)}")
            return 0.0

    def _extract_required_experience(self, job_description: str) -> int:
        """Extract required years of experience from job description"""
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*yrs?\s*(?:of\s*)?experience'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE)
            if matches:
                return int(matches[0])
        
        return 0

    async def _generate_match_recommendations(self, analysis: Dict[str, Any], job) -> List[str]:
        """Generate recommendations for improving job match"""
        recommendations = []
        
        # Skill gap analysis
        job_skills = self._extract_technologies_from_text(job.description)
        resume_skills = []
        
        for category_skills in analysis["skills"]["skills_by_category"].values():
            resume_skills.extend(category_skills)
        
        missing_skills = set(job_skills) - set(resume_skills)
        if missing_skills:
            recommendations.append(f"Consider developing skills in: {', '.join(list(missing_skills)[:3])}")
        
        # Experience recommendations
        required_exp = self._extract_required_experience(job.description)
        candidate_exp = analysis["experience"]["total_years"]
        
        if candidate_exp < required_exp:
            recommendations.append(f"Gain {required_exp - candidate_exp} more years of relevant experience")
        
        return recommendations
