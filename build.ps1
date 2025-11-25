# Many-Agents 构建脚本

# 1. 安装 Node.js 依赖
Write-Host "安装 Node.js 依赖..." -ForegroundColor Green
npm install

# 2. 安装 Python 依赖
Write-Host "安装 Python 依赖..." -ForegroundColor Green
pip install -r requirements.txt

# 3. 安装 Playwright 浏览器
Write-Host "安装 Playwright 浏览器..." -ForegroundColor Green
python -m playwright install chromium

# 4. 构建 Vue 前端
Write-Host "构建 Vue 前端..." -ForegroundColor Green
npm run build

# 5. 打包 Electron 应用
Write-Host "打包 Electron 应用..." -ForegroundColor Green
npm run electron:build

Write-Host "构建完成！" -ForegroundColor Cyan
Write-Host "安装包位于: dist-electron 目录" -ForegroundColor Cyan
