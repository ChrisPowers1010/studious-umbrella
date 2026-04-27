$screenshotsPath = "C:\temp\Screenshots"
$shareXConfigDir = Join-Path $env:APPDATA "ShareX"
$appConfigPath   = Join-Path $shareXConfigDir "ApplicationConfig.json"

New-Item -ItemType Directory -Force -Path $screenshotsPath | Out-Null
Write-Host "Created: $screenshotsPath" -ForegroundColor Green

if (-not (Test-Path $shareXConfigDir)) {
    Write-Host "Launch ShareX once first, then re-run this script." -ForegroundColor Yellow
    exit 0
}

if (Test-Path $appConfigPath) {
    Copy-Item $appConfigPath "$appConfigPath.bak" -Force
    $config = Get-Content $appConfigPath -Raw | ConvertFrom-Json
} else {
    $config = [PSCustomObject]@{}
}

$config | Add-Member -Force -NotePropertyName "ScreenshotsFolder"   -NotePropertyValue $screenshotsPath
$config | Add-Member -Force -NotePropertyName "FileNamingPattern"    -NotePropertyValue "%y-%mo-%d_%h-%mi-%s"
$config | Add-Member -Force -NotePropertyName "SaveImageToFile"      -NotePropertyValue $true
$config | Add-Member -Force -NotePropertyName "CopyImageToClipboard" -NotePropertyValue $true
$config | ConvertTo-Json -Depth 10 | Set-Content $appConfigPath -Encoding UTF8
Write-Host "ShareX config updated." -ForegroundColor Green

$hotkeys = @(
    [PSCustomObject]@{ HotkeyType="CaptureRegion";       Hotkey="Ctrl+PrintScreen";       Description="Capture region" },
    [PSCustomObject]@{ HotkeyType="CaptureRegionAnnotate"; Hotkey="Ctrl+Shift+PrintScreen"; Description="Capture region + annotate" },
    [PSCustomObject]@{ HotkeyType="CaptureActiveWindow"; Hotkey="PrintScreen";             Description="Capture active window" }
)
$hotkeys | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $shareXConfigDir "HotkeysConfig.json") -Encoding UTF8
Write-Host "Done. Restart ShareX." -ForegroundColor Yellow
