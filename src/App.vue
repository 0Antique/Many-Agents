<template>
  <div class="many-agents-app">
    <header class="app-header">
      <h1>Many-Agents - AI 大模型对话助手</h1>
    </header>

    <div class="app-content">
      <!-- 侧边栏：模型选择 -->
      <aside class="sidebar">
        <h3>模型选择</h3>
        <div class="model-list">
          <el-checkbox-group v-model="selectedModels">
            <el-checkbox 
              v-for="model in availableModels" 
              :key="model.id" 
              :label="model.id"
              class="model-checkbox"
            >
              {{ model.name }}
            </el-checkbox>
          </el-checkbox-group>
        </div>
        
        <div class="login-section">
          <h3>登录管理</h3>
          <el-button 
            v-for="model in selectedModels" 
            :key="model" 
            @click="openLoginWindow(model)" 
            size="small"
            class="login-btn"
          >
            登录 {{ getModelName(model) }}
          </el-button>
        </div>
      </aside>

      <!-- 主区域 -->
      <main class="main-area">
        <!-- 输入区域 -->
        <div class="input-area">
          <div class="input-controls">
            <el-checkbox v-model="deepThinking">深度思考</el-checkbox>
          </div>
          <el-input
            v-model="question"
            type="textarea"
            :rows="4"
            placeholder="请输入您的问题..."
            class="question-input"
          />
          <div class="action-buttons">
            <el-button type="primary" @click="submitQuestion" :loading="isLoading">
              {{ isLoading ? '提问中...' : '提交问题' }}
            </el-button>
            <el-button @click="clearAll">清空</el-button>
          </div>
        </div>

        <!-- 回答展示区域 - 标签页 -->
        <div class="response-area">
          <el-tabs v-model="activeTab" type="card" class="response-tabs">
            <el-tab-pane 
              v-for="model in selectedModels" 
              :key="model" 
              :label="getModelName(model)" 
              :name="model"
            >
              <div class="response-content">
                <div v-if="responses[model] && responses[model].loading" class="loading-indicator">
                  <el-icon class="is-loading"><Loading /></el-icon>
                  <span>{{ getModelName(model) }} 正在思考中...</span>
                </div>
                <div v-else-if="responses[model] && responses[model].content" class="response-text">
                  {{ responses[model].content }}
                </div>
                <div v-else class="empty-response">
                  暂无回答
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import axios from 'axios'

// 可用的大模型列表
const availableModels = ref([
  { id: 'doubao', name: '豆包', url: 'https://www.doubao.com' },
  { id: 'deepseek', name: 'DeepSeek', url: 'https://chat.deepseek.com' },
  { id: 'yuanbao', name: '腾讯元宝', url: 'https://yuanbao.tencent.com' },
  { id: 'kimi', name: 'Kimi', url: 'https://kimi.moonshot.cn' }
])

// 选中的模型
const selectedModels = ref(['doubao', 'deepseek'])

// 用户输入的问题
const question = ref('')

// 深度思考选项
const deepThinking = ref(false)

// 是否正在加载
const isLoading = ref(false)

// 当前激活的标签页
const activeTab = ref('doubao')

// 存储各个模型的回答
const responses = reactive({})

// Python 后端服务地址
const BACKEND_URL = 'http://localhost:5000'

// 获取模型名称
const getModelName = (modelId) => {
  const model = availableModels.value.find(m => m.id === modelId)
  return model ? model.name : modelId
}

// 打开登录窗口
const openLoginWindow = (modelId) => {
  const model = availableModels.value.find(m => m.id === modelId)
  if (model) {
    // 通知后端打开登录窗口
    axios.post(`${BACKEND_URL}/open-login`, { modelId, url: model.url })
      .then(() => {
        ElMessage.success(`正在打开 ${model.name} 登录页面...`)
      })
      .catch(error => {
        ElMessage.error(`打开登录页面失败: ${error.message}`)
      })
  }
}

// 提交问题
const submitQuestion = async () => {
  if (!question.value.trim()) {
    ElMessage.warning('请输入问题')
    return
  }

  if (selectedModels.value.length === 0) {
    ElMessage.warning('请至少选择一个模型')
    return
  }

  isLoading.value = true

  // 初始化所有选中模型的响应状态
  selectedModels.value.forEach(modelId => {
    responses[modelId] = { loading: true, content: '' }
  })

  try {
    // 向后端发送提问请求
    const response = await axios.post(`${BACKEND_URL}/ask`, {
      question: question.value,
      models: selectedModels.value,
      deepThinking: deepThinking.value
    })

    if (response.data.success) {
      ElMessage.success('问题已发送到所有模型')
      
      // 轮询获取回答
      pollResponses()
    } else {
      ElMessage.error('提交问题失败')
      isLoading.value = false
    }
  } catch (error) {
    ElMessage.error(`请求失败: ${error.message}`)
    isLoading.value = false
  }
}

// 轮询获取回答
const pollResponses = async () => {
  const maxAttempts = 60 // 最多轮询 60 次（约 2 分钟）
  let attempts = 0

  const poll = setInterval(async () => {
    attempts++

    try {
      const response = await axios.get(`${BACKEND_URL}/responses`, {
        params: { models: selectedModels.value.join(',') }
      })

      if (response.data.responses) {
        // 更新回答
        Object.keys(response.data.responses).forEach(modelId => {
          if (responses[modelId]) {
            responses[modelId] = {
              loading: false,
              content: response.data.responses[modelId]
            }
          }
        })

        // 检查是否所有模型都已回答
        const allCompleted = selectedModels.value.every(
          modelId => responses[modelId] && !responses[modelId].loading
        )

        if (allCompleted || attempts >= maxAttempts) {
          clearInterval(poll)
          isLoading.value = false
        }
      }
    } catch (error) {
      console.error('轮询失败:', error)
      if (attempts >= maxAttempts) {
        clearInterval(poll)
        isLoading.value = false
      }
    }
  }, 2000) // 每 2 秒轮询一次
}

// 清空所有内容
const clearAll = () => {
  question.value = ''
  Object.keys(responses).forEach(key => {
    responses[key] = { loading: false, content: '' }
  })
}
</script>

<style scoped>
.many-agents-app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.app-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 250px;
  background: white;
  padding: 20px;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
  overflow-y: auto;
}

.sidebar h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
  color: #333;
}

.model-list {
  margin-bottom: 30px;
}

.model-checkbox {
  display: block;
  margin-bottom: 10px;
}

.login-section {
  border-top: 1px solid #e4e7ed;
  padding-top: 20px;
}

.login-btn {
  display: block;
  width: 100%;
  margin-bottom: 10px;
}

.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow: hidden;
}

.input-area {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.input-controls {
  margin-bottom: 10px;
}

.question-input {
  margin-bottom: 15px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.response-area {
  flex: 1;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.response-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.response-content {
  height: 500px;
  overflow-y: auto;
  padding: 20px;
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #409eff;
  font-size: 14px;
}

.response-text {
  white-space: pre-wrap;
  line-height: 1.6;
  color: #333;
}

.empty-response {
  color: #909399;
  text-align: center;
  padding: 40px;
}

:deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
}

:deep(.el-tab-pane) {
  height: 100%;
}
</style>
