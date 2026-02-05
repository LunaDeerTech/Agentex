<script setup lang="ts">
  import { computed } from 'vue'
  import { cn } from '@/lib/utils'

  interface Props {
    modelValue?: string | number
    placeholder?: string
    disabled?: boolean
    type?: 'text' | 'email' | 'password' | 'number' | 'search' | 'tel' | 'url'
    class?: string
    min?: number | string
    max?: number | string
    step?: number | string
  }

  const props = withDefaults(defineProps<Props>(), {
    modelValue: '',
    placeholder: '',
    disabled: false,
    type: 'text',
    class: ''
  })

  const emit = defineEmits<{
    'update:modelValue': [value: string | number]
  }>()

  const inputClasses = computed(() =>
    cn(
      'flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50',
      props.class
    )
  )

  function handleInput(event: Event) {
    const target = event.target as HTMLInputElement
    const value = props.type === 'number' ? target.valueAsNumber : target.value
    emit('update:modelValue', value)
  }
</script>

<template>
  <input
    :type="type"
    :value="modelValue"
    :placeholder="placeholder"
    :disabled="disabled"
    :min="min"
    :max="max"
    :step="step"
    :class="inputClasses"
    @input="handleInput"
  />
</template>
