from typing import Any, Dict, Optional, List, Tuple
WEATHER_DESCRIPTIONS = {
    "Clear": "맑음",
    "Clouds": "구름 많음",
    "Rain": "비",
    "Snow": "눈",
    "Thunderstorm": "천둥번개",
    "Drizzle": "이슬비",
    "Mist": "안개"
}
class Weather:
    """날씨 정보를 담는 클래스"""
    
    def __init__(self, data: Dict[str, Any]):
        # 위치 정보
        self.coord = {
            "lat": data.get("coord", {}).get("lat"),
            "lon": data.get("coord", {}).get("lon")
        }
        self.location_name = data.get("name")
        self.country = data.get("sys", {}).get("country")
        
        # 날씨 상태
        weather_data = data.get("weather", [{}])[0]
        self.weather_id = weather_data.get("id")
        self.weather_main = weather_data.get("main")
        self.weather_description = weather_data.get("description")
        self.weather_icon = weather_data.get("icon")
        
        # 온도 정보 (켈빈에서 섭씨로 변환)
        main_data = data.get("main", {})
        self.temp = self._kelvin_to_celsius(main_data.get("temp"))
        self.feels_like = self._kelvin_to_celsius(main_data.get("feels_like"))
        self.temp_min = self._kelvin_to_celsius(main_data.get("temp_min"))
        self.temp_max = self._kelvin_to_celsius(main_data.get("temp_max"))
        
        # 습도
        self.humidity = main_data.get("humidity")
        
        # 바람 정보
        wind_data = data.get("wind", {})
        self.wind_speed = wind_data.get("speed")
        
        # 강수량 정보 (비일 경우)
        self.rain_1h = 0.0
        if self.weather_main == "Rain":
            self.rain_1h = data.get("rain", {}).get("1h", 0.0)
    
    def _kelvin_to_celsius(self, kelvin: Optional[float]) -> Optional[float]:
        """켈빈 온도를 섭씨로 변환"""
        if kelvin is None:
            return None
        return round(kelvin - 273.15, 2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Weather 객체를 딕셔너리로 변환"""
        return {
            "coord": self.coord,
            "location_name": self.location_name,
            "country": self.country,
            "weather": {
                "id": self.weather_id,
                "main": self.weather_main,
                "description": self.weather_description,
                "icon": self.weather_icon
            },
            "temperature": {
                "current": self.temp,
                "feels_like": self.feels_like,
                "min": self.temp_min,
                "max": self.temp_max
            },
            "humidity": self.humidity,
            "wind_speed": self.wind_speed,
            "rain_1h": self.rain_1h if self.weather_main == "Rain" else None
        }
    
    def __str__(self) -> str:
        return f"{self.location_name}, {self.country}: {self.weather_main}, {self.temp}°C (체감 {self.feels_like}°C)"