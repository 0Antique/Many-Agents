<template>
  <div class="many-agents-app">
    <header class="app-header">
      <h1>Many-Agents - AI 大模型对话助手</h1>
    </header>

    <div class="app-content">
      <aside class="sidebar">
        <h3>模型选择</h3>
        <div class="model-list">
          <el-checkbox-group v-model="selected">
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
            v-for="modelId in selected"
            :key="modelId"
            @click="openLogin(modelId)"
            size="small"
            class="login-btn"
          >
            登录 {{ getModelName(modelId) }}
          </el-button>
        </div>
      </aside>

      <main class="main-slot">
        <slot></slot>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  availableModels: { type: Array, default: () => [] },
  selectedModels: { type: Array, default: () => [] },
  openLoginWindow: { type: Function, default: () => {} }
})
const emit = defineEmits(['update:selectedModels'])

const selected = computed({
  get: () => props.selectedModels,
  set: (v) => emit('update:selectedModels', v)
})

const openLogin = (modelId) => {
  props.openLoginWindow && props.openLoginWindow(modelId)
}

const getModelName = (modelId) => {
  const m = props.availableModels.find(x => x.id === modelId)
  return m ? m.name : modelId
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

.app-header h1 { margin: 0; font-size: 24px; font-weight: 600; }

.app-content { display: flex; flex: 1; overflow: hidden; }

.sidebar { width: 250px; background: white; padding: 20px; box-shadow: 2px 0 8px rgba(0,0,0,0.05); overflow-y:auto }
.sidebar h3 { margin-top: 0; margin-bottom: 15px; font-size: 16px; color:#333 }
.model-list { margin-bottom: 20px }
.model-checkbox { display:block; margin-bottom:10px }
.login-section { border-top:1px solid #e4e7ed; padding-top:20px }
.login-btn { display:block; width:100%; margin-bottom:10px }

.main-slot { flex: 1; display: flex; flex-direction: column; padding: 20px; overflow: hidden }
</style>
