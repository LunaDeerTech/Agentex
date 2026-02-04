<script setup lang="ts">
  import { ref } from 'vue'
  import { useAuthStore } from '@/stores/auth'
  import Button from '@/components/ui/Button.vue'
  import Input from '@/components/ui/Input.vue'
  import Card from '@/components/ui/Card.vue'
  import { User, Loader2 } from 'lucide-vue-next'

  const authStore = useAuthStore()

  const isEditing = ref(false)
  const isLoading = ref(false)

  const form = ref({
    username: authStore.user?.username || '',
    email: authStore.user?.email || ''
    // avatar: authStore.user?.avatar || ''
  })

  const passwordForm = ref({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })

  const handleUpdateProfile = async () => {
    isLoading.value = true
    try {
      // await authStore.updateProfile(form.value)
      await new Promise(resolve => setTimeout(resolve, 1000)) // Mock
      isEditing.value = false
    } finally {
      isLoading.value = false
    }
  }
</script>

<template>
  <div class="space-y-8">
    <div>
      <h3 class="text-2xl font-semibold tracking-tight text-[var(--color-text-primary)]">
        Profile
      </h3>
      <p class="text-sm text-[var(--color-text-secondary)]">
        Manage your personal information and account settings.
      </p>
    </div>

    <Card class="p-6">
      <div class="flex flex-col sm:flex-row items-start gap-6">
        <div
          class="h-20 w-20 rounded-full bg-[var(--color-bg-elevated)] border border-[var(--color-border-muted)] flex items-center justify-center text-[var(--color-text-tertiary)] shrink-0 self-center sm:self-auto"
        >
          <!-- <img v-if="form.avatar" :src="form.avatar" class="h-full w-full rounded-full object-cover" /> -->
          <User class="h-10 w-10" />
        </div>

        <div class="space-y-4 flex-1 w-full max-w-md">
          <div class="grid w-full items-center gap-2">
            <label class="text-sm font-medium leading-none text-[var(--color-text-secondary)]"
              >Username</label
            >
            <Input v-model="form.username" :disabled="!isEditing" />
          </div>
          <div class="grid w-full items-center gap-2">
            <label class="text-sm font-medium leading-none text-[var(--color-text-secondary)]"
              >Email</label
            >
            <Input v-model="form.email" disabled class="opacity-70 bg-[var(--color-bg-tertiary)]" />
          </div>

          <div class="flex gap-2 pt-2">
            <Button v-if="!isEditing" @click="isEditing = true" variant="outline" size="sm"
              >Edit Profile</Button
            >
            <template v-else>
              <Button @click="handleUpdateProfile" :disabled="isLoading" size="sm">
                <Loader2 v-if="isLoading" class="mr-2 h-4 w-4 animate-spin" />
                Save Changes
              </Button>
              <Button variant="ghost" @click="isEditing = false" :disabled="isLoading" size="sm"
                >Cancel</Button
              >
            </template>
          </div>
        </div>
      </div>
    </Card>

    <div class="border-t border-[var(--color-border-muted)]" />

    <div>
      <h4 class="text-lg font-medium text-[var(--color-text-primary)] mb-4">Security</h4>
      <Card class="p-6 max-w-md space-y-4">
        <div class="grid w-full items-center gap-2">
          <label class="text-sm font-medium text-[var(--color-text-secondary)]"
            >Current Password</label
          >
          <Input v-model="passwordForm.currentPassword" type="password" />
        </div>
        <div class="grid w-full items-center gap-2">
          <label class="text-sm font-medium text-[var(--color-text-secondary)]">New Password</label>
          <Input v-model="passwordForm.newPassword" type="password" />
        </div>
        <div class="grid w-full items-center gap-2">
          <label class="text-sm font-medium text-[var(--color-text-secondary)]"
            >Confirm New Password</label
          >
          <Input v-model="passwordForm.confirmPassword" type="password" />
        </div>
        <div class="pt-2">
          <Button variant="outline" size="sm">Update Password</Button>
        </div>
      </Card>
    </div>
  </div>
</template>
