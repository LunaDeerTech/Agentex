<script setup lang="ts">
  import { computed } from 'vue'
  import { cn } from '@/lib/utils'

  interface Props {
    modelValue?: string
    placeholder?: string
    disabled?: boolean
    type?: 'text' | 'email' | 'password' | 'number' | 'search' | 'tel' | 'url'
    class?: string
  }

  const props = withDefaults(defineProps<Props>(), {
    modelValue: '',
    placeholder: '',
    disabled: false,
    type: 'text',
    class: ''
  })

  const emit = defineEmits<{
    'update:modelValue': [value: string]
  }>()

  const inputClasses = computed(() =>
    cn(
      'flex h-9 w-full rounded-md border border-[var(--color-border-default)] bg-[var(--color-bg-secondary)] px-3 py-1 text-sm text-[var(--color-text-primary)] transition-colors',
      'placeholder:text-[var(--color-text-tertiary)]',
      'focus:border-[var(--color-border-focus)] focus:outline-none',
      'disabled:cursor-not-allowed disabled:opacity-50',
      props.class
    )
  )

  function handleInput(event: Event) {
    const target = event.target as HTMLInputElement
    emit('update:modelValue', target.value)
  }
</script>

<template>
  <input
    :type="type"
    :value="modelValue"
    :placeholder="placeholder"
    :disabled="disabled"
    :class="inputClasses"
    @input="handleInput"
  />
</template>
