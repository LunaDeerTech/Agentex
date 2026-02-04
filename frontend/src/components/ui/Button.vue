<script setup lang="ts">
  import { computed } from 'vue'
  import { cva, type VariantProps } from 'class-variance-authority'
  import { cn } from '@/lib/utils'

  const buttonVariants = cva(
    'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--color-border-focus)] disabled:pointer-events-none disabled:opacity-50',
    {
      variants: {
        variant: {
          default:
            'bg-[var(--color-accent-primary)] text-[var(--color-text-primary)] hover:bg-[var(--color-accent-hover)]',
          destructive: 'bg-[var(--color-error)] text-[var(--color-text-primary)] hover:opacity-90',
          outline:
            'border border-[var(--color-border-default)] bg-transparent hover:bg-[var(--color-bg-hover)] hover:border-[var(--color-text-tertiary)]',
          secondary:
            'bg-[var(--color-bg-secondary)] text-[var(--color-text-primary)] border border-[var(--color-border-default)] hover:bg-[var(--color-bg-hover)]',
          ghost: 'hover:bg-[var(--color-bg-hover)] hover:text-[var(--color-text-primary)]',
          link: 'text-[var(--color-accent-primary)] underline-offset-4 hover:underline'
        },
        size: {
          default: 'h-9 px-4 py-2',
          sm: 'h-8 rounded-md px-3 text-xs',
          lg: 'h-10 rounded-md px-8',
          icon: 'h-9 w-9'
        }
      },
      defaultVariants: {
        variant: 'default',
        size: 'default'
      }
    }
  )

  type ButtonVariants = VariantProps<typeof buttonVariants>

  interface Props {
    variant?: ButtonVariants['variant']
    size?: ButtonVariants['size']
    asChild?: boolean
    disabled?: boolean
    type?: 'button' | 'submit' | 'reset'
  }

  const props = withDefaults(defineProps<Props>(), {
    variant: 'default',
    size: 'default',
    asChild: false,
    disabled: false,
    type: 'button'
  })

  const classes = computed(() => cn(buttonVariants({ variant: props.variant, size: props.size })))
</script>

<template>
  <button :type="type" :class="classes" :disabled="disabled">
    <slot />
  </button>
</template>
