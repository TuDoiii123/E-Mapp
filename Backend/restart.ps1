# Kill process đang dùng port 8888
$port = 8888
$process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -First 1

if ($process) {
    Write-Host "Killing process $process on port $port..." -ForegroundColor Yellow
    Stop-Process -Id $process -Force
    Start-Sleep -Seconds 1
}

Write-Host "    Starting server..." -ForegroundColor Green
node server.js
