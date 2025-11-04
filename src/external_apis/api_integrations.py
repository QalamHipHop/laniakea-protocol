"""
Laniakea Protocol - External API Integrations (Enhanced)
یکپارچگی با API های خارجی با منطق Cache و Retry
"""

import os
import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime, timedelta
from functools import wraps

# --- Cache Mechanism (Simple In-Memory) ---
API_CACHE: Dict[str, Any] = {}
CACHE_DURATION = timedelta(hours=1)

def cache_result(key_prefix: str, duration: timedelta = CACHE_DURATION):
    """دکوراتور برای کش کردن نتایج API"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # ساخت کلید کش بر اساس نام تابع و آرگومان‌ها
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args[1:]) # skip self
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            # بررسی کش
            if cache_key in API_CACHE:
                timestamp, data = API_CACHE[cache_key]
                if datetime.now() - timestamp < duration:
                    # print(f"Cache hit for {cache_key}")
                    return data
                # print(f"Cache expired for {cache_key}")

            # اجرای تابع
            result = await func(*args, **kwargs)
            
            # ذخیره در کش
            if result and not result.get("error"):
                API_CACHE[cache_key] = (datetime.now(), result)
            
            return result
        return wrapper
    return decorator

# --- Retry Mechanism ---
async def fetch_with_retry(session: aiohttp.ClientSession, url: str, params: Dict[str, Any], max_retries: int = 3):
    """درخواست HTTP با منطق تلاش مجدد"""
    for attempt in range(max_retries):
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429: # Rate Limit
                    print(f"Rate limit hit. Retrying in {2**attempt} seconds...")
                    await asyncio.sleep(2**attempt)
                    continue
                else:
                    return {"error": f"Status {response.status}", "detail": await response.text()}
        except aiohttp.ClientError as e:
            print(f"Connection error: {e}. Retrying in {2**attempt} seconds...")
            await asyncio.sleep(2**attempt)
    return {"error": "Max retries exceeded"}


class APIProvider(str, Enum):
    """ارائه‌دهندگان API"""
    NASA = "nasa"
    WEATHER = "weather"
    FINANCIAL = "financial"
    WOLFRAM = "wolfram"
    NEWS = "news"
    ARXIV = "arxiv"
    WIKIPEDIA = "wikipedia"
    # اضافه شدن API های جدید
    QUANTUM_COMPUTING = "quantum_computing" # برای داده‌های کوانتومی
    GEOSPATIAL = "geospatial" # برای داده‌های مکانی دقیق


class NASAClient:
    """
    کلاینت NASA APIs
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("NASA_API_KEY", "DEMO_KEY")
        self.base_url = "https://api.nasa.gov"
    
    @cache_result("nasa_apod")
    async def get_apod(self, date: Optional[str] = None) -> Dict[str, Any]:
        """دریافت تصویر نجومی روز"""
        url = f"{self.base_url}/planetary/apod"
        params = {"api_key": self.api_key}
        if date:
            params["date"] = date
        
        async with aiohttp.ClientSession() as session:
            return await fetch_with_retry(session, url, params)
    
    @cache_result("nasa_neo")
    async def get_near_earth_objects(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """دریافت اجرام نزدیک به زمین"""
        url = f"{self.base_url}/neo/rest/v1/feed"
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "api_key": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            return await fetch_with_retry(session, url, params)
    
    @cache_result("nasa_mars_rover", duration=timedelta(days=1))
    async def get_mars_rover_photos(
        self,
        rover: str = "curiosity",
        sol: int = 1000,
        camera: Optional[str] = None
    ) -> Dict[str, Any]:
        """دریافت تصاویر مریخ‌نورد"""
        url = f"{self.base_url}/mars-photos/api/v1/rovers/{rover}/photos"
        params = {
            "sol": sol,
            "api_key": self.api_key
        }
        if camera:
            params["camera"] = camera
        
        async with aiohttp.ClientSession() as session:
            return await fetch_with_retry(session, url, params)


class WeatherClient:
    """کلاینت OpenWeatherMap API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    @cache_result("weather_current", duration=timedelta(minutes=10))
    async def get_current_weather(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Dict[str, Any]:
        """دریافت آب و هوای فعلی"""
        if not self.api_key:
            return {"error": "API key not configured"}
        
        url = f"{self.base_url}/weather"
        params = {
            "appid": self.api_key,
            "units": "metric"
        }
        
        if city:
            params["q"] = city
        elif lat and lon:
            params["lat"] = lat
            params["lon"] = lon
        else:
            return {"error": "City or coordinates required"}
        
        async with aiohttp.ClientSession() as session:
            return await fetch_with_retry(session, url, params)
    
    @cache_result("weather_forecast", duration=timedelta(hours=3))
    async def get_forecast(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Dict[str, Any]:
        """دریافت پیش‌بینی 5 روزه"""
        if not self.api_key:
            return {"error": "API key not configured"}
        
        url = f"{self.base_url}/forecast"
        params = {
            "appid": self.api_key,
            "units": "metric"
        }
        
        if city:
            params["q"] = city
        elif lat and lon:
            params["lat"] = lat
            params["lon"] = lon
        else:
            return {"error": "City or coordinates required"}
        
        async with aiohttp.ClientSession() as session:
            return await fetch_with_retry(session, url, params)


class FinancialClient:
    """کلاینت Alpha Vantage API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ALPHAVANTAGE_API_KEY")
        self.base_url = "https://www.alphavantage.co/query"
    
    @cache_result("financial_stock", duration=timedelta(hours=4))
    async def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """دریافت قیمت سهام"""
        if not self.api_key:
            return {"error": "API key not configured"}
        
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            return await fetch_with_retry(session, self.base_url, params)
    
    @cache_result("financial_crypto", duration=timedelta(minutes=15))
    async def get_crypto_price(
        self,
        symbol: str = "BTC",
        market: str = "USD"
    ) -> Dict[str, Any]:
        """دریافت قیمت ارز دیجیتال"""
        if not self.api_key:
            return {"error": "API key not configured"}
        
        params = {
            "function": "DIGITAL_CURRENCY_DAILY",
            "symbol": symbol,
            "market": market,
            "apikey": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            return await fetch_with_retry(session, self.base_url, params)
    
    @cache_result("financial_indicator", duration=timedelta(days=1))
    async def get_economic_indicator(
        self,
        indicator: str = "GDP",
        interval: str = "annual"
    ) -> Dict[str, Any]:
        """دریافت شاخص اقتصادی"""
        if not self.api_key:
            return {"error": "API key not configured"}
        
        params = {
            "function": indicator,
            "interval": interval,
            "apikey": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            return await fetch_with_retry(session, self.base_url, params)


class WolframAlphaClient:
    """کلاینت Wolfram Alpha API"""
    
    def __init__(self, app_id: Optional[str] = None):
        self.app_id = app_id or os.getenv("WOLFRAM_APP_ID")
        self.base_url = "http://api.wolframalpha.com/v2/query"
    
    @cache_result("wolfram_query", duration=timedelta(days=7))
    async def query(
        self,
        input_query: str,
        format: str = "plaintext"
    ) -> Dict[str, Any]:
        """اجرای یک کوئری محاسباتی/دانشی"""
        if not self.app_id:
            return {"error": "App ID not configured"}
        
        params = {
            "input": input_query,
            "appid": self.app_id,
            "output": "json",
            "format": format
        }
        
        async with aiohttp.ClientSession() as session:
            # Wolfram Alpha API XML برمی‌گرداند، اما با output=json می‌توان JSON گرفت
            response_data = await fetch_with_retry(session, self.base_url, params)
            
            # پردازش پاسخ JSON Wolfram Alpha
            if response_data and response_data.get("queryresult"):
                return response_data["queryresult"]
            return response_data


class QuantumClient:
    """
    کلاینت شبیه‌سازی کوانتومی (مثلاً IBM Qiskit Runtime یا یک شبیه‌ساز محلی)
    """
    
    def __init__(self):
        # در این نسخه، فقط یک شبیه‌ساز ساده را فرض می‌کنیم
        self.is_ready = True
        
    async def get_quantum_random_number(self, bits: int = 16) -> Dict[str, Any]:
        """شبیه‌سازی تولید عدد تصادفی کوانتومی"""
        await asyncio.sleep(0.1) # شبیه‌سازی تأخیر
        random_int = random.getrandbits(bits)
        return {
            "random_number": random_int,
            "bits": bits,
            "source": "simulated_quantum_randomness"
        }

    async def get_quantum_entanglement_status(self) -> Dict[str, Any]:
        """شبیه‌سازی وضعیت درهم‌تنیدگی کوانتومی"""
        await asyncio.sleep(0.2)
        status = "stable" if random.random() > 0.1 else "decoherence_detected"
        return {
            "status": status,
            "qubits": 5,
            "fidelity": random.uniform(0.8, 0.99)
        }


class APIManager:
    """مدیریت کننده مرکزی API ها"""
    
    def __init__(self):
        self.nasa_client = NASAClient()
        self.weather_client = WeatherClient()
        self.financial_client = FinancialClient()
        self.wolfram_client = WolframAlphaClient()
        self.quantum_client = QuantumClient()
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "last_reset": datetime.now().isoformat()
        }
        
    def get_client(self, provider: APIProvider):
        """دریافت کلاینت بر اساس نام"""
        if provider == APIProvider.NASA:
            return self.nasa_client
        elif provider == APIProvider.WEATHER:
            return self.weather_client
        elif provider == APIProvider.FINANCIAL:
            return self.financial_client
        elif provider == APIProvider.WOLFRAM:
            return self.wolfram_client
        elif provider == APIProvider.QUANTUM_COMPUTING:
            return self.quantum_client
        # ... سایر کلاینت‌ها
        return None

    def get_stats(self) -> Dict[str, Any]:
        """دریافت آمار API Manager"""
        return {
            "clients_initialized": [p.value for p in APIProvider],
            "cache_size": len(API_CACHE),
            "stats": self.stats
        }

# Singleton
_api_manager: Optional[APIManager] = None

def get_api_manager() -> APIManager:
    """دریافت نمونه Singleton از APIManager"""
    global _api_manager
    if _api_manager is None:
        _api_manager = APIManager()
    return _api_manager

# برای جلوگیری از خطای import
if __name__ == "__main__":
    async def main():
        manager = get_api_manager()
        print(manager.get_stats())
        
        # مثال استفاده از NASA API
        apod = await manager.nasa_client.get_apod()
        print(f"APOD Title: {apod.get('title', 'N/A')}")
        
        # مثال استفاده از Quantum API
        q_rand = await manager.quantum_client.get_quantum_random_number(bits=32)
        print(f"Quantum Random: {q_rand.get('random_number')}")

    # os.environ["NASA_API_KEY"] = "DEMO_KEY" # برای تست
    # asyncio.run(main())
