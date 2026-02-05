<script setup lang="ts">
  import { Bot } from 'lucide-vue-next'

  const emit = defineEmits<{
    (e: 'action', action: string): void
  }>()
</script>

<template>
  <div
    class="flex flex-col items-center justify-center h-full max-w-2xl text-center space-y-8 mt-[-10vh]"
  >
    <div
      class="w-20 h-20 rounded-3xl bg-gradient-to-br from-indigo-500/10 to-purple-500/10 flex items-center justify-center border border-indigo-500/20 shadow-2xl shadow-indigo-500/5"
    >
      <Bot class="w-10 h-10 text-indigo-400" :stroke-width="1.5" />
    </div>
    <div class="space-y-2">
      <h1 class="text-2xl font-semibold tracking-tight text-foreground">
        How can I help you today?
      </h1>
      <p class="text-muted-foreground text-sm max-w-md mx-auto">
        I can assist you with coding, analysis, and creative tasks. I have access to tools and your
        knowledge base.
      </p>
    </div>

    <!-- Quick Starters -->
    <div class="grid grid-cols-2 gap-3 w-full max-w-lg">
      <button
        class="p-3 rounded-xl border border-border bg-card hover:bg-accent/50 hover:border-accent/50 transition-all text-left text-sm group"
        @click="emit('action', 'Analyze code')"
      >
        <div class="font-medium text-foreground mb-1 group-hover:text-primary transition-colors">
          Analyze code
        </div>
        <div class="text-xs text-muted-foreground">Check for bugs in my project</div>
      </button>
      <button
        class="p-3 rounded-xl border border-border bg-card hover:bg-accent/50 hover:border-accent/50 transition-all text-left text-sm group"
        @click="emit('action', 'Summarize text')"
      >
        <div class="font-medium text-foreground mb-1 group-hover:text-primary transition-colors">
          Summarize text
        </div>
        <div class="text-xs text-muted-foreground">Create a summary of this document</div>
      </button>
    </div>
  </div>
</template>
