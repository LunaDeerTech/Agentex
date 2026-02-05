<script setup lang="ts">
  import EmptyState from '@/components/ui/EmptyState.vue'
</script>

<template>
  <div>
    <h3 class="text-2xl font-semibold tracking-tight text-foreground">API Keys</h3>
    <p class="text-sm text-muted-foreground mb-6">
      Manage your API keys for accessing external services.
    </p>

    <EmptyState
      title="No API keys found"
      description="You haven't created any API keys yet. Create one to authenticate with the Agentex API."
    />
  </div>
</template>
