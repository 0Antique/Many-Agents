<template>
  <div class="main-area">
    <!-- 上方：对话区 -->
    <div class="chat-area">
      <div class="response-area">
        <el-tabs v-model="localActiveTab" type="card" class="response-tabs">
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
              <div v-else class="empty-response">暂无回答</div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <div class="input-area">
        <div class="input-controls">
          <el-checkbox v-model="localDeepThinking">深度思考</el-checkbox>
        </div>
        <el-input
          v-model="localQuestion"
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
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Loading } from '@element-plus/icons-vue'

const props = defineProps({
  selectedModels: { type: Array, default: () => [] },
  availableModels: { type: Array, default: () => [] },
  question: { type: String, default: '' },
  deepThinking: { type: Boolean, default: false },
  isLoading: { type: Boolean, default: false },
  activeTab: { type: String, default: '' },
  responses: { type: Object, default: () => ({}) },
  getModelName: { type: Function, default: (id) => id },
  submitQuestion: { type: Function, default: () => {} },
  clearAll: { type: Function, default: () => {} }
})

const emit = defineEmits(['update:question','update:deepThinking','update:activeTab'])

const localQuestion = computed({ get: () => props.question, set: v => emit('update:question', v) })
const localDeepThinking = computed({ get: () => props.deepThinking, set: v => emit('update:deepThinking', v) })
const localActiveTab = computed({ get: () => props.activeTab, set: v => emit('update:activeTab', v) })

const previewText = (modelId) => {
  const r = props.responses[modelId]
  if (!r) return '暂无回答'
  if (r.loading) return '思考中...'
  if (r.content) return r.content.slice(0, 60)
  return '暂无回答'
}
</script>

<style scoped>
.main-area { display: flex; flex-direction: column; gap: 16px; height: 100%; }
.models-top { min-height: 80px; }
.model-cards { display:flex; gap:10px; flex-wrap:wrap }
.model-card { background:#fff; padding:10px 14px; border-radius:8px; box-shadow:0 1px 4px rgba(0,0,0,0.05); min-width:160px }
.model-name { font-weight:600; margin-bottom:6px }
.model-preview { color:#666; font-size:13px }
.chat-area { display:flex; flex-direction:column; flex:1; gap:12px }
.response-area { flex:1; background: white; border-radius:8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); overflow:hidden; display:flex; flex-direction:column }
.input-area { background: white; padding: 16px; border-radius:8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05) }
.input-controls { margin-bottom: 10px }
.question-input { margin-bottom: 12px }
.action-buttons { display:flex; gap:10px }
.response-content { height: 300px; overflow-y:auto; padding:20px }
.loading-indicator { display:flex; align-items:center; gap:10px; color:#409eff }
.response-text { white-space:pre-wrap; line-height:1.6; color:#333 }

:deep(.el-tabs__content) { flex:1; overflow:hidden }
:deep(.el-tab-pane) { height:100% }
</style>
