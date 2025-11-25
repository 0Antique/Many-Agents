const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')
const { spawn } = require('child_process')

let mainWindow
let pythonProcess

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webviewTag: true
    }
  })

  // 开发环境加载 Vite 服务器
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    // 生产环境加载打包后的文件
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// 启动 Python 后端服务
function startPythonBackend() {
  const pythonPath = process.env.NODE_ENV === 'development' 
    ? 'python' 
    : path.join(process.resourcesPath, 'python', 'python.exe')
  
  const scriptPath = process.env.NODE_ENV === 'development'
    ? path.join(__dirname, '../python/server.py')
    : path.join(process.resourcesPath, 'python', 'server.py')

  pythonProcess = spawn(pythonPath, [scriptPath])

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python: ${data}`)
  })

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python Error: ${data}`)
  })

  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`)
  })
}

app.whenReady().then(() => {
  createWindow()
  startPythonBackend()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (pythonProcess) {
    pythonProcess.kill()
  }
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// IPC 通信处理
ipcMain.handle('send-question', async (event, data) => {
  // 转发到 Python 后端
  return { success: true }
})
