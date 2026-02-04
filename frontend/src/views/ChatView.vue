<script setup lang="ts">
  import { ref } from 'vue'
  import { Send, Menu, Plus, Settings } from 'lucide-vue-next'
  import { useSessionStore, useAppStore } from '@/stores'

  const sessionStore = useSessionStore()
  const appStore = useAppStore()

  const inputMessage = ref('')

  function handleSend() {
    if (!inputMessage.value.trim() || sessionStore.isStreaming) return

    // TODO: Implement actual message sending
    console.log('Sending message:', inputMessage.value)
    inputMessage.value = ''
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }
</script>

<template>
  <div class="chat-view">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: appStore.sidebarCollapsed }">
      <div class="sidebar-header">
        <button class="icon-btn" @click="appStore.toggleSidebar">
          <Menu class="w-5 h-5" />
        </button>
        <button class="icon-btn">
          <Plus class="w-5 h-5" />
        </button>
      </div>

      <div class="sidebar-content">
        <div class="empty-sessions">
          <p>No conversations yet</p>
          <p class="text-muted">Start a new chat to begin</p>
        </div>
      </div>

      <div class="sidebar-footer">
        <button class="icon-btn">
          <Settings class="w-5 h-5" />
        </button>
      </div>
    </aside>

    <!-- Main Chat Area -->
    <main class="chat-main">
      <!-- Messages Area -->
      <div class="messages-area">
        <div class="empty-chat">
          <h2>Start a Conversation</h2>
          <p>Send a message to begin chatting with the AI agent</p>
        </div>
      </div>

      <!-- Input Area -->
      <div class="input-area">
        <div class="input-container">
          <textarea
            ref="inputRef"
            v-model="inputMessage"
            class="message-input"
            placeholder="Type your message..."
            rows="1"
            @keydown="handleKeydown"
          ></textarea>
          <button
            class="send-btn"
            :disabled="!inputMessage.trim() || sessionStore.isStreaming"
            @click="handleSend"
          >
            <Send class="w-4 h-4" />
          </button>
        </div>
        <p class="input-hint">Press Enter to send, Shift+Enter for new line</p>
      </div>
    </main>
  </div>
</template>

<style scoped>
  .chat-view {
    display: flex;
    height: 100vh;
    background: var(--color-bg-primary);
  }

  /* Sidebar */
  .sidebar {
    width: 260px;
    display: flex;
    flex-direction: column;
    background: var(--color-bg-secondary);
    border-right: var(--border-width) solid var(--color-border-default);
    transition: width var(--transition-normal);
  }

  .sidebar.collapsed {
    width: 60px;
  }

  .sidebar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-3);
    border-bottom: var(--border-width) solid var(--color-border-muted);
  }

  .sidebar.collapsed .sidebar-header {
    justify-content: center;
  }

  .sidebar.collapsed .sidebar-header > :last-child {
    display: none;
  }

  .sidebar-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--spacing-3);
  }

  .sidebar-footer {
    padding: var(--spacing-3);
    border-top: var(--border-width) solid var(--color-border-muted);
  }

  .empty-sessions {
    text-align: center;
    padding: var(--spacing-8) var(--spacing-4);
    color: var(--color-text-tertiary);
    font-size: var(--text-sm);
  }

  .sidebar.collapsed .empty-sessions {
    display: none;
  }

  .text-muted {
    color: var(--color-text-disabled);
    font-size: var(--text-xs);
    margin-top: var(--spacing-1);
  }

  /* Icon Button */
  .icon-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    background: transparent;
    border: var(--border-width) solid transparent;
    border-radius: var(--radius-md);
    color: var(--color-text-secondary);
    cursor: pointer;
    transition:
      background var(--transition-fast),
      color var(--transition-fast),
      border-color var(--transition-fast);
  }

  .icon-btn:hover {
    background: var(--color-bg-hover);
    color: var(--color-text-primary);
    border-color: var(--color-border-default);
  }

  /* Main Chat Area */
  .chat-main {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .messages-area {
    flex: 1;
    overflow-y: auto;
    padding: var(--spacing-6);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .empty-chat {
    text-align: center;
    color: var(--color-text-secondary);
  }

  .empty-chat h2 {
    font-size: var(--text-xl);
    font-weight: var(--font-semibold);
    margin-bottom: var(--spacing-2);
    color: var(--color-text-primary);
  }

  .empty-chat p {
    font-size: var(--text-sm);
    color: var(--color-text-tertiary);
  }

  /* Input Area */
  .input-area {
    padding: var(--spacing-4) var(--spacing-6) var(--spacing-6);
    border-top: var(--border-width) solid var(--color-border-muted);
  }

  .input-container {
    display: flex;
    align-items: flex-end;
    gap: var(--spacing-3);
    padding: var(--spacing-3);
    background: var(--color-bg-secondary);
    border: var(--border-width) solid var(--color-border-default);
    border-radius: var(--radius-lg);
    transition: border-color var(--transition-fast);
  }

  .input-container:focus-within {
    border-color: var(--color-border-focus);
  }

  .message-input {
    flex: 1;
    background: transparent;
    border: none;
    color: var(--color-text-primary);
    font-size: var(--text-base);
    font-family: var(--font-sans);
    resize: none;
    min-height: 24px;
    max-height: 200px;
    line-height: 1.5;
  }

  .message-input::placeholder {
    color: var(--color-text-tertiary);
  }

  .send-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    background: var(--color-accent-primary);
    border: none;
    border-radius: var(--radius-md);
    color: var(--color-text-primary);
    cursor: pointer;
    transition:
      background var(--transition-fast),
      opacity var(--transition-fast);
  }

  .send-btn:hover:not(:disabled) {
    background: var(--color-accent-hover);
  }

  .send-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .input-hint {
    margin-top: var(--spacing-2);
    font-size: var(--text-xs);
    color: var(--color-text-disabled);
    text-align: center;
  }
</style>
