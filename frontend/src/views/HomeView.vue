<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isHovered = ref(false)

const features = [
  { icon: 'ChatDotRound', title: 'Agent 对话', desc: '多种 Agent 架构支持' },
  { icon: 'Connection', title: 'MCP 集成', desc: '标准 MCP 协议支持' },
  { icon: 'Document', title: '知识库', desc: 'RAG 增强检索' },
  { icon: 'Cpu', title: 'SKILL 管理', desc: '自定义技能编排' },
]

function goToChat() {
  router.push('/chat')
}

function goToLogin() {
  router.push('/login')
}
</script>

<template>
  <div class="home-container">
    <div class="home-content">
      <!-- Logo & Title -->
      <div class="hero-section">
        <div class="logo">
          <el-icon :size="64" color="#409EFF">
            <Cpu />
          </el-icon>
        </div>
        <h1 class="title">Agentex</h1>
        <p class="subtitle">Web AI Agent Platform</p>
        <p class="description">
          集成 MCP 能力、RAG 知识库、SKILL 管理和规则引擎的智能 Agent 平台
        </p>
      </div>

      <!-- Features -->
      <div class="features-section">
        <div v-for="feature in features" :key="feature.title" class="feature-card">
          <el-icon :size="32" color="#409EFF">
            <component :is="feature.icon" />
          </el-icon>
          <h3>{{ feature.title }}</h3>
          <p>{{ feature.desc }}</p>
        </div>
      </div>

      <!-- Actions -->
      <div class="actions-section">
        <el-button
          type="primary"
          size="large"
          :class="{ 'is-hovered': isHovered }"
          @mouseenter="isHovered = true"
          @mouseleave="isHovered = false"
          @click="goToChat"
        >
          <el-icon class="el-icon--left"><ChatDotRound /></el-icon>
          开始对话
        </el-button>
        <el-button size="large" @click="goToLogin"> 登录 / 注册 </el-button>
      </div>

      <!-- Version Info -->
      <div class="version-info">
        <span>Version 1.0.0</span>
        <el-divider direction="vertical" />
        <span>Powered by Vue 3 + FastAPI</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-container {
  width: 100%;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;
}

.home-content {
  max-width: 800px;
  width: 100%;
  text-align: center;
}

.hero-section {
  margin-bottom: 48px;
}

.logo {
  margin-bottom: 24px;
  display: inline-flex;
  padding: 20px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  backdrop-filter: blur(10px);
}

.title {
  font-size: 48px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 8px;
  letter-spacing: 2px;
}

.subtitle {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 16px;
}

.description {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
  max-width: 500px;
  margin: 0 auto;
  line-height: 1.6;
}

.features-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 48px;
}

@media (max-width: 768px) {
  .features-section {
    grid-template-columns: repeat(2, 1fr);
  }
}

.feature-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 24px 16px;
  transition: all 0.3s ease;
}

.feature-card:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-4px);
}

.feature-card h3 {
  color: #fff;
  font-size: 16px;
  margin: 12px 0 8px;
}

.feature-card p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
}

.actions-section {
  margin-bottom: 32px;
}

.actions-section .el-button {
  margin: 0 8px;
  min-width: 140px;
}

.version-info {
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
}
</style>
