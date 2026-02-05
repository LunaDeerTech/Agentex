<script setup lang="ts">
  import { ref, reactive, watch } from 'vue'
  import { useAuthStore } from '@/stores/auth'
  import Button from '@/components/ui/Button.vue'
  import Input from '@/components/ui/Input.vue'
  import Card from '@/components/ui/Card.vue'
  import { User, Loader2, Mail, Shield, Lock, Camera, Save, X } from 'lucide-vue-next'

  const authStore = useAuthStore()

  const isEditing = ref(false)
  const isLoading = ref(false)
  const isUpdatingPassword = ref(false)

  // Profile Form
  const form = ref({
    username: authStore.user?.username || '',
    email: authStore.user?.email || ''
  })

  // Watch for changes in user data (e.g. after fetchUser completes)
  watch(
    () => authStore.user,
    user => {
      if (user && !isEditing.value) {
        form.value.username = user.username
        form.value.email = user.email
      }
    },
    { immediate: true }
  )

  // Password Form
  const passwordForm = reactive({
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

  const handleUpdatePassword = async () => {
    isUpdatingPassword.value = true
    try {
      await new Promise(resolve => setTimeout(resolve, 1000)) // Mock
      // Reset form
      passwordForm.currentPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmPassword = ''
    } finally {
      isUpdatingPassword.value = false
    }
  }
</script>

<template>
  <div class="space-y-8 animate-in fade-in duration-500">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="space-y-1">
        <h3 class="text-2xl font-semibold tracking-tight text-foreground">Profile</h3>
        <p class="text-sm text-muted-foreground">
          Manage your personal information and account settings.
        </p>
      </div>
    </div>

    <div class="grid gap-8">
      <!-- Personal Information -->
      <Card class="p-6">
        <div class="flex flex-col md:flex-row gap-8">
          <!-- Avatar Section -->
          <div class="flex flex-col items-center gap-3 shrink-0">
            <div class="relative group cursor-pointer">
              <div
                class="h-24 w-24 rounded-full bg-muted border-2 border-border flex items-center justify-center text-muted-foreground overflow-hidden transition-all duration-200 group-hover:border-primary/50"
              >
                <User class="h-10 w-10" />
              </div>
              <div
                class="absolute inset-0 flex items-center justify-center bg-black/40 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-200"
              >
                <Camera class="h-6 w-6 text-white" />
              </div>
            </div>
            <div class="text-center">
              <p class="text-sm font-medium text-foreground">Profile Picture</p>
              <p class="text-xs text-muted-foreground mt-0.5">JPG or PNG, max 2MB</p>
            </div>
          </div>

          <!-- Divider on mobile -->
          <div class="h-px w-full bg-border md:hidden"></div>

          <!-- Form Details -->
          <div class="flex-1 space-y-6 max-w-xl">
            <div class="grid gap-4">
              <div class="space-y-2">
                <label class="text-sm font-medium text-foreground flex items-center gap-2">
                  <User class="w-4 h-4 text-muted-foreground" />
                  Username
                </label>
                <Input
                  v-model="form.username"
                  :disabled="!isEditing"
                  class="bg-background"
                  :class="!isEditing ? 'border-transparent bg-muted/50 text-muted-foreground' : ''"
                />
              </div>

              <div class="space-y-2">
                <label class="text-sm font-medium text-foreground flex items-center gap-2">
                  <Mail class="w-4 h-4 text-muted-foreground" />
                  Email Address
                </label>
                <div class="relative">
                  <Input
                    v-model="form.email"
                    disabled
                    class="bg-muted pl-9 text-muted-foreground"
                  />
                  <div class="absolute left-3 top-2.5 text-muted-foreground">
                    <Lock class="w-4 h-4 opacity-50" />
                  </div>
                </div>
                <p class="text-xs text-muted-foreground mt-1">
                  Email address cannot be changed. Please contact support for assistance.
                </p>
              </div>
            </div>

            <div class="flex gap-3 pt-2">
              <Button
                v-if="!isEditing"
                variant="outline"
                size="sm"
                class="gap-2"
                @click="isEditing = true"
              >
                Edit Profile
              </Button>
              <template v-else>
                <Button :disabled="isLoading" size="sm" class="gap-2" @click="handleUpdateProfile">
                  <Loader2 v-if="isLoading" class="h-4 w-4 animate-spin" />
                  <Save v-else class="h-4 w-4" />
                  Save Changes
                </Button>
                <Button
                  variant="ghost"
                  :disabled="isLoading"
                  size="sm"
                  class="gap-2"
                  @click="isEditing = false"
                >
                  <X class="h-4 w-4" />
                  Cancel
                </Button>
              </template>
            </div>
          </div>
        </div>
      </Card>

      <!-- Security Section -->
      <div class="space-y-4">
        <div class="flex items-center gap-2 pb-2 border-b border-border">
          <Shield class="w-5 h-5 text-primary" />
          <h4 class="text-lg font-medium text-foreground">Security</h4>
        </div>

        <Card class="p-6">
          <div class="max-w-xl space-y-6">
            <div class="grid gap-4">
              <div class="space-y-2">
                <label class="text-sm font-medium text-foreground">Current Password</label>
                <Input v-model="passwordForm.currentPassword" type="password" placeholder="" />
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-2">
                  <label class="text-sm font-medium text-foreground">New Password</label>
                  <Input v-model="passwordForm.newPassword" type="password" placeholder="" />
                </div>
                <div class="space-y-2">
                  <label class="text-sm font-medium text-foreground">Confirm Password</label>
                  <Input v-model="passwordForm.confirmPassword" type="password" placeholder="" />
                </div>
              </div>
            </div>

            <div class="flex items-center justify-between pt-2">
              <p class="text-xs text-muted-foreground">
                Password must be at least 8 characters long.
              </p>
              <Button
                :disabled="isUpdatingPassword"
                variant="outline"
                size="sm"
                @click="handleUpdatePassword"
              >
                <Loader2 v-if="isUpdatingPassword" class="mr-2 h-4 w-4 animate-spin" />
                Update Password
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  </div>
</template>
