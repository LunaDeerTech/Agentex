<script setup lang="ts">
// Chat view - placeholder
</script>

<template>
  <div class="chat-container">
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <el-button type="primary" class="new-chat-btn">
          <el-icon class="el-icon--left"><Plus /></el-icon>
          新建会话
        </el-button>
      </div>
      <div class="session-list">
        <div class="session-item active">
          <el-icon><ChatDotRound /></el-icon>
          <span>新会话</span>
        </div>
      </div>
      <div class="sidebar-footer">
        <router-link to="/settings">
          <el-button text>
            <el-icon><Setting /></el-icon>
            设置
          </el-button>
        </router-link>
      </div>
    </div>
    <div class="chat-main">
      <div class="chat-messages">
        <div class="empty-state">
          <el-icon :size="64" color="#c0c4cc">
            <ChatDotRound />
          </el-icon>
          <p>开始一段新的对话</p>
        </div>
      </div>
      <div class="chat-input">
        <div class="input-toolbar">
          <el-select placeholder="选择 Agent" size="small" style="width: 120px">
            <el-option label="ReAct" value="react" />
          </el-select>
          <el-select placeholder="选择模型" size="small" style="width: 140px">
            <el-option label="GPT-4o" value="gpt-4o" />
          </el-select>
        </div>
        <div class="input-area">
          <el-input
            type="textarea"
            :rows="2"
            placeholder="请输入您的问题..."
            resize="none"
          />
          <el-button type="primary" :icon="Promotion" circle />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Promotion } from '@element-plus/icons-vue'
export default {
  data() {
    return { Promotion }
  },
}
</script>

<style scoped>
.chat-container {
  display: flex;
  height: 100vh;
  background-color: var(--bg-color);
}

.chat-sidebar {
  width: 260px;
  background-color: #fff;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.new-chat-btn {
  width: 100%;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.session-item:hover,
.session-item.active {
  background-color: #f5f7fa;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border-color);
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.empty-state {
  text-align: center;
  color: var(--text-color-secondary);
}

.empty-state p {
  margin-top: 16px;
}

.chat-input {
  padding: 16px 24px;
  background-color: #fff;
  border-top: 1px solid var(--border-color);
}

.input-toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.input-area {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.input-area .el-textarea {
  flex: 1;
}
</style>
