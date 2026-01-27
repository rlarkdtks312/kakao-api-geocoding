"""
호환용 래퍼 모듈 (Deprecated)

기존 코드(`from kakao_geocoding import geocode, reverse_geocode`)가 깨지지 않도록 유지합니다.
새 기능(Kakao/Naver 분기)은 `geocoding.py`를 사용하세요.
"""

from __future__ import annotations

import pandas as pd
from typing import Optional, Union

from geocoding import (  # noqa: F401
    KakaoGeocodingAPI,
    geocode as _geocode,
    reverse_geocode as _reverse_geocode,
)


def geocode(
    df: pd.DataFrame,
    address_column: str,
    longitude_column: str = "longitude",
    latitude_column: str = "latitude",
    delay: float = 0.1,
) -> pd.DataFrame:
    return _geocode(
        df=df,
        address_column=address_column,
        longitude_column=longitude_column,
        latitude_column=latitude_column,
        delay=delay,
        provider="kakao",
    )


def reverse_geocode(
    df: pd.DataFrame,
    longitude_column: str,
    latitude_column: str,
    address_column: str = "address",
    road_address_column: str = "road_address",
    include_details: bool = True,
    save_json: Optional[Union[str, bool]] = None,
    delay: float = 0.1,
) -> pd.DataFrame:
    return _reverse_geocode(
        df=df,
        longitude_column=longitude_column,
        latitude_column=latitude_column,
        address_column=address_column,
        road_address_column=road_address_column,
        include_details=include_details,
        save_json=save_json,
        delay=delay,
        provider="kakao",
    )
