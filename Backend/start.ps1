# E-Mapp Backend — Start / Restart
# Chạy: .\start.ps1
# Đổi port : .\start.ps1 -Port 8889

param([int]$Port = 8888)

Set-Location $PSScriptRoot

Write-Host ""
Write-Host "  ╔══════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║       E-Mapp Backend API         ║" -ForegroundColor Cyan
Write-Host "  ║       http://localhost:$Port      ║" -ForegroundColor Cyan
Write-Host "  ╚══════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ── Kill tiến trình đang chiếm port ──────────────────────────────────────────
$conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($conn) {
    $pid_ = $conn.OwningProcess
    $pname = (Get-Process -Id $pid_ -ErrorAction SilentlyContinue).ProcessName
    Write-Host "  Stopping '$pname' (PID $pid_) on port $Port..." -ForegroundColor Yellow
    Stop-Process -Id $pid_ -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 800
}

# ── Tạo venv nếu chưa có ─────────────────────────────────────────────────────
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "  [setup] Tao moi truong ao Python..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [loi] Khong tim thay Python 3. Cai Python 3.10+ truoc." -ForegroundColor Red
        pause; exit 1
    }
}

# ── Kích hoạt venv ────────────────────────────────────────────────────────────
& ".venv\Scripts\Activate.ps1"

# ── Cài requirements nếu chưa có Flask ───────────────────────────────────────
python -c "import flask" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [setup] Cai dat thu vien..." -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host ""
}

# ── Tạo .env nếu chưa có ─────────────────────────────────────────────────────
if (-not (Test-Path ".env")) {
    Write-Host "  [setup] Tao .env mac dinh..." -ForegroundColor Yellow
    @"
PORT=8888
JWT_SECRET=change-this-secret-in-production
JWT_EXPIRES_IN=7d
FLASK_ENV=development
"@ | Set-Content ".env"
    Write-Host "  [!] Da tao .env — hay cap nhat cac key truoc khi deploy!" -ForegroundColor Yellow
    Write-Host ""
}

# ── Khởi động ─────────────────────────────────────────────────────────────────
$env:PORT = $Port
Write-Host "  Starting..." -ForegroundColor Green
Write-Host ""
python server.py
