<script setup lang="ts">
// Rules engine placeholder view
</script>

<template>
  <div class="rules-view">
    <div class="page-header">
      <h2>规则引擎</h2>
      <el-button type="primary">
        <el-icon class="el-icon--left"><Plus /></el-icon>
        创建规则
      </el-button>
    </div>

    <el-empty description="暂无规则" />
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
