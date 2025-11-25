# Many-Agents 开发模式启动脚本

Write-Host "启动 Many-Agents 开发环境..." -ForegroundColor Green

# 1. 启动 Python 后端服务
Write-Host "启动 Python 后端服务..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python python/server.py"

# 2. 等待后端服务启动
Write-Host "等待后端服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# 3. 启动 Electron 开发模式
Write-Host "启动 Electron 应用..." -ForegroundColor Yellow
npm run electron:dev
