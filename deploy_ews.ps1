# Praeventix EWS - Platinum Deployment Launcher
# This script starts the full stack: Backend (BentoML) and Frontend (Next.js)

Write-Host "🚀 Starting Praeventix EWS Platinum Stack..." -ForegroundColor Cyan

# 1. Start Backend
Write-Host "🧠 Launching Multi-Agent AI Backend on port 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; py -m bentoml serve service:BankRiskService --port 8000"

# 2. Wait for Backend (Briefly)
Start-Sleep -Seconds 5

# 3. Start Frontend
Write-Host "🌐 Launching Enterprise Dashboard on port 3000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev"

Write-Host "✅ Full Stack Deployment in Progress!" -ForegroundColor Cyan
Write-Host "Monitor: http://localhost:3000/customers" -ForegroundColor Gray
Write-Host "Showcase: Full_Project_Showcase.html" -ForegroundColor Gray
