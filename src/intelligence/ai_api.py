"""
Laniakea Protocol - AI API Integration
لایه انتزاعی برای تعامل با مدل‌های زبان بزرگ (LLM)
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional, List
from enum import Enum
from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from datetime import datetime

# تنظیمات OpenAI Client
# از متغیرهای محیطی که در sandbox تنظیم شده‌اند استفاده می‌شود
try:
    client = OpenAI()
    async_client = AsyncOpenAI()
except Exception as e:
    print(f"Error initializing OpenAI clients: {e}")
    client = None
    async_client = None

class LLMProvider(str, Enum):
    """ارائه‌دهندگان LLM"""
    GEMINI_FLASH = "gemini-2.5-flash"
    GPT_MINI = "gpt-4.1-mini"
    GPT_NANO = "gpt-4.1-nano"

class AI_API:
    """
    کلاس اصلی برای تعامل با LLM ها
    """
    
    def __init__(self):
        self.default_model = LLMProvider.GEMINI_FLASH.value
        self.stats = {
            "total_calls": 0,
            "last_call": None
        }

    def generate_text_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> str:
        """
        تولید متن به صورت همزمان (Synchronous)
        """
        if not client:
            return json.dumps({"error": "OpenAI client not initialized"})
            
        self.stats["total_calls"] += 1
        self.stats["last_call"] = datetime.now().isoformat()
        
        model_name = model if model else self.default_model
        
        messages: List[ChatCompletionMessageParam] = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            content = response.choices[0].message.content
            if content is None:
                print(f"❌ LLM API Error ({model_name}): Content is None")
                return json.dumps({"error": "LLM generation failed: Content is None"})
            return content.strip()
            
        except Exception as e:
            print(f"❌ LLM API Error ({model_name}): {e}")
            return json.dumps({"error": f"LLM generation failed: {e}"})

    async def generate_text_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> str:
        """
        تولید متن به صورت ناهمزمان (Asynchronous)
        """
        if not async_client:
            return json.dumps({"error": "OpenAI async client not initialized"})
            
        self.stats["total_calls"] += 1
        self.stats["last_call"] = datetime.now().isoformat()
        
        model_name = model if model else self.default_model
        
        messages: List[ChatCompletionMessageParam] = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await async_client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            content = response.choices[0].message.content
            if content is None:
                print(f"❌ LLM API Error ({model_name}): Content is None")
                return json.dumps({"error": "LLM generation failed: Content is None"})
            return content.strip()
            
        except Exception as e:
            print(f"❌ LLM API Error ({model_name}): {e}")
            return json.dumps({"error": f"LLM generation failed: {e}"})

    def get_stats(self) -> Dict[str, Any]:
        """دریافت آمار API"""
        return self.stats

# Singleton
_ai_api: Optional[AI_API] = None

def get_ai_api() -> AI_API:
    """دریافت نمونه Singleton از AI_API"""
    global _ai_api
    if _ai_api is None:
        _ai_api = AI_API()
    return _ai_api

# نصب کتابخانه openai در صورت نیاز
try:
    import openai
except ImportError:
    print("Installing openai library...")
    os.system("pip3 install openai")
    import openai

from enum import Enum # برای تعریف LLMProvider
