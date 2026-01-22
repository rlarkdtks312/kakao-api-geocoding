# Git PATH 영구 추가 스크립트
# 관리자 권한으로 실행해야 할 수 있습니다.

Write-Host "Git PATH 추가 중..." -ForegroundColor Yellow

$gitPath = "C:\Program Files\Git\cmd"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

# Git 경로가 이미 있는지 확인
if ($currentPath -notlike "*$gitPath*") {
    # 사용자 PATH에 추가
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$gitPath", "User")
    Write-Host "✓ Git 경로가 사용자 PATH에 추가되었습니다." -ForegroundColor Green
    Write-Host ""
    Write-Host "새 PowerShell 창을 열어서 다음 명령어로 확인하세요:" -ForegroundColor Cyan
    Write-Host "  git --version" -ForegroundColor White
} else {
    Write-Host "✓ Git 경로가 이미 PATH에 포함되어 있습니다." -ForegroundColor Green
}

# 현재 세션에도 즉시 적용
$env:Path += ";$gitPath"

Write-Host ""
Write-Host "현재 세션에서 Git 버전 확인:" -ForegroundColor Cyan
git --version
