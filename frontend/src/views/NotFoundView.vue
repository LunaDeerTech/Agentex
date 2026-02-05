<script setup lang="ts">
  import { Home, ArrowLeft } from 'lucide-vue-next'
  import { RouterLink, useRouter } from 'vue-router'
  import Button from '@/components/ui/Button.vue'

  const router = useRouter()
</script>

<template>
  <div class="flex min-h-screen items-center justify-center p-8 bg-background text-foreground">
    <div class="text-center max-w-[400px]">
      <h1 class="text-[8rem] font-bold leading-none text-muted-foreground/30 mb-4 select-none">
        404
      </h1>
      <h2 class="text-2xl font-semibold mb-3">Page Not Found</h2>
      <p class="text-muted-foreground mb-8">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <div class="flex gap-4 justify-center flex-wrap">
        <Button as-child>
          <RouterLink to="/">
            <Home class="w-4 h-4" />
            <span>Go Home</span>
          </RouterLink>
        </Button>
        <Button variant="outline" @click="router.back()">
          <ArrowLeft class="w-4 h-4" />
          <span>Go Back</span>
        </Button>
      </div>
    </div>
  </div>
</template>
