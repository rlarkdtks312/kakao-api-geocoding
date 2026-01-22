# Git 설치 가이드

Git이 설치되어 있지 않아 GitHub에 배포할 수 없습니다. 다음 방법으로 Git을 설치하세요.

## 방법 1: Git 공식 웹사이트에서 설치 (권장)

1. **Git 다운로드**
   - https://git-scm.com/download/win 방문
   - 자동으로 Windows용 설치 프로그램 다운로드 시작

2. **설치 프로그램 실행**
   - 다운로드한 `.exe` 파일 실행
   - 기본 설정으로 설치 진행 (Next 클릭)
   - **중요**: "Git from the command line and also from 3rd-party software" 옵션 선택 (기본값)

3. **설치 확인**
   - PowerShell 또는 CMD를 새로 열기 (중요!)
   - 다음 명령어 실행:
   ```bash
   git --version
   ```
   - 버전 정보가 표시되면 설치 완료

## 방법 2: winget 사용 (Windows 10/11)

PowerShell을 관리자 권한으로 실행한 후:

```powershell
winget install --id Git.Git -e --source winget
```

## 방법 3: Chocolatey 사용 (Chocolatey가 설치된 경우)

```powershell
choco install git
```

## 설치 후 다음 단계

Git 설치가 완료되면:

1. **PowerShell 또는 CMD를 새로 열기** (중요: 기존 창은 닫고 새로 열어야 PATH가 적용됨)

2. 프로젝트 디렉토리로 이동:
   ```bash
   cd C:\Users\BNA_Server\geocoding
   ```

3. Git 저장소 초기화:
   ```bash
   git init
   ```

4. GitHub 저장소 생성 후 원격 저장소 추가:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
   ```

5. 파일 추가 및 커밋:
   ```bash
   git add .
   git commit -m "Initial commit: 카카오 지오코딩 모듈"
   git branch -M main
   git push -u origin main
   ```

## 문제 해결

### Git 설치 후에도 명령어를 찾을 수 없는 경우

1. PowerShell/CMD를 완전히 종료하고 새로 열기
2. 시스템 재시작 (가장 확실한 방법)
3. Git 설치 경로 확인:
   - 기본 경로: `C:\Program Files\Git\cmd\git.exe`
   - PATH 환경 변수에 추가되어 있는지 확인

### PATH 확인 방법

PowerShell에서:
```powershell
$env:PATH -split ';' | Select-String -Pattern 'Git'
```

Git 경로가 보이지 않으면 수동으로 PATH에 추가해야 합니다.

### PATH에 Git 경로 추가하기

PowerShell에서 다음 명령어를 실행하세요:

```powershell
# Git 경로를 사용자 PATH에 영구적으로 추가
$gitPath = "C:\Program Files\Git\cmd"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$gitPath*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$gitPath", "User")
    Write-Host "Git 경로가 PATH에 추가되었습니다. 새 PowerShell 창을 열어주세요."
} else {
    Write-Host "Git 경로가 이미 PATH에 포함되어 있습니다."
}
```

또는 `fix_git_path.ps1` 스크립트를 실행하세요:

```powershell
.\fix_git_path.ps1
```

**중요**: PATH를 수정한 후에는 **새 PowerShell 창을 열어야** 변경사항이 적용됩니다.
