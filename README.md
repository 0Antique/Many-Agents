# Many-Agents

一款同时与多个 AI 大模型对话的桌面应用程序。

## 功能特点

- 🤖 **多模型支持**：同时与豆包、DeepSeek、腾讯元宝、Kimi 等多个 AI 大模型对话
- 🎯 **统一输入**：一次输入，多个模型同时响应
- 📊 **对比查看**：通过标签页轻松切换查看不同模型的回答
- 💾 **状态保存**：自动保存登录状态，无需重复登录
- 🎨 **美观界面**：基于 Vue 3 和 Element Plus 的现代化 UI

## 技术栈

### 前端
- Electron - 跨平台桌面应用框架
- Vue 3 - 渐进式 JavaScript 框架
- Element Plus - Vue 3 组件库
- Vite - 快速构建工具

### 后端
- Python 3.8+
- Flask - Web 框架
- Playwright - 浏览器自动化工具

## 安装依赖

### 1. Node.js 依赖

```powershell
npm install
```

### 2. Python 依赖

```powershell
pip install -r requirements.txt
```

### 3. Playwright 浏览器

```powershell
python -m playwright install chromium
```

## 开发模式

```powershell
# 使用启动脚本（推荐）
.\dev.ps1

# 或手动启动
# 终端 1：启动 Python 后端
python python/server.py

# 终端 2：启动 Electron 应用
npm run electron:dev
```

## 构建发布

```powershell
# 使用构建脚本（推荐）
.\build.ps1

# 或手动构建
npm run build
npm run electron:build
```

构建完成后，安装包位于 `dist-electron` 目录。

## 使用说明

### 首次使用

1. 启动应用后，在左侧选择要使用的 AI 模型
2. 点击对应的"登录"按钮，在打开的浏览器窗口中登录账号
3. 登录成功后，软件会自动保存登录状态

### 发起提问

1. 在输入框中输入您的问题
2. 可选择是否开启"深度思考"模式（如果模型支持）
3. 点击"提交问题"按钮
4. 在标签页中查看各个模型的回答

### 查看回答

- 点击不同的标签页可以切换查看各个模型的回答
- 回答会实时更新，等待时会显示加载动画

## 项目结构

```
Many-Agents/
├── electron/           # Electron 主进程
│   ├── main.js        # 主进程入口
│   └── preload.js     # 预加载脚本
├── python/            # Python 后端
│   ├── server.py      # Flask 服务器
│   └── browser_utils.py  # 浏览器工具函数
├── src/               # Vue 前端源码
│   ├── App.vue        # 主组件
│   ├── main.js        # 入口文件
│   └── style.css      # 全局样式
├── build/             # 构建资源
├── dist/              # 前端构建输出
├── dist-electron/     # Electron 打包输出
├── index.html         # HTML 模板
├── package.json       # Node.js 配置
├── requirements.txt   # Python 依赖
├── vite.config.js     # Vite 配置
├── build.ps1          # 构建脚本
└── dev.ps1            # 开发启动脚本
```

## 支持的模型

- 豆包 (Doubao)
- DeepSeek
- 腾讯元宝 (Yuanbao)
- Kimi

*注：可以通过修改配置文件添加更多模型*

## 常见问题

### Q: 浏览器窗口没有打开？
A: 确保已正确安装 Playwright 浏览器：`python -m playwright install chromium`

### Q: 后端服务启动失败？
A: 检查 Python 依赖是否完整安装，端口 5000 是否被占用

### Q: 无法获取模型回答？
A: 确保已经登录对应的模型账号，某些模型可能需要手动完成验证码

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
