"""
Laniakea Protocol - AI API Module
ماژول API هوش مصنوعی برای تعامل با مدل‌های زبان بزرگ
"""

import os
from typing import Dict, Any, Optional, List
from openai import OpenAI, AsyncOpenAI

# کلاینت OpenAI به صورت خودکار از متغیرهای محیطی استفاده می‌کند
# OPENAI_API_KEY, OPENAI_BASE_URL

class AI_API:
    """
    یک کلاینت یکپارچه برای تعامل با مدل‌های زبان بزرگ مختلف
    که از فرمت API OpenAI پشتیبانی می‌کنند (مانند Gemini, GPT-4, و غیره).
    """
    
    def __init__(self, model: str = "gemini-2.5-flash"):
        """
        Args:
            model: مدل پیش‌فرض برای استفاده (مثلاً 'gemini-2.5-flash', 'gpt-4.1-mini')
        """
        self.default_model = model
        
        try:
            self.client = AsyncOpenAI()
            self.sync_client = OpenAI()
            print(f"🤖 AI API client initialized for model 	'{self.default_model}	'")
        except Exception as e:
            print(f"🔥 Failed to initialize AI API client: {e}")
            self.client = None
            self.sync_client = None

    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1500,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        تولید متن با استفاده از مدل زبان
        
        Args:
            prompt: متن ورودی برای مدل
            model: نام مدل برای استفاده (در صورت عدم تعیین، از پیش‌فرض استفاده می‌شود)
            max_tokens: حداکثر تعداد توکن‌های خروجی
            temperature: میزان خلاقیت (0.0 تا 1.0)
            system_prompt: دستورالعمل سیستمی برای مدل
        
        Returns:
            متن تولید شده یا None در صورت خطا
        """
        if not self.client:
            return None

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error during text generation: {e}")
            return None

    def generate_text_sync(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1500,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        نسخه همزمان (sync) تولید متن
        """
        if not self.sync_client:
            return None

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.sync_client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error during sync text generation: {e}")
            return None

    async def analyze_code(
        self,
        code: str,
        language: str = "python"
    ) -> Optional[Dict[str, Any]]:
        """
        تحلیل یک قطعه کد
        
        Args:
            code: کد برای تحلیل
            language: زبان برنامه‌نویسی
        
        Returns:
            یک دیکشنری شامل تحلیل کد یا None
        """
        system_prompt = f"You are a code analysis expert. Analyze the following {language} code. Provide a JSON response with fields: 'quality_score' (0-100), 'suggestions' (list of strings), 'complexity' (string: 'low', 'medium', 'high'), and 'summary' (string)."
        
        response_text = await self.generate_text(
            prompt=code,
            system_prompt=system_prompt,
            temperature=0.2
        )
        
        if response_text:
            try:
                import json
                return json.loads(response_text)
            except json.JSONDecodeError:
                print("Failed to parse AI response as JSON")
                return {"summary": response_text}
        return None

# Singleton instance
_ai_api_instance = None

def get_ai_api() -> AI_API:
    """
    دریافت instance یکتای AI_API
    """
    global _ai_api_instance
    if _ai_api_instance is None:
        _ai_api_instance = AI_API()
    return _ai_api_instance
