"""
카카오 API를 사용한 지오코딩 및 역지오코딩 모듈

이 모듈은 카카오 로컬 API를 사용하여:
- 주소를 좌표로 변환 (지오코딩)
- 좌표를 주소로 변환 (역지오코딩)

데이터프레임(엑셀/CSV)을 입력으로 받아 변환 결과를 추가합니다.
"""

import os
import time
import json
import requests
import pandas as pd
from typing import Optional, Union
from pathlib import Path
from datetime import datetime


class KakaoGeocodingAPI:
    """카카오 지오코딩 API 클래스 (내부 사용)"""
    
    BASE_URL = "https://dapi.kakao.com/v2/local"
    
    def __init__(self, api_key: Optional[str] = None):
        """API 키 초기화"""
        if api_key is None:
            api_key = os.getenv('KAKAO_REST_API_KEY')
            if not api_key:
                try:
                    from config import KAKAO_REST_API_KEY
                    api_key = KAKAO_REST_API_KEY
                except ImportError:
                    raise ValueError(
                        "API 키를 찾을 수 없습니다. "
                        "환경변수 KAKAO_REST_API_KEY를 설정하거나 "
                        "config.py 파일에 KAKAO_REST_API_KEY를 정의하세요."
                    )
        
        self.api_key = api_key
        self.headers = {
            "Authorization": f"KakaoAK {self.api_key}"
        }
    
    def _geocode_address(self, address: str) -> Optional[dict]:
        """주소를 좌표로 변환 (단일 주소)"""
        if pd.isna(address) or address == "":
            return None
        
        url = f"{self.BASE_URL}/search/address.json"
        params = {"query": str(address), "size": 1}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=5)
            
            # 403 오류인 경우 더 자세한 정보 출력
            if response.status_code == 403:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("msg", "알 수 없는 오류")
                    error_code = error_data.get("code", "")
                    print(f"지오코딩 오류 (403 Forbidden): {error_msg} (코드: {error_code})")
                    print(f"API 키 확인이 필요합니다. 카카오 개발자 콘솔에서:")
                    print("1. REST API 키가 올바른지 확인")
                    print("2. 로컬 API가 활성화되어 있는지 확인")
                    print("3. 앱 도메인이 설정되어 있는지 확인")
                except:
                    print(f"지오코딩 오류 (403 Forbidden): API 키 인증 실패")
                    print(f"현재 사용 중인 API 키: {self.api_key[:10]}...")
            
            response.raise_for_status()
            data = response.json()
            
            documents = data.get("documents", [])
            if documents:
                doc = documents[0]
                return {
                    "longitude": float(doc.get("x", 0)),
                    "latitude": float(doc.get("y", 0)),
                    "address_name": doc.get("address_name", ""),
                    "address_type": doc.get("address_type", "")
                }
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                # 이미 위에서 처리했으므로 여기서는 추가 출력 없음
                pass
            else:
                print(f"지오코딩 HTTP 오류 (주소: {address}): {str(e)}")
        except Exception as e:
            print(f"지오코딩 오류 (주소: {address}): {str(e)}")
        
        return None
    
    def _reverse_geocode_coords(self, longitude: float, latitude: float, include_details: bool = True, save_json: Optional[str] = None) -> Optional[dict]:
        """
        좌표를 주소로 변환 (단일 좌표)
        
        Args:
            longitude: 경도
            latitude: 위도
            include_details: 상세 정보 포함 여부 (시도, 시군구, 읍면동리 등)
            save_json: JSON 파일 저장 경로 (None이면 저장하지 않음)
        
        Returns:
            주소 정보 딕셔너리 (include_details=True일 경우 모든 상세 정보 포함)
        """
        if pd.isna(longitude) or pd.isna(latitude):
            return None
        
        url = f"{self.BASE_URL}/geo/coord2address.json"
        params = {
            "x": str(longitude),
            "y": str(latitude),
            "input_coord": "WGS84"
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=5)
            
            # 403 오류인 경우 더 자세한 정보 출력
            if response.status_code == 403:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("msg", "알 수 없는 오류")
                    error_code = error_data.get("code", "")
                    print(f"역지오코딩 오류 (403 Forbidden): {error_msg} (코드: {error_code})")
                    print(f"API 키 확인이 필요합니다. 카카오 개발자 콘솔에서:")
                    print("1. REST API 키가 올바른지 확인")
                    print("2. 로컬 API가 활성화되어 있는지 확인")
                    print("3. 앱 도메인이 설정되어 있는지 확인")
                except:
                    print(f"역지오코딩 오류 (403 Forbidden): API 키 인증 실패")
                    print(f"현재 사용 중인 API 키: {self.api_key[:10]}...")
            
            response.raise_for_status()
            data = response.json()
            
            # JSON 파일로 저장
            if save_json:
                json_data = {
                    "request": {
                        "url": url,
                        "params": params,
                        "longitude": longitude,
                        "latitude": latitude,
                        "timestamp": datetime.now().isoformat()
                    },
                    "response": {
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "data": data
                    }
                }
                
                json_path = Path(save_json)
                # 디렉토리가 없으면 생성
                json_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                
                print(f"API 응답이 JSON 파일로 저장되었습니다: {json_path}")
            
            documents = data.get("documents", [])
            if documents:
                doc = documents[0]
                result = {}
                
                # 도로명 주소 정보
                if "road_address" in doc:
                    road = doc["road_address"]
                    result["road_address"] = road.get("address_name", "")  # 전체 도로명 주소
                    result["road_zone_no"] = road.get("zone_no", "")  # 우편번호
                    
                    if include_details:
                        result["road_region_1depth"] = road.get("region_1depth_name", "")  # 시도
                        result["road_region_2depth"] = road.get("region_2depth_name", "")  # 시군구
                        result["road_region_3depth"] = road.get("region_3depth_name", "")  # 읍면동
                        result["road_name"] = road.get("road_name", "")  # 도로명
                        result["road_main_building_no"] = road.get("main_building_no", "")  # 건물 본번
                        result["road_sub_building_no"] = road.get("sub_building_no", "")  # 건물 부번
                        result["road_building_name"] = road.get("building_name", "")  # 건물명
                        result["road_underground_yn"] = road.get("underground_yn", "")  # 지하 여부
                else:
                    result["road_address"] = ""
                    result["road_zone_no"] = ""
                    if include_details:
                        result["road_region_1depth"] = ""
                        result["road_region_2depth"] = ""
                        result["road_region_3depth"] = ""
                        result["road_name"] = ""
                        result["road_main_building_no"] = ""
                        result["road_sub_building_no"] = ""
                        result["road_building_name"] = ""
                        result["road_underground_yn"] = ""
                
                # 지번 주소 정보
                if "address" in doc:
                    addr = doc["address"]
                    result["address"] = addr.get("address_name", "")  # 전체 지번 주소
                    
                    if include_details:
                        result["address_region_1depth"] = addr.get("region_1depth_name", "")  # 시도
                        result["address_region_2depth"] = addr.get("region_2depth_name", "")  # 시군구
                        result["address_region_3depth"] = addr.get("region_3depth_name", "")  # 동/리
                        result["address_region_3depth_h"] = addr.get("region_3depth_h_name", "")  # 행정동명
                        result["address_h_code"] = addr.get("h_code", "")  # 행정 코드
                        result["address_b_code"] = addr.get("b_code", "")  # 법정 코드
                        result["address_main_no"] = addr.get("main_address_no", "")  # 지번 주번지
                        result["address_sub_no"] = addr.get("sub_address_no", "")  # 지번 부번지
                        result["address_mountain_yn"] = addr.get("mountain_yn", "")  # 산 여부
                else:
                    result["address"] = ""
                    if include_details:
                        result["address_region_1depth"] = ""
                        result["address_region_2depth"] = ""
                        result["address_region_3depth"] = ""
                        result["address_region_3depth_h"] = ""
                        result["address_h_code"] = ""
                        result["address_b_code"] = ""
                        result["address_main_no"] = ""
                        result["address_sub_no"] = ""
                        result["address_mountain_yn"] = ""
                
                return result
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                # 이미 위에서 처리했으므로 여기서는 추가 출력 없음
                pass
            else:
                print(f"역지오코딩 HTTP 오류 (좌표: {longitude}, {latitude}): {str(e)}")
        except Exception as e:
            print(f"역지오코딩 오류 (좌표: {longitude}, {latitude}): {str(e)}")
        
        return None


# 전역 API 인스턴스 (초기화는 지연 로딩)
_api_instance = None


def _get_api_instance():
    """API 인스턴스 가져오기 (싱글톤 패턴)"""
    global _api_instance
    if _api_instance is None:
        _api_instance = KakaoGeocodingAPI()
    return _api_instance


def geocode(df: pd.DataFrame, 
            address_column: str,
            longitude_column: str = "longitude",
            latitude_column: str = "latitude",
            delay: float = 0.1) -> pd.DataFrame:
    """
    주소 컬럼을 좌표로 변환하여 데이터프레임에 추가
    
    Args:
        df: 입력 데이터프레임
        address_column: 주소가 있는 컬럼명
        longitude_column: 경도 컬럼명 (기본값: "longitude")
        latitude_column: 위도 컬럼명 (기본값: "latitude")
        delay: API 호출 간 지연 시간(초) - API 제한을 피하기 위해 (기본값: 0.1)
    
    Returns:
        변환 결과가 추가된 데이터프레임
    
    Example:
        >>> import pandas as pd
        >>> from kakao_geocoding import geocode
        >>> 
        >>> df = pd.DataFrame({
        ...     'name': ['강남역', '역삼역'],
        ...     'address': ['서울시 강남구 강남대로', '서울시 강남구 역삼동']
        ... })
        >>> result = geocode(df, 'address')
        >>> print(result[['address', 'longitude', 'latitude']])
    """
    if address_column not in df.columns:
        raise ValueError(f"컬럼 '{address_column}'이 데이터프레임에 없습니다.")
    
    df = df.copy()
    api = _get_api_instance()
    
    # 결과 컬럼 초기화
    df[longitude_column] = None
    df[latitude_column] = None
    
    print(f"지오코딩 시작: 총 {len(df)}개 주소 처리 중...")
    
    for idx, row in df.iterrows():
        address = row[address_column]
        result = api._geocode_address(address)
        
        if result:
            df.at[idx, longitude_column] = result["longitude"]
            df.at[idx, latitude_column] = result["latitude"]
        
        # API 제한을 피하기 위한 지연
        if delay > 0:
            time.sleep(delay)
        
        # 진행 상황 출력
        if (idx + 1) % 10 == 0:
            print(f"진행 중: {idx + 1}/{len(df)} ({((idx+1)/len(df)*100):.1f}%)")
    
    print(f"지오코딩 완료: {df[longitude_column].notna().sum()}개 주소 변환 성공")
    
    return df


def reverse_geocode(df: pd.DataFrame,
                   longitude_column: str,
                   latitude_column: str,
                   address_column: str = "address",
                   road_address_column: str = "road_address",
                   include_details: bool = True,
                   save_json: Optional[Union[str, bool]] = None,
                   delay: float = 0.1) -> pd.DataFrame:
    """
    좌표 컬럼을 주소로 변환하여 데이터프레임에 추가
    
    카카오 API는 한 번의 호출로 도로명 주소와 지번 주소를 모두 반환합니다.
    include_details=True일 경우 시도, 시군구, 읍면동리 등 상세 정보도 함께 가져옵니다.
    
    Args:
        df: 입력 데이터프레임
        longitude_column: 경도 컬럼명
        latitude_column: 위도 컬럼명
        address_column: 지번 주소 컬럼명 (기본값: "address")
        road_address_column: 도로명 주소 컬럼명 (기본값: "road_address")
        include_details: 상세 정보 포함 여부 (기본값: True)
            - True: 도로명/지번 주소 + 시도, 시군구, 읍면동리, 건물명, 우편번호 등 모든 정보
            - False: 도로명 주소와 지번 주소만
        save_json: JSON 파일 저장 옵션 (기본값: None)
            - None: 저장하지 않음
            - True 또는 "auto": 자동으로 파일명 생성 (reverse_geocode_YYYYMMDD_HHMMSS.json)
            - 문자열: 지정한 경로에 저장 (여러 행일 경우 인덱스 추가)
        delay: API 호출 간 지연 시간(초) - API 제한을 피하기 위해 (기본값: 0.1)
    
    Returns:
        변환 결과가 추가된 데이터프레임
        
        include_details=True일 경우 추가되는 컬럼:
        - 도로명 주소 관련: road_zone_no (우편번호), road_region_1depth (시도), 
          road_region_2depth (시군구), road_region_3depth (읍면동), road_name (도로명), 
          road_main_building_no (건물 본번), road_sub_building_no (건물 부번), 
          road_building_name (건물명), road_underground_yn (지하 여부)
        - 지번 주소 관련: address_region_1depth (시도), address_region_2depth (시군구),
          address_region_3depth (동/리), address_region_3depth_h (행정동명),
          address_h_code (행정 코드), address_b_code (법정 코드),
          address_main_no (지번 주번지), address_sub_no (지번 부번지),
          address_mountain_yn (산 여부)
    
    Example:
        >>> import pandas as pd
        >>> from kakao_geocoding import reverse_geocode
        >>> 
        >>> df = pd.DataFrame({
        ...     'name': ['위치1', '위치2'],
        ...     'lon': [127.0276108, 127.0286108],
        ...     'lat': [37.4979420, 37.4989420]
        ... })
        >>> 
        >>> # 기본 사용 (모든 상세 정보 포함)
        >>> result = reverse_geocode(df, 'lon', 'lat')
        >>> print(result[['lon', 'lat', 'road_address', 'road_region_1depth', 'road_region_2depth']])
        >>> 
        >>> # 간단한 주소만 필요한 경우
        >>> result = reverse_geocode(df, 'lon', 'lat', include_details=False)
        >>> print(result[['lon', 'lat', 'road_address', 'address']])
    """
    if longitude_column not in df.columns:
        raise ValueError(f"컬럼 '{longitude_column}'이 데이터프레임에 없습니다.")
    if latitude_column not in df.columns:
        raise ValueError(f"컬럼 '{latitude_column}'이 데이터프레임에 없습니다.")
    
    df = df.copy()
    api = _get_api_instance()
    
    # 기본 컬럼 초기화
    df[address_column] = None
    df[road_address_column] = None
    
    # 상세 정보 컬럼 초기화
    if include_details:
        detail_columns = [
            # 도로명 주소 상세
            "road_zone_no", "road_region_1depth", "road_region_2depth", "road_region_3depth",
            "road_name", "road_main_building_no", "road_sub_building_no", 
            "road_building_name", "road_underground_yn",
            # 지번 주소 상세
            "address_region_1depth", "address_region_2depth", "address_region_3depth",
            "address_region_3depth_h", "address_h_code", "address_b_code",
            "address_main_no", "address_sub_no", "address_mountain_yn"
        ]
        for col in detail_columns:
            df[col] = None
    
    print(f"역지오코딩 시작: 총 {len(df)}개 좌표 처리 중...")
    if include_details:
        print("상세 정보 포함: 시도, 시군구, 읍면동리, 건물명, 우편번호 등")
    
    # JSON 저장 경로 설정
    json_base_path = None
    if save_json:
        if save_json is True or save_json == "auto":
            # 자동 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_base_path = f"reverse_geocode_{timestamp}"
        else:
            json_base_path = save_json
    
    for idx, row in df.iterrows():
        lon = row[longitude_column]
        lat = row[latitude_column]
        
        # JSON 저장 경로 결정
        json_path = None
        if json_base_path:
            if len(df) == 1:
                # 단일 행인 경우
                json_path = f"{json_base_path}.json"
            else:
                # 여러 행인 경우 인덱스 추가
                json_path = f"{json_base_path}_{idx}.json"
        
        result = api._reverse_geocode_coords(lon, lat, include_details=include_details, save_json=json_path)
        
        if result:
            # 기본 주소 정보
            df.at[idx, address_column] = result.get("address", "")
            df.at[idx, road_address_column] = result.get("road_address", "")
            
            # 상세 정보
            if include_details:
                # 도로명 주소 상세
                df.at[idx, "road_zone_no"] = result.get("road_zone_no", "")
                df.at[idx, "road_region_1depth"] = result.get("road_region_1depth", "")
                df.at[idx, "road_region_2depth"] = result.get("road_region_2depth", "")
                df.at[idx, "road_region_3depth"] = result.get("road_region_3depth", "")
                df.at[idx, "road_name"] = result.get("road_name", "")
                df.at[idx, "road_main_building_no"] = result.get("road_main_building_no", "")
                df.at[idx, "road_sub_building_no"] = result.get("road_sub_building_no", "")
                df.at[idx, "road_building_name"] = result.get("road_building_name", "")
                df.at[idx, "road_underground_yn"] = result.get("road_underground_yn", "")
                
                # 지번 주소 상세
                df.at[idx, "address_region_1depth"] = result.get("address_region_1depth", "")
                df.at[idx, "address_region_2depth"] = result.get("address_region_2depth", "")
                df.at[idx, "address_region_3depth"] = result.get("address_region_3depth", "")
                df.at[idx, "address_region_3depth_h"] = result.get("address_region_3depth_h", "")
                df.at[idx, "address_h_code"] = result.get("address_h_code", "")
                df.at[idx, "address_b_code"] = result.get("address_b_code", "")
                df.at[idx, "address_main_no"] = result.get("address_main_no", "")
                df.at[idx, "address_sub_no"] = result.get("address_sub_no", "")
                df.at[idx, "address_mountain_yn"] = result.get("address_mountain_yn", "")
        
        # API 제한을 피하기 위한 지연
        if delay > 0:
            time.sleep(delay)
        
        # 진행 상황 출력
        if (idx + 1) % 10 == 0:
            print(f"진행 중: {idx + 1}/{len(df)} ({((idx+1)/len(df)*100):.1f}%)")
    
    success_count = df[road_address_column].notna().sum()
    print(f"역지오코딩 완료: {success_count}개 좌표 변환 성공")
    
    return df
