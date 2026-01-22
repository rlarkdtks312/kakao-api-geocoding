@echo off
chcp 65001 >nul
echo ========================================
echo 카카오 지오코딩 모듈 환경 설정 및 실행
echo ========================================
echo.

REM 현재 디렉토리로 이동
cd /d "%~dp0"

REM 1. Python 설치 확인
echo [1단계] Python 설치 확인 중...
python --version >nul 2>&1
if errorlevel 1 (
    echo 오류: Python이 설치되어 있지 않습니다.
    echo Python을 설치한 후 다시 실행하세요.
    pause
    exit /b 1
)

python --version
echo Python 확인 완료
echo.

REM 2. 가상환경 생성
echo [2단계] 가상환경 생성 중...
if exist .venv (
    echo 가상환경이 이미 존재합니다. 기존 가상환경을 사용합니다.
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo 오류: 가상환경 생성 실패
        pause
        exit /b 1
    )
    echo 가상환경 생성 완료
)
echo.

REM 3. 가상환경 활성화 및 패키지 설치
echo [3단계] 가상환경 활성화 및 패키지 설치 중...
call .venv\Scripts\activate.bat

REM pip 업그레이드
python -m pip install --upgrade pip --quiet

REM requirements.txt 확인
if not exist requirements.txt (
    echo 오류: requirements.txt 파일이 없습니다.
    pause
    exit /b 1
)

REM 패키지 설치
echo 패키지 설치 중...
pip install -r requirements.txt
if errorlevel 1 (
    echo 오류: 패키지 설치 실패
    pause
    exit /b 1
)
echo 패키지 설치 완료
echo.

REM 4. config.py 확인
echo [4단계] 설정 파일 확인 중...
if not exist config.py (
    echo config.py 파일이 없습니다.
    if exist config.py.example (
        echo config.py.example을 복사하여 config.py를 생성합니다.
        copy config.py.example config.py >nul
        echo.
        echo ========================================
        echo 중요: config.py 파일을 열어서 API 키를 입력하세요!
        echo ========================================
        echo.
    ) else (
        echo config.py.example 파일도 없습니다.
    )
) else (
    echo config.py 파일이 존재합니다.
)
echo.

REM 5. addresses.xlsx 확인 (패키지 설치 후)
echo [5단계] 예제 파일 확인 중...
if not exist addresses.xlsx (
    echo addresses.xlsx 파일이 없습니다.
    echo 예제 파일을 생성합니다...
    python -c "import pandas as pd; df = pd.DataFrame({'name': ['(주)씨에스리'], 'address': ['서울시 마포구 월드컵북로 396 (상암동, 누리꿈스퀘어) 비즈니스타워 8층']}); df.to_excel('addresses.xlsx', index=False); print('addresses.xlsx 파일 생성 완료')"
    if errorlevel 1 (
        echo 경고: addresses.xlsx 파일 생성 실패 (나중에 수동으로 생성 가능)
    )
) else (
    echo addresses.xlsx 파일이 존재합니다.
)
echo.

REM 6. 환경 설정 완료 및 실행 옵션
echo ========================================
echo 환경 설정 완료!
echo ========================================
echo.
echo 다음 중 하나를 선택하세요:
echo.
echo [1] Jupyter Notebook 실행 (example.ipynb)
echo [2] Python 인터프리터 실행
echo [3] 종료
echo.
set /p choice="선택 (1-3): "

if "%choice%"=="1" (
    echo.
    echo Jupyter Notebook을 실행합니다...
    jupyter notebook example.ipynb
) else if "%choice%"=="2" (
    echo.
    echo Python 인터프리터를 실행합니다...
    echo 가상환경이 활성화된 상태입니다.
    echo 모듈을 사용하려면: from kakao_geocoding import geocode, reverse_geocode
    echo.
    python
) else (
    echo 종료합니다.
    deactivate
    exit /b 0
)

REM 가상환경 비활성화는 사용자가 직접 종료할 때까지 유지
REM deactivate
