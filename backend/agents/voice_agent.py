"""
Voice Agent - Real speech-to-text and text-to-speech processing
Integrates with cloud services for voice processing
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, BinaryIO
import io
import wave
import json
from datetime import datetime
import uuid
import aiofiles
import aiohttp
import base64

# Cloud TTS/STT services
import azure.cognitiveservices.speech as speechsdk
from google.cloud import speech as google_speech
from google.cloud import texttospeech as google_tts
import openai

from backend.utils.config import settings

logger = logging.getLogger(__name__)

class VoiceAgent:
    def __init__(self):
        self.is_initialized = False
        self.azure_speech_config = None
        self.google_speech_client = None
        self.google_tts_client = None
        self.supported_languages = [
            "en-US", "en-GB", "es-ES", "fr-FR", "de-DE", "it-IT", "pt-BR", "hi-IN"
        ]
        self.voice_profiles = {}

    async def initialize(self):
        """Initialize voice processing services"""
        try:
            logger.info("Initializing Voice Agent...")
            
            # Initialize Azure Speech Services
            if settings.AZURE_SPEECH_KEY and settings.AZURE_SPEECH_REGION:
                self.azure_speech_config = speechsdk.SpeechConfig(
                    subscription=settings.AZURE_SPEECH_KEY,
                    region=settings.AZURE_SPEECH_REGION
                )
                self.azure_speech_config.speech_recognition_language = "en-US"
            
            # Initialize Google Cloud Speech
            if settings.GOOGLE_CLOUD_CREDENTIALS:
                self.google_speech_client = google_speech.SpeechClient()
                self.google_tts_client = google_tts.TextToSpeechClient()
            
            # Initialize OpenAI for Whisper
            if settings.OPENAI_API_KEY:
                openai.api_key = settings.OPENAI_API_KEY
            
            # Load voice profiles
            await self._load_voice_profiles()
            
            self.is_initialized = True
            logger.info("Voice Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Voice Agent: {str(e)}")
            raise

    def is_ready(self) -> bool:
        """Check if agent is ready"""
        return self.is_initialized

    async def _load_voice_profiles(self):
        """Load available voice profiles for different languages"""
        self.voice_profiles = {
            "en-US": {
                "neural": ["en-US-AriaNeural", "en-US-JennyNeural", "en-US-GuyNeural"],
                "standard": ["en-US-AriaRUS", "en-US-BenjaminRUS", "en-US-ZiraRUS"]
            },
            "en-GB": {
                "neural": ["en-GB-SoniaNeural", "en-GB-RyanNeural"],
                "standard": ["en-GB-Susan", "en-GB-George"]
            },
            "es-ES": {
                "neural": ["es-ES-ElviraNeural", "es-ES-AlvaroNeural"],
                "standard": ["es-ES-Laura", "es-ES-Pablo"]
            },
            "fr-FR": {
                "neural": ["fr-FR-DeniseNeural", "fr-FR-HenriNeural"],
                "standard": ["fr-FR-Julie", "fr-FR-Paul"]
            },
            "de-DE": {
                "neural": ["de-DE-KatjaNeural", "de-DE-ConradNeural"],
                "standard": ["de-DE-Hedda", "de-DE-Stefan"]
            },
            "hi-IN": {
                "neural": ["hi-IN-SwaraNeural", "hi-IN-MadhurNeural"],
                "standard": ["hi-IN-Kalpana", "hi-IN-Hemant"]
            }
        }

    async def speech_to_text(self, audio_content: bytes, filename: str = None, language: str = "en-US") -> Dict[str, Any]:
        """Convert speech to text using multiple services for best accuracy"""
        try:
            # Try multiple services for best results
            results = []
            
            # Try OpenAI Whisper first (usually most accurate)
            whisper_result = await self._whisper_transcribe(audio_content, filename)
            if whisper_result:
                results.append(whisper_result)
            
            # Try Azure Speech Services
            azure_result = await self._azure_speech_to_text(audio_content, language)
            if azure_result:
                results.append(azure_result)
            
            # Try Google Cloud Speech
            google_result = await self._google_speech_to_text(audio_content, language)
            if google_result:
                results.append(google_result)
            
            # Select best result based on confidence
            best_result = max(results, key=lambda x: x.get("confidence", 0)) if results else None
            
            if not best_result:
                raise Exception("All speech recognition services failed")
            
            # Enhance result with additional analysis
            enhanced_result = await self._enhance_transcription_result(best_result)
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Speech to text error: {str(e)}")
            raise

    async def _whisper_transcribe(self, audio_content: bytes, filename: str = None) -> Optional[Dict[str, Any]]:
        """Transcribe using OpenAI Whisper"""
        try:
            # Save audio to temporary file
            temp_filename = filename or f"temp_audio_{uuid.uuid4()}.wav"
            
            # Convert audio if needed
            audio_file = io.BytesIO(audio_content)
            
            # Use OpenAI Whisper API
            response = await openai.Audio.atranscribe(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json"
            )
            
            return {
                "transcript": response.text,
                "confidence": 0.95,  # Whisper typically has high confidence
                "service": "whisper",
                "language": response.language,
                "duration": response.duration,
                "segments": response.segments if hasattr(response, 'segments') else []
            }
            
        except Exception as e:
            logger.error(f"Whisper transcription error: {str(e)}")
            return None

    async def _azure_speech_to_text(self, audio_content: bytes, language: str) -> Optional[Dict[str, Any]]:
        """Transcribe using Azure Speech Services"""
        try:
            if not self.azure_speech_config:
                return None
            
            # Configure for the specified language
            self.azure_speech_config.speech_recognition_language = language
            
            # Create audio stream
            audio_stream = speechsdk.audio.PushAudioInputStream()
            audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)
            
            # Create speech recognizer
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.azure_speech_config,
                audio_config=audio_config
            )
            
            # Push audio data
            audio_stream.write(audio_content)
            audio_stream.close()
            
            # Perform recognition
            result = speech_recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                # Extract confidence from detailed results
                confidence = 0.8  # Default confidence for Azure
                if hasattr(result, 'properties'):
                    confidence_str = result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult)
                    if confidence_str:
                        try:
                            json_result = json.loads(confidence_str)
                            confidence = json_result.get('NBest', [{}])[0].get('Confidence', 0.8)
                        except:
                            pass
                
                return {
                    "transcript": result.text,
                    "confidence": confidence,
                    "service": "azure",
                    "language": language,
                    "duration": result.duration.total_seconds() if result.duration else 0
                }
            else:
                logger.warning(f"Azure speech recognition failed: {result.reason}")
                return None
                
        except Exception as e:
            logger.error(f"Azure speech to text error: {str(e)}")
            return None

    async def _google_speech_to_text(self, audio_content: bytes, language: str) -> Optional[Dict[str, Any]]:
        """Transcribe using Google Cloud Speech"""
        try:
            if not self.google_speech_client:
                return None
            
            # Configure recognition
            config = google_speech.RecognitionConfig(
                encoding=google_speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=16000,
                language_code=language,
                enable_automatic_punctuation=True,
                enable_word_confidence=True,
                enable_word_time_offsets=True
            )
            
            audio = google_speech.RecognitionAudio(content=audio_content)
            
            # Perform recognition
            response = self.google_speech_client.recognize(config=config, audio=audio)
            
            if response.results:
                result = response.results[0]
                alternative = result.alternatives[0]
                
                return {
                    "transcript": alternative.transcript,
                    "confidence": alternative.confidence,
                    "service": "google",
                    "language": language,
                    "words": [
                        {
                            "word": word.word,
                            "confidence": word.confidence,
                            "start_time": word.start_time.total_seconds(),
                            "end_time": word.end_time.total_seconds()
                        }
                        for word in alternative.words
                    ] if hasattr(alternative, 'words') else []
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Google speech to text error: {str(e)}")
            return None

    async def _enhance_transcription_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance transcription with additional analysis"""
        try:
            transcript = result["transcript"]
            
            # Add metadata
            enhanced_result = {
                **result,
                "word_count": len(transcript.split()),
                "character_count": len(transcript),
                "processed_at": datetime.utcnow().isoformat(),
                "quality_score": await self._assess_transcription_quality(transcript),
                "sentiment": await self._analyze_speech_sentiment(transcript),
                "speaking_rate": await self._calculate_speaking_rate(result),
                "clarity_indicators": await self._analyze_speech_clarity(result)
            }
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Transcription enhancement error: {str(e)}")
            return result

    async def _assess_transcription_quality(self, transcript: str) -> float:
        """Assess the quality of transcription"""
        try:
            # Basic quality indicators
            word_count = len(transcript.split())
            
            # Check for common transcription errors
            error_indicators = ["[inaudible]", "[unclear]", "um", "uh", "..."]
            error_count = sum(transcript.lower().count(indicator) for indicator in error_indicators)
            
            # Calculate quality score
            if word_count == 0:
                return 0.0
            
            error_ratio = error_count / word_count
            quality_score = max(0.0, 1.0 - error_ratio) * 100
            
            return quality_score
            
        except Exception as e:
            logger.error(f"Quality assessment error: {str(e)}")
            return 50.0

    async def _analyze_speech_sentiment(self, transcript: str) -> Dict[str, Any]:
        """Analyze sentiment of spoken content"""
        try:
            # Use a simple sentiment analysis (could be enhanced with specialized models)
            positive_words = ["good", "great", "excellent", "positive", "happy", "confident"]
            negative_words = ["bad", "terrible", "negative", "sad", "worried", "concerned"]
            
            transcript_lower = transcript.lower()
            positive_count = sum(word in transcript_lower for word in positive_words)
            negative_count = sum(word in transcript_lower for word in negative_words)
            
            if positive_count > negative_count:
                sentiment = "positive"
                score = 0.6 + (positive_count - negative_count) * 0.1
            elif negative_count > positive_count:
                sentiment = "negative"
                score = 0.4 - (negative_count - positive_count) * 0.1
            else:
                sentiment = "neutral"
                score = 0.5
            
            return {
                "sentiment": sentiment,
                "score": max(0.0, min(1.0, score)),
                "positive_indicators": positive_count,
                "negative_indicators": negative_count
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return {"sentiment": "neutral", "score": 0.5}

    async def _calculate_speaking_rate(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate speaking rate metrics"""
        try:
            transcript = result["transcript"]
            duration = result.get("duration", 0)
            
            if duration == 0:
                return {"words_per_minute": 0, "rate_category": "unknown"}
            
            word_count = len(transcript.split())
            words_per_minute = (word_count / duration) * 60
            
            # Categorize speaking rate
            if words_per_minute < 120:
                rate_category = "slow"
            elif words_per_minute < 160:
                rate_category = "normal"
            elif words_per_minute < 200:
                rate_category = "fast"
            else:
                rate_category = "very_fast"
            
            return {
                "words_per_minute": words_per_minute,
                "rate_category": rate_category,
                "total_words": word_count,
                "duration_seconds": duration
            }
            
        except Exception as e:
            logger.error(f"Speaking rate calculation error: {str(e)}")
            return {"words_per_minute": 0, "rate_category": "unknown"}

    async def _analyze_speech_clarity(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze speech clarity indicators"""
        try:
            confidence = result.get("confidence", 0.5)
            transcript = result["transcript"]
            
            # Clarity indicators
            clarity_indicators = {
                "high_confidence": confidence > 0.9,
                "medium_confidence": 0.7 <= confidence <= 0.9,
                "low_confidence": confidence < 0.7,
                "has_hesitations": any(word in transcript.lower() for word in ["um", "uh", "er"]),
                "complete_sentences": transcript.count('.') > 0,
                "clear_articulation": confidence > 0.8 and len(transcript.split()) > 5
            }
            
            # Overall clarity score
            clarity_score = confidence * 100
            if clarity_indicators["has_hesitations"]:
                clarity_score -= 10
            if not clarity_indicators["complete_sentences"]:
                clarity_score -= 5
            
            clarity_score = max(0, min(100, clarity_score))
            
            return {
                "clarity_score": clarity_score,
                "indicators": clarity_indicators,
                "overall_assessment": "clear" if clarity_score > 70 else "unclear"
            }
            
        except Exception as e:
            logger.error(f"Clarity analysis error: {str(e)}")
            return {"clarity_score": 50, "overall_assessment": "unknown"}

    async def text_to_speech(self, text: str, voice: str = "en-US-AriaNeural", language: str = "en-US", speed: float = 1.0) -> Dict[str, Any]:
        """Convert text to speech using multiple services"""
        try:
            # Try different TTS services
            results = []
            
            # Try Azure TTS first (usually best quality)
            azure_result = await self._azure_text_to_speech(text, voice, language, speed)
            if azure_result:
                results.append(azure_result)
            
            # Try Google TTS as fallback
            google_result = await self._google_text_to_speech(text, voice, language, speed)
            if google_result:
                results.append(google_result)
            
            # Select best result (prefer Azure for quality)
            best_result = results[0] if results else None
            
            if not best_result:
                raise Exception("All text-to-speech services failed")
            
            # Enhance result with metadata
            enhanced_result = await self._enhance_tts_result(best_result, text)
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Text to speech error: {str(e)}")
            raise

    async def _azure_text_to_speech(self, text: str, voice: str, language: str, speed: float) -> Optional[Dict[str, Any]]:
        """Generate speech using Azure TTS"""
        try:
            if not self.azure_speech_config:
                return None
            
            # Configure voice
            self.azure_speech_config.speech_synthesis_voice_name = voice
            
            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.azure_speech_config,
                audio_config=None  # Return audio data directly
            )
            
            # Create SSML for better control
            ssml = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{language}">
                <voice name="{voice}">
                    <prosody rate="{speed}">
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
            
            # Synthesize speech
            result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                # Save audio to file
                audio_filename = f"tts_output_{uuid.uuid4()}.wav"
                audio_path = f"/tmp/{audio_filename}"
                
                async with aiofiles.open(audio_path, "wb") as f:
                    await f.write(result.audio_data)
                
                return {
                    "audio_data": result.audio_data,
                    "audio_path": audio_path,
                    "audio_filename": audio_filename,
                    "service": "azure",
                    "voice": voice,
                    "language": language,
                    "duration": len(result.audio_data) / 32000,  # Approximate duration
                    "format": "wav"
                }
            else:
                logger.warning(f"Azure TTS failed: {result.reason}")
                return None
                
        except Exception as e:
            logger.error(f"Azure TTS error: {str(e)}")
            return None

    async def _google_text_to_speech(self, text: str, voice: str, language: str, speed: float) -> Optional[Dict[str, Any]]:
        """Generate speech using Google Cloud TTS"""
        try:
            if not self.google_tts_client:
                return None
            
            # Configure synthesis input
            synthesis_input = google_tts.SynthesisInput(text=text)
            
            # Map voice name to Google format
            google_voice_name = self._map_voice_to_google(voice, language)
            
            # Configure voice
            voice_config = google_tts.VoiceSelectionParams(
                language_code=language,
                name=google_voice_name,
                ssml_gender=google_tts.SsmlVoiceGender.NEUTRAL
            )
            
            # Configure audio
            audio_config = google_tts.AudioConfig(
                audio_encoding=google_tts.AudioEncoding.MP3,
                speaking_rate=speed
            )
            
            # Synthesize speech
            response = self.google_tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice_config,
                audio_config=audio_config
            )
            
            # Save audio to file
            audio_filename = f"tts_output_{uuid.uuid4()}.mp3"
            audio_path = f"/tmp/{audio_filename}"
            
            async with aiofiles.open(audio_path, "wb") as f:
                await f.write(response.audio_content)
            
            return {
                "audio_data": response.audio_content,
                "audio_path": audio_path,
                "audio_filename": audio_filename,
                "service": "google",
                "voice": google_voice_name,
                "language": language,
                "duration": len(response.audio_content) / 24000,  # Approximate duration
                "format": "mp3"
            }
            
        except Exception as e:
            logger.error(f"Google TTS error: {str(e)}")
            return None

    def _map_voice_to_google(self, voice: str, language: str) -> str:
        """Map Azure voice names to Google voice names"""
        google_voice_mapping = {
            "en-US-AriaNeural": "en-US-Wavenet-F",
            "en-US-JennyNeural": "en-US-Wavenet-G",
            "en-US-GuyNeural": "en-US-Wavenet-B",
            "en-GB-SoniaNeural": "en-GB-Wavenet-A",
            "en-GB-RyanNeural": "en-GB-Wavenet-B",
            "es-ES-ElviraNeural": "es-ES-Wavenet-A",
            "fr-FR-DeniseNeural": "fr-FR-Wavenet-A",
            "de-DE-KatjaNeural": "de-DE-Wavenet-A",
            "hi-IN-SwaraNeural": "hi-IN-Wavenet-A"
        }
        
        return google_voice_mapping.get(voice, f"{language}-Wavenet-A")

    async def _enhance_tts_result(self, result: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """Enhance TTS result with additional metadata"""
        try:
            enhanced_result = {
                **result,
                "original_text": original_text,
                "text_length": len(original_text),
                "word_count": len(original_text.split()),
                "estimated_speaking_time": len(original_text.split()) / 150 * 60,  # Assuming 150 WPM
                "generated_at": datetime.utcnow().isoformat(),
                "audio_url": f"/api/voice/audio/{result['audio_filename']}",
                "quality_metrics": await self._assess_tts_quality(result)
            }
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"TTS enhancement error: {str(e)}")
            return result

    async def _assess_tts_quality(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess TTS output quality"""
        try:
            # Basic quality metrics
            audio_size = len(result.get("audio_data", b""))
            duration = result.get("duration", 0)
            
            # Quality indicators
            quality_metrics = {
                "audio_size_kb": audio_size / 1024,
                "bitrate_estimate": (audio_size * 8) / max(duration, 1) / 1000,  # kbps
                "service_quality": {
                    "azure": 95,
                    "google": 90,
                    "openai": 85
                }.get(result.get("service", "unknown"), 70),
                "format_quality": {
                    "wav": 100,
                    "mp3": 85,
                    "ogg": 80
                }.get(result.get("format", "unknown"), 70)
            }
            
            # Overall quality score
            overall_quality = (
                quality_metrics["service_quality"] * 0.6 +
                quality_metrics["format_quality"] * 0.4
            )
            
            quality_metrics["overall_quality"] = overall_quality
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"TTS quality assessment error: {str(e)}")
            return {"overall_quality": 70}

    async def get_available_voices(self, language: str = None) -> Dict[str, List[str]]:
        """Get available voices for TTS"""
        try:
            if language:
                return {language: self.voice_profiles.get(language, [])}
            else:
                return self.voice_profiles
                
        except Exception as e:
            logger.error(f"Voice listing error: {str(e)}")
            return {}

    async def analyze_voice_characteristics(self, audio_content: bytes) -> Dict[str, Any]:
        """Analyze voice characteristics from audio"""
        try:
            # First transcribe to get basic info
            transcription = await self.speech_to_text(audio_content)
            
            # Analyze voice characteristics
            characteristics = {
                "transcription_confidence": transcription.get("confidence", 0),
                "speaking_rate": transcription.get("speaking_rate", {}),
                "clarity": transcription.get("clarity_indicators", {}),
                "sentiment": transcription.get("sentiment", {}),
                "voice_quality": await self._analyze_voice_quality(audio_content),
                "emotional_tone": await self._analyze_emotional_tone(transcription.get("transcript", "")),
                "communication_style": await self._analyze_communication_style(transcription.get("transcript", ""))
            }
            
            return characteristics
            
        except Exception as e:
            logger.error(f"Voice analysis error: {str(e)}")
            return {}

    async def _analyze_voice_quality(self, audio_content: bytes) -> Dict[str, Any]:
        """Analyze technical voice quality"""
        try:
            # Basic audio analysis (would use audio processing libraries in production)
            audio_size = len(audio_content)
            
            # Placeholder analysis (would use actual audio processing)
            quality_metrics = {
                "volume_level": "normal",  # Would analyze actual volume
                "background_noise": "low",  # Would detect noise levels
                "audio_clarity": "high" if audio_size > 10000 else "medium",
                "technical_quality_score": min(100, audio_size / 1000)
            }
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Voice quality analysis error: {str(e)}")
            return {}

    async def _analyze_emotional_tone(self, transcript: str) -> Dict[str, Any]:
        """Analyze emotional tone from transcript"""
        try:
            # Emotional indicators
            emotions = {
                "enthusiasm": ["excited", "amazing", "fantastic", "love", "passionate"],
                "confidence": ["confident", "sure", "definitely", "absolutely", "certain"],
                "nervousness": ["nervous", "worried", "anxious", "unsure", "maybe"],
                "professionalism": ["professional", "experience", "responsible", "dedicated"],
                "friendliness": ["friendly", "team", "collaborate", "help", "support"]
            }
            
            transcript_lower = transcript.lower()
            emotion_scores = {}
            
            for emotion, indicators in emotions.items():
                score = sum(1 for indicator in indicators if indicator in transcript_lower)
                emotion_scores[emotion] = min(100, score * 20)  # Scale to 0-100
            
            # Determine dominant emotion
            dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1]) if emotion_scores else ("neutral", 50)
            
            return {
                "emotion_scores": emotion_scores,
                "dominant_emotion": dominant_emotion[0],
                "emotional_intensity": dominant_emotion[1],
                "overall_tone": "positive" if dominant_emotion[1] > 60 else "neutral"
            }
            
        except Exception as e:
            logger.error(f"Emotional tone analysis error: {str(e)}")
            return {}

    async def _analyze_communication_style(self, transcript: str) -> Dict[str, Any]:
        """Analyze communication style from transcript"""
        try:
            # Communication style indicators
            style_indicators = {
                "direct": ["directly", "simply", "clearly", "straightforward"],
                "detailed": ["specifically", "particularly", "detailed", "comprehensive"],
                "collaborative": ["we", "team", "together", "collaborate"],
                "analytical": ["analyze", "consider", "evaluate", "assess"],
                "creative": ["innovative", "creative", "unique", "original"]
            }
            
            transcript_lower = transcript.lower()
            style_scores = {}
            
            for style, indicators in style_indicators.items():
                score = sum(1 for indicator in indicators if indicator in transcript_lower)
                style_scores[style] = score
            
            # Determine communication style
            dominant_style = max(style_scores.items(), key=lambda x: x[1]) if style_scores else ("balanced", 0)
            
            # Additional metrics
            sentence_count = len(transcript.split('.'))
            word_count = len(transcript.split())
            avg_sentence_length = word_count / max(sentence_count, 1)
            
            return {
                "style_scores": style_scores,
                "dominant_style": dominant_style[0],
                "communication_complexity": "complex" if avg_sentence_length > 20 else "simple",
                "verbosity": "verbose" if word_count > 100 else "concise",
                "structure": "structured" if sentence_count > 3 else "informal"
            }
            
        except Exception as e:
            logger.error(f"Communication style analysis error: {str(e)}")
            return {}

    async def create_voice_profile(self, user_id: str, audio_samples: List[bytes]) -> Dict[str, Any]:
        """Create a voice profile for a user"""
        try:
            # Analyze multiple audio samples
            profile_data = {
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "samples_analyzed": len(audio_samples),
                "characteristics": [],
                "average_metrics": {}
            }
            
            # Analyze each sample
            for i, audio_content in enumerate(audio_samples):
                characteristics = await self.analyze_voice_characteristics(audio_content)
                profile_data["characteristics"].append({
                    "sample_id": i + 1,
                    "characteristics": characteristics
                })
            
            # Calculate average metrics
            if profile_data["characteristics"]:
                profile_data["average_metrics"] = await self._calculate_average_voice_metrics(
                    profile_data["characteristics"]
                )
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Voice profile creation error: {str(e)}")
            return {}

    async def _calculate_average_voice_metrics(self, characteristics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate average voice metrics from multiple samples"""
        try:
            if not characteristics_list:
                return {}
            
            # Aggregate metrics
            total_confidence = 0
            total_clarity = 0
            emotion_counts = {}
            style_counts = {}
            
            for char_data in characteristics_list:
                char = char_data["characteristics"]
                
                # Confidence
                total_confidence += char.get("transcription_confidence", 0)
                
                # Clarity
                clarity_score = char.get("clarity", {}).get("clarity_score", 0)
                total_clarity += clarity_score
                
                # Emotions
                emotions = char.get("emotional_tone", {}).get("emotion_scores", {})
                for emotion, score in emotions.items():
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + score
                
                # Communication styles
                styles = char.get("communication_style", {}).get("style_scores", {})
                for style, score in styles.items():
                    style_counts[style] = style_counts.get(style, 0) + score
            
            sample_count = len(characteristics_list)
            
            # Calculate averages
            average_metrics = {
                "average_confidence": total_confidence / sample_count,
                "average_clarity": total_clarity / sample_count,
                "dominant_emotions": {
                    emotion: score / sample_count
                    for emotion, score in emotion_counts.items()
                },
                "communication_styles": {
                    style: score / sample_count
                    for style, score in style_counts.items()
                },
                "voice_consistency": await self._calculate_voice_consistency(characteristics_list)
            }
            
            return average_metrics
            
        except Exception as e:
            logger.error(f"Average metrics calculation error: {str(e)}")
            return {}

    async def _calculate_voice_consistency(self, characteristics_list: List[Dict[str, Any]]) -> float:
        """Calculate how consistent the voice characteristics are across samples"""
        try:
            if len(characteristics_list) < 2:
                return 100.0  # Perfect consistency with single sample
            
            # Compare confidence scores across samples
            confidences = [
                char_data["characteristics"].get("transcription_confidence", 0)
                for char_data in characteristics_list
            ]
            
            # Calculate standard deviation
            mean_confidence = sum(confidences) / len(confidences)
            variance = sum((x - mean_confidence) ** 2 for x in confidences) / len(confidences)
            std_dev = variance ** 0.5
            
            # Convert to consistency score (lower std_dev = higher consistency)
            consistency_score = max(0, 100 - (std_dev * 100))
            
            return consistency_score
            
        except Exception as e:
            logger.error(f"Voice consistency calculation error: {str(e)}")
            return 50.0
