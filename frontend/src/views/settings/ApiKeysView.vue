<template>
  <div>
    <h3 class="text-2xl font-semibold tracking-tight text-[var(--color-text-primary)]">API Keys</h3>
    <p class="text-sm text-[var(--color-text-secondary)] mb-6">
      Manage your API keys for accessing external services.
    </p>

    <div
      class="p-12 border border-dashed border-[var(--color-border-muted)] rounded-lg flex flex-col items-center justify-center text-center bg-[var(--color-bg-subtle)]"
    >
      <div class="text-[var(--color-text-tertiary)] mb-2 text-sm font-medium">
        No API keys found
      </div>
      <div class="text-xs text-[var(--color-text-disabled)] max-w-xs">
        You haven't created any API keys yet. Create one to authenticate with the Agentex API.
      </div>
    </div>
  </div>
</template>
