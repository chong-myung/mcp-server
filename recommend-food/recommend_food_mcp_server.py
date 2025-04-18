from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os
import requests
import json
from typing import List, Optional
from restaurant_models import Restaurant, RestaurantDetail

load_dotenv()

mcp = FastMCP("recommend_food_server")

LOCATION_API_KEY = os.getenv("LOCATION_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 키워드 매핑 딕셔너리: 일반적인 음식/장소 키워드를 Google Places API 타입으로 매핑
KEYWORD_TO_TYPE_MAPPING = {
    # 음식점 유형
    "식당": "restaurant",
    "레스토랑": "restaurant",
    "음식점": "restaurant",
    "한식": "restaurant",
    "중식": "restaurant",
    "일식": "restaurant",
    "양식": "restaurant",
    "분식": "restaurant",
    "고기집": "restaurant",
    "치킨": "restaurant",
    "피자": "restaurant",
    "햄버거": "restaurant",
    
    # 카페
    "카페": "cafe",
    "커피": "cafe",
    "스타벅스": "cafe",
    "디저트": "cafe|bakery",
    "베이커리": "bakery",
    "빵집": "bakery",
    
    # 술집
    "술집": "bar",
    "바": "bar",
    "호프": "bar",
    "맥주": "bar",
    "와인": "bar",
    
    # 편의점/마트
    "마트": "convenience_store",
    "편의점": "convenience_store",
    "슈퍼": "convenience_store",
    "상점": "store",
    
    # 기타 장소 타입
    "약국": "pharmacy",
    "병원": "hospital",
    "은행": "bank",
    "학교": "school",
    "공원": "park",
    "주차장": "parking",
    "주유소": "gas_station",
    "호텔": "lodging",
    "영화관": "movie_theater",
    "극장": "movie_theater",
}

@mcp.tool()
def infer_place_type_from_keyword(keyword):
    """키워드를 분석하여 적절한 Google Places API 장소 타입을 추론합니다"""
    # 키워드를 소문자로 변환하고 공백 제거
    processed_keyword = keyword.lower().strip()
    # 매핑 딕셔너리에서 일치하는 키워드 찾기
    for key, place_type in KEYWORD_TO_TYPE_MAPPING.items():
        if key in processed_keyword:
            return place_type
    # 기본값은 restaurant
    return None

# 입력한 한글 주소를 영문으로 변환
@mcp.tool()
def convert_to_english_address(korean_address):
    """한글 주소를 영문 주소로 변경합니다. """
    url = "https://business.juso.go.kr/addrlink/addrEngApi.do"
    params = {
        "confmKey": LOCATION_API_KEY,
        "currentPage": 1,
        "countPerPage": 10,
        "keyword": korean_address,
        "resultType": "json"
    }
    
    response = requests.get(url, params=params)
    result = response.json()
    # 결과가 있는 경우 첫 번째 주소 반환
    if result.get("results", {}).get("common", {}).get("totalCount", "0") != "0":
        first_address = result["results"]["juso"][0]["roadAddr"]
        return first_address
    return None

# 영문주소를 이용한 좌표 조회
@mcp.tool()
def get_coordinates(english_address):
    """영문주소를 이용하여 위도,경도를 구합니다."""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": english_address,
        "key": GOOGLE_API_KEY
    }
    
    response = requests.get(url, params=params)
    result = response.json()
    
    if result["status"] == "OK":
        location = result["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        return None

# 좌표를 이용한 반경 내 음식점 조회 (키워드 기반 타입 추론)
@mcp.tool()
def find_restaurants_by_keyword(lat, lng, keyword,language="ko", open=None, maxCount="5"):
    """구글 주소API 를 이용하여 좌표를 이용한 근처 가게 추천"""
    inferred_type = infer_place_type_from_keyword(keyword)
    if inferred_type is None or inferred_type == "":
        inferred_type = "restaurant"

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "type": inferred_type,
        "keyword": keyword,
        "key": GOOGLE_API_KEY,
        "language" : language,
        "rankby" : "distance"
    }
    
    response = requests.get(url, params=params)
    results = response.json()
    
    restaurants = []
    results_list = results.get("results", [])

    if not isinstance(results_list, list):
        return  # 또는 적절한 예외 처리
    elif results_list.__sizeof__== 0:
        return;
    
    sorted_results = sorted(
        results_list,
        key=lambda x: float(x.get("rating") or 0.0),
        reverse=True
    )
    for result in sorted_results:
        # open 파라미터에 따른 필터링
        if open is True:
            # open이 True일 때는 영업중인지 먼저 확인
            is_open = result.get("opening_hours", {}).get("open_now")
            if not is_open:
                continue
        
        # 필터링을 통과한 경우에만 Restaurant 객체 생성
        restaurant = Restaurant.from_google_place(result)
        restaurants.append(restaurant)
        
        # 결과가 5개가 되면 중단
        if len(restaurants) >= int(maxCount):
            break
    
    return restaurants
    

# 추천 음식점 정보를 음식점 상세정보 조회
@mcp.tool()
def get_restaurant_details(place_id):
    """레스토랑의 place_id의 상세정보를 이용하여 구글 상세 주소API 조회,이름,주소,이번주 운영시간을 보여준다. """
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,rating,user_ratings_total,opening_hours,price_level,photos",
        "key": GOOGLE_API_KEY,
        "language": "ko"  # 한글로 결과 받기
    }
    
    response = requests.get(url, params=params)
    result = response.json().get("result", {})
    
    return RestaurantDetail.from_google_place_details(result)

if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run()



#사용 예시
# if __name__ == "__main__":
#     # 한글 주소를 영문으로 변환
#     korean_address = "서울시 강서구 강서로 7길 20-22"
#     english_address_result = convert_to_english_address(korean_address)
#     print("영문 주소 변환 결과:", english_address_result)
    
#     # 예시로 영문 주소 직접 사용
#     english_address = "20-22 Gangseo-ro 7-gil, Gangseo-gu, Seoul"
    
#     # 좌표 조회
#     lat, lng = get_coordinates(english_address)
#     print(f"좌표: 위도 {lat}, 경도 {lng}")
    
#     # 음식 키워드로 근처 음식점 검색
#     keyword = "카페"
#     restaurants = find_restaurants_by_keyword(lat, lng, keyword)
#     print(f"'{keyword}' 카페 검색 결과:")
#     for restaurant in restaurants:
#         print(f"이름: {restaurant.name}, 영업중: {restaurant.open_now}, 평점: {restaurant.rating}")
    
#     # 특정 음식점 상세 정보 조회 (첫 번째 검색 결과 사용)
#     if restaurants and len(restaurants) > 0:
#         place_id = restaurants[0].place_id
#         details = get_restaurant_details(place_id)
#         print("음식점 상세 정보:")
#         print(f"이름: {details.name}")
#         print(f"주소: {details.formatted_address}")
#         if details.weekday_text:
#             print("영업시간:")
#             for hours in details.weekday_text:
#                 print(f"  {hours}")
#         else:
#             print("영업시간 정보 없음")