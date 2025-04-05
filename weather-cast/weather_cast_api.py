from dotenv import load_dotenv
from httpx import HTTPStatusError
import httpx
import os
import time
from typing import Any, Dict, Optional, List, Tuple
import math
from weather_models import Weather

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Weather data cache
weather_cache: Dict[str, Tuple[float, 'Weather']] = {}  # key: "lat_lng", value: (timestamp, Weather object)
CACHE_EXPIRY = 60 * 15  # 15 minutes
LOCATION_RADIUS = 1.0  # 1km

def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """두 지점 간의 거리를 km 단위로 계산 (Haversine 공식)"""
    # 지구 반경 (km)
    R = 6371.0
    
    # 라디안으로 변환
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # 좌표 차이
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    # Haversine 공식
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance

def _find_cached_weather(lat: float, lng: float) -> Optional[Weather]:
    """캐시에서 주어진 위치에 가까운 날씨 정보를 찾음"""
    current_time = time.time()
    
    # 캐시에서 만료된 항목 제거
    expired_keys = [k for k, (timestamp, _) in weather_cache.items() if current_time - timestamp > CACHE_EXPIRY]
    for key in expired_keys:
        del weather_cache[key]
    
    # 1km 이내의 캐시된 위치 찾기
    for key, (timestamp, weather) in weather_cache.items():
        cached_lat = weather.coord["lat"]
        cached_lon = weather.coord["lon"]
        
        if _haversine_distance(lat, lng, cached_lat, cached_lon) <= LOCATION_RADIUS:
            return weather
    
    return None

async def get_weather_data(lat: float, lng: float) -> Any:
    """현재 날씨를 알려준다. 캐싱 기능 포함."""
    # 캐시에서 먼저 확인
    cached_weather = _find_cached_weather(lat, lng)
    if cached_weather:
        print("캐시에서 날씨 정보 가져옴")
        return cached_weather
    
    headers = {
    }

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={API_KEY}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            weather_data = response.json()
            
            # Weather 객체 생성 및 캐시에 저장
            weather = Weather(weather_data)
            cache_key = f"{lat}_{lng}"
            weather_cache[cache_key] = (time.time(), weather)
            
            return weather
        except HTTPStatusError as e:
            print(f"HTTP 오류 발생: {e}")
            return None
        except Exception as e:
            print(f"오류 발생: {e}")
            return None
    
async def main():
    weather = await get_weather_data(37.4990106, 127.0328414)
    print(weather)
    
    # 캐싱 테스트 (약간 다른 위치 - 1km 이내)
    print("\n약간 다른 위치에서 날씨 정보 요청 (캐시에서 가져와야 함)")
    weather2 = await  get_weather_data(37.4990206, 127.0328614)
    print(weather2)
    
    if weather2 is not None:
        print("\n날씨 정보 상세:")
        print(weather2.to_dict())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())