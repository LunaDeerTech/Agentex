<script setup lang="ts">
  import { type Component } from 'vue'
  import { cn } from '@/lib/utils'

  defineProps<{
    title?: string
    description?: string
    icon?: Component
    class?: string
  }>()
</script>

<template>
  <div
    :class="
      cn(
        'flex flex-col items-center justify-center p-12 text-center border border-dashed border-border rounded-lg bg-muted/20',
        $props.class
      )
    "
  >
    <div
      v-if="$slots.icon || icon"
      class="flex items-center justify-center w-16 h-16 rounded-full bg-muted mb-6"
    >
      <slot name="icon">
        <component :is="icon" v-if="icon" class="w-8 h-8 text-muted-foreground" />
      </slot>
    </div>
    <slot>
      <h3 v-if="title" class="text-lg font-medium text-foreground mb-2">{{ title }}</h3>
      <p v-if="description" class="text-sm text-muted-foreground max-w-sm mb-6 leading-relaxed">
        {{ description }}
      </p>
    </slot>
    <slot name="actions" />
  </div>
</template>
