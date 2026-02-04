<script setup lang="ts">
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuthStore } from '@/stores/auth'
  import { Button, Input } from '@/components/ui'
  import { Loader2 } from 'lucide-vue-next'

  const router = useRouter()
  const authStore = useAuthStore()

  const username = ref('')
  const password = ref('')
  const error = ref('')

  const handleLogin = async () => {
    if (!username.value || !password.value) {
      error.value = 'Please enter both username and password'
      return
    }

    error.value = ''

    try {
      await authStore.login({ username: username.value, password: password.value })
      router.push('/')
    } catch (err: any) {
      console.error(err)
      if (err.response && err.response.data && err.response.data.detail) {
        error.value = err.response.data.detail
      } else if (err.message) {
        error.value = err.message
      } else {
        error.value = 'Login failed'
      }
    }
  }
</script>

<template>
  <div
    class="flex min-h-screen items-center justify-center bg-background px-4 font-sans text-foreground"
  >
    <div class="w-full max-w-sm space-y-6">
      <div class="flex flex-col space-y-2 text-center">
        <h1 class="text-2xl font-semibold tracking-tight">Agentex</h1>
        <p class="text-sm text-muted-foreground">Sign in to your account</p>
      </div>

      <div class="rounded-xl border border-border bg-card text-card-foreground shadow-sm p-6">
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div class="space-y-2">
            <label
              class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >Username</label
            >
            <Input
              v-model="username"
              type="text"
              placeholder="admin"
              required
              class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <label
                class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >Password</label
              >
            </div>
            <Input
              v-model="password"
              type="password"
              required
              class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>

          <div v-if="error" class="text-sm text-destructive font-medium text-center">
            {{ error }}
          </div>

          <Button type="submit" class="w-full" :disabled="authStore.isLoading">
            <Loader2 v-if="authStore.isLoading" class="mr-2 h-4 w-4 animate-spin" />
            Sign In
          </Button>
        </form>
      </div>

      <p class="px-8 text-center text-sm text-muted-foreground">
        <router-link to="/register" class="hover:text-primary underline underline-offset-4">
          Don't have an account? Sign Up
        </router-link>
      </p>
    </div>
  </div>
</template>
