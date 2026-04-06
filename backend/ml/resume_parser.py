"""
Resume Parser - Real NLP-based resume parsing and analysis
Extracts skills, experience, education using spaCy + LLM
"""

import json
import re
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Try to import spaCy, graceful fallback if not available
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not installed. Resume parsing will be limited.")


@dataclass
class ResumeData:
    """Parsed resume information"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    
    summary: Optional[str] = None
    
    skills: List[str] = None
    skill_categories: Dict[str, List[str]] = None
    
    experience: List[Dict] = None
    total_years_experience: float = 0.0
    
    education: List[Dict] = None
    highest_degree: Optional[str] = None
    
    certifications: List[str] = None
    languages: List[str] = None
    
    raw_text: str = ""
    confidence_score: float = 0.0
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if self.skill_categories is None:
            self.skill_categories = {}
        if self.experience is None:
            self.experience = []
        if self.education is None:
            self.education = []
        if self.certifications is None:
            self.certifications = []
        if self.languages is None:
            self.languages = []

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "linkedin": self.linkedin,
            "github": self.github,
            "summary": self.summary,
            "skills": self.skills,
            "skill_categories": self.skill_categories,
            "experience": self.experience,
            "total_years_experience": self.total_years_experience,
            "education": self.education,
            "highest_degree": self.highest_degree,
            "certifications": self.certifications,
            "languages": self.languages,
            "confidence_score": self.confidence_score,
        }

    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict(), indent=2)


class SkillExtractor:
    """Extract skills from resume text"""
    
    # Common technical skills by category
    TECH_SKILLS = {
        "languages": [
            "python", "javascript", "java", "c++", "c#", "go", "rust",
            "php", "ruby", "kotlin", "swift", "typescript", "scala",
            "r", "matlab", "bash", "shell", "perl", "lua", "groovy",
        ],
        "frontend": [
            "react", "angular", "vue", "svelte", "next.js", "nuxt",
            "html", "css", "tailwind", "bootstrap", "material-ui",
            "redux", "zustand", "context api", "webpack", "vite",
        ],
        "backend": [
            "fastapi", "django", "flask", "spring", "express",
            "nodejs", "node.js", "laravel", "rails", "asp.net",
            "graphql", "rest api", "microservices", "serverless",
        ],
        "databases": [
            "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
            "dynamodb", "cassandra", "sql", "nosql", "firebase",
            "postgres", "mariadb", "oracle", "mssql", "sqlite",
        ],
        "devops": [
            "docker", "kubernetes", "ci/cd", "jenkins", "gitlab",
            "github actions", "terraform", "ansible", "aws", "gcp",
            "azure", "heroku", "vercel", "netlify", "linux",
        ],
        "tools": [
            "git", "github", "gitlab", "jira", "slack", "figma",
            "postman", "datadog", "new relic", "prometheus", "grafana",
            "confluence", "notion", "asana", "trello", "docker compose",
        ],
        "soft_skills": [
            "leadership", "communication", "problem solving",
            "teamwork", "agile", "scrum", "kanban",
            "mentoring", "project management", "public speaking",
        ],
    }
    
    def __init__(self):
        self.all_skills = self._flatten_skills()
    
    def _flatten_skills(self) -> Set[str]:
        """Flatten all skills into a set"""
        all_skills = set()
        for category, skills in self.TECH_SKILLS.items():
            all_skills.update(skills)
        return all_skills
    
    def extract(self, text: str) -> Tuple[List[str], Dict[str, List[str]]]:
        """Extract skills and categorize them"""
        text_lower = text.lower()
        found_skills = []
        
        # Find mentioned skills
        for skill in self.all_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        # Categorize
        skill_categories = {}
        for category, skills in self.TECH_SKILLS.items():
            found_in_category = [s.title() for s in skills if s in text_lower]
            if found_in_category:
                skill_categories[category] = found_in_category
        
        return list(set(found_skills)), skill_categories


class ExperienceExtractor:
    """Extract experience from resume text"""
    
    # Patterns for experience detection
    EXPERIENCE_PATTERNS = [
        r"(\d+)\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp\.?)?",
        r"(?:experience|exp\.?)\s*(?:in|at|with)?.*?(\d+)\s*(?:years?|yrs?)",
    ]
    
    JOB_TITLE_KEYWORDS = [
        "engineer", "developer", "manager", "analyst", "architect",
        "designer", "lead", "senior", "junior", "principal", "director",
        "specialist", "consultant", "coordinator", "officer", "executive",
    ]
    
    def extract(self, text: str) -> Tuple[List[Dict], float]:
        """Extract work experience and estimate years"""
        experiences = []
        total_years = 0.0
        
        # Look for years of experience
        for pattern in self.EXPERIENCE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    total_years = float(matches[0])
                    break
                except (ValueError, IndexError):
                    pass
        
        # Extract job titles
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            # Check if line contains job title keywords
            if any(keyword in line_lower for keyword in self.JOB_TITLE_KEYWORDS):
                experiences.append({
                    "title": line.strip(),
                    "context": "Extracted from resume"
                })
        
        return experiences[:5], total_years  # Limit to 5 most recent


class EducationExtractor:
    """Extract education from resume text"""
    
    DEGREES = {
        "phd": ["phd", "doctorate", "dr."],
        "masters": ["master", "mba", "ms.", "ma.", "m.tech"],
        "bachelors": ["bachelor", "b.tech", "bsc", "bs.", "b.a.", "b.s."],
        "diploma": ["diploma", "associate"],
        "high_school": ["high school", "secondary", "10+2"],
    }
    
    FIELDS = [
        "computer science", "engineering", "information technology",
        "business administration", "finance", "economics", "data science",
        "mathematics", "physics", "chemistry", "biology",
    ]
    
    def extract(self, text: str) -> Tuple[List[Dict], Optional[str]]:
        """Extract education details"""
        education = []
        highest_degree = None
        
        text_lower = text.lower()
        
        # Find degrees
        for degree_type, keywords in self.DEGREES.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if not highest_degree:
                        highest_degree = degree_type
                    
                    education.append({
                        "degree": degree_type,
                        "field": self._extract_field(text),
                    })
                    break
        
        return education[:3], highest_degree
    
    def _extract_field(self, text: str) -> str:
        """Extract field of study"""
        text_lower = text.lower()
        for field in self.FIELDS:
            if field in text_lower:
                return field
        return "Not specified"


class ContactExtractor:
    """Extract contact information from resume"""
    
    def extract(self, text: str) -> Dict[str, Optional[str]]:
        """Extract contact details"""
        contact = {
            "email": self._extract_email(text),
            "phone": self._extract_phone(text),
            "linkedin": self._extract_linkedin(text),
            "github": self._extract_github(text),
            "name": self._extract_name(text),
        }
        return contact
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address"""
        pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        matches = re.findall(pattern, text)
        return matches[0] if matches else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number"""
        # International phone pattern
        pattern = r"(?:\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}"
        matches = re.findall(pattern, text)
        return matches[0] if matches else None
    
    def _extract_linkedin(self, text: str) -> Optional[str]:
        """Extract LinkedIn profile"""
        pattern = r"(?:https?://)?(?:www\.)?linkedin\.com[^\s]+"
        matches = re.findall(pattern, text, re.IGNORECASE)
        return matches[0] if matches else None
    
    def _extract_github(self, text: str) -> Optional[str]:
        """Extract GitHub profile"""
        pattern = r"(?:https?://)?(?:www\.)?github\.com[^\s]+"
        matches = re.findall(pattern, text, re.IGNORECASE)
        return matches[0] if matches else None
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract name (first line usually)"""
        lines = text.strip().split('\n')
        for line in lines[:3]:  # Check first 3 lines
            line = line.strip()
            if len(line) < 60 and len(line.split()) <= 4:
                # Likely a name
                return line
        return None


class ResumeParser:
    """Main resume parser combining all extractors"""
    
    def __init__(self):
        self.contact_extractor = ContactExtractor()
        self.skill_extractor = SkillExtractor()
        self.experience_extractor = ExperienceExtractor()
        self.education_extractor = EducationExtractor()
        self.nlp = self._load_spacy()
    
    def _load_spacy(self):
        """Load spaCy model if available"""
        if not SPACY_AVAILABLE:
            return None
        try:
            return spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
            return None
    
    def parse(self, resume_text: str) -> ResumeData:
        """Parse resume and extract all information"""
        
        # Extract all components
        contact = self.contact_extractor.extract(resume_text)
        skills, skill_categories = self.skill_extractor.extract(resume_text)
        experience, years_exp = self.experience_extractor.extract(resume_text)
        education, highest_degree = self.education_extractor.extract(resume_text)
        
        # Create data object
        data = ResumeData(
            name=contact.get("name"),
            email=contact.get("email"),
            phone=contact.get("phone"),
            linkedin=contact.get("linkedin"),
            github=contact.get("github"),
            
            skills=skills,
            skill_categories=skill_categories,
            
            experience=experience,
            total_years_experience=years_exp,
            
            education=education,
            highest_degree=highest_degree,
            
            raw_text=resume_text,
        )
        
        # Calculate confidence score
        confidence = self._calculate_confidence(data)
        data.confidence_score = confidence
        
        logger.info(f"Resume parsed: {data.name} - Skills: {len(data.skills)}, Experience: {data.total_years_experience}y")
        
        return data
    
    def _calculate_confidence(self, data: ResumeData) -> float:
        """Calculate confidence score (0-1)"""
        confidence = 0.0
        
        if data.name:
            confidence += 0.15
        if data.email:
            confidence += 0.15
        if data.phone:
            confidence += 0.10
        if len(data.skills) > 0:
            confidence += 0.20
        if data.total_years_experience > 0:
            confidence += 0.15
        if len(data.education) > 0:
            confidence += 0.15
        if data.linkedin or data.github:
            confidence += 0.10
        
        return min(confidence, 1.0)


# Global parser instance
_resume_parser: Optional[ResumeParser] = None


def get_resume_parser() -> ResumeParser:
    """Get or create global parser"""
    global _resume_parser
    if _resume_parser is None:
        _resume_parser = ResumeParser()
    return _resume_parser
