<script setup lang="ts">
// SKILL management placeholder view
</script>

<template>
  <div class="skills-view">
    <div class="page-header">
      <h2>SKILL 管理</h2>
      <el-button type="primary">
        <el-icon class="el-icon--left"><Plus /></el-icon>
        创建 SKILL
      </el-button>
    </div>

    <el-empty description="暂无 SKILL" />
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
