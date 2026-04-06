"""
LLM Client - Real OpenAI/Claude integration for HR agent logic
Handles all AI model interactions across the system
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any, AsyncGenerator
from enum import Enum
from datetime import datetime
import asyncio

try:
    from openai import AsyncOpenAI, OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from backend.utils.config import settings

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    CLAUDE = "claude"
    GROQ = "groq"


class LLMConfig:
    """Configuration for LLM clients"""
    def __init__(
        self,
        provider: LLMProvider = LLMProvider.OPENAI,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = 60,
    ):
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout


class Message:
    """Structured message for LLM"""
    def __init__(self, role: str, content: str, name: Optional[str] = None):
        self.role = role  # "system", "user", "assistant"
        self.content = content
        self.name = name

    def to_dict(self) -> Dict[str, str]:
        msg = {"role": self.role, "content": self.content}
        if self.name:
            msg["name"] = self.name
        return msg


class LLMClient:
    """Real LLM client with support for OpenAI and Claude"""

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self.provider = self.config.provider
        self.model = self.config.model
        
        self._init_clients()
        self.conversation_history: List[Message] = []
        logger.info(f"LLM Client initialized with provider: {self.provider}, model: {self.model}")

    def _init_clients(self):
        """Initialize LLM clients based on configured provider"""
        if self.provider == LLMProvider.OPENAI:
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI SDK not installed. Run: pip install openai")
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            
            self.async_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.sync_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
        elif self.provider == LLMProvider.CLAUDE:
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("Anthropic SDK not installed. Run: pip install anthropic")
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            
            self.async_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.sync_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def add_system_context(self, system_prompt: str):
        """Add system context for conversation"""
        self.conversation_history.insert(0, Message("system", system_prompt))

    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append(Message(role, content))

    async def complete(
        self,
        prompt: str,
        system_context: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Get completion from LLM (async)
        
        Args:
            prompt: User prompt/message
            system_context: Optional system prompt override
            temperature: Optional temperature override
            max_tokens: Optional token limit override
            
        Returns:
            LLM response text
        """
        try:
            messages = []
            
            if system_context:
                messages.append({"role": "system", "content": system_context})
            
            # Add conversation history
            for msg in self.conversation_history:
                messages.append(msg.to_dict())
            
            # Add current prompt
            messages.append({"role": "user", "content": prompt})

            if self.provider == LLMProvider.OPENAI:
                response = await self.async_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature or self.config.temperature,
                    max_tokens=max_tokens or self.config.max_tokens,
                    timeout=self.config.timeout,
                )
                return response.choices[0].message.content
                
            elif self.provider == LLMProvider.CLAUDE:
                sys_msg = system_context or (self.conversation_history[0].content if self.conversation_history[0].role == "system" else None)
                user_messages = [m for m in messages if m["role"] != "system"]
                
                response = await self.async_client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens or self.config.max_tokens,
                    system=sys_msg,
                    messages=user_messages,
                )
                return response.content[0].text
                
        except Exception as e:
            logger.error(f"Error getting LLM completion: {e}")
            raise

    async def stream_complete(
        self,
        prompt: str,
        system_context: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Get streaming completion from LLM
        
        Yields:
            Chunks of response text
        """
        try:
            messages = []
            
            if system_context:
                messages.append({"role": "system", "content": system_context})
            
            for msg in self.conversation_history:
                messages.append(msg.to_dict())
            
            messages.append({"role": "user", "content": prompt})

            if self.provider == LLMProvider.OPENAI:
                with self.sync_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    stream=True,
                ) as stream:
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
                            
        except Exception as e:
            logger.error(f"Error in streaming completion: {e}")
            raise

    def structured_output(
        self,
        prompt: str,
        response_schema: Dict[str, Any],
        system_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get structured JSON output from LLM
        
        Args:
            prompt: User prompt
            response_schema: Expected JSON schema
            system_context: Optional system prompt
            
        Returns:
            Parsed JSON response
        """
        schema_instruction = f"""
        You must respond with valid JSON matching this schema:
        {json.dumps(response_schema, indent=2)}
        """
        
        full_prompt = f"{prompt}\n\n{schema_instruction}"
        
        try:
            response_text = asyncio.run(self.complete(
                full_prompt,
                system_context=system_context
            ))
            
            # Parse JSON from response
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                raise ValueError(f"Could not parse JSON from response: {response_text}")
                
        except Exception as e:
            logger.error(f"Error in structured output: {e}")
            raise

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return [msg.to_dict() for msg in self.conversation_history]


# Global LLM client instance
_llm_client: Optional[LLMClient] = None


def get_llm_client(config: Optional[LLMConfig] = None) -> LLMClient:
    """Get or create global LLM client"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient(config)
    return _llm_client


def reset_llm_client():
    """Reset global LLM client"""
    global _llm_client
    _llm_client = None
