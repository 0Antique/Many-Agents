"""
浏览器自动化辅助模块
提供通用的浏览器操作函数
"""

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
import time


def safe_fill(page: Page, selector: str, text: str, timeout: int = 10000):
    """安全地填充输入框"""
    try:
        page.wait_for_selector(selector, timeout=timeout)
        element = page.locator(selector)
        element.fill(text)
        return True
    except PlaywrightTimeoutError:
        return False
    except Exception as e:
        print(f'填充输入框失败: {e}')
        return False


def safe_click(page: Page, selector: str, timeout: int = 10000):
    """安全地点击元素"""
    try:
        page.wait_for_selector(selector, timeout=timeout)
        element = page.locator(selector)
        element.click()
        return True
    except PlaywrightTimeoutError:
        return False
    except Exception as e:
        print(f'点击元素失败: {e}')
        return False


def wait_for_response(page: Page, selector: str, timeout: int = 60000, poll_interval: int = 1000):
    """等待回答出现并获取内容"""
    start_time = time.time()
    
    while (time.time() - start_time) * 1000 < timeout:
        try:
            elements = page.locator(selector).all()
            if elements:
                # 获取最后一个元素的文本
                last_element = elements[-1]
                text = last_element.inner_text()
                
                if text and len(text) > 10:  # 确保有实质内容
                    return text
            
            time.sleep(poll_interval / 1000)
        
        except Exception as e:
            print(f'获取回答失败: {e}')
            time.sleep(poll_interval / 1000)
    
    return None


def get_all_text(page: Page, selector: str):
    """获取所有匹配元素的文本"""
    try:
        elements = page.locator(selector).all()
        texts = [elem.inner_text() for elem in elements]
        return texts
    except Exception as e:
        print(f'获取文本失败: {e}')
        return []
