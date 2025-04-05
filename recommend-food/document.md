# 파이썬을 이용한 MCP 서버 구축
지도 API 를 이용하여, 내 위치 조회, 가까운 음식점 조회, 음식 키워드를 이용한 음식점 조회

## MCP (Model Context Protocol)
 - AI 가 외부 소스(DB,API,Search...) 에 연결하여 해당 소스를 이용할 수 있는 표준화된 프로토콜
   - **MCP Server** : 사용할 수 있는 도구(tool) 를 정의하고 제공하는 서버
   - **MCP Client** : Claude , Cursor, OpenAI Agent sdk 가 MCP Server 를 이용
   - https://modelcontextprotocol.io/introduction

## 참조 API 링크
 - 행안부 영문주소변환 API :  https://business.juso.go.kr/addrlink/openApi/searchApi.do
 - 구글 지오코딩 API : https://developers.google.com/maps/documentation/geocoding/start?hl=ko&_gl=1
 - 키워드 기반 장소 검색 : https://developers.google.com/maps/documentation/places/web-service/search-text?hl=ko


