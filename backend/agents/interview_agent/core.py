"""
Interview Agent Core - Complete interview automation system
Handles chat, voice, video interviews with full AI evaluation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
import openai
from datetime import datetime, timedelta
import json
import uuid
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from transformers import pipeline, AutoTokenizer, AutoModel
import torch

from ..base_agent import BaseAgent
from .question_generator import QuestionGenerator
from .evaluation_engine import EvaluationEngine
from .voice_processor import VoiceProcessor
from .video_analyzer import VideoAnalyzer
from .behavioral_analyzer import BehavioralAnalyzer
from backend.database.mongo_database import get_mongo_client
from backend.database.sql_database import SessionLocal
from models.sql_models import InterviewSession, Candidate, Job
from backend.utils.config import settings

logger = logging.getLogger(__name__)

class InterviewAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "interview_agent"
        self.question_generator = QuestionGenerator()
        self.evaluation_engine = EvaluationEngine()
        self.voice_processor = VoiceProcessor()
        self.video_analyzer = VideoAnalyzer()
        self.behavioral_analyzer = BehavioralAnalyzer()
        
        # AI Models
        self.nlp = None
        self.sentiment_analyzer = None
        self.emotion_classifier = None
        self.embedding_model = None
        self.tokenizer = None
        
        # Interview configurations
        self.interview_types = {
            "technical": {
                "duration": 45,
                "question_count": 8,
                "categories": ["technical", "problem_solving", "system_design"]
            },
            "behavioral": {
                "duration": 30,
                "question_count": 6,
                "categories": ["behavioral", "cultural_fit", "leadership"]
            },
            "comprehensive": {
                "duration": 60,
                "question_count": 12,
                "categories": ["technical", "behavioral", "cultural_fit", "problem_solving"]
            },
            "screening": {
                "duration": 15,
                "question_count": 4,
                "categories": ["basic_technical", "communication"]
            }
        }

    async def initialize(self):
        """Initialize all interview components"""
        try:
            logger.info("Initializing Interview Agent...")
            
            # Initialize base components
            await super().initialize()
            
            # Load NLP models
            self.nlp = spacy.load("en_core_web_sm")
            
            # Initialize sentiment analysis
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Initialize emotion classification
            self.emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base"
            )
            
            # Load embedding model
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.embedding_model = AutoModel.from_pretrained(model_name)
            
            # Initialize sub-components
            await self.question_generator.initialize()
            await self.evaluation_engine.initialize()
            await self.voice_processor.initialize()
            await self.video_analyzer.initialize()
            await self.behavioral_analyzer.initialize()
            
            self.is_initialized = True
            logger.info("Interview Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Interview Agent: {str(e)}")
            raise

    async def start_interview_session(self, candidate_id: str, job_id: str, interview_type: str, 
                                    mode: str = "chat", interviewer_id: str = None) -> Dict[str, Any]:
        """Start a new interview session"""
        try:
            session_id = str(uuid.uuid4())
            
            # Get candidate and job information
            candidate_info = await self._get_candidate_info(candidate_id)
            job_info = await self._get_job_info(job_id)
            
            # Generate interview questions
            questions = await self.question_generator.generate_questions(
                interview_type=interview_type,
                job_description=job_info.get("description", ""),
                candidate_background=candidate_info.get("background", ""),
                difficulty_level=self._determine_difficulty_level(candidate_info)
            )
            
            # Create session data
            session_data = {
                "id": session_id,
                "candidate_id": candidate_id,
                "job_id": job_id,
                "interview_type": interview_type,
                "mode": mode,  # chat, voice, video
                "status": "active",
                "started_at": datetime.utcnow().isoformat(),
                "interviewer_id": interviewer_id or "ai_interviewer",
                "questions": questions,
                "current_question_index": 0,
                "responses": [],
                "evaluation": {
                    "scores": {},
                    "detailed_feedback": [],
                    "overall_score": 0.0,
                    "recommendation": ""
                },
                "metadata": {
                    "candidate_info": candidate_info,
                    "job_info": job_info,
                    "session_config": self.interview_types.get(interview_type, {})
                }
            }
            
            # Generate welcome message
            welcome_message = await self._generate_welcome_message(session_data)
            session_data["welcome_message"] = welcome_message
            
            # Store session
            await self._store_session(session_data)
            
            # Get first question
            first_question = await self._get_current_question(session_data)
            
            return {
                "session_id": session_id,
                "welcome_message": welcome_message,
                "first_question": first_question,
                "session_info": {
                    "type": interview_type,
                    "mode": mode,
                    "estimated_duration": self.interview_types.get(interview_type, {}).get("duration", 30),
                    "total_questions": len(questions)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to start interview session: {str(e)}")
            raise

    async def process_response(self, session_id: str, response: str, 
                             response_type: str = "text", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process candidate response and generate next action"""
        try:
            # Get session data
            session_data = await self._get_session_data(session_id)
            if not session_data:
                raise ValueError("Session not found")
            
            # Get current question
            current_question = await self._get_current_question(session_data)
            
            # Analyze response
            analysis = await self._analyze_response(
                response=response,
                question=current_question,
                session_data=session_data,
                response_type=response_type,
                metadata=metadata
            )
            
            # Store response and analysis
            response_data = {
                "question_id": current_question.get("id"),
                "question_text": current_question.get("text"),
                "response": response,
                "response_type": response_type,
                "analysis": analysis,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            session_data["responses"].append(response_data)
            
            # Update evaluation scores
            await self._update_evaluation_scores(session_data, analysis)
            
            # Generate AI feedback
            ai_feedback = await self._generate_ai_feedback(response, current_question, analysis)
            
            # Determine next action
            next_action = await self._determine_next_action(session_data, analysis)
            
            # Update session
            await self._update_session(session_data)
            
            return {
                "ai_feedback": ai_feedback,
                "analysis_summary": {
                    "overall_score": analysis.get("overall_score", 0),
                    "key_strengths": analysis.get("strengths", []),
                    "areas_for_improvement": analysis.get("improvements", [])
                },
                "next_action": next_action,
                "session_progress": {
                    "current_question": session_data["current_question_index"] + 1,
                    "total_questions": len(session_data["questions"]),
                    "completion_percentage": ((session_data["current_question_index"] + 1) / len(session_data["questions"])) * 100
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to process response: {str(e)}")
            raise

    async def _analyze_response(self, response: str, question: Dict[str, Any], 
                              session_data: Dict[str, Any], response_type: str = "text",
                              metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Comprehensive response analysis"""
        try:
            analysis = {
                "response_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "response_type": response_type,
                "question_category": question.get("category", ""),
                "scores": {},
                "detailed_analysis": {},
                "strengths": [],
                "improvements": [],
                "overall_score": 0.0
            }
            
            # Text-based analysis
            if response_type in ["text", "voice"]:
                # Basic metrics
                analysis["detailed_analysis"]["text_metrics"] = await self._analyze_text_metrics(response)
                
                # Sentiment analysis
                analysis["detailed_analysis"]["sentiment"] = await self._analyze_sentiment(response)
                
                # Emotion analysis
                analysis["detailed_analysis"]["emotion"] = await self._analyze_emotion(response)
                
                # Technical content analysis
                if question.get("category") in ["technical", "problem_solving"]:
                    analysis["detailed_analysis"]["technical"] = await self._analyze_technical_content(response, question)
                
                # Behavioral analysis
                if question.get("category") in ["behavioral", "cultural_fit"]:
                    analysis["detailed_analysis"]["behavioral"] = await self._analyze_behavioral_content(response, question)
                
                # Communication quality
                analysis["detailed_analysis"]["communication"] = await self._analyze_communication_quality(response)
                
                # Relevance to question
                analysis["detailed_analysis"]["relevance"] = await self._analyze_relevance(response, question)
            
            # Voice-specific analysis
            if response_type == "voice" and metadata:
                analysis["detailed_analysis"]["voice"] = await self.voice_processor.analyze_voice_characteristics(
                    audio_data=metadata.get("audio_data"),
                    transcript=response
                )
            
            # Video-specific analysis
            if response_type == "video" and metadata:
                analysis["detailed_analysis"]["video"] = await self.video_analyzer.analyze_video_response(
                    video_data=metadata.get("video_data"),
                    transcript=response
                )
            
            # Calculate scores
            analysis["scores"] = await self._calculate_response_scores(analysis["detailed_analysis"], question)
            
            # Generate overall score
            analysis["overall_score"] = await self._calculate_overall_response_score(analysis["scores"])
            
            # Generate strengths and improvements
            analysis["strengths"], analysis["improvements"] = await self._generate_feedback_points(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Response analysis error: {str(e)}")
            return {"overall_score": 0.0, "error": str(e)}

    async def _analyze_text_metrics(self, response: str) -> Dict[str, Any]:
        """Analyze basic text metrics"""
        try:
            words = response.split()
            sentences = response.split('.')
            
            return {
                "word_count": len(words),
                "sentence_count": len([s for s in sentences if s.strip()]),
                "avg_sentence_length": len(words) / max(len([s for s in sentences if s.strip()]), 1),
                "character_count": len(response),
                "unique_words": len(set(word.lower() for word in words)),
                "vocabulary_richness": len(set(word.lower() for word in words)) / max(len(words), 1)
            }
        except Exception as e:
            logger.error(f"Text metrics analysis error: {str(e)}")
            return {}

    async def _analyze_sentiment(self, response: str) -> Dict[str, Any]:
        """Analyze sentiment of response"""
        try:
            result = self.sentiment_analyzer(response)
            return {
                "label": result[0]["label"],
                "score": result[0]["score"],
                "confidence": result[0]["score"]
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return {"label": "NEUTRAL", "score": 0.5}

    async def _analyze_emotion(self, response: str) -> Dict[str, Any]:
        """Analyze emotional tone"""
        try:
            result = self.emotion_classifier(response)
            return {
                "emotion": result[0]["label"],
                "confidence": result[0]["score"],
                "all_emotions": result
            }
        except Exception as e:
            logger.error(f"Emotion analysis error: {str(e)}")
            return {"emotion": "neutral", "confidence": 0.5}

    async def _analyze_technical_content(self, response: str, question: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical content quality"""
        try:
            # Technical keywords detection
            technical_keywords = [
                "algorithm", "complexity", "optimization", "scalability", "performance",
                "database", "api", "framework", "architecture", "design pattern",
                "testing", "debugging", "deployment", "security", "authentication"
            ]
            
            response_lower = response.lower()
            found_keywords = [kw for kw in technical_keywords if kw in response_lower]
            
            # Code quality indicators
            code_indicators = ["function", "class", "method", "variable", "loop", "condition"]
            code_mentions = [ind for ind in code_indicators if ind in response_lower]
            
            # Best practices mentions
            best_practices = ["clean code", "documentation", "version control", "code review", "testing"]
            practices_mentioned = [bp for bp in best_practices if bp in response_lower]
            
            # Use AI to assess technical accuracy
            accuracy_score = await self._assess_technical_accuracy_with_ai(response, question)
            
            return {
                "technical_keywords": found_keywords,
                "keyword_count": len(found_keywords),
                "code_indicators": code_mentions,
                "best_practices": practices_mentioned,
                "technical_depth_score": min(len(found_keywords) * 10, 100),
                "accuracy_score": accuracy_score,
                "overall_technical_score": (min(len(found_keywords) * 10, 100) + accuracy_score) / 2
            }
            
        except Exception as e:
            logger.error(f"Technical content analysis error: {str(e)}")
            return {"overall_technical_score": 50.0}

    async def _assess_technical_accuracy_with_ai(self, response: str, question: Dict[str, Any]) -> float:
        """Use AI to assess technical accuracy"""
        try:
            prompt = f"""
            Assess the technical accuracy of this response on a scale of 0-100:
            
            Question: {question.get('text', '')}
            Response: {response}
            
            Consider:
            1. Factual correctness
            2. Proper use of technical terminology
            3. Logical reasoning and approach
            4. Completeness of the answer
            5. Best practices mentioned
            
            Return only a number between 0-100.
            """
            
            response_obj = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a technical expert evaluating interview responses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            score_text = response_obj.choices[0].message.content.strip()
            return float(score_text) if score_text.replace('.', '').isdigit() else 50.0
            
        except Exception as e:
            logger.error(f"AI technical accuracy assessment error: {str(e)}")
            return 50.0

    async def _analyze_behavioral_content(self, response: str, question: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze behavioral response quality"""
        try:
            # STAR method detection (Situation, Task, Action, Result)
            star_indicators = {
                "situation": ["situation", "when", "time", "project", "challenge"],
                "task": ["task", "responsibility", "goal", "objective", "needed"],
                "action": ["action", "did", "implemented", "decided", "approached"],
                "result": ["result", "outcome", "achieved", "improved", "success"]
            }
            
            response_lower = response.lower()
            star_scores = {}
            
            for component, indicators in star_indicators.items():
                score = sum(1 for indicator in indicators if indicator in response_lower)
                star_scores[component] = min(score * 25, 100)
            
            # Leadership indicators
            leadership_keywords = ["led", "managed", "coordinated", "mentored", "guided", "influenced"]
            leadership_score = sum(1 for kw in leadership_keywords if kw in response_lower) * 15
            
            # Collaboration indicators
            collaboration_keywords = ["team", "collaborated", "worked together", "coordinated", "communicated"]
            collaboration_score = sum(1 for kw in collaboration_keywords if kw in response_lower) * 15
            
            # Problem-solving indicators
            problem_solving_keywords = ["problem", "challenge", "solution", "resolved", "analyzed"]
            problem_solving_score = sum(1 for kw in problem_solving_keywords if kw in response_lower) * 15
            
            return {
                "star_method_scores": star_scores,
                "star_completeness": sum(star_scores.values()) / 4,
                "leadership_score": min(leadership_score, 100),
                "collaboration_score": min(collaboration_score, 100),
                "problem_solving_score": min(problem_solving_score, 100),
                "overall_behavioral_score": (
                    sum(star_scores.values()) / 4 + 
                    min(leadership_score, 100) + 
                    min(collaboration_score, 100) + 
                    min(problem_solving_score, 100)
                ) / 4
            }
            
        except Exception as e:
            logger.error(f"Behavioral content analysis error: {str(e)}")
            return {"overall_behavioral_score": 50.0}

    async def _analyze_communication_quality(self, response: str) -> Dict[str, Any]:
        """Analyze communication quality"""
        try:
            # Basic structure analysis
            sentences = [s.strip() for s in response.split('.') if s.strip()]
            words = response.split()
            
            # Clarity indicators
            clarity_indicators = {
                "clear_structure": len(sentences) >= 2,
                "appropriate_length": 50 <= len(words) <= 300,
                "proper_grammar": not any(word in response.lower() for word in ["um", "uh", "like", "you know"]),
                "complete_thoughts": all(len(s.split()) >= 3 for s in sentences[:3])
            }
            
            # Articulation score
            articulation_score = sum(clarity_indicators.values()) * 25
            
            # Vocabulary assessment
            unique_words = len(set(word.lower() for word in words))
            vocabulary_score = min((unique_words / max(len(words), 1)) * 200, 100)
            
            # Coherence assessment
            coherence_score = await self._assess_coherence(response)
            
            return {
                "clarity_indicators": clarity_indicators,
                "articulation_score": articulation_score,
                "vocabulary_score": vocabulary_score,
                "coherence_score": coherence_score,
                "overall_communication_score": (articulation_score + vocabulary_score + coherence_score) / 3
            }
            
        except Exception as e:
            logger.error(f"Communication quality analysis error: {str(e)}")
            return {"overall_communication_score": 50.0}

    async def _assess_coherence(self, response: str) -> float:
        """Assess response coherence using AI"""
        try:
            sentences = [s.strip() for s in response.split('.') if s.strip()]
            if len(sentences) < 2:
                return 70.0  # Single sentence responses are considered moderately coherent
            
            # Calculate semantic similarity between consecutive sentences
            embeddings = []
            for sentence in sentences[:5]:  # Limit to first 5 sentences
                embedding = await self._get_text_embedding(sentence)
                embeddings.append(embedding)
            
            if len(embeddings) < 2:
                return 70.0
            
            # Calculate average similarity between consecutive sentences
            similarities = []
            for i in range(len(embeddings) - 1):
                sim = cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]
                similarities.append(sim)
            
            avg_similarity = sum(similarities) / len(similarities)
            coherence_score = min(avg_similarity * 150, 100)  # Scale to 0-100
            
            return max(coherence_score, 30.0)  # Minimum coherence score
            
        except Exception as e:
            logger.error(f"Coherence assessment error: {str(e)}")
            return 50.0

    async def _get_text_embedding(self, text: str) -> np.ndarray:
        """Get text embedding using transformer model"""
        try:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
            
            with torch.no_grad():
                outputs = self.embedding_model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)
            
            return embeddings.numpy().flatten()
            
        except Exception as e:
            logger.error(f"Embedding generation error: {str(e)}")
            return np.zeros(384)  # Default embedding size

    async def _analyze_relevance(self, response: str, question: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze response relevance to question"""
        try:
            question_text = question.get("text", "")
            
            # Semantic similarity
            question_embedding = await self._get_text_embedding(question_text)
            response_embedding = await self._get_text_embedding(response)
            
            similarity = cosine_similarity([question_embedding], [response_embedding])[0][0]
            relevance_score = similarity * 100
            
            # Keyword overlap
            question_words = set(question_text.lower().split())
            response_words = set(response.lower().split())
            
            # Remove common stop words
            stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
            question_words -= stop_words
            response_words -= stop_words
            
            overlap = len(question_words & response_words)
            keyword_relevance = (overlap / max(len(question_words), 1)) * 100
            
            # Combined relevance score
            combined_relevance = (relevance_score * 0.7) + (keyword_relevance * 0.3)
            
            return {
                "semantic_similarity": relevance_score,
                "keyword_overlap": keyword_relevance,
                "combined_relevance": combined_relevance,
                "relevance_category": self._categorize_relevance(combined_relevance)
            }
            
        except Exception as e:
            logger.error(f"Relevance analysis error: {str(e)}")
            return {"combined_relevance": 50.0, "relevance_category": "moderate"}

    def _categorize_relevance(self, score: float) -> str:
        """Categorize relevance score"""
        if score >= 80:
            return "highly_relevant"
        elif score >= 60:
            return "relevant"
        elif score >= 40:
            return "moderately_relevant"
        else:
            return "low_relevance"

    async def _calculate_response_scores(self, detailed_analysis: Dict[str, Any], question: Dict[str, Any]) -> Dict[str, float]:
        """Calculate individual scores for different aspects"""
        try:
            scores = {}
            
            # Technical competency (for technical questions)
            if question.get("category") in ["technical", "problem_solving"]:
                technical_data = detailed_analysis.get("technical", {})
                scores["technical_competency"] = technical_data.get("overall_technical_score", 50.0)
            
            # Behavioral competency (for behavioral questions)
            if question.get("category") in ["behavioral", "cultural_fit"]:
                behavioral_data = detailed_analysis.get("behavioral", {})
                scores["behavioral_competency"] = behavioral_data.get("overall_behavioral_score", 50.0)
            
            # Communication quality (all questions)
            communication_data = detailed_analysis.get("communication", {})
            scores["communication"] = communication_data.get("overall_communication_score", 50.0)
            
            # Relevance (all questions)
            relevance_data = detailed_analysis.get("relevance", {})
            scores["relevance"] = relevance_data.get("combined_relevance", 50.0)
            
            # Sentiment and emotion (all questions)
            sentiment_data = detailed_analysis.get("sentiment", {})
            emotion_data = detailed_analysis.get("emotion", {})
            
            # Convert sentiment to score
            sentiment_score = sentiment_data.get("score", 0.5) * 100
            if sentiment_data.get("label") == "NEGATIVE":
                sentiment_score = 100 - sentiment_score
            
            scores["attitude"] = sentiment_score
            
            # Confidence level
            confidence_indicators = ["confident", "sure", "definitely", "absolutely", "certain"]
            uncertainty_indicators = ["maybe", "perhaps", "i think", "probably", "might"]
            
            response_text = detailed_analysis.get("text_metrics", {})
            # This would need the original response text, simplified for now
            scores["confidence"] = 75.0  # Default confidence score
            
            return scores
            
        except Exception as e:
            logger.error(f"Score calculation error: {str(e)}")
            return {"overall": 50.0}

    async def _calculate_overall_response_score(self, scores: Dict[str, float]) -> float:
        """Calculate overall response score"""
        try:
            if not scores:
                return 0.0
            
            # Weight different aspects
            weights = {
                "technical_competency": 0.3,
                "behavioral_competency": 0.3,
                "communication": 0.25,
                "relevance": 0.15,
                "attitude": 0.05,
                "confidence": 0.05
            }
            
            weighted_score = 0.0
            total_weight = 0.0
            
            for aspect, score in scores.items():
                weight = weights.get(aspect, 0.1)
                weighted_score += score * weight
                total_weight += weight
            
            if total_weight > 0:
                overall_score = weighted_score / total_weight
            else:
                overall_score = sum(scores.values()) / len(scores)
            
            return min(max(overall_score, 0.0), 100.0)
            
        except Exception as e:
            logger.error(f"Overall score calculation error: {str(e)}")
            return 50.0

    async def _generate_feedback_points(self, analysis: Dict[str, Any]) -> tuple:
        """Generate strengths and improvement points"""
        try:
            strengths = []
            improvements = []
            
            scores = analysis.get("scores", {})
            detailed_analysis = analysis.get("detailed_analysis", {})
            
            # Analyze each aspect
            for aspect, score in scores.items():
                if score >= 80:
                    strengths.append(f"Strong {aspect.replace('_', ' ')}")
                elif score < 60:
                    improvements.append(f"Improve {aspect.replace('_', ' ')}")
            
            # Specific feedback based on detailed analysis
            communication_data = detailed_analysis.get("communication", {})
            if communication_data.get("vocabulary_score", 0) >= 80:
                strengths.append("Rich vocabulary and articulation")
            
            technical_data = detailed_analysis.get("technical", {})
            if technical_data.get("keyword_count", 0) >= 5:
                strengths.append("Good technical knowledge demonstration")
            
            behavioral_data = detailed_analysis.get("behavioral", {})
            star_completeness = behavioral_data.get("star_completeness", 0)
            if star_completeness >= 75:
                strengths.append("Well-structured behavioral responses using STAR method")
            elif star_completeness < 50:
                improvements.append("Use STAR method (Situation, Task, Action, Result) for behavioral questions")
            
            # Limit to top items
            return strengths[:3], improvements[:3]
            
        except Exception as e:
            logger.error(f"Feedback generation error: {str(e)}")
            return [], []

    async def _generate_ai_feedback(self, response: str, question: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Generate AI-powered feedback"""
        try:
            overall_score = analysis.get("overall_score", 0)
            strengths = analysis.get("strengths", [])
            improvements = analysis.get("improvements", [])
            
            prompt = f"""
            Generate encouraging and constructive feedback for this interview response:
            
            Question: {question.get('text', '')}
            Response: {response[:500]}...
            
            Analysis Summary:
            - Overall Score: {overall_score:.1f}/100
            - Strengths: {', '.join(strengths)}
            - Areas for Improvement: {', '.join(improvements)}
            
            Provide:
            1. Positive acknowledgment of their response
            2. Specific strengths highlighted
            3. Constructive suggestions for improvement (if any)
            4. Encouragement for the next question
            
            Keep it professional, encouraging, and under 150 words.
            """
            
            response_obj = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional, encouraging AI interviewer providing constructive feedback."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response_obj.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI feedback generation error: {str(e)}")
            return "Thank you for your response. Let's continue with the next question."

    async def _determine_next_action(self, session_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Determine what to do next in the interview"""
        try:
            current_index = session_data.get("current_question_index", 0)
            total_questions = len(session_data.get("questions", []))
            
            # Check if we need a follow-up question
            overall_score = analysis.get("overall_score", 0)
            relevance_score = analysis.get("scores", {}).get("relevance", 0)
            
            # If response quality is low, ask follow-up
            if overall_score < 60 or relevance_score < 50:
                current_question = session_data["questions"][current_index]
                follow_ups = current_question.get("follow_up_questions", [])
                
                if follow_ups and not session_data.get("follow_up_asked", False):
                    session_data["follow_up_asked"] = True
                    return {
                        "action": "follow_up",
                        "question": {
                            "text": follow_ups[0],
                            "type": "follow_up",
                            "category": current_question.get("category")
                        },
                        "reason": "Seeking more detailed response"
                    }
            
            # Move to next question
            if current_index + 1 < total_questions:
                session_data["current_question_index"] = current_index + 1
                session_data["follow_up_asked"] = False
                next_question = session_data["questions"][current_index + 1]
                
                return {
                    "action": "next_question",
                    "question": next_question,
                    "progress": {
                        "current": current_index + 2,
                        "total": total_questions,
                        "percentage": ((current_index + 2) / total_questions) * 100
                    }
                }
            else:
                # End interview
                session_data["status"] = "completed"
                session_data["completed_at"] = datetime.utcnow().isoformat()
                
                # Generate final evaluation
                final_evaluation = await self._generate_final_evaluation(session_data)
                session_data["evaluation"]["final_report"] = final_evaluation
                
                return {
                    "action": "end_interview",
                    "message": "Thank you for completing the interview. I'll now prepare your evaluation report.",
                    "final_evaluation": final_evaluation
                }
            
        except Exception as e:
            logger.error(f"Next action determination error: {str(e)}")
            return {"action": "error", "message": "An error occurred during the interview."}

    async def _generate_final_evaluation(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive final evaluation"""
        try:
            responses = session_data.get("responses", [])
            interview_type = session_data.get("interview_type", "")
            
            # Calculate overall scores
            all_scores = []
            category_scores = {}
            
            for response in responses:
                analysis = response.get("analysis", {})
                overall_score = analysis.get("overall_score", 0)
                all_scores.append(overall_score)
                
                # Category-wise scores
                question_category = response.get("question_category", "general")
                if question_category not in category_scores:
                    category_scores[question_category] = []
                category_scores[question_category].append(overall_score)
            
            # Calculate averages
            overall_average = sum(all_scores) / len(all_scores) if all_scores else 0
            category_averages = {
                category: sum(scores) / len(scores)
                for category, scores in category_scores.items()
            }
            
            # Generate recommendation
            recommendation = await self._generate_hiring_recommendation(overall_average, category_averages, session_data)
            
            # Compile strengths and improvements
            all_strengths = []
            all_improvements = []
            
            for response in responses:
                analysis = response.get("analysis", {})
                all_strengths.extend(analysis.get("strengths", []))
                all_improvements.extend(analysis.get("improvements", []))
            
            # Remove duplicates and get top items
            unique_strengths = list(set(all_strengths))[:5]
            unique_improvements = list(set(all_improvements))[:5]
            
            # Generate AI summary
            ai_summary = await self._generate_ai_evaluation_summary(session_data, overall_average, category_averages)
            
            final_evaluation = {
                "overall_score": overall_average,
                "category_scores": category_averages,
                "recommendation": recommendation,
                "strengths": unique_strengths,
                "areas_for_improvement": unique_improvements,
                "ai_summary": ai_summary,
                "interview_duration": self._calculate_interview_duration(session_data),
                "response_quality_trend": self._analyze_response_trend(responses),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return final_evaluation
            
        except Exception as e:
            logger.error(f"Final evaluation generation error: {str(e)}")
            return {"overall_score": 0, "recommendation": "Review Required"}

    async def _generate_hiring_recommendation(self, overall_score: float, category_scores: Dict[str, float], session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate hiring recommendation based on scores"""
        try:
            interview_type = session_data.get("interview_type", "")
            job_info = session_data.get("metadata", {}).get("job_info", {})
            
            # Scoring thresholds
            thresholds = {
                "strong_hire": 85,
                "hire": 75,
                "maybe": 60,
                "no_hire": 0
            }
            
            # Determine recommendation
            if overall_score >= thresholds["strong_hire"]:
                recommendation = "Strong Hire"
                confidence = "High"
            elif overall_score >= thresholds["hire"]:
                recommendation = "Hire"
                confidence = "Medium-High"
            elif overall_score >= thresholds["maybe"]:
                recommendation = "Maybe"
                confidence = "Medium"
            else:
                recommendation = "No Hire"
                confidence = "High"
            
            # Additional considerations
            considerations = []
            
            # Check for red flags
            if any(score < 40 for score in category_scores.values()):
                considerations.append("Significant weakness in key areas")
                if recommendation in ["Strong Hire", "Hire"]:
                    recommendation = "Maybe"
                    confidence = "Low"
            
            # Check for exceptional performance
            if any(score >= 90 for score in category_scores.values()):
                considerations.append("Exceptional performance in key areas")
            
            return {
                "recommendation": recommendation,
                "confidence": confidence,
                "reasoning": f"Based on overall score of {overall_score:.1f}/100",
                "considerations": considerations,
                "next_steps": self._suggest_next_steps(recommendation, category_scores)
            }
            
        except Exception as e:
            logger.error(f"Hiring recommendation error: {str(e)}")
            return {"recommendation": "Review Required", "confidence": "Low"}

    def _suggest_next_steps(self, recommendation: str, category_scores: Dict[str, float]) -> List[str]:
        """Suggest next steps based on recommendation"""
        next_steps = []
        
        if recommendation == "Strong Hire":
            next_steps = [
                "Proceed with offer preparation",
                "Conduct reference checks",
                "Schedule final discussion with hiring manager"
            ]
        elif recommendation == "Hire":
            next_steps = [
                "Conduct additional technical assessment if needed",
                "Reference checks",
                "Hiring manager review"
            ]
        elif recommendation == "Maybe":
            next_steps = [
                "Additional interview round recommended",
                "Focus on weak areas identified",
                "Consider alternative role if available"
            ]
        else:  # No Hire
            next_steps = [
                "Send polite rejection email",
                "Provide constructive feedback if requested",
                "Keep profile for future opportunities"
            ]
        
        return next_steps

    async def _generate_ai_evaluation_summary(self, session_data: Dict[str, Any], overall_score: float, category_scores: Dict[str, float]) -> str:
        """Generate AI-powered evaluation summary"""
        try:
            interview_type = session_data.get("interview_type", "")
            candidate_info = session_data.get("metadata", {}).get("candidate_info", {})
            job_info = session_data.get("metadata", {}).get("job_info", {})
            
            prompt = f"""
            Generate a comprehensive interview evaluation summary:
            
            Interview Details:
            - Type: {interview_type}
            - Overall Score: {overall_score:.1f}/100
            - Category Scores: {json.dumps(category_scores, indent=2)}
            
            Candidate Background: {candidate_info.get('background', 'Not provided')}
            Job Role: {job_info.get('title', 'Not specified')}
            
            Provide a professional evaluation summary including:
            1. Overall performance assessment
            2. Key strengths demonstrated
            3. Areas needing development
            4. Fit for the role
            5. Specific recommendations
            
            Keep it professional and constructive, around 200-250 words.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert HR professional providing interview evaluations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI evaluation summary error: {str(e)}")
            return f"Interview completed with overall score of {overall_score:.1f}/100. Detailed analysis available in the evaluation report."

    def _calculate_interview_duration(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate interview duration"""
        try:
            started_at = datetime.fromisoformat(session_data.get("started_at", ""))
            completed_at = datetime.fromisoformat(session_data.get("completed_at", datetime.utcnow().isoformat()))
            
            duration = completed_at - started_at
            duration_minutes = duration.total_seconds() / 60
            
            return {
                "total_minutes": duration_minutes,
                "formatted_duration": f"{int(duration_minutes // 60)}h {int(duration_minutes % 60)}m",
                "started_at": session_data.get("started_at"),
                "completed_at": session_data.get("completed_at")
            }
            
        except Exception as e:
            logger.error(f"Duration calculation error: {str(e)}")
            return {"total_minutes": 0, "formatted_duration": "Unknown"}

    def _analyze_response_trend(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trend in response quality"""
        try:
            scores = [response.get("analysis", {}).get("overall_score", 0) for response in responses]
            
            if len(scores) < 2:
                return {"trend": "insufficient_data"}
            
            # Calculate trend
            first_half = scores[:len(scores)//2]
            second_half = scores[len(scores)//2:]
            
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            improvement = second_avg - first_avg
            
            if improvement > 10:
                trend = "improving"
            elif improvement < -10:
                trend = "declining"
            else:
                trend = "consistent"
            
            return {
                "trend": trend,
                "improvement": improvement,
                "first_half_average": first_avg,
                "second_half_average": second_avg,
                "score_progression": scores
            }
            
        except Exception as e:
            logger.error(f"Response trend analysis error: {str(e)}")
            return {"trend": "unknown"}

    # Helper methods for session management
    async def _get_candidate_info(self, candidate_id: str) -> Dict[str, Any]:
        """Get candidate information"""
        try:
            db = SessionLocal()
            candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
            db.close()
            
            if candidate:
                return {
                    "id": candidate.id,
                    "name": candidate.name,
                    "email": candidate.email,
                    "background": f"Candidate applying for position, current status: {candidate.status}"
                }
            return {}
        except Exception as e:
            logger.error(f"Candidate info retrieval error: {str(e)}")
            return {}

    async def _get_job_info(self, job_id: str) -> Dict[str, Any]:
        """Get job information"""
        try:
            db = SessionLocal()
            job = db.query(Job).filter(Job.id == job_id).first()
            db.close()
            
            if job:
                return {
                    "id": job.id,
                    "title": job.title,
                    "description": job.description,
                    "requirements": job.requirements
                }
            return {}
        except Exception as e:
            logger.error(f"Job info retrieval error: {str(e)}")
            return {}

    def _determine_difficulty_level(self, candidate_info: Dict[str, Any]) -> str:
        """Determine interview difficulty level based on candidate background"""
        # Simplified logic - would be more sophisticated in practice
        return "intermediate"

    async def _generate_welcome_message(self, session_data: Dict[str, Any]) -> str:
        """Generate personalized welcome message"""
        try:
            candidate_name = session_data.get("metadata", {}).get("candidate_info", {}).get("name", "Candidate")
            interview_type = session_data.get("interview_type", "")
            job_title = session_data.get("metadata", {}).get("job_info", {}).get("title", "this position")
            
            welcome_messages = {
                "technical": f"Hello {candidate_name}! Welcome to your technical interview for {job_title}. I'm your AI interviewer, and I'll be assessing your technical skills, problem-solving abilities, and coding expertise. We'll cover various technical topics relevant to the role. Are you ready to begin?",
                "behavioral": f"Hi {candidate_name}! I'm excited to learn more about your professional experiences and how you handle various workplace situations. This behavioral interview will help us understand your soft skills, leadership qualities, and cultural fit for {job_title}. Shall we get started?",
                "comprehensive": f"Welcome {candidate_name}! I'll be conducting a comprehensive interview covering both technical and behavioral aspects for the {job_title} position. We'll discuss your technical expertise, past experiences, and how you approach various challenges. Ready to begin?",
                "screening": f"Hello {candidate_name}! This is a brief screening interview for {job_title}. I'll ask you a few questions to understand your background and basic qualifications. Let's get started!"
            }
            
            return welcome_messages.get(interview_type, f"Welcome {candidate_name}! I'm your AI interviewer. Are you ready to begin?")
            
        except Exception as e:
            logger.error(f"Welcome message generation error: {str(e)}")
            return "Welcome to your interview! I'm your AI interviewer. Are you ready to begin?"

    async def _get_current_question(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get current question from session"""
        try:
            questions = session_data.get("questions", [])
            current_index = session_data.get("current_question_index", 0)
            
            if current_index < len(questions):
                return questions[current_index]
            return {}
        except Exception as e:
            logger.error(f"Current question retrieval error: {str(e)}")
            return {}

    async def _store_session(self, session_data: Dict[str, Any]):
        """Store session in databases"""
        try:
            # Store in SQL
            db = SessionLocal()
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
            db.add(interview_session)
            db.commit()
            db.close()
            
            # Store detailed data in MongoDB
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.interview_sessions.insert_one(session_data)
            
        except Exception as e:
            logger.error(f"Session storage error: {str(e)}")
            raise

    async def _get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data from MongoDB"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            session_data = await mongo_db.interview_sessions.find_one({"id": session_id})
            return session_data
        except Exception as e:
            logger.error(f"Session retrieval error: {str(e)}")
            return None

    async def _update_session(self, session_data: Dict[str, Any]):
        """Update session in databases"""
        try:
            # Update SQL
            db = SessionLocal()
            interview_session = db.query(InterviewSession).filter(InterviewSession.id == session_data["id"]).first()
            if interview_session:
                interview_session.status = session_data["status"]
                interview_session.overall_score = session_data["evaluation"]["overall_score"]
                if session_data.get("completed_at"):
                    interview_session.completed_at = datetime.fromisoformat(session_data["completed_at"])
                db.commit()
            db.close()
            
            # Update MongoDB
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.interview_sessions.replace_one(
                {"id": session_data["id"]},
                session_data
            )
            
        except Exception as e:
            logger.error(f"Session update error: {str(e)}")

    async def _update_evaluation_scores(self, session_data: Dict[str, Any], analysis: Dict[str, Any]):
        """Update evaluation scores in session"""
        try:
            evaluation = session_data["evaluation"]
            scores = analysis.get("scores", {})
            
            # Update individual scores
            for aspect, score in scores.items():
                if aspect not in evaluation["scores"]:
                    evaluation["scores"][aspect] = []
                evaluation["scores"][aspect].append(score)
            
            # Calculate running overall score
            all_response_scores = [resp.get("analysis", {}).get("overall_score", 0) for resp in session_data.get("responses", [])]
            if all_response_scores:
                evaluation["overall_score"] = sum(all_response_scores) / len(all_response_scores)
            
        except Exception as e:
            logger.error(f"Evaluation score update error: {str(e)}")

    # Public methods for external access
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current session status"""
        try:
            session_data = await self._get_session_data(session_id)
            if not session_data:
                return {"error": "Session not found"}
            
            return {
                "session_id": session_id,
                "status": session_data.get("status"),
                "progress": {
                    "current_question": session_data.get("current_question_index", 0) + 1,
                    "total_questions": len(session_data.get("questions", [])),
                    "completion_percentage": ((session_data.get("current_question_index", 0) + 1) / len(session_data.get("questions", []))) * 100
                },
                "current_scores": session_data.get("evaluation", {}).get("scores", {}),
                "overall_score": session_data.get("evaluation", {}).get("overall_score", 0)
            }
            
        except Exception as e:
            logger.error(f"Session status retrieval error: {str(e)}")
            return {"error": str(e)}

    async def get_interview_report(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive interview report"""
        try:
            session_data = await self._get_session_data(session_id)
            if not session_data:
                return {"error": "Session not found"}
            
            if session_data.get("status") != "completed":
                return {"error": "Interview not completed yet"}
            
            return session_data.get("evaluation", {}).get("final_report", {})
            
        except Exception as e:
            logger.error(f"Interview report retrieval error: {str(e)}")
            return {"error": str(e)}

    async def end_interview_session(self, session_id: str, reason: str = "completed") -> Dict[str, Any]:
        """End interview session manually"""
        try:
            session_data = await self._get_session_data(session_id)
            if not session_data:
                return {"error": "Session not found"}
            
            session_data["status"] = "ended"
            session_data["end_reason"] = reason
            session_data["completed_at"] = datetime.utcnow().isoformat()
            
            # Generate final evaluation even if incomplete
            final_evaluation = await self._generate_final_evaluation(session_data)
            session_data["evaluation"]["final_report"] = final_evaluation
            
            await self._update_session(session_data)
            
            return {
                "message": "Interview session ended successfully",
                "final_evaluation": final_evaluation
            }
            
        except Exception as e:
            logger.error(f"Interview session end error: {str(e)}")
            return {"error": str(e)}
