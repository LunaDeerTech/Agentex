<script setup lang="ts">
import { ref } from 'vue'

interface Model {
  id: string
  name: string
  provider: string
  modelId: string
  status: 'available' | 'unavailable'
}

const models = ref<Model[]>([
  { id: '1', name: 'GPT-4o', provider: 'OpenAI', modelId: 'gpt-4o', status: 'available' },
  {
    id: '2',
    name: 'Claude 3.5',
    provider: 'Anthropic',
    modelId: 'claude-3.5-sonnet',
    status: 'available',
  },
])

const dialogVisible = ref(false)

function openAddDialog() {
  dialogVisible.value = true
}
</script>

<template>
  <div class="models-view">
    <div class="page-header">
      <h2>模型管理</h2>
      <el-button type="primary" @click="openAddDialog">
        <el-icon class="el-icon--left"><Plus /></el-icon>
        添加模型
      </el-button>
    </div>

    <el-table :data="models" stripe>
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="provider" label="提供商" />
      <el-table-column prop="modelId" label="模型 ID" />
      <el-table-column prop="status" label="状态">
        <template #default="{ row }">
          <el-tag :type="row.status === 'available' ? 'success' : 'danger'">
            {{ row.status === 'available' ? '可用' : '不可用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default>
          <el-button text type="primary" size="small">编辑</el-button>
          <el-button text type="danger" size="small">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="添加模型" width="500">
      <el-form label-width="100px">
        <el-form-item label="模型名称">
          <el-input placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item label="提供商">
          <el-select placeholder="请选择提供商">
            <el-option label="OpenAI" value="openai" />
            <el-option label="Anthropic" value="anthropic" />
          </el-select>
        </el-form-item>
        <el-form-item label="API 地址">
          <el-input placeholder="https://api.openai.com/v1" />
        </el-form-item>
        <el-form-item label="API 密钥">
          <el-input type="password" placeholder="请输入 API 密钥" />
        </el-form-item>
        <el-form-item label="模型 ID">
          <el-input placeholder="gpt-4o" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0;
}
</style>
