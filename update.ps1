$repo = "D:\Web\Reimbursement"
Set-Location $repo

Write-Host "=== Discard __pycache__ local changes ===" -ForegroundColor Cyan
git checkout -- fastapi/__pycache__/

Write-Host "=== Git pull ===" -ForegroundColor Cyan
git pull

Write-Host "=== Rebuild frontend ===" -ForegroundColor Cyan
Push-Location ABUS
npm run build
Pop-Location

Write-Host "=== Restart backend ===" -ForegroundColor Cyan
Get-Process -Name python -ErrorAction SilentlyContinue | ForEach-Object {
    $cmd = (Get-WmiObject Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine
    if ($cmd -match "main\.py") {
        $_.Kill()
        Write-Host "Backend stopped (PID $($_.Id))" -ForegroundColor Yellow
    }
}

$logFile = Join-Path $repo "..\fastapi.log"
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "Set-Location '$repo\fastapi'; python main.py" -WindowStyle Normal

Write-Host "=== Done ===" -ForegroundColor Green
