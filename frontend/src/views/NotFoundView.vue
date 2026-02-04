<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function goHome() {
  router.push('/')
}
</script>

<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <h1 class="error-code">404</h1>
      <p class="error-message">页面不存在</p>
      <p class="error-description">抱歉，您访问的页面不存在或已被移除。</p>
      <el-button type="primary" @click="goHome">
        <el-icon class="el-icon--left"><HomeFilled /></el-icon>
        返回首页
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.not-found-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--bg-color);
}

.not-found-content {
  text-align: center;
}

.error-code {
  font-size: 120px;
  font-weight: 700;
  color: var(--color-primary);
  margin: 0;
  line-height: 1;
}

.error-message {
  font-size: 24px;
  color: var(--text-color-primary);
  margin: 16px 0;
}

.error-description {
  font-size: 14px;
  color: var(--text-color-secondary);
  margin-bottom: 32px;
}
</style>
