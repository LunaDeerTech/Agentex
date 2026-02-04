<script setup lang="ts">
// MCP connections placeholder view
</script>

<template>
  <div class="mcp-view">
    <div class="page-header">
      <h2>MCP 连接管理</h2>
      <el-button type="primary">
        <el-icon class="el-icon--left"><Plus /></el-icon>
        添加连接
      </el-button>
    </div>

    <el-empty description="暂无 MCP 连接" />
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
