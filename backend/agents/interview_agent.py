"""
Interview Agent - AI-powered interview conductor
Handles both chat and voice interviews with real AI
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import openai
from datetime import datetime, timedelta
import json
import uuid
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from backend.database.sql_database import SessionLocal
from backend.database.mongo_database import get_mongo_client
from backend.models.sql_models import InterviewSession, InterviewMessage, Candidate
from backend.utils.config import settings

logger = logging.getLogger(__name__)

class InterviewAgent:
    def __init__(self):
        self.is_initialized = False
        self.sentiment_analyzer = None
        self.emotion_classifier = None
        self.tokenizer = None
        self.embedding_model = None
        self.question_bank = {}
        self.evaluation_criteria = {}

    async def initialize(self):
        """Initialize AI models for interview processing"""
        try:
            logger.info("Initializing Interview Agent...")
            
            # Initialize OpenAI
            openai.api_key = settings.OPENAI_API_KEY
            
            # Load sentiment analysis model
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Load emotion classification model
            self.emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base"
            )
            
            # Load embedding model for semantic analysis
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.embedding_model = AutoModel.from_pretrained(model_name)
            
            # Load question banks
            await self._load_question_banks()
            
            # Load evaluation criteria
            await self._load_evaluation_criteria()
            
            self.is_initialized = True
            logger.info("Interview Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Interview Agent: {str(e)}")
            raise

    def is_ready(self) -> bool:
        """Check if agent is ready"""
        return self.is_initialized

    async def _load_question_banks(self):
        """Load interview question banks by category"""
        self.question_bank = {
            "technical": [
                "Explain the difference between synchronous and asynchronous programming.",
                "How would you optimize a slow database query?",
                "Describe your approach to debugging a complex issue in production.",
                "What are the principles of good software design?",
                "How do you ensure code quality in your projects?",
                "Explain the concept of microservices and their benefits.",
                "How would you handle a situation where your application needs to scale?",
                "Describe your experience with version control and collaboration.",
                "What testing strategies do you use in your development process?",
                "How do you stay updated with new technologies and best practices?"
            ],
            "behavioral": [
                "Tell me about a time when you had to work under pressure.",
                "Describe a situation where you had to learn something new quickly.",
                "How do you handle conflicts with team members?",
                "Tell me about a project you're particularly proud of.",
                "Describe a time when you made a mistake and how you handled it.",
                "How do you prioritize tasks when you have multiple deadlines?",
                "Tell me about a time when you had to give difficult feedback.",
                "Describe your ideal work environment.",
                "How do you handle criticism of your work?",
                "Tell me about a time when you went above and beyond."
            ],
            "situational": [
                "How would you approach a project with unclear requirements?",
                "What would you do if you disagreed with your manager's decision?",
                "How would you handle a situation where a team member isn't contributing?",
                "What would you do if you discovered a security vulnerability?",
                "How would you approach working with a difficult client?",
                "What would you do if you realized you couldn't meet a deadline?",
                "How would you handle a situation where you need to learn a new technology quickly?",
                "What would you do if you found a bug in production?",
                "How would you approach mentoring a junior developer?",
                "What would you do if you had to work with legacy code?"
            ],
            "cultural": [
                "What motivates you in your work?",
                "How do you define success?",
                "What type of work environment do you thrive in?",
                "How do you handle work-life balance?",
                "What are your long-term career goals?",
                "How do you prefer to receive feedback?",
                "What role do you typically take in team projects?",
                "How do you approach continuous learning?",
                "What values are important to you in a workplace?",
                "How do you handle change and uncertainty?"
            ]
        }

    async def _load_evaluation_criteria(self):
        """Load evaluation criteria for different aspects"""
        self.evaluation_criteria = {
            "technical_competency": {
                "weight": 0.3,
                "factors": ["accuracy", "depth", "problem_solving", "best_practices"]
            },
            "communication": {
                "weight": 0.25,
                "factors": ["clarity", "articulation", "listening", "engagement"]
            },
            "cultural_fit": {
                "weight": 0.2,
                "factors": ["values_alignment", "team_collaboration", "adaptability"]
            },
            "experience_relevance": {
                "weight": 0.15,
                "factors": ["relevant_experience", "project_complexity", "leadership"]
            },
            "problem_solving": {
                "weight": 0.1,
                "factors": ["analytical_thinking", "creativity", "decision_making"]
            }
        }

    async def start_session(self, candidate_id: str, interview_type: str, job_id: str, user_id: str) -> Dict[str, Any]:
        """Start a new interview session"""
        try:
            session_id = str(uuid.uuid4())
            
            # Generate initial questions based on interview type and job
            questions = await self._generate_interview_questions(interview_type, job_id)
            
            session_data = {
                "id": session_id,
                "candidate_id": candidate_id,
                "job_id": job_id,
                "interview_type": interview_type,
                "status": "active",
                "current_question_index": 0,
                "questions": questions,
                "started_at": datetime.utcnow().isoformat(),
                "interviewer_id": user_id,
                "evaluation": {
                    "scores": {},
                    "notes": [],
                    "overall_score": 0.0
                }
            }
            
            # Generate welcome message
            welcome_message = await self._generate_welcome_message(candidate_id, interview_type)
            session_data["welcome_message"] = welcome_message
            
            # Ask first question
            first_question = await self._get_next_question(session_data)
            session_data["current_question"] = first_question
            
            return session_data
            
        except Exception as e:
            logger.error(f"Session start error: {str(e)}")
            raise

    async def _generate_interview_questions(self, interview_type: str, job_id: str) -> List[Dict[str, Any]]:
        """Generate personalized interview questions"""
        try:
            questions = []
            
            # Base questions by type
            if interview_type == "technical":
                base_questions = self.question_bank["technical"][:5]
                base_questions.extend(self.question_bank["behavioral"][:3])
            elif interview_type == "behavioral":
                base_questions = self.question_bank["behavioral"][:6]
                base_questions.extend(self.question_bank["cultural"][:2])
            else:  # comprehensive
                base_questions = (
                    self.question_bank["technical"][:3] +
                    self.question_bank["behavioral"][:3] +
                    self.question_bank["situational"][:2] +
                    self.question_bank["cultural"][:2]
                )
            
            # Convert to structured format
            for i, question_text in enumerate(base_questions):
                questions.append({
                    "id": f"q_{i+1}",
                    "text": question_text,
                    "category": self._categorize_question(question_text),
                    "expected_duration": 180,  # 3 minutes
                    "follow_up_questions": await self._generate_follow_up_questions(question_text)
                })
            
            return questions
            
        except Exception as e:
            logger.error(f"Question generation error: {str(e)}")
            return []

    def _categorize_question(self, question_text: str) -> str:
        """Categorize question based on content"""
        question_lower = question_text.lower()
        
        if any(word in question_lower for word in ["technical", "code", "algorithm", "database", "system"]):
            return "technical"
        elif any(word in question_lower for word in ["time when", "situation", "experience", "example"]):
            return "behavioral"
        elif any(word in question_lower for word in ["would you", "how would", "what would"]):
            return "situational"
        else:
            return "cultural"

    async def _generate_follow_up_questions(self, main_question: str) -> List[str]:
        """Generate follow-up questions using AI"""
        try:
            prompt = f"""
            Generate 2-3 relevant follow-up questions for this interview question:
            "{main_question}"
            
            Follow-up questions should:
            1. Dig deeper into the candidate's response
            2. Explore specific examples or details
            3. Assess problem-solving approach
            
            Return only the questions, one per line.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert interviewer creating follow-up questions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            follow_ups = response.choices[0].message.content.strip().split('\n')
            return [q.strip() for q in follow_ups if q.strip()]
            
        except Exception as e:
            logger.error(f"Follow-up generation error: {str(e)}")
            return []

    async def _generate_welcome_message(self, candidate_id: str, interview_type: str) -> str:
        """Generate personalized welcome message"""
        try:
            # Get candidate info (simplified)
            candidate_name = "Candidate"  # Would fetch from database
            
            welcome_templates = {
                "technical": f"Hello {candidate_name}! Welcome to your technical interview. I'm your AI interviewer, and I'll be assessing your technical skills and problem-solving abilities. We'll cover programming concepts, system design, and your hands-on experience. Are you ready to begin?",
                "behavioral": f"Hi {candidate_name}! I'm excited to learn more about your professional experiences and how you handle various workplace situations. This behavioral interview will help us understand your soft skills and cultural fit. Shall we get started?",
                "comprehensive": f"Welcome {candidate_name}! I'll be conducting a comprehensive interview covering both technical and behavioral aspects. We'll discuss your technical expertise, past experiences, and how you approach challenges. Ready to begin?"
            }
            
            return welcome_templates.get(interview_type, welcome_templates["comprehensive"])
            
        except Exception as e:
            logger.error(f"Welcome message generation error: {str(e)}")
            return "Welcome to your interview! I'm your AI interviewer. Are you ready to begin?"

    async def process_message(self, session_id: str, message: str, message_type: str = "text") -> Dict[str, Any]:
        """Process candidate's response and generate AI reply"""
        try:
            # Get session data
            session_data = await self._get_session_data(session_id)
            if not session_data:
                raise ValueError("Session not found")
            
            # Analyze the response
            analysis = await self._analyze_response(message, session_data)
            
            # Update evaluation scores
            await self._update_evaluation_scores(session_data, analysis)
            
            # Generate AI response
            ai_response = await self._generate_ai_response(message, session_data, analysis)
            
            # Determine next action (next question, follow-up, or end)
            next_action = await self._determine_next_action(session_data, analysis)
            
            response_data = {
                "ai_message": ai_response,
                "analysis": analysis,
                "next_action": next_action,
                "session_status": session_data["status"],
                "current_scores": session_data["evaluation"]["scores"]
            }
            
            # Update session data
            await self._update_session_data(session_id, session_data)
            
            return response_data
            
        except Exception as e:
            logger.error(f"Message processing error: {str(e)}")
            raise

    async def _analyze_response(self, message: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive analysis of candidate's response"""
        try:
            analysis = {
                "sentiment": await self._analyze_sentiment(message),
                "emotion": await self._analyze_emotion(message),
                "technical_content": await self._analyze_technical_content(message),
                "communication_quality": await self._analyze_communication_quality(message),
                "relevance": await self._analyze_relevance(message, session_data),
                "completeness": await self._analyze_completeness(message, session_data),
                "confidence_level": await self._analyze_confidence(message)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Response analysis error: {str(e)}")
            return {}

    async def _analyze_sentiment(self, message: str) -> Dict[str, Any]:
        """Analyze sentiment of the response"""
        try:
            result = self.sentiment_analyzer(message)
            return {
                "label": result[0]["label"],
                "score": result[0]["score"]
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return {"label": "NEUTRAL", "score": 0.5}

    async def _analyze_emotion(self, message: str) -> Dict[str, Any]:
        """Analyze emotional tone of the response"""
        try:
            result = self.emotion_classifier(message)
            return {
                "emotion": result[0]["label"],
                "confidence": result[0]["score"]
            }
        except Exception as e:
            logger.error(f"Emotion analysis error: {str(e)}")
            return {"emotion": "neutral", "confidence": 0.5}

    async def _analyze_technical_content(self, message: str) -> Dict[str, Any]:
        """Analyze technical depth and accuracy"""
        try:
            # Technical keywords and concepts
            technical_keywords = [
                "algorithm", "database", "api", "framework", "architecture",
                "scalability", "performance", "security", "testing", "deployment",
                "microservices", "cloud", "devops", "agile", "scrum"
            ]
            
            message_lower = message.lower()
            found_keywords = [kw for kw in technical_keywords if kw in message_lower]
            
            # Calculate technical depth score
            technical_score = min(len(found_keywords) * 10, 100)
            
            # Use AI to assess technical accuracy
            accuracy_score = await self._assess_technical_accuracy(message)
            
            return {
                "technical_keywords": found_keywords,
                "technical_depth_score": technical_score,
                "accuracy_score": accuracy_score,
                "overall_technical_score": (technical_score + accuracy_score) / 2
            }
            
        except Exception as e:
            logger.error(f"Technical analysis error: {str(e)}")
            return {"overall_technical_score": 50.0}

    async def _assess_technical_accuracy(self, message: str) -> float:
        """Use AI to assess technical accuracy of response"""
        try:
            prompt = f"""
            Assess the technical accuracy of this response on a scale of 0-100:
            "{message}"
            
            Consider:
            1. Factual correctness
            2. Use of proper terminology
            3. Logical reasoning
            4. Best practices mentioned
            
            Return only a number between 0-100.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a technical expert evaluating accuracy."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            score_text = response.choices[0].message.content.strip()
            return float(score_text) if score_text.isdigit() else 50.0
            
        except Exception as e:
            logger.error(f"Technical accuracy assessment error: {str(e)}")
            return 50.0

    async def _analyze_communication_quality(self, message: str) -> Dict[str, Any]:
        """Analyze communication quality"""
        try:
            words = message.split()
            sentences = message.split('.')
            
            # Basic metrics
            word_count = len(words)
            sentence_count = len([s for s in sentences if s.strip()])
            avg_sentence_length = word_count / max(sentence_count, 1)
            
            # Clarity score based on sentence structure
            clarity_score = min(100, max(0, 100 - abs(avg_sentence_length - 15) * 2))
            
            # Vocabulary richness
            unique_words = len(set(word.lower() for word in words))
            vocabulary_score = min(100, (unique_words / max(word_count, 1)) * 200)
            
            # Structure and coherence
            structure_score = await self._assess_response_structure(message)
            
            return {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "avg_sentence_length": avg_sentence_length,
                "clarity_score": clarity_score,
                "vocabulary_score": vocabulary_score,
                "structure_score": structure_score,
                "overall_communication_score": (clarity_score + vocabulary_score + structure_score) / 3
            }
            
        except Exception as e:
            logger.error(f"Communication analysis error: {str(e)}")
            return {"overall_communication_score": 50.0}

    async def _assess_response_structure(self, message: str) -> float:
        """Assess the structure and coherence of the response"""
        try:
            # Check for logical flow indicators
            flow_indicators = [
                "first", "second", "then", "next", "finally", "however", "therefore",
                "because", "since", "although", "moreover", "furthermore"
            ]
            
            message_lower = message.lower()
            flow_count = sum(1 for indicator in flow_indicators if indicator in message_lower)
            
            # Structure score based on flow indicators and length
            structure_score = min(100, flow_count * 15 + len(message.split()) * 0.5)
            
            return structure_score
            
        except Exception as e:
            logger.error(f"Structure assessment error: {str(e)}")
            return 50.0

    async def _analyze_relevance(self, message: str, session_data: Dict[str, Any]) -> float:
        """Analyze how relevant the response is to the question"""
        try:
            current_question = session_data.get("current_question", {})
            question_text = current_question.get("text", "")
            
            if not question_text:
                return 50.0
            
            # Use embeddings to calculate semantic similarity
            question_embedding = await self._get_text_embedding(question_text)
            response_embedding = await self._get_text_embedding(message)
            
            similarity = cosine_similarity([question_embedding], [response_embedding])[0][0]
            relevance_score = similarity * 100
            
            return max(0, min(100, relevance_score))
            
        except Exception as e:
            logger.error(f"Relevance analysis error: {str(e)}")
            return 50.0

    async def _get_text_embedding(self, text: str) -> np.ndarray:
        """Get text embedding using transformer model"""
        try:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
            
            with torch.no_grad():
                outputs = self.embedding_model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)
            
            return embeddings.numpy().flatten()
            
        except Exception as e:
            logger.error(f"Embedding generation error: {str(e)}")
            return np.zeros(384)  # Default embedding size

    async def _analyze_completeness(self, message: str, session_data: Dict[str, Any]) -> float:
        """Analyze completeness of the response"""
        try:
            current_question = session_data.get("current_question", {})
            question_category = current_question.get("category", "")
            
            # Expected response length by category
            expected_lengths = {
                "technical": 100,
                "behavioral": 150,
                "situational": 120,
                "cultural": 80
            }
            
            expected_length = expected_lengths.get(question_category, 100)
            actual_length = len(message.split())
            
            # Calculate completeness score
            if actual_length >= expected_length:
                completeness_score = 100
            else:
                completeness_score = (actual_length / expected_length) * 100
            
            return min(100, completeness_score)
            
        except Exception as e:
            logger.error(f"Completeness analysis error: {str(e)}")
            return 50.0

    async def _analyze_confidence(self, message: str) -> float:
        """Analyze confidence level in the response"""
        try:
            # Confidence indicators
            confident_phrases = [
                "i am confident", "i know", "definitely", "certainly", "absolutely",
                "i have experience", "i successfully", "i led", "i managed"
            ]
            
            uncertain_phrases = [
                "i think", "maybe", "perhaps", "i'm not sure", "i believe",
                "probably", "might", "could be", "i guess"
            ]
            
            message_lower = message.lower()
            
            confident_count = sum(1 for phrase in confident_phrases if phrase in message_lower)
            uncertain_count = sum(1 for phrase in uncertain_phrases if phrase in message_lower)
            
            # Calculate confidence score
            confidence_score = 50 + (confident_count * 10) - (uncertain_count * 5)
            
            return max(0, min(100, confidence_score))
            
        except Exception as e:
            logger.error(f"Confidence analysis error: {str(e)}")
            return 50.0

    async def _update_evaluation_scores(self, session_data: Dict[str, Any], analysis: Dict[str, Any]):
        """Update evaluation scores based on response analysis"""
        try:
            current_question = session_data.get("current_question", {})
            question_category = current_question.get("category", "")
            
            # Map analysis to evaluation criteria
            scores = session_data["evaluation"]["scores"]
            
            # Technical competency
            if question_category == "technical":
                technical_score = analysis.get("technical_content", {}).get("overall_technical_score", 50)
                scores["technical_competency"] = scores.get("technical_competency", [])
                scores["technical_competency"].append(technical_score)
            
            # Communication
            comm_score = analysis.get("communication_quality", {}).get("overall_communication_score", 50)
            scores["communication"] = scores.get("communication", [])
            scores["communication"].append(comm_score)
            
            # Cultural fit (for behavioral/cultural questions)
            if question_category in ["behavioral", "cultural"]:
                cultural_score = (
                    analysis.get("sentiment", {}).get("score", 0.5) * 50 +
                    analysis.get("confidence_level", 50)
                ) / 2
                scores["cultural_fit"] = scores.get("cultural_fit", [])
                scores["cultural_fit"].append(cultural_score)
            
            # Problem solving (for situational questions)
            if question_category == "situational":
                problem_solving_score = (
                    analysis.get("relevance", 50) +
                    analysis.get("completeness", 50)
                ) / 2
                scores["problem_solving"] = scores.get("problem_solving", [])
                scores["problem_solving"].append(problem_solving_score)
            
            # Calculate overall score
            await self._calculate_overall_score(session_data)
            
        except Exception as e:
            logger.error(f"Score update error: {str(e)}")

    async def _calculate_overall_score(self, session_data: Dict[str, Any]):
        """Calculate overall interview score"""
        try:
            scores = session_data["evaluation"]["scores"]
            criteria = self.evaluation_criteria
            
            weighted_score = 0.0
            total_weight = 0.0
            
            for criterion, config in criteria.items():
                if criterion in scores and scores[criterion]:
                    avg_score = sum(scores[criterion]) / len(scores[criterion])
                    weight = config["weight"]
                    weighted_score += avg_score * weight
                    total_weight += weight
            
            if total_weight > 0:
                overall_score = weighted_score / total_weight
            else:
                overall_score = 0.0
            
            session_data["evaluation"]["overall_score"] = overall_score
            
        except Exception as e:
            logger.error(f"Overall score calculation error: {str(e)}")

    async def _generate_ai_response(self, message: str, session_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Generate contextual AI response"""
        try:
            current_question = session_data.get("current_question", {})
            question_text = current_question.get("text", "")
            
            # Create context for AI response
            context = {
                "question": question_text,
                "response_quality": analysis.get("communication_quality", {}),
                "technical_depth": analysis.get("technical_content", {}),
                "sentiment": analysis.get("sentiment", {}),
                "session_progress": session_data.get("current_question_index", 0)
            }
            
            prompt = f"""
            You are an AI interviewer. The candidate just answered: "{message}"
            
            Question asked: "{question_text}"
            
            Response analysis:
            - Communication quality: {context['response_quality'].get('overall_communication_score', 50)}/100
            - Technical depth: {context['technical_depth'].get('overall_technical_score', 50)}/100
            - Sentiment: {context['sentiment'].get('label', 'NEUTRAL')}
            
            Generate a natural, encouraging response that:
            1. Acknowledges their answer
            2. Provides brief feedback if appropriate
            3. Transitions to the next question or follow-up
            
            Keep it conversational and professional.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional, encouraging AI interviewer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI response generation error: {str(e)}")
            return "Thank you for that response. Let me ask you another question."

    async def _determine_next_action(self, session_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Determine what to do next in the interview"""
        try:
            current_index = session_data.get("current_question_index", 0)
            total_questions = len(session_data.get("questions", []))
            current_question = session_data.get("current_question", {})
            
            # Check if we need a follow-up question
            response_quality = analysis.get("communication_quality", {}).get("overall_communication_score", 50)
            completeness = analysis.get("completeness", 50)
            
            if response_quality < 60 or completeness < 60:
                # Generate follow-up question
                follow_ups = current_question.get("follow_up_questions", [])
                if follow_ups:
                    return {
                        "action": "follow_up",
                        "question": follow_ups[0],
                        "reason": "Need more detail or clarification"
                    }
            
            # Move to next question
            if current_index + 1 < total_questions:
                next_question = session_data["questions"][current_index + 1]
                session_data["current_question_index"] = current_index + 1
                session_data["current_question"] = next_question
                
                return {
                    "action": "next_question",
                    "question": next_question["text"],
                    "question_data": next_question
                }
            else:
                # End interview
                session_data["status"] = "completed"
                session_data["completed_at"] = datetime.utcnow().isoformat()
                
                return {
                    "action": "end_interview",
                    "message": "Thank you for completing the interview. I'll now prepare your evaluation report."
                }
            
        except Exception as e:
            logger.error(f"Next action determination error: {str(e)}")
            return {"action": "error", "message": "An error occurred during the interview."}

    async def _get_next_question(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get the next question in the interview"""
        try:
            questions = session_data.get("questions", [])
            current_index = session_data.get("current_question_index", 0)
            
            if current_index < len(questions):
                return questions[current_index]
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Next question retrieval error: {str(e)}")
            return {}

    async def store_session(self, session_data: Dict[str, Any], db_session, mongo_db):
        """Store interview session in databases"""
        try:
            # Store in SQL database
            interview_session = InterviewSession(
                id=session_data["id"],
                candidate_id=session_data["candidate_id"],
                job_id=session_data["job_id"],
                interview_type=session_data["interview_type"],
                status=session_data["status"],
                started_at=datetime.fromisoformat(session_data["started_at"]),
                interviewer_id=session_data["interviewer_id"],
                overall_score=session_data["evaluation"]["overall_score"]
            )
            
            db_session.add(interview_session)
            db_session.commit()
            
            # Store detailed session data in MongoDB
            mongo_collection = mongo_db.interview_sessions
            await mongo_collection.insert_one(session_data)
            
            logger.info(f"Interview session {session_data['id']} stored successfully")
            
        except Exception as e:
            logger.error(f"Session storage error: {str(e)}")
            db_session.rollback()
            raise

    async def store_message(self, session_id: str, user_message: str, ai_response: Dict[str, Any], mongo_db):
        """Store interview message exchange"""
        try:
            message_data = {
                "session_id": session_id,
                "user_message": user_message,
                "ai_response": ai_response,
                "timestamp": datetime.utcnow().isoformat(),
                "analysis": ai_response.get("analysis", {})
            }
            
            mongo_collection = mongo_db.interview_messages
            await mongo_collection.insert_one(message_data)
            
        except Exception as e:
            logger.error(f"Message storage error: {str(e)}")

    async def get_evaluation(self, session_id: str, db_session) -> Dict[str, Any]:
        """Get comprehensive interview evaluation"""
        try:
            # Get session from SQL
            session_record = db_session.query(InterviewSession).filter(
                InterviewSession.id == session_id
            ).first()
            
            if not session_record:
                raise ValueError("Session not found")
            
            # Get detailed data from MongoDB
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            
            session_collection = mongo_db.interview_sessions
            session_data = await session_collection.find_one({"id": session_id})
            
            messages_collection = mongo_db.interview_messages
            messages = await messages_collection.find({"session_id": session_id}).to_list(None)
            
            # Generate comprehensive evaluation
            evaluation = await self._generate_comprehensive_evaluation(session_data, messages)
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Evaluation retrieval error: {str(e)}")
            raise

    async def _generate_comprehensive_evaluation(self, session_data: Dict[str, Any], messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive evaluation report"""
        try:
            evaluation = {
                "session_id": session_data["id"],
                "overall_score": session_data["evaluation"]["overall_score"],
                "detailed_scores": session_data["evaluation"]["scores"],
                "strengths": [],
                "areas_for_improvement": [],
                "recommendations": [],
                "interview_summary": "",
                "hiring_recommendation": "",
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Analyze performance across criteria
            scores = session_data["evaluation"]["scores"]
            
            # Identify strengths and weaknesses
            for criterion, score_list in scores.items():
                if score_list:
                    avg_score = sum(score_list) / len(score_list)
                    if avg_score >= 80:
                        evaluation["strengths"].append(f"Strong {criterion.replace('_', ' ')}")
                    elif avg_score < 60:
                        evaluation["areas_for_improvement"].append(f"Improve {criterion.replace('_', ' ')}")
            
            # Generate AI-powered summary and recommendations
            ai_summary = await self._generate_ai_evaluation_summary(session_data, messages)
            evaluation.update(ai_summary)
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Comprehensive evaluation error: {str(e)}")
            return {}

    async def _generate_ai_evaluation_summary(self, session_data: Dict[str, Any], messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate AI-powered evaluation summary"""
        try:
            # Prepare context for AI
            overall_score = session_data["evaluation"]["overall_score"]
            scores = session_data["evaluation"]["scores"]
            
            # Sample responses for analysis
            sample_responses = []
            for msg in messages[-5:]:  # Last 5 responses
                if msg.get("user_message"):
                    sample_responses.append(msg["user_message"][:200])  # Truncate for token limits
            
            prompt = f"""
            Generate a comprehensive interview evaluation based on:
            
            Overall Score: {overall_score:.1f}/100
            Detailed Scores: {json.dumps(scores, indent=2)}
            
            Sample Responses:
            {chr(10).join(sample_responses)}
            
            Provide:
            1. Interview Summary (2-3 sentences)
            2. Top 3 Strengths
            3. Top 3 Areas for Improvement
            4. Hiring Recommendation (Strong Hire/Hire/Maybe/No Hire)
            5. Specific Recommendations for candidate development
            
            Format as JSON with keys: interview_summary, strengths, areas_for_improvement, hiring_recommendation, recommendations
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert HR professional providing interview evaluations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            try:
                ai_evaluation = json.loads(response.choices[0].message.content)
                return ai_evaluation
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "interview_summary": response.choices[0].message.content[:200],
                    "hiring_recommendation": "Hire" if overall_score >= 70 else "Maybe"
                }
            
        except Exception as e:
            logger.error(f"AI evaluation summary error: {str(e)}")
            return {
                "interview_summary": "Evaluation completed successfully.",
                "hiring_recommendation": "Review Required"
            }

    async def _get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data from MongoDB"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            mongo_collection = mongo_db.interview_sessions
            
            session_data = await mongo_collection.find_one({"id": session_id})
            return session_data
            
        except Exception as e:
            logger.error(f"Session data retrieval error: {str(e)}")
            return None

    async def _update_session_data(self, session_id: str, session_data: Dict[str, Any]):
        """Update session data in MongoDB"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            mongo_collection = mongo_db.interview_sessions
            
            await mongo_collection.replace_one(
                {"id": session_id},
                session_data
            )
            
        except Exception as e:
            logger.error(f"Session data update error: {str(e)}")
