<script setup lang="ts">
  import { cn } from '@/lib/utils'

  interface Props {
    class?: string
  }

  const props = withDefaults(defineProps<Props>(), {
    class: ''
  })
</script>

<template>
  <div
    :class="
      cn(
        'rounded-xl border border-[var(--color-border-default)] bg-[var(--color-bg-secondary)] text-[var(--color-text-primary)] shadow-sm',
        props.class
      )
    "
  >
    <slot />
  </div>
</template>
