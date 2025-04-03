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
    return response.json()

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

# 좌표를 이용한 반경 500m내 내가 원하는 음식점 조회 (최대 5개)
@mcp.tool()
def find_restaurants_by_keyword(lat, lng, keyword, radius=500, open=None,maxCount="5"):
    """구글 주소API 를 이용하여 좌표를 이용한 반경 Nm내 내가 원하는 음식점 조회"""
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": "restaurant|cafe|bakery|bar",
        "keyword": keyword,
        "key": GOOGLE_API_KEY
    }
    
    response = requests.get(url, params=params)
    results = response.json()
    
    restaurants = []
    if results.get("results"):
        for result in results["results"]:
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
        "key": GOOGLE_API_KEY
    }
    
    response = requests.get(url, params=params)
    result = response.json().get("result", {})
    
    return RestaurantDetail.from_google_place_details(result)

if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run()



# 사용 예시
# if __name__ == "__main__":
#     # 한글 주소를 영문으로 변환
#     korean_address = "서울특별시 강남구 테헤란로 131"
#     english_address_result = convert_to_english_address(korean_address)
#     print("영문 주소 변환 결과:", english_address_result)
    
#     # 예시로 영문 주소 직접 사용
#     english_address = "131, Teheran-ro, Gangnam-gu, Seoul"
    
#     # 좌표 조회
#     lat, lng = get_coordinates(english_address)
#     print(f"좌표: 위도 {lat}, 경도 {lng}")
    
#     # 음식 키워드로 근처 음식점 검색
#     keyword = "한식"
#     restaurants = find_restaurants_by_keyword(lat, lng, keyword)
#     print(f"'{keyword}' 음식점 검색 결과:")
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