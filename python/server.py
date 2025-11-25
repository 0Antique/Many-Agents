"""
Many-Agents Python 后端服务
使用 Playwright 实现浏览器自动化控制多个 AI 模型
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import threading
import json
import os
from pathlib import Path

app = Flask(__name__)
CORS(app)

# 浏览器实例和页面管理
browser_context = None
pages = {}
responses = {}

# 存储登录状态的目录
STATE_DIR = Path.home() / '.many-agents'
STATE_DIR.mkdir(exist_ok=True)

# AI 模型配置
MODELS = {
    'doubao': {
        'name': '豆包',
        'url': 'https://www.doubao.com/chat/',
        'input_selector': 'textarea[placeholder*="输入"], textarea[placeholder*="问题"]',
        'submit_selector': 'button[type="submit"]',
        'response_selector': '.markdown-body, .message-content'
    },
    'deepseek': {
        'name': 'DeepSeek',
        'url': 'https://chat.deepseek.com/',
        'input_selector': 'textarea',
        'submit_selector': 'button[type="submit"]',
        'response_selector': '.markdown-body'
    },
    'yuanbao': {
        'name': '腾讯元宝',
        'url': 'https://yuanbao.tencent.com/chat',
        'input_selector': 'textarea',
        'submit_selector': 'button[aria-label*="发送"]',
        'response_selector': '.answer-content'
    },
    'kimi': {
        'name': 'Kimi',
        'url': 'https://kimi.moonshot.cn/',
        'input_selector': 'textarea',
        'submit_selector': 'button[type="submit"]',
        'response_selector': '.chat-content'
    }
}


def init_browser():
    """初始化浏览器"""
    global browser_context
    
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=False,  # 非无头模式，用户可以看到浏览器
        args=['--start-maximized']
    )
    
    # 创建持久化上下文，保存登录状态
    browser_context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    
    return browser_context


def load_cookies(model_id):
    """加载指定模型的 cookies"""
    cookie_file = STATE_DIR / f'{model_id}_cookies.json'
    if cookie_file.exists():
        try:
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            return cookies
        except:
            return None
    return None


def save_cookies(model_id, cookies):
    """保存指定模型的 cookies"""
    cookie_file = STATE_DIR / f'{model_id}_cookies.json'
    with open(cookie_file, 'w', encoding='utf-8') as f:
        json.dump(cookies, f)


@app.route('/open-login', methods=['POST'])
def open_login():
    """打开登录页面"""
    global browser_context, pages
    
    data = request.json
    model_id = data.get('modelId')
    url = data.get('url')
    
    if not browser_context:
        init_browser()
    
    try:
        # 创建新页面或使用现有页面
        if model_id in pages:
            page = pages[model_id]
        else:
            page = browser_context.new_page()
            pages[model_id] = page
            
            # 尝试加载之前保存的 cookies
            cookies = load_cookies(model_id)
            if cookies:
                browser_context.add_cookies(cookies)
        
        # 导航到登录页面
        page.goto(url, wait_until='networkidle', timeout=30000)
        
        return jsonify({'success': True, 'message': f'{model_id} 登录页面已打开'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/ask', methods=['POST'])
def ask_question():
    """向选中的模型发送问题"""
    global pages, responses
    
    data = request.json
    question = data.get('question')
    model_ids = data.get('models', [])
    deep_thinking = data.get('deepThinking', False)
    
    if not question:
        return jsonify({'success': False, 'error': '问题不能为空'}), 400
    
    # 清空之前的回答
    responses = {}
    
    # 对每个模型发送问题
    for model_id in model_ids:
        thread = threading.Thread(
            target=send_question_to_model,
            args=(model_id, question, deep_thinking)
        )
        thread.start()
    
    return jsonify({'success': True, 'message': '问题已发送'})


def send_question_to_model(model_id, question, deep_thinking=False):
    """向指定模型发送问题"""
    global pages, responses
    
    try:
        if model_id not in pages:
            return
        
        page = pages[model_id]
        model_config = MODELS.get(model_id)
        
        if not model_config:
            responses[model_id] = f'错误：未找到模型 {model_id} 的配置'
            return
        
        # 等待输入框加载
        page.wait_for_selector(model_config['input_selector'], timeout=10000)
        
        # 输入问题
        input_element = page.locator(model_config['input_selector'])
        input_element.fill(question)
        
        # 如果支持深度思考，可以在这里添加相应的操作
        # 具体实现取决于各个模型的界面
        
        # 点击发送按钮
        submit_button = page.locator(model_config['submit_selector'])
        submit_button.click()
        
        # 等待回答出现
        page.wait_for_selector(model_config['response_selector'], timeout=60000)
        
        # 等待一段时间以确保回答完整
        page.wait_for_timeout(3000)
        
        # 获取回答内容
        response_elements = page.locator(model_config['response_selector']).all()
        if response_elements:
            # 获取最后一个回答（最新的）
            response_text = response_elements[-1].inner_text()
            responses[model_id] = response_text
        else:
            responses[model_id] = '未能获取回答'
        
        # 保存 cookies
        cookies = browser_context.cookies()
        save_cookies(model_id, cookies)
        
    except PlaywrightTimeoutError:
        responses[model_id] = '错误：等待回答超时'
    except Exception as e:
        responses[model_id] = f'错误：{str(e)}'


@app.route('/responses', methods=['GET'])
def get_responses():
    """获取所有模型的回答"""
    models = request.args.get('models', '').split(',')
    
    # 过滤出请求的模型的回答
    filtered_responses = {
        model_id: responses.get(model_id, '')
        for model_id in models if model_id
    }
    
    return jsonify({'responses': filtered_responses})


@app.route('/save-state', methods=['POST'])
def save_state():
    """保存当前浏览器状态"""
    global browser_context
    
    if browser_context:
        try:
            cookies = browser_context.cookies()
            for model_id in MODELS.keys():
                save_cookies(model_id, cookies)
            return jsonify({'success': True, 'message': '状态已保存'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return jsonify({'success': False, 'error': '浏览器未初始化'}), 400


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'message': 'Many-Agents 后端服务运行中'})


if __name__ == '__main__':
    print('Many-Agents 后端服务启动中...')
    print('服务地址: http://localhost:5000')
    
    # 初始化浏览器
    init_browser()
    
    # 启动 Flask 服务
    app.run(host='0.0.0.0', port=5000, debug=False)
