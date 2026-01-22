# GitHub 배포 가이드

이 문서는 이 프로젝트를 GitHub에 배포하기 위한 가이드입니다.

## 배포 전 체크리스트

### ✅ 보안 확인
- [x] `config.py`가 `.gitignore`에 포함되어 있음
- [x] `config.py.example`에 실제 API 키가 아닌 플레이스홀더만 포함
- [x] 민감한 정보가 코드에 하드코딩되어 있지 않음

### ✅ 파일 확인
- [x] `.gitignore`에 불필요한 파일들이 포함되어 있음
  - 결과 파일 (`result.xlsx`)
  - API 응답 JSON 파일 (`reverse_geocode_*.json`)
  - 가상환경 (`.venv/`)
  - IDE 설정 파일
- [x] `config.py.example` 파일이 존재하고 올바른 형식임
- [x] `README.md`가 충분히 상세함

### ✅ 포함할 파일
- [x] `kakao_geocoding.py` - 메인 모듈
- [x] `requirements.txt` - 의존성 목록
- [x] `config.py.example` - 설정 파일 예제
- [x] `setup_and_run.bat` - Windows 환경 설정 스크립트
- [x] `example.ipynb` - 사용 예제
- [x] `addresses.xlsx` - 예제 데이터 파일
- [x] `README.md` - 프로젝트 문서
- [x] `.gitignore` - Git 무시 파일 목록

## 사전 요구사항

### Git 설치 확인

Git이 설치되어 있지 않다면 먼저 설치해야 합니다.

```bash
# Git 설치 여부 확인
git --version
```

Git이 설치되어 있지 않다면 `GIT_SETUP.md` 파일을 참고하여 설치하세요.

## GitHub 배포 단계

### 1. GitHub 저장소 생성

1. GitHub에 로그인
2. 새 저장소 생성 (New Repository)
3. 저장소 이름 설정 (예: `kakao-geocoding`)
4. Public 또는 Private 선택
5. **README, .gitignore, LICENSE는 추가하지 않음** (이미 있음)

### 2. 로컬 Git 저장소 초기화 (아직 안 했다면)

```bash
# Git 저장소 초기화
git init

# 원격 저장소 추가
git remote add origin https://github.com/YOUR_USERNAME/kakao-geocoding.git
```

### 3. 파일 추가 및 커밋

```bash
# 모든 파일 추가
git add .

# 커밋
git commit -m "Initial commit: 카카오 지오코딩 모듈"

# 메인 브랜치 이름 확인 및 설정
git branch -M main

# GitHub에 푸시
git push -u origin main
```

### 4. 배포 후 확인

- [ ] GitHub 저장소에서 모든 파일이 올바르게 업로드되었는지 확인
- [ ] `config.py`가 업로드되지 않았는지 확인 (`.gitignore` 확인)
- [ ] `README.md`가 올바르게 표시되는지 확인
- [ ] `example.ipynb`가 GitHub에서 렌더링되는지 확인

## 추가 권장 사항

### LICENSE 파일 추가 (선택사항)

프로젝트에 라이선스를 추가하려면:

1. GitHub에서 저장소 생성 시 LICENSE 템플릿 선택
2. 또는 로컬에서 LICENSE 파일 생성 후 추가

### GitHub Releases (선택사항)

버전 관리가 필요하다면:

1. GitHub 저장소의 Releases 섹션으로 이동
2. "Create a new release" 클릭
3. 태그 버전 입력 (예: `v1.0.0`)
4. 릴리스 노트 작성
5. 소스 코드를 zip 파일로 다운로드 가능하게 설정

### GitHub Pages (선택사항)

문서를 웹으로 호스팅하려면:

1. Settings > Pages로 이동
2. Source를 `main` 브랜치로 설정
3. `/docs` 폴더 또는 루트 선택

## 문제 해결

### config.py가 실수로 커밋된 경우

```bash
# Git 히스토리에서 제거
git rm --cached config.py
git commit -m "Remove config.py from repository"

# .gitignore에 추가되어 있는지 확인
# 이미 추가되어 있다면, 다음 커밋부터는 무시됨
```

### 민감한 정보가 커밋된 경우

1. GitHub에서 해당 파일 삭제
2. Git 히스토리에서 완전히 제거 (필요시)
3. API 키 재발급 (보안상 권장)

## 참고

- 카카오 API 사용 약관 준수
- API 키는 절대 공개 저장소에 커밋하지 마세요
- `.gitignore`를 정기적으로 확인하세요
