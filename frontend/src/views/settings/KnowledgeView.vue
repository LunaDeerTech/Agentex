<script setup lang="ts">
// Knowledge base placeholder view
</script>

<template>
  <div class="knowledge-view">
    <div class="page-header">
      <h2>知识库管理</h2>
      <el-button type="primary">
        <el-icon class="el-icon--left"><Plus /></el-icon>
        创建知识库
      </el-button>
    </div>

    <el-empty description="暂无知识库" />
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
