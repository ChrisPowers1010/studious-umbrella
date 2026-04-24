# Safely sync local repo when `git pull` is blocked by untracked files.
# Run from repository root:
#   powershell -ExecutionPolicy Bypass -File .\sync_repo_safe.ps1

$ErrorActionPreference = "Stop"

Write-Host "Creating backup folder..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path .\local_backup | Out-Null

Copy-Item .\it_workflow_agent.py .\local_backup\ -ErrorAction SilentlyContinue
Copy-Item .\ui_app.py .\local_backup\ -ErrorAction SilentlyContinue
Copy-Item .\examples .\local_backup\ -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Cleaning untracked files that block pull..." -ForegroundColor Cyan
git clean -fd

Write-Host "Pulling latest changes on current branch..." -ForegroundColor Cyan
git pull

$hasUi = Test-Path .\ui_app.py
if (-not $hasUi) {
  Write-Host "ui_app.py not found on current branch. Checking for feature branch..." -ForegroundColor Yellow
  $branchRef = "origin/codex/develop-it-workflow-assistant-agent"
  $hasFeature = git branch -r | Select-String -SimpleMatch $branchRef

  if ($hasFeature) {
    Write-Host "Switching to feature branch with UI files..." -ForegroundColor Yellow
    git checkout -B codex/develop-it-workflow-assistant-agent $branchRef
    git pull
  }
}

Write-Host "Done. Verify files:" -ForegroundColor Green
Get-ChildItem .\it_workflow_agent.py -ErrorAction SilentlyContinue
Get-ChildItem .\examples\ticket.json -ErrorAction SilentlyContinue
Get-ChildItem .\ui_app.py -ErrorAction SilentlyContinue

if (-not (Test-Path .\ui_app.py)) {
  Write-Host "UI file still missing on this branch. CLI is available. Run triage with:" -ForegroundColor Yellow
  Write-Host "python .\\it_workflow_agent.py triage --ticket-file .\\examples\\ticket.json" -ForegroundColor Yellow
}
