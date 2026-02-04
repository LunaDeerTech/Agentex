<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const router = useRouter()

const menuItems = [
  { path: '/settings/profile', title: '个人信息', icon: 'User' },
  { path: '/settings/models', title: '模型管理', icon: 'Cpu', divider: '资源管理' },
  { path: '/settings/mcp', title: 'MCP 连接', icon: 'Connection' },
  { path: '/settings/knowledge', title: '知识库', icon: 'Collection' },
  { path: '/settings/skills', title: 'SKILL 管理', icon: 'Aim' },
  { path: '/settings/rules', title: '规则引擎', icon: 'Lightning' },
]

const currentPath = computed(() => route.path)

function goBack() {
  router.push('/chat')
}
</script>

<template>
  <div class="settings-container">
    <div class="settings-header">
      <el-button text @click="goBack">
        <el-icon class="el-icon--left"><ArrowLeft /></el-icon>
        返回
      </el-button>
      <h1>设置</h1>
    </div>

    <div class="settings-content">
      <div class="settings-sidebar">
        <el-menu :default-active="currentPath" router>
          <template v-for="item in menuItems" :key="item.path">
            <div v-if="item.divider" class="menu-divider">
              {{ item.divider }}
            </div>
            <el-menu-item :index="item.path">
              <el-icon>
                <component :is="item.icon" />
              </el-icon>
              <span>{{ item.title }}</span>
            </el-menu-item>
          </template>
        </el-menu>
      </div>

      <div class="settings-main">
        <RouterView />
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-container {
  min-height: 100vh;
  background-color: var(--bg-color);
}

.settings-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  background-color: #fff;
  border-bottom: 1px solid var(--border-color);
}

.settings-header h1 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0;
}

.settings-content {
  display: flex;
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  gap: 24px;
}

.settings-sidebar {
  width: 200px;
  flex-shrink: 0;
}

.settings-sidebar .el-menu {
  border-right: none;
  background-color: transparent;
}

.menu-divider {
  font-size: 12px;
  color: var(--text-color-secondary);
  padding: 16px 20px 8px;
  text-transform: uppercase;
}

.menu-divider:first-child {
  padding-top: 0;
}

.settings-main {
  flex: 1;
  background-color: #fff;
  border-radius: 8px;
  padding: 24px;
  min-height: 600px;
}
</style>
