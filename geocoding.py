"""
Kakao / Naver API를 사용한 지오코딩 및 역지오코딩 모듈

이 모듈은 두 Provider를 지원합니다.
- Kakao Local API
- Naver Maps (NCP) Geocoding API

공개 함수는 데이터프레임(엑셀/CSV 로딩 결과)을 입력으로 받아 변환 결과 컬럼을 추가합니다.
- geocode: 주소 → (경도, 위도)
- reverse_geocode: (경도, 위도) → (도로명/지번 주소 및 상세 정보)
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

import pandas as pd
import requests


class KakaoGeocodingAPI:
    """카카오 지오코딩 API 클래스 (내부 사용)"""

    BASE_URL = "https://dapi.kakao.com/v2/local"

    def __init__(self, api_key: Optional[str] = None):
        if api_key is None:
            api_key = os.getenv("KAKAO_REST_API_KEY")
            if not api_key:
                try:
                    from config import KAKAO_REST_API_KEY  # type: ignore

                    api_key = KAKAO_REST_API_KEY
                except ImportError:
                    raise ValueError(
                        "API 키를 찾을 수 없습니다. "
                        "환경변수 KAKAO_REST_API_KEY를 설정하거나 "
                        "config.py 파일에 KAKAO_REST_API_KEY를 정의하세요."
                    )

        self.api_key = api_key
        self.headers = {"Authorization": f"KakaoAK {self.api_key}"}

    def geocode_address(self, address: str) -> Optional[dict]:
        """주소를 좌표로 변환 (단일 주소)"""
        if pd.isna(address) or address == "":
            return None

        url = f"{self.BASE_URL}/search/address.json"
        params = {"query": str(address), "size": 1}

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)

            if response.status_code == 403:
                _print_kakao_403_details(response, self.api_key, context="지오코딩")

            response.raise_for_status()
            data = response.json()

            documents = data.get("documents", [])
            if documents:
                doc = documents[0]
                return {
                    "longitude": float(doc.get("x", 0) or 0),
                    "latitude": float(doc.get("y", 0) or 0),
                    "address_name": doc.get("address_name", ""),
                    "address_type": doc.get("address_type", ""),
                }
        except requests.exceptions.HTTPError as e:
            if getattr(e.response, "status_code", None) != 403:
                print(f"지오코딩 HTTP 오류 (주소: {address}): {str(e)}")
        except Exception as e:
            print(f"지오코딩 오류 (주소: {address}): {str(e)}")

        return None

    def reverse_geocode_coords(
        self,
        longitude: float,
        latitude: float,
        include_details: bool = True,
        save_json: Optional[str] = None,
    ) -> Optional[dict]:
        """좌표를 주소로 변환 (단일 좌표)"""
        if pd.isna(longitude) or pd.isna(latitude):
            return None

        url = f"{self.BASE_URL}/geo/coord2address.json"
        params = {"x": str(longitude), "y": str(latitude), "input_coord": "WGS84"}

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)

            if response.status_code == 403:
                _print_kakao_403_details(response, self.api_key, context="역지오코딩")

            response.raise_for_status()
            data = response.json()

            if save_json:
                _save_api_json(
                    save_json=save_json,
                    request_url=url,
                    request_params=params,
                    longitude=longitude,
                    latitude=latitude,
                    response=response,
                    data=data,
                )

            documents = data.get("documents", [])
            if not documents:
                return None

            doc = documents[0]
            result: Dict[str, Any] = {}

            # 도로명 주소 정보
            if "road_address" in doc and doc["road_address"]:
                road = doc["road_address"]
                result["road_address"] = road.get("address_name", "")
                result["road_zone_no"] = road.get("zone_no", "")

                if include_details:
                    result["road_region_1depth"] = road.get("region_1depth_name", "")
                    result["road_region_2depth"] = road.get("region_2depth_name", "")
                    result["road_region_3depth"] = road.get("region_3depth_name", "")
                    result["road_name"] = road.get("road_name", "")
                    result["road_main_building_no"] = road.get("main_building_no", "")
                    result["road_sub_building_no"] = road.get("sub_building_no", "")
                    result["road_building_name"] = road.get("building_name", "")
                    result["road_underground_yn"] = road.get("underground_yn", "")
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
            if "address" in doc and doc["address"]:
                addr = doc["address"]
                result["address"] = addr.get("address_name", "")

                if include_details:
                    result["address_region_1depth"] = addr.get("region_1depth_name", "")
                    result["address_region_2depth"] = addr.get("region_2depth_name", "")
                    result["address_region_3depth"] = addr.get("region_3depth_name", "")
                    result["address_region_3depth_h"] = addr.get("region_3depth_h_name", "")
                    result["address_h_code"] = addr.get("h_code", "")
                    result["address_b_code"] = addr.get("b_code", "")
                    result["address_main_no"] = addr.get("main_address_no", "")
                    result["address_sub_no"] = addr.get("sub_address_no", "")
                    result["address_mountain_yn"] = addr.get("mountain_yn", "")
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
            if getattr(e.response, "status_code", None) != 403:
                print(f"역지오코딩 HTTP 오류 (좌표: {longitude}, {latitude}): {str(e)}")
        except Exception as e:
            print(f"역지오코딩 오류 (좌표: {longitude}, {latitude}): {str(e)}")

        return None


class NaverGeocodingAPI:
    """
    네이버 지도(NCP) 지오코딩/역지오코딩 API 클래스 (내부 사용)

    필요 키:
    - NAVER_MAPS_API_KEY_ID: X-NCP-APIGW-API-KEY-ID
    - NAVER_MAPS_API_KEY: X-NCP-APIGW-API-KEY
    """

    # NCP Maps API 문서 기준 Base URL
    # - Geocoding: https://maps.apigw.ntruss.com/map-geocode/v2
    # - Reverse Geocoding: https://maps.apigw.ntruss.com/map-reversegeocode/v2
    BASE_URL = "https://maps.apigw.ntruss.com"

    def __init__(self, api_key_id: Optional[str] = None, api_key: Optional[str] = None):
        if api_key_id is None:
            api_key_id = os.getenv("NAVER_MAPS_API_KEY_ID")
        if api_key is None:
            api_key = os.getenv("NAVER_MAPS_API_KEY")

        if not api_key_id or not api_key:
            try:
                # Jupyter 등에서 config.py를 수정한 뒤에도 이전 값이 캐시될 수 있어
                # 필요 시 1회 reload를 시도합니다.
                import importlib

                import config  # type: ignore

                api_key_id = api_key_id or getattr(config, "NAVER_MAPS_API_KEY_ID", None)
                api_key = api_key or getattr(config, "NAVER_MAPS_API_KEY", None)

                if (not api_key_id or not api_key) and hasattr(importlib, "reload"):
                    importlib.reload(config)
                    api_key_id = api_key_id or getattr(config, "NAVER_MAPS_API_KEY_ID", None)
                    api_key = api_key or getattr(config, "NAVER_MAPS_API_KEY", None)
            except ImportError:
                pass

        if not api_key_id or not api_key:
            raise ValueError(
                "API 키를 찾을 수 없습니다. "
                "환경변수 NAVER_MAPS_API_KEY_ID / NAVER_MAPS_API_KEY를 설정하거나 "
                "config.py 파일에 NAVER_MAPS_API_KEY_ID / NAVER_MAPS_API_KEY를 정의하세요."
            )

        self.api_key_id = api_key_id
        self.api_key = api_key
        self.headers = {
            # NCP 문서 예시(curl) 기준으로 소문자 헤더를 사용합니다.
            # (HTTP 헤더는 원칙적으로 대소문자 무관하지만, 일부 게이트웨이/프록시에서
            # 케이스 이슈가 나는 사례가 있어 안전하게 맞춥니다.)
            "x-ncp-apigw-api-key-id": self.api_key_id,
            "x-ncp-apigw-api-key": self.api_key,
            "accept": "application/json",
        }

    def geocode_address(self, address: str) -> Optional[dict]:
        if pd.isna(address) or address == "":
            return None

        url = f"{self.BASE_URL}/map-geocode/v2/geocode"
        params = {"query": str(address)}

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code in (401, 403):
                _print_naver_auth_error(response)
            response.raise_for_status()
            data = response.json()

            addresses = data.get("addresses", [])
            if not addresses:
                return None

            first = addresses[0]
            return {
                "longitude": float(first.get("x", 0) or 0),
                "latitude": float(first.get("y", 0) or 0),
                "road_address": first.get("roadAddress", "") or "",
                "address": first.get("jibunAddress", "") or "",
            }
        except requests.exceptions.HTTPError as e:
            resp = getattr(e, "response", None)
            if resp is not None and resp.status_code in (401, 403):
                _print_naver_auth_error(resp)
            print(
                f"지오코딩 오류(Naver) (주소: {address}): "
                f"{getattr(resp, 'status_code', 'unknown')} {str(e)}"
            )
            return None
        except Exception as e:
            print(f"지오코딩 오류(Naver) (주소: {address}): {str(e)}")
            return None

    def reverse_geocode_coords(
        self,
        longitude: float,
        latitude: float,
        include_details: bool = True,
        save_json: Optional[str] = None,
    ) -> Optional[dict]:
        if pd.isna(longitude) or pd.isna(latitude):
            return None

        url = f"{self.BASE_URL}/map-reversegeocode/v2/gc"
        params = {
            "coords": f"{longitude},{latitude}",
            "output": "json",
            # roadaddr, addr 순으로 시도 (권장 조합)
            "orders": "roadaddr,addr",
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code in (401, 403):
                _print_naver_auth_error(response)
            response.raise_for_status()
            data = response.json()

            if save_json:
                _save_api_json(
                    save_json=save_json,
                    request_url=url,
                    request_params=params,
                    longitude=longitude,
                    latitude=latitude,
                    response=response,
                    data=data,
                )

            results = (data.get("results") or []) if isinstance(data, dict) else []
            if not results:
                return None

            road = _pick_naver_result(results, "roadaddr")
            addr = _pick_naver_result(results, "addr")
            base = road or addr or results[0]

            out: Dict[str, Any] = {
                "road_address": _naver_result_text(road) if road else "",
                "address": _naver_result_text(addr) if addr else "",
            }

            if include_details:
                # 공통 region 추출 (road 우선)
                region = (base.get("region") or {}) if isinstance(base, dict) else {}
                area1 = (region.get("area1") or {}).get("name", "")
                area2 = (region.get("area2") or {}).get("name", "")
                area3 = (region.get("area3") or {}).get("name", "")

                out["road_zone_no"] = ""  # Naver reverse 응답엔 우편번호가 없거나 제한적이라 빈값
                out["road_region_1depth"] = area1
                out["road_region_2depth"] = area2
                out["road_region_3depth"] = area3
                out["road_name"] = _naver_road_name(road) if road else ""
                out["road_main_building_no"] = ""
                out["road_sub_building_no"] = ""
                out["road_building_name"] = _naver_building_name(road) if road else ""
                out["road_underground_yn"] = ""

                out["address_region_1depth"] = area1
                out["address_region_2depth"] = area2
                out["address_region_3depth"] = area3
                out["address_region_3depth_h"] = ""
                out["address_h_code"] = ""
                out["address_b_code"] = ""
                out["address_main_no"] = ""
                out["address_sub_no"] = ""
                out["address_mountain_yn"] = ""

            return out
        except requests.exceptions.HTTPError as e:
            resp = getattr(e, "response", None)
            if resp is not None and resp.status_code in (401, 403):
                _print_naver_auth_error(resp)
            print(
                f"역지오코딩 오류(Naver) (좌표: {longitude}, {latitude}): "
                f"{getattr(resp, 'status_code', 'unknown')} {str(e)}"
            )
            return None
        except Exception as e:
            print(f"역지오코딩 오류(Naver) (좌표: {longitude}, {latitude}): {str(e)}")
            return None


_provider_instances: Dict[str, Any] = {}


def _get_provider(provider: str):
    p = (provider or "kakao").strip().lower()
    if p not in ("kakao", "naver"):
        raise ValueError("provider는 'kakao' 또는 'naver'만 지원합니다.")

    if p in _provider_instances:
        return _provider_instances[p]

    if p == "kakao":
        inst = KakaoGeocodingAPI()
    else:
        inst = NaverGeocodingAPI()

    _provider_instances[p] = inst
    return inst


def geocode(
    df: pd.DataFrame,
    address_column: str,
    longitude_column: str = "longitude",
    latitude_column: str = "latitude",
    delay: float = 0.1,
    provider: str = "kakao",
) -> pd.DataFrame:
    """
    주소 컬럼을 좌표로 변환하여 데이터프레임에 추가

    Args:
        df: 입력 데이터프레임
        address_column: 주소가 있는 컬럼명
        longitude_column: 경도 컬럼명
        latitude_column: 위도 컬럼명
        delay: API 호출 간 지연 시간(초)
        provider: 'kakao' | 'naver'
    """
    if address_column not in df.columns:
        raise ValueError(f"컬럼 '{address_column}'이 데이터프레임에 없습니다.")

    df = df.copy()
    api = _get_provider(provider)

    df[longitude_column] = None
    df[latitude_column] = None

    print(f"지오코딩 시작(provider={provider}): 총 {len(df)}개 주소 처리 중...")

    for i, (idx, row) in enumerate(df.iterrows(), start=1):
        address = row[address_column]
        result = api.geocode_address(address)

        if result:
            df.at[idx, longitude_column] = result.get("longitude")
            df.at[idx, latitude_column] = result.get("latitude")

        if delay > 0:
            time.sleep(delay)

        if i % 10 == 0:
            print(f"진행 중: {i}/{len(df)} ({(i/len(df)*100):.1f}%)")

    print(f"지오코딩 완료: {df[longitude_column].notna().sum()}개 주소 변환 성공")
    return df


def reverse_geocode(
    df: pd.DataFrame,
    longitude_column: str,
    latitude_column: str,
    address_column: str = "address",
    road_address_column: str = "road_address",
    include_details: bool = True,
    save_json: Optional[Union[str, bool]] = None,
    delay: float = 0.1,
    provider: str = "kakao",
) -> pd.DataFrame:
    """
    좌표 컬럼을 주소로 변환하여 데이터프레임에 추가

    Args:
        df: 입력 데이터프레임
        longitude_column: 경도 컬럼명
        latitude_column: 위도 컬럼명
        address_column: 지번 주소 컬럼명
        road_address_column: 도로명 주소 컬럼명
        include_details: 상세 정보 포함 여부
        save_json: JSON 파일 저장 옵션 (None/True/"auto"/str)
        delay: API 호출 간 지연 시간(초)
        provider: 'kakao' | 'naver'
    """
    if longitude_column not in df.columns:
        raise ValueError(f"컬럼 '{longitude_column}'이 데이터프레임에 없습니다.")
    if latitude_column not in df.columns:
        raise ValueError(f"컬럼 '{latitude_column}'이 데이터프레임에 없습니다.")

    df = df.copy()
    api = _get_provider(provider)

    df[address_column] = None
    df[road_address_column] = None

    detail_columns = [
        "road_zone_no",
        "road_region_1depth",
        "road_region_2depth",
        "road_region_3depth",
        "road_name",
        "road_main_building_no",
        "road_sub_building_no",
        "road_building_name",
        "road_underground_yn",
        "address_region_1depth",
        "address_region_2depth",
        "address_region_3depth",
        "address_region_3depth_h",
        "address_h_code",
        "address_b_code",
        "address_main_no",
        "address_sub_no",
        "address_mountain_yn",
    ]
    if include_details:
        for col in detail_columns:
            df[col] = None

    print(f"역지오코딩 시작(provider={provider}): 총 {len(df)}개 좌표 처리 중...")
    if include_details:
        print("상세 정보 포함: 시도, 시군구, 읍면동리, 건물명, 우편번호 등(가능한 범위)")

    json_base_path = None
    if save_json:
        if save_json is True or save_json == "auto":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_base_path = f"reverse_geocode_{provider}_{timestamp}"
        else:
            json_base_path = str(save_json)

    for i, (idx, row) in enumerate(df.iterrows(), start=1):
        lon = row[longitude_column]
        lat = row[latitude_column]

        json_path = None
        if json_base_path:
            if len(df) == 1:
                json_path = f"{json_base_path}.json"
            else:
                json_path = f"{json_base_path}_{idx}.json"

        result = api.reverse_geocode_coords(
            lon, lat, include_details=include_details, save_json=json_path
        )

        if result:
            df.at[idx, address_column] = result.get("address", "")
            df.at[idx, road_address_column] = result.get("road_address", "")

            if include_details:
                for col in detail_columns:
                    df.at[idx, col] = result.get(col, "")

        if delay > 0:
            time.sleep(delay)

        if i % 10 == 0:
            print(f"진행 중: {i}/{len(df)} ({(i/len(df)*100):.1f}%)")

    success_count = df[road_address_column].notna().sum()
    print(f"역지오코딩 완료: {success_count}개 좌표 변환 성공")
    return df


def kakao_geocode(*args, **kwargs) -> pd.DataFrame:
    kwargs["provider"] = "kakao"
    return geocode(*args, **kwargs)


def naver_geocode(*args, **kwargs) -> pd.DataFrame:
    kwargs["provider"] = "naver"
    return geocode(*args, **kwargs)


def kakao_reverse_geocode(*args, **kwargs) -> pd.DataFrame:
    kwargs["provider"] = "kakao"
    return reverse_geocode(*args, **kwargs)


def naver_reverse_geocode(*args, **kwargs) -> pd.DataFrame:
    kwargs["provider"] = "naver"
    return reverse_geocode(*args, **kwargs)


def _save_api_json(
    save_json: str,
    request_url: str,
    request_params: Dict[str, Any],
    longitude: float,
    latitude: float,
    response: requests.Response,
    data: Any,
) -> None:
    json_data = {
        "request": {
            "url": request_url,
            "params": request_params,
            "longitude": longitude,
            "latitude": latitude,
            "timestamp": datetime.now().isoformat(),
        },
        "response": {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "data": data,
        },
    }

    json_path = Path(save_json)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)


def _print_kakao_403_details(response: requests.Response, api_key: str, context: str) -> None:
    try:
        error_data = response.json()
        error_msg = error_data.get("msg", "알 수 없는 오류")
        error_code = error_data.get("code", "")
        print(f"{context} 오류 (403 Forbidden): {error_msg} (코드: {error_code})")
    except Exception:
        print(f"{context} 오류 (403 Forbidden): API 키 인증 실패")
    print("API 키 확인이 필요합니다. 카카오 개발자 콘솔에서:")
    print("1. REST API 키가 올바른지 확인")
    print("2. 로컬 API가 활성화되어 있는지 확인")
    print("3. 앱 도메인이 설정되어 있는지 확인")
    if api_key:
        print(f"현재 사용 중인 API 키(일부): {api_key[:10]}...")


def _pick_naver_result(results: list, name: str) -> Optional[dict]:
    for r in results:
        if isinstance(r, dict) and r.get("name") == name:
            return r
    return None


def _naver_result_text(result: Optional[dict]) -> str:
    if not result or not isinstance(result, dict):
        return ""
    txt = result.get("text")
    if isinstance(txt, str) and txt.strip():
        return txt.strip()

    # text가 없으면 region/land 기반으로 최대한 조합
    region = result.get("region") or {}
    land = result.get("land") or {}
    parts = [
        (region.get("area1") or {}).get("name", ""),
        (region.get("area2") or {}).get("name", ""),
        (region.get("area3") or {}).get("name", ""),
        (region.get("area4") or {}).get("name", ""),
    ]
    parts = [p for p in parts if p]

    land_name = land.get("name") or ""
    number1 = land.get("number1") or ""
    number2 = land.get("number2") or ""
    if land_name:
        parts.append(str(land_name))
    if number1:
        num = f"{number1}-{number2}" if number2 else f"{number1}"
        parts.append(num)

    return " ".join([str(p).strip() for p in parts if str(p).strip()])


def _naver_road_name(result: Optional[dict]) -> str:
    if not result or not isinstance(result, dict):
        return ""
    land = result.get("land") or {}
    # roadaddr 결과에서 land.name이 도로명인 경우가 많음
    name = land.get("name")
    return str(name).strip() if name else ""


def _naver_building_name(result: Optional[dict]) -> str:
    if not result or not isinstance(result, dict):
        return ""
    land = result.get("land") or {}
    addition0 = land.get("addition0") or {}
    name = addition0.get("value") if isinstance(addition0, dict) else ""
    return str(name).strip() if name else ""


def _print_naver_auth_error(response: requests.Response) -> None:
    """
    Naver OpenAPI Gateway 인증/권한 오류(401/403) 디버깅용 출력.
    - 401: 키 불일치/무효/다른 상품 키
    - 403: 권한/상품 미활성화/허용 정책(IP 등) 문제 가능
    """
    try:
        body = response.json()
    except Exception:
        body = response.text

    print("Naver API 인증/권한 오류 상세:")
    print(f"- status_code: {response.status_code}")
    print(f"- response: {body}")
    print("체크리스트:")
    print("- Naver Cloud Platform에서 'Maps'의 Geocoding/Reverse Geocoding 사용 설정 여부")
    print("- API Gateway 키 2종(ID/KEY)이 해당 프로젝트/상품의 값인지")
    print("- (설정한 경우) 호출 허용 정책(IP 제한 등)에 현재 환경이 포함되는지")

