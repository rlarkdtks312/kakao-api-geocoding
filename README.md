# 카카오 지오코딩 및 역지오코딩 모듈

카카오 로컬 API를 사용하여 주소와 좌표를 변환하는 Python 모듈입니다.
**데이터프레임(엑셀/CSV)을 입력으로 받아 변환 결과를 추가합니다.**

## 기능

- **지오코딩**: 주소 컬럼을 좌표(경도, 위도) 컬럼으로 변환
- **역지오코딩**: 좌표 컬럼을 주소 컬럼으로 변환 (도로명 주소, 지번 주소, 상세 정보 포함)
- **API 응답 저장**: 역지오코딩 시 API 응답을 JSON 파일로 저장 가능

## 설치

### 방법 1: 배치 파일 사용 (권장 - Windows)

가장 간단한 방법입니다. 모든 설정을 자동으로 수행합니다.

```bash
# 배치 파일 실행
setup_and_run.bat
```

배치 파일이 자동으로:
1. Python 설치 확인
2. 가상환경(.venv) 생성
3. 필요한 패키지 설치
4. config.py 파일 생성 (없는 경우)
5. addresses.xlsx 예제 파일 생성 (없는 경우)
6. 실행 옵션 제공 (Jupyter Notebook, Python 인터프리터)

### 방법 2: 수동 설치

#### 1. 패키지 설치

```bash
# 가상환경 생성 (선택사항)
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 패키지 설치
pip install -r requirements.txt
```

#### 2. API 키 설정

카카오 개발자 콘솔에서 REST API 키를 발급받으세요:
- [카카오 개발자 콘솔](https://developers.kakao.com)
- [로컬 API 가이드](https://developers.kakao.com/docs/latest/ko/local/dev-guide)

#### 방법 1: config.py 파일 사용 (권장)

```bash
# 예제 파일을 복사
cp config.py.example config.py

# config.py 파일을 열어서 API 키 입력
# KAKAO_REST_API_KEY = "실제_API_키"
```

#### 방법 2: 환경 변수 사용

```bash
# Windows (PowerShell)
$env:KAKAO_REST_API_KEY="실제_API_키"

# Windows (CMD)
set KAKAO_REST_API_KEY=실제_API_키

# Linux/Mac
export KAKAO_REST_API_KEY="실제_API_키"
```

## 사용 방법

### 기본 사용법: 지오코딩 (주소 → 좌표)

```python
import pandas as pd
from kakao_geocoding import geocode

# 데이터프레임 생성
df = pd.DataFrame({
    'name': ['강남역', '역삼역'],
    'address': [
        '서울특별시 강남구 강남대로 396',
        '서울특별시 강남구 역삼동'
    ]
})

# 지오코딩 수행 (주소 컬럼을 좌표로 변환)
result = geocode(df, address_column='address')

# 결과 확인
print(result[['name', 'address', 'longitude', 'latitude']])
```

### 기본 사용법: 역지오코딩 (좌표 → 주소)

```python
import pandas as pd
from kakao_geocoding import reverse_geocode

# 데이터프레임 생성
df = pd.DataFrame({
    'name': ['위치1', '위치2'],
    'lon': [127.0276108, 127.0286108],
    'lat': [37.4979420, 37.4989420]
})

# 역지오코딩 수행 (좌표를 주소로 변환)
# 기본적으로 모든 상세 정보가 포함됩니다
result = reverse_geocode(
    df,
    longitude_column='lon',
    latitude_column='lat'
)

# 결과 확인
print(result[['name', 'lon', 'lat', 'road_address', 'address']])
```

### 역지오코딩: 상세 정보 포함/제외

```python
# 모든 상세 정보 포함 (기본값)
result = reverse_geocode(
    df,
    longitude_column='lon',
    latitude_column='lat',
    include_details=True  # 시도, 시군구, 읍면동리, 건물명, 우편번호 등 모든 정보
)

# 간단한 주소만 필요한 경우
result = reverse_geocode(
    df,
    longitude_column='lon',
    latitude_column='lat',
    include_details=False  # 도로명 주소와 지번 주소만
)
```

### 역지오코딩: API 응답 JSON 저장

```python
# 자동 파일명으로 저장 (reverse_geocode_YYYYMMDD_HHMMSS.json)
result = reverse_geocode(
    df,
    longitude_column='lon',
    latitude_column='lat',
    save_json=True
)

# 지정한 파일명으로 저장
result = reverse_geocode(
    df,
    longitude_column='lon',
    latitude_column='lat',
    save_json='my_response.json'
)

# 여러 행일 경우 인덱스가 자동 추가됨
# my_response_0.json, my_response_1.json, ...
```

### 엑셀/CSV 파일 읽기 및 처리

```python
import pandas as pd
from kakao_geocoding import geocode

# 엑셀 파일 읽기 (pandas 기본 기능 사용)
df = pd.read_excel('addresses.xlsx')

# 지오코딩 수행
result = geocode(df, address_column='주소')

# 결과 저장
result.to_excel('result.xlsx', index=False)
```

### 커스텀 컬럼명 사용

```python
from kakao_geocoding import geocode

df = pd.DataFrame({
    '장소명': ['카카오 본사'],
    '주소': ['제주특별자치도 제주시 첨단로 242']
})

# 커스텀 컬럼명으로 지오코딩
result = geocode(
    df,
    address_column='주소',
    longitude_column='경도',  # 기본값: 'longitude'
    latitude_column='위도'    # 기본값: 'latitude'
)
```

### 역지오코딩 커스텀 컬럼명

```python
from kakao_geocoding import reverse_geocode

result = reverse_geocode(
    df,
    longitude_column='lon',
    latitude_column='lat',
    address_column='지번주소',        # 기본값: 'address'
    road_address_column='도로명주소'   # 기본값: 'road_address'
)
```

## 함수 설명

### `geocode(df, address_column, ...)`

주소 컬럼을 좌표로 변환하여 데이터프레임에 추가합니다.

**매개변수:**
- `df` (pd.DataFrame): 입력 데이터프레임
- `address_column` (str): 주소가 있는 컬럼명
- `longitude_column` (str, 선택): 경도 컬럼명 (기본값: "longitude")
- `latitude_column` (str, 선택): 위도 컬럼명 (기본값: "latitude")
- `delay` (float, 선택): API 호출 간 지연 시간(초) (기본값: 0.1)

**반환값:**
- `pd.DataFrame`: 변환 결과가 추가된 데이터프레임

**반환되는 컬럼:**
- 원본 데이터프레임의 모든 컬럼
- `longitude_column` (기본값: "longitude"): 경도 (float)
- `latitude_column` (기본값: "latitude"): 위도 (float)

**예제:**
```python
df = pd.DataFrame({'address': ['서울시 강남구']})
result = geocode(df, 'address')
# 결과: address, longitude, latitude 컬럼 포함
```

---

### `reverse_geocode(df, longitude_column, latitude_column, ...)`

좌표 컬럼을 주소로 변환하여 데이터프레임에 추가합니다.
**카카오 API는 한 번의 호출로 도로명 주소와 지번 주소를 모두 반환합니다.**

**매개변수:**
- `df` (pd.DataFrame): 입력 데이터프레임
- `longitude_column` (str): 경도 컬럼명
- `latitude_column` (str): 위도 컬럼명
- `address_column` (str, 선택): 지번 주소 컬럼명 (기본값: "address")
- `road_address_column` (str, 선택): 도로명 주소 컬럼명 (기본값: "road_address")
- `include_details` (bool, 선택): 상세 정보 포함 여부 (기본값: True)
  - `True`: 도로명/지번 주소 + 시도, 시군구, 읍면동리, 건물명, 우편번호 등 모든 정보
  - `False`: 도로명 주소와 지번 주소만
- `save_json` (str/bool, 선택): JSON 파일 저장 옵션 (기본값: None)
  - `None`: 저장하지 않음
  - `True` 또는 `"auto"`: 자동으로 파일명 생성 (`reverse_geocode_YYYYMMDD_HHMMSS.json`)
  - 문자열: 지정한 경로에 저장 (여러 행일 경우 인덱스 추가)
- `delay` (float, 선택): API 호출 간 지연 시간(초) (기본값: 0.1)

**반환값:**
- `pd.DataFrame`: 변환 결과가 추가된 데이터프레임

**반환되는 컬럼:**

#### 기본 컬럼 (항상 포함)
- 원본 데이터프레임의 모든 컬럼
- `address_column` (기본값: "address"): 전체 지번 주소 (str)
- `road_address_column` (기본값: "road_address"): 전체 도로명 주소 (str)

#### 상세 정보 컬럼 (`include_details=True`일 경우 추가)

**도로명 주소 관련:**
- `road_zone_no`: 우편번호 (5자리, str)
- `road_region_1depth`: 시도 (예: "서울특별시", str)
- `road_region_2depth`: 시군구 (예: "강남구", str)
- `road_region_3depth`: 읍면동 (예: "역삼동", str)
- `road_name`: 도로명 (예: "테헤란로", str)
- `road_main_building_no`: 건물 본번 (str)
- `road_sub_building_no`: 건물 부번 (str)
- `road_building_name`: 건물명 (str)
- `road_underground_yn`: 지하 여부 ("Y" 또는 "N", str)

**지번 주소 관련:**
- `address_region_1depth`: 시도 (예: "서울특별시", str)
- `address_region_2depth`: 시군구 (예: "강남구", str)
- `address_region_3depth`: 동/리 (예: "역삼동", str)
- `address_region_3depth_h`: 행정동명 (str)
- `address_h_code`: 행정 코드 (10자리, str)
- `address_b_code`: 법정 코드 (10자리, str)
- `address_main_no`: 지번 주번지 (str)
- `address_sub_no`: 지번 부번지 (str)
- `address_mountain_yn`: 산 여부 ("Y" 또는 "N", str)

**예제:**
```python
df = pd.DataFrame({
    'lon': [127.0276108],
    'lat': [37.4979420]
})

# 모든 상세 정보 포함
result = reverse_geocode(df, 'lon', 'lat', include_details=True)
# 결과: lon, lat, address, road_address + 18개의 상세 정보 컬럼

# 간단한 주소만
result = reverse_geocode(df, 'lon', 'lat', include_details=False)
# 결과: lon, lat, address, road_address만
```

---

## JSON 파일 저장 기능

역지오코딩 시 `save_json` 파라미터를 사용하면 API 응답 전체를 JSON 파일로 저장할 수 있습니다.

### 저장되는 JSON 파일 구조

```json
{
  "request": {
    "url": "https://dapi.kakao.com/v2/local/geo/coord2address.json",
    "params": {
      "x": "126.889783",
      "y": "37.579428",
      "input_coord": "WGS84"
    },
    "longitude": 126.889783,
    "latitude": 37.579428,
    "timestamp": "2025-01-22T16:27:07.123456"
  },
  "response": {
    "status_code": 200,
    "headers": {
      "Content-Type": "application/json;charset=UTF-8",
      ...
    },
    "data": {
      "meta": {
        "total_count": 1
      },
      "documents": [
        {
          "road_address": {
            "address_name": "서울특별시 마포구 월드컵북로 396",
            "region_1depth_name": "서울특별시",
            "region_2depth_name": "마포구",
            "region_3depth_name": "상암동",
            "road_name": "월드컵북로",
            "main_building_no": "396",
            "sub_building_no": "",
            "building_name": "",
            "zone_no": "03925",
            ...
          },
          "address": {
            "address_name": "서울 마포구 상암동 1605",
            "region_1depth_name": "서울특별시",
            "region_2depth_name": "마포구",
            "region_3depth_name": "상암동",
            "h_code": "1144012900",
            "b_code": "1144012600",
            ...
          }
        }
      ]
    }
  }
}
```

### 사용 예제

```python
# 자동 파일명 생성
result = reverse_geocode(df, 'lon', 'lat', save_json=True)
# → reverse_geocode_20250122_162707.json 생성

# 지정한 파일명
result = reverse_geocode(df, 'lon', 'lat', save_json='api_response.json')
# → api_response.json 생성

# 여러 행일 경우
df = pd.DataFrame({
    'lon': [127.0, 128.0],
    'lat': [37.0, 38.0]
})
result = reverse_geocode(df, 'lon', 'lat', save_json='responses')
# → responses_0.json, responses_1.json 생성
```

---

## 주의사항

1. **API 제한**: 카카오 API는 일일 호출 제한이 있습니다. 대량 데이터 처리 시 `delay` 파라미터를 조정하세요.
2. **진행 상황**: 처리 중 진행 상황이 자동으로 출력됩니다.
3. **에러 처리**: 변환 실패한 행은 None 값으로 채워집니다.
4. **모듈 재로드**: Python 인터프리터에서 모듈을 수정한 경우, `importlib.reload()`를 사용하거나 인터프리터를 재시작해야 변경사항이 반영됩니다.

---

## API 참고 자료

- [카카오 로컬 API 공식 문서](https://developers.kakao.com/docs/latest/ko/local/dev-guide)
- [주소로 좌표 변환](https://developers.kakao.com/docs/latest/ko/local/dev-guide#주소로-좌표변환)
- [좌표로 주소 변환](https://developers.kakao.com/docs/latest/ko/local/dev-guide#좌표로-주소변환)

---

## 보안 주의사항

- `config.py` 파일은 `.gitignore`에 포함되어 있어 Git에 업로드되지 않습니다
- API 키는 절대 공개 저장소에 커밋하지 마세요
- 환경 변수를 사용하는 경우, 프로덕션 환경에서는 안전한 방식으로 관리하세요

---

## 기여하기

버그 리포트, 기능 제안, Pull Request를 환영합니다!

## 라이선스

이 모듈은 카카오 API를 사용합니다. 카카오 API 사용 약관을 준수해야 합니다.
