<script setup lang="ts">
import { ref } from 'vue'
import { UserFilled, Plus } from '@element-plus/icons-vue'

const isEditing = ref(false)

const profile = ref({
  username: 'demo_user',
  email: 'demo@example.com',
  role: 'Developer',
  createdAt: '2025-01-15',
})
</script>

<template>
  <div class="profile-view">
    <h2>个人信息</h2>

    <el-card class="profile-card">
      <template #header>
        <span>基本信息</span>
      </template>

      <div class="profile-content">
        <div class="avatar-section">
          <el-avatar :size="80" :icon="UserFilled" />
          <el-button size="small" text type="primary">更换头像</el-button>
        </div>

        <el-descriptions :column="1" border>
          <el-descriptions-item label="用户名">{{ profile.username }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ profile.email }}</el-descriptions-item>
          <el-descriptions-item label="角色">{{ profile.role }}</el-descriptions-item>
          <el-descriptions-item label="注册时间">{{ profile.createdAt }}</el-descriptions-item>
        </el-descriptions>

        <el-button type="primary" @click="isEditing = true">编辑信息</el-button>
      </div>
    </el-card>

    <el-card class="profile-card">
      <template #header>
        <span>安全设置</span>
      </template>

      <div class="security-item">
        <div class="security-info">
          <span class="label">密码</span>
          <span class="value">••••••••••••</span>
        </div>
        <el-button text type="primary">修改密码</el-button>
      </div>
    </el-card>

    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>API 密钥</span>
          <el-button size="small" type="primary">
            <el-icon class="el-icon--left"><Plus /></el-icon>
            新建
          </el-button>
        </div>
      </template>

      <el-table :data="[]" empty-text="暂无 API 密钥">
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="key" label="密钥" />
        <el-table-column prop="createdAt" label="创建时间" />
        <el-table-column label="操作" width="100">
          <template #default>
            <el-button type="danger" text size="small">撤销</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.profile-view h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin-bottom: 24px;
}

.profile-card {
  margin-bottom: 24px;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.security-info {
  display: flex;
  gap: 16px;
}

.security-info .label {
  color: var(--text-color-secondary);
}

.security-info .value {
  color: var(--text-color-primary);
}
</style>
