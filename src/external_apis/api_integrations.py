"""
Laniakea Protocol - External API Integrations
یکپارچگی با API های خارجی

این ماژول اتصال به API های مختلف را فراهم می‌کند:
- NASA APIs (APOD, NeoWs, Mars Rover)
- Weather APIs (OpenWeatherMap)
- Financial APIs (Alpha Vantage)
- Wolfram Alpha
- News APIs
"""

import os
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime, timedelta


class APIProvider(str, Enum):
    """ارائه‌دهندگان API"""
    NASA = "nasa"
    WEATHER = "weather"
    FINANCIAL = "financial"
    WOLFRAM = "wolfram"
    NEWS = "news"
    ARXIV = "arxiv"
    WIKIPEDIA = "wikipedia"


class NASAClient:
    """
    کلاینت NASA APIs
    
    APIs:
    - APOD: Astronomy Picture of the Day
    - NeoWs: Near Earth Object Web Service
    - Mars Rover Photos
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("NASA_API_KEY", "DEMO_KEY")
        self.base_url = "https://api.nasa.gov"
    
    async def get_apod(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        دریافت تصویر نجومی روز
        
        Args:
            date: تاریخ (YYYY-MM-DD) یا None برای امروز
        
        Returns:
            اطلاعات تصویر
        """
        url = f"{self.base_url}/planetary/apod"
        params = {"api_key": self.api_key}
        
        if date:
            params["date"] = date
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Status {response.status}"}
    
    async def get_near_earth_objects(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        دریافت اجرام نزدیک به زمین
        
        Args:
            start_date: تاریخ شروع (YYYY-MM-DD)
            end_date: تاریخ پایان (YYYY-MM-DD)
        
        Returns:
            لیست اجرام
        """
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
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Status {response.status}"}
    
    async def get_mars_rover_photos(
        self,
        rover: str = "curiosity",
        sol: int = 1000,
        camera: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        دریافت تصاویر مریخ‌نورد
        
        Args:
            rover: نام مریخ‌نورد (curiosity, opportunity, spirit)
            sol: روز مریخی
            camera: نام دوربین
        
        Returns:
            لیست تصاویر
        """
        url = f"{self.base_url}/mars-photos/api/v1/rovers/{rover}/photos"
        params = {
            "sol": sol,
            "api_key": self.api_key
        }
        
        if camera:
            params["camera"] = camera
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Status {response.status}"}


class WeatherClient:
    """
    کلاینت OpenWeatherMap API
    
    APIs:
    - Current Weather
    - 5 Day Forecast
    - Historical Data
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    async def get_current_weather(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        دریافت آب و هوای فعلی
        
        Args:
            city: نام شهر
            lat: عرض جغرافیایی
            lon: طول جغرافیایی
        
        Returns:
            اطلاعات آب و هوا
        """
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
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Status {response.status}"}
    
    async def get_forecast(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        دریافت پیش‌بینی 5 روزه
        
        Args:
            city: نام شهر
            lat: عرض جغرافیایی
            lon: طول جغرافیایی
        
        Returns:
            پیش‌بینی آب و هوا
        """
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
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Status {response.status}"}


class FinancialClient:
    """
    کلاینت Alpha Vantage API
    
    APIs:
    - Stock Prices
    - Cryptocurrency
    - Economic Indicators
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ALPHAVANTAGE_API_KEY")
        self.base_url = "https://www.alphavantage.co/query"
    
    async def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """
        دریافت قیمت سهام
        
        Args:
            symbol: نماد سهام (مثلاً IBM)
        
        Returns:
            اطلاعات قیمت
        """
        if not self.api_key:
            return {"error": "API key not configured"}
        
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Status {response.status}"}
    
    async def get_crypto_price(
        self,
        symbol: str = "BTC",
        market: str = "USD"
    ) -> Dict[str, Any]:
        """
        دریافت قیمت ارز دیجیتال
        
        Args:
            symbol: نماد ارز (مثلاً BTC)
            market: بازار (مثلاً USD)
        
        Returns:
            اطلاعات قیمت
        """
        if not self.api_key:
            return {"error": "API key not configured"}
        
        params = {
            "function": "DIGITAL_CURRENCY_DAILY",
            "symbol": symbol,
            "market": market,
            "apikey": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Status {response.status}"}
    
    async def get_economic_indicator(
        self,
        indicator: str = "GDP",
        interval: str = "annual"
    ) -> Dict[str, Any]:
        """
        دریافت شاخص اقتصادی
        
        Args:
            indicator: نوع شاخص (GDP, INFLATION, etc.)
            interval: بازه زمانی
        
        Returns:
            داده‌های شاخص
        """
        if not self.api_key:
            return {"error": "API key not configured"}
        
        params = {
            "function": indicator,
            "interval": interval,
            "apikey": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Status {response.status}"}


class WolframAlphaClient:
    """
    کلاینت Wolfram Alpha API
    
    برای محاسبات ریاضی و علمی پیچیده
    """
    
    def __init__(self, app_id: Optional[str] = None):
        self.app_id = app_id or os.getenv("WOLFRAM_APP_ID")
        self.base_url = "http://api.wolframalpha.com/v2/query"
    
    async def query(
        self,
        input_text: str,
        format: str = "plaintext"
    ) -> Dict[str, Any]:
        """
        پرسش از Wolfram Alpha
        
        Args:
            input_text: متن پرسش
            format: فرمت خروجی (plaintext, image)
        
        Returns:
            پاسخ
        """
        if not self.app_id:
            return {"error": "App ID not configured"}
        
        params = {
            "input": input_text,
            "appid": self.app_id,
            "format": format,
            "output": "json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Status {response.status}"}


class NewsClient:
    """
    کلاینت NewsAPI.org
    
    برای دریافت اخبار
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2"
    
    async def get_everything(
        self,
        query: str,
        from_date: Optional[str] = None,
        sort_by: str = "popularity"
    ) -> Dict[str, Any]:
        """
        جستجوی اخبار
        
        Args:
            query: کلمه کلیدی
            from_date: از تاریخ (YYYY-MM-DD)
            sort_by: مرتب‌سازی (relevancy, popularity, publishedAt)
        
        Returns:
            لیست اخبار
        """
        if not self.api_key:
            return {"error": "API key not configured"}
        
        url = f"{self.base_url}/everything"
        params = {
            "q": query,
            "sortBy": sort_by,
            "apiKey": self.api_key
        }
        
        if from_date:
            params["from"] = from_date
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Status {response.status}"}


class APIIntegrationManager:
    """
    مدیر یکپارچگی API ها
    
    این کلاس تمام کلاینت‌های API را مدیریت می‌کند
    """
    
    def __init__(self):
        self.nasa = NASAClient()
        self.weather = WeatherClient()
        self.financial = FinancialClient()
        self.wolfram = WolframAlphaClient()
        self.news = NewsClient()
        
        print("🌐 API Integration Manager initialized")
    
    async def query_api(
        self,
        provider: APIProvider,
        endpoint: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        پرسش عمومی از API
        
        Args:
            provider: ارائه‌دهنده API
            endpoint: نقطه پایانی
            params: پارامترها
        
        Returns:
            پاسخ API
        """
        try:
            if provider == APIProvider.NASA:
                if endpoint == "apod":
                    return await self.nasa.get_apod(params.get("date"))
                elif endpoint == "neo":
                    return await self.nasa.get_near_earth_objects(
                        params.get("start_date"),
                        params.get("end_date")
                    )
                elif endpoint == "mars":
                    return await self.nasa.get_mars_rover_photos(
                        params.get("rover", "curiosity"),
                        params.get("sol", 1000),
                        params.get("camera")
                    )
            
            elif provider == APIProvider.WEATHER:
                if endpoint == "current":
                    return await self.weather.get_current_weather(
                        params.get("city"),
                        params.get("lat"),
                        params.get("lon")
                    )
                elif endpoint == "forecast":
                    return await self.weather.get_forecast(
                        params.get("city"),
                        params.get("lat"),
                        params.get("lon")
                    )
            
            elif provider == APIProvider.FINANCIAL:
                if endpoint == "stock":
                    return await self.financial.get_stock_price(params.get("symbol"))
                elif endpoint == "crypto":
                    return await self.financial.get_crypto_price(
                        params.get("symbol", "BTC"),
                        params.get("market", "USD")
                    )
                elif endpoint == "indicator":
                    return await self.financial.get_economic_indicator(
                        params.get("indicator", "GDP"),
                        params.get("interval", "annual")
                    )
            
            elif provider == APIProvider.WOLFRAM:
                return await self.wolfram.query(
                    params.get("input"),
                    params.get("format", "plaintext")
                )
            
            elif provider == APIProvider.NEWS:
                return await self.news.get_everything(
                    params.get("query"),
                    params.get("from_date"),
                    params.get("sort_by", "popularity")
                )
            
            return {"error": "Unknown endpoint"}
        
        except Exception as e:
            return {"error": str(e)}
    
    def get_stats(self) -> Dict:
        """دریافت آمار"""
        return {
            "providers": [p.value for p in APIProvider],
            "nasa_configured": bool(self.nasa.api_key != "DEMO_KEY"),
            "weather_configured": bool(self.weather.api_key),
            "financial_configured": bool(self.financial.api_key),
            "wolfram_configured": bool(self.wolfram.app_id),
            "news_configured": bool(self.news.api_key)
        }


# Singleton instance
_api_manager = None


def get_api_manager() -> APIIntegrationManager:
    """دریافت instance مدیر API"""
    global _api_manager
    if _api_manager is None:
        _api_manager = APIIntegrationManager()
    return _api_manager
