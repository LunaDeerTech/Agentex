<script setup lang="ts">
  import { Home, ArrowLeft } from 'lucide-vue-next'
  import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="not-found-view">
    <div class="content">
      <h1 class="error-code">404</h1>
      <h2 class="error-title">Page Not Found</h2>
      <p class="error-description">The page you're looking for doesn't exist or has been moved.</p>
      <div class="actions">
        <RouterLink to="/" class="btn btn-primary">
          <Home class="w-4 h-4" />
          <span>Go Home</span>
        </RouterLink>
        <button class="btn btn-secondary" @click="$router.back()">
          <ArrowLeft class="w-4 h-4" />
          <span>Go Back</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
  .not-found-view {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-8);
  }

  .content {
    text-align: center;
    max-width: 400px;
  }

  .error-code {
    font-size: 8rem;
    font-weight: var(--font-bold);
    line-height: 1;
    color: var(--color-text-tertiary);
    margin-bottom: var(--spacing-4);
  }

  .error-title {
    font-size: var(--text-2xl);
    font-weight: var(--font-semibold);
    margin-bottom: var(--spacing-3);
  }

  .error-description {
    color: var(--color-text-secondary);
    margin-bottom: var(--spacing-8);
  }

  .actions {
    display: flex;
    gap: var(--spacing-4);
    justify-content: center;
    flex-wrap: wrap;
  }

  .btn {
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-2);
    padding: var(--spacing-3) var(--spacing-5);
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    border-radius: var(--radius-md);
    border: var(--border-width) solid transparent;
    cursor: pointer;
    transition:
      background var(--transition-fast),
      border-color var(--transition-fast);
    text-decoration: none;
  }

  .btn-primary {
    background: var(--color-accent-primary);
    color: var(--color-text-primary);
    border-color: var(--color-accent-primary);
  }

  .btn-primary:hover {
    background: var(--color-accent-hover);
    border-color: var(--color-accent-hover);
  }

  .btn-secondary {
    background: transparent;
    color: var(--color-text-primary);
    border-color: var(--color-border-default);
  }

  .btn-secondary:hover {
    background: var(--color-bg-hover);
    border-color: var(--color-text-tertiary);
  }
</style>
