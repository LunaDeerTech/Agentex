<script setup lang="ts">
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuthStore } from '@/stores/auth'
  import { Button, Input, Card } from '@/components/ui'
  import { Loader2 } from 'lucide-vue-next'

  const router = useRouter()
  const authStore = useAuthStore()

  const username = ref('')
  const email = ref('')
  const password = ref('')
  const confirmPassword = ref('')
  const error = ref('')

  const getByteLength = (value: string) => new TextEncoder().encode(value).length

  const handleRegister = async () => {
    if (!username.value || !email.value || !password.value || !confirmPassword.value) {
      error.value = 'Please fill in all fields'
      return
    }

    const passwordBytes = getByteLength(password.value)
    if (passwordBytes < 8) {
      error.value = 'Password must be at least 8 characters'
      return
    }

    if (passwordBytes > 72) {
      error.value = 'Password cannot be longer than 72 bytes'
      return
    }

    if (password.value !== confirmPassword.value) {
      error.value = 'Passwords do not match'
      return
    }

    error.value = ''

    try {
      await authStore.register({
        username: username.value,
        email: email.value,
        password: password.value
      })
      // Assuming register logs in automatically or redirects.
      // If auth store handles logic, we can just redirect.
      router.push('/')
    } catch (err: any) {
      console.error(err)
      if (err?.message) {
        error.value = err.message
      } else {
        error.value = 'Registration failed'
      }
    }
  }
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-[var(--color-bg-primary)] px-4">
    <Card class="w-full max-w-md p-8 border-[var(--color-border-default)]">
      <div class="mb-8 text-center">
        <h1 class="text-2xl font-semibold text-[var(--color-text-primary)]">Agentex</h1>
        <p class="mt-2 text-sm text-[var(--color-text-secondary)]">Create your account</p>
      </div>

      <form class="space-y-4" @submit.prevent="handleRegister">
        <div class="space-y-2">
          <label class="text-sm font-medium text-[var(--color-text-secondary)]">Username</label>
          <Input
            v-model="username"
            placeholder="Choose a username"
            type="text"
            :disabled="authStore.isLoading"
            class="bg-[var(--color-bg-tertiary)]"
          />
        </div>

        <div class="space-y-2">
          <label class="text-sm font-medium text-[var(--color-text-secondary)]">Email</label>
          <Input
            v-model="email"
            placeholder="Enter your email"
            type="email"
            :disabled="authStore.isLoading"
            class="bg-[var(--color-bg-tertiary)]"
          />
        </div>

        <div class="space-y-2">
          <label class="text-sm font-medium text-[var(--color-text-secondary)]">Password</label>
          <Input
            v-model="password"
            placeholder="Create a password"
            type="password"
            :disabled="authStore.isLoading"
            class="bg-[var(--color-bg-tertiary)]"
          />
          <p class="text-xs text-[var(--color-text-tertiary)]">
            8–72 bytes. Longer passwords will be rejected by the server.
          </p>
        </div>

        <div class="space-y-2">
          <label class="text-sm font-medium text-[var(--color-text-secondary)]"
            >Confirm Password</label
          >
          <Input
            v-model="confirmPassword"
            placeholder="Confirm your password"
            type="password"
            :disabled="authStore.isLoading"
            class="bg-[var(--color-bg-tertiary)]"
          />
        </div>

        <div
          v-if="error"
          class="text-sm text-[var(--color-error)] border border-[var(--color-error)]/20 bg-[var(--color-error-bg)] p-2 rounded"
        >
          {{ error }}
        </div>

        <Button type="submit" class="w-full" :disabled="authStore.isLoading">
          <Loader2 v-if="authStore.isLoading" class="mr-2 h-4 w-4 animate-spin" />
          {{ authStore.isLoading ? 'Sign up' : 'Sign up' }}
        </Button>
      </form>

      <div class="mt-6 text-center text-sm text-[var(--color-text-secondary)]">
        Already have an account?
        <router-link to="/login" class="text-[var(--color-accent-primary)] hover:underline">
          Sign in
        </router-link>
      </div>
    </Card>
  </div>
</template>
