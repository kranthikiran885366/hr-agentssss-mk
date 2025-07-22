"""
Evaluation Engine - Advanced interview response evaluation
Uses multiple AI models and scoring algorithms
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import openai
import spacy
from transformers import pipeline
import torch
from datetime import datetime
import json

from backend.utils.config import settings

logger = logging.getLogger(__name__)

class EvaluationEngine:
    def __init__(self):
        self.is_initialized = False
        self.nlp = None
        self.sentiment_analyzer = None
        self.emotion_classifier = None
        self.coherence_model = None
        self.technical_evaluator = None
        self.behavioral_evaluator = None
        
        # Evaluation criteria and weights
        self.evaluation_criteria = {
            "technical_competency": {
                "weight": 0.35,
                "sub_criteria": {
                    "accuracy": 0.4,
                    "depth": 0.3,
                    "best_practices": 0.2,
                    "problem_solving": 0.1
                }
            },
            "communication": {
                "weight": 0.25,
                "sub_criteria": {
                    "clarity": 0.3,
                    "articulation": 0.25,
                    "structure": 0.25,
                    "vocabulary": 0.2
                }
            },
            "behavioral_competency": {
                "weight": 0.20,
                "sub_criteria": {
                    "star_method": 0.3,
                    "leadership": 0.25,
                    "teamwork": 0.25,
                    "adaptability": 0.2
                }
            },
            "cultural_fit": {
                "weight": 0.15,
                "sub_criteria": {
                    "values_alignment": 0.4,
                    "motivation": 0.3,
                    "attitude": 0.3
                }
            },
            "relevance": {
                "weight": 0.05,
                "sub_criteria": {
                    "question_relevance": 0.6,
                    "completeness": 0.4
                }
            }
        }

    async def initialize(self):
        """Initialize evaluation models and components"""
        try:
            logger.info("Initializing Evaluation Engine...")
            
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
            
            # Initialize specialized evaluators
            self.technical_evaluator = TechnicalEvaluator()
            self.behavioral_evaluator = BehavioralEvaluator()
            
            await self.technical_evaluator.initialize()
            await self.behavioral_evaluator.initialize()
            
            self.is_initialized = True
            logger.info("Evaluation Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Evaluation Engine: {str(e)}")
            raise

    async def evaluate_response(self, response: str, question: Dict[str, Any], 
                              context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Comprehensive response evaluation"""
        try:
            evaluation = {
                "response_id": context.get("response_id", "unknown"),
                "timestamp": datetime.utcnow().isoformat(),
                "question_category": question.get("category", "general"),
                "scores": {},
                "detailed_analysis": {},
                "strengths": [],
                "improvements": [],
                "overall_score": 0.0,
                "confidence": 0.0
            }
            
            # Basic text analysis
            evaluation["detailed_analysis"]["text_metrics"] = await self._analyze_text_metrics(response)
            
            # Sentiment and emotion analysis
            evaluation["detailed_analysis"]["sentiment"] = await self._analyze_sentiment(response)
            evaluation["detailed_analysis"]["emotion"] = await self._analyze_emotion(response)
            
            # Communication quality analysis
            evaluation["detailed_analysis"]["communication"] = await self._evaluate_communication_quality(response)
            
            # Relevance analysis
            evaluation["detailed_analysis"]["relevance"] = await self._evaluate_relevance(response, question)
            
            # Category-specific evaluation
            if question.get("category") in ["technical", "problem_solving"]:
                evaluation["detailed_analysis"]["technical"] = await self.technical_evaluator.evaluate(response, question)
            
            if question.get("category") in ["behavioral", "cultural_fit"]:
                evaluation["detailed_analysis"]["behavioral"] = await self.behavioral_evaluator.evaluate(response, question)
            
            # Calculate individual scores
            evaluation["scores"] = await self._calculate_scores(evaluation["detailed_analysis"], question)
            
            # Calculate overall score
            evaluation["overall_score"] = await self._calculate_overall_score(evaluation["scores"], question)
            
            # Generate strengths and improvements
            evaluation["strengths"], evaluation["improvements"] = await self._generate_feedback(evaluation)
            
            # Calculate confidence in evaluation
            evaluation["confidence"] = await self._calculate_evaluation_confidence(evaluation)
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Response evaluation error: {str(e)}")
            return {"overall_score": 0.0, "error": str(e)}

    async def _analyze_text_metrics(self, response: str) -> Dict[str, Any]:
        """Analyze basic text metrics"""
        try:
            doc = self.nlp(response)
            
            # Basic counts
            words = [token.text for token in doc if not token.is_space]
            sentences = list(doc.sents)
            
            # Advanced metrics
            unique_words = len(set(word.lower() for word in words if word.isalpha()))
            avg_word_length = np.mean([len(word) for word in words if word.isalpha()])
            avg_sentence_length = len(words) / max(len(sentences), 1)
            
            # Readability metrics
            syllable_count = sum(self._count_syllables(word) for word in words if word.isalpha())
            flesch_score = self._calculate_flesch_score(len(words), len(sentences), syllable_count)
            
            # Linguistic complexity
            pos_tags = [token.pos_ for token in doc]
            pos_diversity = len(set(pos_tags)) / max(len(pos_tags), 1)
            
            return {
                "word_count": len(words),
                "sentence_count": len(sentences),
                "unique_words": unique_words,
                "vocabulary_richness": unique_words / max(len(words), 1),
                "avg_word_length": avg_word_length,
                "avg_sentence_length": avg_sentence_length,
                "flesch_readability": flesch_score,
                "pos_diversity": pos_diversity,
                "character_count": len(response),
                "complexity_score": self._calculate_complexity_score(doc)
            }
            
        except Exception as e:
            logger.error(f"Text metrics analysis error: {str(e)}")
            return {}

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)"""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent e
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(syllable_count, 1)

    def _calculate_flesch_score(self, words: int, sentences: int, syllables: int) -> float:
        """Calculate Flesch readability score"""
        if sentences == 0 or words == 0:
            return 0.0
        
        avg_sentence_length = words / sentences
        avg_syllables_per_word = syllables / words
        
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        return max(0.0, min(100.0, score))

    def _calculate_complexity_score(self, doc) -> float:
        """Calculate linguistic complexity score"""
        try:
            # Count complex structures
            complex_structures = 0
            
            for token in doc:
                # Subordinate clauses
                if token.dep_ in ["advcl", "acl", "relcl"]:
                    complex_structures += 1
                
                # Passive voice
                if token.dep_ == "auxpass":
                    complex_structures += 1
                
                # Complex verb forms
                if token.pos_ == "VERB" and len(token.text) > 6:
                    complex_structures += 1
            
            # Normalize by sentence count
            sentence_count = len(list(doc.sents))
            complexity_score = (complex_structures / max(sentence_count, 1)) * 20
            
            return min(complexity_score, 100.0)
            
        except Exception as e:
            logger.error(f"Complexity calculation error: {str(e)}")
            return 50.0

    async def _analyze_sentiment(self, response: str) -> Dict[str, Any]:
        """Analyze sentiment with detailed breakdown"""
        try:
            # Overall sentiment
            sentiment_result = self.sentiment_analyzer(response)
            
            # Sentence-level sentiment
            sentences = response.split('.')
            sentence_sentiments = []
            
            for sentence in sentences[:5]:  # Limit to first 5 sentences
                if sentence.strip():
                    sent_result = self.sentiment_analyzer(sentence.strip())
                    sentence_sentiments.append({
                        "text": sentence.strip()[:100],
                        "sentiment": sent_result[0]["label"],
                        "score": sent_result[0]["score"]
                    })
            
            # Calculate sentiment consistency
            sentiment_scores = [s["score"] for s in sentence_sentiments]
            sentiment_consistency = 1.0 - np.std(sentiment_scores) if sentiment_scores else 1.0
            
            return {
                "overall_sentiment": sentiment_result[0]["label"],
                "overall_score": sentiment_result[0]["score"],
                "sentence_sentiments": sentence_sentiments,
                "sentiment_consistency": sentiment_consistency,
                "positive_indicators": self._count_positive_indicators(response),
                "negative_indicators": self._count_negative_indicators(response)
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return {"overall_sentiment": "NEUTRAL", "overall_score": 0.5}

    def _count_positive_indicators(self, response: str) -> int:
        """Count positive language indicators"""
        positive_words = [
            "excellent", "great", "successful", "achieved", "improved", "effective",
            "confident", "passionate", "excited", "love", "enjoy", "proud"
        ]
        response_lower = response.lower()
        return sum(1 for word in positive_words if word in response_lower)

    def _count_negative_indicators(self, response: str) -> int:
        """Count negative language indicators"""
        negative_words = [
            "difficult", "challenging", "failed", "problem", "issue", "struggle",
            "worried", "concerned", "frustrated", "disappointed"
        ]
        response_lower = response.lower()
        return sum(1 for word in negative_words if word in response_lower)

    async def _analyze_emotion(self, response: str) -> Dict[str, Any]:
        """Analyze emotional content"""
        try:
            emotion_result = self.emotion_classifier(response)
            
            # Get all emotion scores
            all_emotions = {result["label"]: result["score"] for result in emotion_result}
            
            # Determine dominant emotion
            dominant_emotion = max(all_emotions.items(), key=lambda x: x[1])
            
            # Calculate emotional intensity
            emotion_scores = list(all_emotions.values())
            emotional_intensity = max(emotion_scores) - min(emotion_scores)
            
            return {
                "dominant_emotion": dominant_emotion[0],
                "emotion_confidence": dominant_emotion[1],
                "all_emotions": all_emotions,
                "emotional_intensity": emotional_intensity,
                "emotional_stability": 1.0 - np.std(emotion_scores)
            }
            
        except Exception as e:
            logger.error(f"Emotion analysis error: {str(e)}")
            return {"dominant_emotion": "neutral", "emotion_confidence": 0.5}

    async def _evaluate_communication_quality(self, response: str) -> Dict[str, Any]:
        """Evaluate communication quality comprehensively"""
        try:
            doc = self.nlp(response)
            
            # Clarity assessment
            clarity_score = await self._assess_clarity(response, doc)
            
            # Structure assessment
            structure_score = await self._assess_structure(response, doc)
            
            # Articulation assessment
            articulation_score = await self._assess_articulation(response, doc)
            
            # Vocabulary assessment
            vocabulary_score = await self._assess_vocabulary(response, doc)
            
            # Coherence assessment
            coherence_score = await self._assess_coherence(response, doc)
            
            # Overall communication score
            communication_scores = {
                "clarity": clarity_score,
                "structure": structure_score,
                "articulation": articulation_score,
                "vocabulary": vocabulary_score,
                "coherence": coherence_score
            }
            
            weights = self.evaluation_criteria["communication"]["sub_criteria"]
            overall_communication = sum(
                score * weights.get(aspect, 0.2) 
                for aspect, score in communication_scores.items()
            )
            
            return {
                **communication_scores,
                "overall_communication_score": overall_communication,
                "communication_level": self._categorize_communication_level(overall_communication)
            }
            
        except Exception as e:
            logger.error(f"Communication quality evaluation error: {str(e)}")
            return {"overall_communication_score": 50.0}

    async def _assess_clarity(self, response: str, doc) -> float:
        """Assess clarity of communication"""
        try:
            clarity_indicators = {
                "clear_sentences": 0,
                "ambiguous_phrases": 0,
                "filler_words": 0,
                "concrete_examples": 0
            }
            
            # Check for filler words
            filler_words = ["um", "uh", "like", "you know", "sort of", "kind of"]
            response_lower = response.lower()
            clarity_indicators["filler_words"] = sum(
                response_lower.count(filler) for filler in filler_words
            )
            
            # Check for concrete examples
            example_indicators = ["for example", "such as", "like when", "instance"]
            clarity_indicators["concrete_examples"] = sum(
                1 for indicator in example_indicators if indicator in response_lower
            )
            
            # Check sentence clarity
            sentences = list(doc.sents)
            for sent in sentences:
                # Simple heuristic: shorter sentences with clear structure
                if 5 <= len(sent) <= 25:  # Reasonable sentence length
                    clarity_indicators["clear_sentences"] += 1
                elif len(sent) > 30:
                    clarity_indicators["ambiguous_phrases"] += 1
            
            # Calculate clarity score
            total_sentences = len(sentences)
            if total_sentences == 0:
                return 50.0
            
            clear_ratio = clarity_indicators["clear_sentences"] / total_sentences
            filler_penalty = min(clarity_indicators["filler_words"] * 5, 30)
            example_bonus = min(clarity_indicators["concrete_examples"] * 10, 20)
            
            clarity_score = (clear_ratio * 80) + example_bonus - filler_penalty
            return max(0.0, min(100.0, clarity_score))
            
        except Exception as e:
            logger.error(f"Clarity assessment error: {str(e)}")
            return 50.0

    async def _assess_structure(self, response: str, doc) -> float:
        """Assess structural organization of response"""
        try:
            structure_indicators = {
                "logical_flow": 0,
                "transitions": 0,
                "introduction": 0,
                "conclusion": 0,
                "organization": 0
            }
            
            # Check for transition words
            transition_words = [
                "first", "second", "then", "next", "finally", "however", "therefore",
                "because", "since", "although", "moreover", "furthermore", "in addition"
            ]
            
            response_lower = response.lower()
            structure_indicators["transitions"] = sum(
                1 for word in transition_words if word in response_lower
            )
            
            # Check for introduction patterns
            intro_patterns = ["let me start", "to begin", "first of all", "initially"]
            structure_indicators["introduction"] = sum(
                1 for pattern in intro_patterns if pattern in response_lower
            )
            
            # Check for conclusion patterns
            conclusion_patterns = ["in conclusion", "to summarize", "finally", "overall"]
            structure_indicators["conclusion"] = sum(
                1 for pattern in conclusion_patterns if pattern in response_lower
            )
            
            # Check logical flow (simplified)
            sentences = list(doc.sents)
            if len(sentences) >= 3:
                # Check if sentences build upon each other
                structure_indicators["logical_flow"] = 1
                structure_indicators["organization"] = 1
            
            # Calculate structure score
            base_score = 50
            transition_bonus = min(structure_indicators["transitions"] * 10, 30)
            intro_bonus = structure_indicators["introduction"] * 10
            conclusion_bonus = structure_indicators["conclusion"] * 10
            flow_bonus = structure_indicators["logical_flow"] * 20
            
            structure_score = base_score + transition_bonus + intro_bonus + conclusion_bonus + flow_bonus
            return max(0.0, min(100.0, structure_score))
            
        except Exception as e:
            logger.error(f"Structure assessment error: {str(e)}")
            return 50.0

    async def _assess_articulation(self, response: str, doc) -> float:
        """Assess articulation quality"""
        try:
            # Check for proper grammar and syntax
            grammar_errors = 0
            for token in doc:
                # Simple grammar checks
                if token.dep_ == "ROOT" and token.pos_ not in ["VERB", "AUX"]:
                    grammar_errors += 1
            
            # Check for repetitive language
            words = [token.text.lower() for token in doc if token.is_alpha]
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            repetition_score = sum(1 for freq in word_freq.values() if freq > 3)
            
            # Check for varied sentence structures
            sentence_lengths = [len(sent) for sent in doc.sents]
            length_variety = np.std(sentence_lengths) if sentence_lengths else 0
            
            # Calculate articulation score
            base_score = 80
            grammar_penalty = min(grammar_errors * 5, 30)
            repetition_penalty = min(repetition_score * 3, 20)
            variety_bonus = min(length_variety * 2, 15)
            
            articulation_score = base_score - grammar_penalty - repetition_penalty + variety_bonus
            return max(0.0, min(100.0, articulation_score))
            
        except Exception as e:
            logger.error(f"Articulation assessment error: {str(e)}")
            return 50.0

    async def _assess_vocabulary(self, response: str, doc) -> float:
        """Assess vocabulary richness and appropriateness"""
        try:
            words = [token.text.lower() for token in doc if token.is_alpha and len(token.text) > 2]
            
            if not words:
                return 0.0
            
            # Vocabulary richness (Type-Token Ratio)
            unique_words = len(set(words))
            total_words = len(words)
            ttr = unique_words / total_words
            
            # Advanced vocabulary indicators
            advanced_words = 0
            for token in doc:
                if len(token.text) > 7 and token.is_alpha:  # Longer words often more sophisticated
                    advanced_words += 1
            
            # Professional vocabulary
            professional_terms = [
                "implement", "analyze", "optimize", "collaborate", "facilitate",
                "coordinate", "strategic", "innovative", "efficient", "comprehensive"
            ]
            
            professional_count = sum(
                1 for term in professional_terms if term in response.lower()
            )
            
            # Calculate vocabulary score
            ttr_score = min(ttr * 150, 70)  # TTR typically 0.4-0.6 for good vocabulary
            advanced_bonus = min(advanced_words * 2, 20)
            professional_bonus = min(professional_count * 5, 15)
            
            vocabulary_score = ttr_score + advanced_bonus + professional_bonus
            return max(0.0, min(100.0, vocabulary_score))
            
        except Exception as e:
            logger.error(f"Vocabulary assessment error: {str(e)}")
            return 50.0

    async def _assess_coherence(self, response: str, doc) -> float:
        """Assess coherence and logical flow"""
        try:
            sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
            
            if len(sentences) < 2:
                return 70.0  # Single sentence responses are moderately coherent
            
            # Calculate semantic similarity between consecutive sentences
            similarities = []
            
            for i in range(len(sentences) - 1):
                # Simple word overlap method (could be enhanced with embeddings)
                words1 = set(sentences[i].lower().split())
                words2 = set(sentences[i + 1].lower().split())
                
                overlap = len(words1 & words2)
                union = len(words1 | words2)
                
                if union > 0:
                    similarity = overlap / union
                    similarities.append(similarity)
            
            if not similarities:
                return 50.0
            
            # Calculate coherence score
            avg_similarity = np.mean(similarities)
            coherence_score = min(avg_similarity * 200, 100)  # Scale to 0-100
            
            # Bonus for logical connectors
            connectors = ["because", "therefore", "however", "moreover", "furthermore"]
            connector_count = sum(1 for conn in connectors if conn in response.lower())
            connector_bonus = min(connector_count * 5, 15)
            
            final_coherence = coherence_score + connector_bonus
            return max(30.0, min(100.0, final_coherence))  # Minimum coherence of 30
            
        except Exception as e:
            logger.error(f"Coherence assessment error: {str(e)}")
            return 50.0

    def _categorize_communication_level(self, score: float) -> str:
        """Categorize communication level"""
        if score >= 85:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "satisfactory"
        elif score >= 45:
            return "needs_improvement"
        else:
            return "poor"

    async def _evaluate_relevance(self, response: str, question: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate response relevance to question"""
        try:
            question_text = question.get("text", "")
            question_keywords = question.get("keywords", [])
            
            # Keyword relevance
            response_lower = response.lower()
            keyword_matches = sum(1 for keyword in question_keywords if keyword.lower() in response_lower)
            keyword_relevance = (keyword_matches / max(len(question_keywords), 1)) * 100
            
            # Semantic relevance (simplified)
            question_words = set(question_text.lower().split())
            response_words = set(response.lower().split())
            
            # Remove stop words
            stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
            question_words -= stop_words
            response_words -= stop_words
            
            word_overlap = len(question_words & response_words)
            semantic_relevance = (word_overlap / max(len(question_words), 1)) * 100
            
            # Completeness check
            expected_duration = question.get("expected_duration", 120)
            response_length = len(response.split())
            expected_length = expected_duration / 2  # Rough estimate: 2 seconds per word
            
            completeness = min((response_length / max(expected_length, 1)) * 100, 100)
            
            # Combined relevance score
            relevance_weights = {"keyword": 0.4, "semantic": 0.4, "completeness": 0.2}
            overall_relevance = (
                keyword_relevance * relevance_weights["keyword"] +
                semantic_relevance * relevance_weights["semantic"] +
                completeness * relevance_weights["completeness"]
            )
            
            return {
                "keyword_relevance": keyword_relevance,
                "semantic_relevance": semantic_relevance,
                "completeness": completeness,
                "overall_relevance": overall_relevance,
                "relevance_category": self._categorize_relevance(overall_relevance)
            }
            
        except Exception as e:
            logger.error(f"Relevance evaluation error: {str(e)}")
            return {"overall_relevance": 50.0, "relevance_category": "moderate"}

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

    async def _calculate_scores(self, detailed_analysis: Dict[str, Any], question: Dict[str, Any]) -> Dict[str, float]:
        """Calculate individual aspect scores"""
        try:
            scores = {}
            
            # Communication score
            communication_data = detailed_analysis.get("communication", {})
            scores["communication"] = communication_data.get("overall_communication_score", 50.0)
            
            # Relevance score
            relevance_data = detailed_analysis.get("relevance", {})
            scores["relevance"] = relevance_data.get("overall_relevance", 50.0)
            
            # Technical competency (if applicable)
            if question.get("category") in ["technical", "problem_solving"]:
                technical_data = detailed_analysis.get("technical", {})
                scores["technical_competency"] = technical_data.get("overall_score", 50.0)
            
            # Behavioral competency (if applicable)
            if question.get("category") in ["behavioral", "cultural_fit"]:
                behavioral_data = detailed_analysis.get("behavioral", {})
                scores["behavioral_competency"] = behavioral_data.get("overall_score", 50.0)
            
            # Cultural fit score
            sentiment_data = detailed_analysis.get("sentiment", {})
            emotion_data = detailed_analysis.get("emotion", {})
            
            # Convert sentiment to cultural fit score
            sentiment_score = sentiment_data.get("overall_score", 0.5) * 100
            if sentiment_data.get("overall_sentiment") == "NEGATIVE":
                sentiment_score = 100 - sentiment_score
            
            # Emotion contribution to cultural fit
            positive_emotions = ["joy", "optimism", "confidence"]
            emotion_score = 75.0  # Default
            if emotion_data.get("dominant_emotion") in positive_emotions:
                emotion_score = 85.0
            elif emotion_data.get("dominant_emotion") in ["anger", "fear", "sadness"]:
                emotion_score = 40.0
            
            scores["cultural_fit"] = (sentiment_score * 0.6) + (emotion_score * 0.4)
            
            return scores
            
        except Exception as e:
            logger.error(f"Score calculation error: {str(e)}")
            return {"overall": 50.0}

    async def _calculate_overall_score(self, scores: Dict[str, float], question: Dict[str, Any]) -> float:
        """Calculate weighted overall score"""
        try:
            if not scores:
                return 0.0
            
            # Get weights based on question category
            question_category = question.get("category", "general")
            
            # Adjust weights based on question type
            if question_category in ["technical", "problem_solving"]:
                weights = {
                    "technical_competency": 0.5,
                    "communication": 0.3,
                    "relevance": 0.15,
                    "cultural_fit": 0.05
                }
            elif question_category in ["behavioral", "cultural_fit"]:
                weights = {
                    "behavioral_competency": 0.4,
                    "communication": 0.3,
                    "cultural_fit": 0.2,
                    "relevance": 0.1
                }
            else:
                # Default weights
                weights = self.evaluation_criteria
                weights = {k: v["weight"] for k, v in weights.items()}
            
            # Calculate weighted score
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
            
            return max(0.0, min(100.0, overall_score))
            
        except Exception as e:
            logger.error(f"Overall score calculation error: {str(e)}")
            return 50.0

    async def _generate_feedback(self, evaluation: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Generate strengths and improvement suggestions"""
        try:
            strengths = []
            improvements = []
            
            scores = evaluation.get("scores", {})
            detailed_analysis = evaluation.get("detailed_analysis", {})
            
            # Analyze each aspect
            for aspect, score in scores.items():
                if score >= 80:
                    strengths.append(f"Strong {aspect.replace('_', ' ')}")
                elif score < 60:
                    improvements.append(f"Improve {aspect.replace('_', ' ')}")
            
            # Specific feedback based on detailed analysis
            communication_data = detailed_analysis.get("communication", {})
            
            # Communication-specific feedback
            if communication_data.get("vocabulary", 0) >= 80:
                strengths.append("Rich vocabulary and professional language")
            elif communication_data.get("vocabulary", 0) < 50:
                improvements.append("Use more varied and professional vocabulary")
            
            if communication_data.get("structure", 0) >= 80:
                strengths.append("Well-structured and organized response")
            elif communication_data.get("structure", 0) < 50:
                improvements.append("Organize responses with clear structure and transitions")
            
            # Technical feedback (if applicable)
            technical_data = detailed_analysis.get("technical", {})
            if technical_data:
                if technical_data.get("depth_score", 0) >= 80:
                    strengths.append("Demonstrates deep technical understanding")
                elif technical_data.get("depth_score", 0) < 50:
                    improvements.append("Provide more technical depth and specific examples")
            
            # Behavioral feedback (if applicable)
            behavioral_data = detailed_analysis.get("behavioral", {})
            if behavioral_data:
                star_score = behavioral_data.get("star_completeness", 0)
                if star_score >= 75:
                    strengths.append("Excellent use of STAR method in behavioral responses")
                elif star_score < 50:
                    improvements.append("Use STAR method (Situation, Task, Action, Result) for behavioral questions")
            
            # Relevance feedback
            relevance_data = detailed_analysis.get("relevance", {})
            if relevance_data.get("overall_relevance", 0) < 60:
                improvements.append("Ensure responses directly address the question asked")
            
            # Limit feedback items
            return strengths[:4], improvements[:4]
            
        except Exception as e:
            logger.error(f"Feedback generation error: {str(e)}")
            return [], []

    async def _calculate_evaluation_confidence(self, evaluation: Dict[str, Any]) -> float:
        """Calculate confidence in the evaluation"""
        try:
            confidence_factors = []
            
            # Response length factor
            text_metrics = evaluation.get("detailed_analysis", {}).get("text_metrics", {})
            word_count = text_metrics.get("word_count", 0)
            
            if word_count >= 50:
                confidence_factors.append(0.9)
            elif word_count >= 20:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.4)
            
            # Analysis completeness factor
            detailed_analysis = evaluation.get("detailed_analysis", {})
            analysis_components = len(detailed_analysis)
            
            if analysis_components >= 4:
                confidence_factors.append(0.9)
            elif analysis_components >= 2:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            # Score consistency factor
            scores = list(evaluation.get("scores", {}).values())
            if scores:
                score_std = np.std(scores)
                if score_std <= 15:  # Consistent scores
                    confidence_factors.append(0.9)
                elif score_std <= 25:
                    confidence_factors.append(0.7)
                else:
                    confidence_factors.append(0.5)
            
            # Overall confidence
            overall_confidence = np.mean(confidence_factors) if confidence_factors else 0.5
            return overall_confidence
            
        except Exception as e:
            logger.error(f"Confidence calculation error: {str(e)}")
            return 0.5

    async def batch_evaluate_responses(self, responses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate multiple responses in batch"""
        try:
            evaluations = []
            
            # Process responses in parallel
            tasks = []
            for response_data in responses:
                task = self.evaluate_response(
                    response=response_data.get("response", ""),
                    question=response_data.get("question", {}),
                    context=response_data.get("context", {})
                )
                tasks.append(task)
            
            evaluations = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions
            for i, evaluation in enumerate(evaluations):
                if isinstance(evaluation, Exception):
                    logger.error(f"Batch evaluation error for response {i}: {str(evaluation)}")
                    evaluations[i] = {"overall_score": 0.0, "error": str(evaluation)}
            
            return evaluations
            
        except Exception as e:
            logger.error(f"Batch evaluation error: {str(e)}")
            return [{"overall_score": 0.0, "error": str(e)} for _ in responses]

    def get_evaluation_statistics(self) -> Dict[str, Any]:
        """Get evaluation engine statistics"""
        try:
            return {
                "criteria_count": len(self.evaluation_criteria),
                "evaluation_criteria": self.evaluation_criteria,
                "supported_categories": ["technical", "behavioral", "cultural_fit", "general"],
                "confidence_factors": ["response_length", "analysis_completeness", "score_consistency"],
                "scoring_range": {"min": 0.0, "max": 100.0}
            }
        except Exception as e:
            logger.error(f"Statistics generation error: {str(e)}")
            return {"error": str(e)}


class TechnicalEvaluator:
    """Specialized evaluator for technical responses"""
    
    def __init__(self):
        self.is_initialized = False
        self.technical_keywords = {}
        self.complexity_patterns = {}
    
    async def initialize(self):
        """Initialize technical evaluator"""
        try:
            # Load technical keyword databases
            self.technical_keywords = {
                "programming": [
                    "algorithm", "data structure", "complexity", "optimization", "recursion",
                    "iteration", "polymorphism", "inheritance", "encapsulation", "abstraction"
                ],
                "system_design": [
                    "scalability", "load balancing", "caching", "database", "microservices",
                    "api", "rest", "graphql", "architecture", "distributed"
                ],
                "best_practices": [
                    "testing", "documentation", "code review", "version control", "ci/cd",
                    "security", "performance", "maintainability", "clean code"
                ]
            }
            
            self.is_initialized = True
            
        except Exception as e:
            logger.error(f"Technical evaluator initialization error: {str(e)}")
            raise
    
    async def evaluate(self, response: str, question: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate technical response"""
        try:
            evaluation = {
                "accuracy_score": await self._assess_technical_accuracy(response, question),
                "depth_score": await self._assess_technical_depth(response),
                "best_practices_score": await self._assess_best_practices(response),
                "problem_solving_score": await self._assess_problem_solving(response),
                "overall_score": 0.0
            }
            
            # Calculate overall technical score
            weights = {"accuracy": 0.4, "depth": 0.3, "best_practices": 0.2, "problem_solving": 0.1}
            evaluation["overall_score"] = sum(
                evaluation[f"{key}_score"] * weight 
                for key, weight in weights.items()
            )
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Technical evaluation error: {str(e)}")
            return {"overall_score": 50.0}

    async def _assess_technical_accuracy(self, response: str, question: Dict[str, Any]) -> float:
        """Assess technical accuracy using AI"""
        try:
            prompt = f"""
            Evaluate the technical accuracy of this response on a scale of 0-100:
            
            Question: {question.get('text', '')}
            Response: {response}
            
            Consider:
            1. Factual correctness
            2. Proper use of technical terminology
            3. Logical reasoning
            4. Industry best practices
            
            Return only a number between 0-100.
            """
            
            response_obj = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a technical expert evaluating responses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            score_text = response_obj.choices[0].message.content.strip()
            return float(score_text) if score_text.replace('.', '').isdigit() else 50.0
            
        except Exception as e:
            logger.error(f"Technical accuracy assessment error: {str(e)}")
            return 50.0

    async def _assess_technical_depth(self, response: str) -> float:
        """Assess technical depth of response"""
        try:
            response_lower = response.lower()
            depth_indicators = {
                "specific_examples": 0,
                "technical_terms": 0,
                "implementation_details": 0,
                "trade_offs": 0
            }
            
            # Check for specific examples
            example_phrases = ["for example", "such as", "like when", "in my experience"]
            depth_indicators["specific_examples"] = sum(
                1 for phrase in example_phrases if phrase in response_lower
            )
            
            # Count technical terms
            all_technical_terms = []
            for category_terms in self.technical_keywords.values():
                all_technical_terms.extend(category_terms)
            
            depth_indicators["technical_terms"] = sum(
                1 for term in all_technical_terms if term in response_lower
            )
            
            # Check for implementation details
            implementation_words = ["implement", "code", "function", "method", "class", "variable"]
            depth_indicators["implementation_details"] = sum(
                1 for word in implementation_words if word in response_lower
            )
            
            # Check for trade-off discussions
            tradeoff_words = ["trade-off", "pros and cons", "advantage", "disadvantage", "however"]
            depth_indicators["trade_offs"] = sum(
                1 for word in tradeoff_words if word in response_lower
            )
            
            # Calculate depth score
            base_score = 40
            example_bonus = min(depth_indicators["specific_examples"] * 15, 30)
            technical_bonus = min(depth_indicators["technical_terms"] * 5, 25)
            implementation_bonus = min(depth_indicators["implementation_details"] * 8, 20)
            tradeoff_bonus = min(depth_indicators["trade_offs"] * 10, 15)
            
            depth_score = base_score + example_bonus + technical_bonus + implementation_bonus + tradeoff_bonus
            return min(depth_score, 100.0)
            
        except Exception as e:
            logger.error(f"Technical depth assessment error: {str(e)}")
            return 50.0

    async def _assess_best_practices(self, response: str) -> float:
        """Assess mention of best practices"""
        try:
            response_lower = response.lower()
            best_practice_terms = self.technical_keywords.get("best_practices", [])
            
            mentioned_practices = sum(
                1 for practice in best_practice_terms if practice in response_lower
            )
            
            # Additional best practice indicators
            additional_practices = [
                "clean code", "solid principles", "dry principle", "kiss principle",
                "code smell", "refactoring", "design pattern", "architecture pattern"
            ]
            
            additional_mentions = sum(
                1 for practice in additional_practices if practice in response_lower
            )
            
            total_mentions = mentioned_practices + additional_mentions
            best_practices_score = min(total_mentions * 20, 100)
            
            return max(best_practices_score, 30.0)  # Minimum score
            
        except Exception as e:
            logger.error(f"Best practices assessment error: {str(e)}")
            return 50.0

    async def _assess_problem_solving(self, response: str) -> float:
        """Assess problem-solving approach"""
        try:
            response_lower = response.lower()
            problem_solving_indicators = {
                "analysis": ["analyze", "identify", "understand", "break down"],
                "approach": ["approach", "strategy", "method", "solution"],
                "steps": ["first", "then", "next", "finally", "step"],
                "alternatives": ["alternative", "option", "different way", "another approach"]
            }
            
            scores = {}
            for category, indicators in problem_solving_indicators.items():
                score = sum(1 for indicator in indicators if indicator in response_lower)
                scores[category] = min(score * 25, 100)
            
            # Calculate overall problem-solving score
            problem_solving_score = sum(scores.values()) / len(scores)
            return max(problem_solving_score, 40.0)
            
        except Exception as e:
            logger.error(f"Problem solving assessment error: {str(e)}")
            return 50.0


class BehavioralEvaluator:
    """Specialized evaluator for behavioral responses"""
    
    def __init__(self):
        self.is_initialized = False
        self.star_indicators = {}
        self.leadership_indicators = {}
    
    async def initialize(self):
        """Initialize behavioral evaluator"""
        try:
            self.star_indicators = {
                "situation": ["situation", "when", "time", "project", "challenge", "context"],
                "task": ["task", "responsibility", "goal", "objective", "needed", "required"],
                "action": ["action", "did", "implemented", "decided", "approached", "took"],
                "result": ["result", "outcome", "achieved", "improved", "success", "impact"]
            }
            
            self.leadership_indicators = [
                "led", "managed", "coordinated", "mentored", "guided", "influenced",
                "motivated", "inspired", "delegated", "supervised", "directed"
            ]
            
            self.is_initialized = True
            
        except Exception as e:
            logger.error(f"Behavioral evaluator initialization error: {str(e)}")
            raise
    
    async def evaluate(self, response: str, question: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate behavioral response"""
        try:
            evaluation = {
                "star_completeness": await self._assess_star_method(response),
                "leadership_score": await self._assess_leadership(response),
                "teamwork_score": await self._assess_teamwork(response),
                "adaptability_score": await self._assess_adaptability(response),
                "overall_score": 0.0
            }
            
            # Calculate overall behavioral score
            weights = {"star_completeness": 0.3, "leadership": 0.25, "teamwork": 0.25, "adaptability": 0.2}
            evaluation["overall_score"] = sum(
                evaluation[f"{key}_score" if key != "star_completeness" else key] * weight 
                for key, weight in weights.items()
            )
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Behavioral evaluation error: {str(e)}")
            return {"overall_score": 50.0}

    async def _assess_star_method(self, response: str) -> float:
        """Assess STAR method completeness"""
        try:
            response_lower = response.lower()
            star_scores = {}
            
            for component, indicators in self.star_indicators.items():
                score = sum(1 for indicator in indicators if indicator in response_lower)
                star_scores[component] = min(score * 25, 100)
            
            # Calculate completeness
            completeness = sum(star_scores.values()) / len(star_scores)
            return completeness
            
        except Exception as e:
            logger.error(f"STAR method assessment error: {str(e)}")
            return 50.0

    async def _assess_leadership(self, response: str) -> float:
        """Assess leadership indicators"""
        try:
            response_lower = response.lower()
            leadership_mentions = sum(
                1 for indicator in self.leadership_indicators if indicator in response_lower
            )
            
            leadership_score = min(leadership_mentions * 20, 100)
            return max(leadership_score, 30.0)
            
        except Exception as e:
            logger.error(f"Leadership assessment error: {str(e)}")
            return 50.0

    async def _assess_teamwork(self, response: str) -> float:
        """Assess teamwork indicators"""
        try:
            response_lower = response.lower()
            teamwork_indicators = [
                "team", "collaborated", "worked together", "coordinated", "communicated",
                "shared", "supported", "helped", "cooperation", "partnership"
            ]
            
            teamwork_mentions = sum(
                1 for indicator in teamwork_indicators if indicator in response_lower
            )
            
            teamwork_score = min(teamwork_mentions * 15, 100)
            return max(teamwork_score, 30.0)
            
        except Exception as e:
            logger.error(f"Teamwork assessment error: {str(e)}")
            return 50.0

    async def _assess_adaptability(self, response: str) -> float:
        """Assess adaptability indicators"""
        try:
            response_lower = response.lower()
            adaptability_indicators = [
                "adapt", "change", "flexible", "adjust", "learn", "new",
                "different", "challenge", "overcome", "pivot", "evolve"
            ]
            
            adaptability_mentions = sum(
                1 for indicator in adaptability_indicators if indicator in response_lower
            )
            
            adaptability_score = min(adaptability_mentions * 12, 100)
            return max(adaptability_score, 30.0)
            
        except Exception as e:
            logger.error(f"Adaptability assessment error: {str(e)}")
            return 50.0
