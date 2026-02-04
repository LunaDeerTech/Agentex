<script setup lang="ts">
  import { useRoute } from 'vue-router'
  import {
    User,
    Key,
    Cpu,
    Network,
    Database,
    Zap,
    Activity,
    Users,
    Settings as SettingsIcon
  } from 'lucide-vue-next'

  const route = useRoute()

  const menuGroups = [
    {
      title: 'Account',
      items: [
        { name: 'Profile', path: '/settings/profile', icon: User },
        { name: 'API Keys', path: '/settings/api-keys', icon: Key }
      ]
    },
    {
      title: 'Resources',
      items: [
        { name: 'Models', path: '/settings/models', icon: Cpu },
        { name: 'MCP Connections', path: '/settings/mcp', icon: Network },
        { name: 'Knowledge Base', path: '/settings/knowledge', icon: Database },
        { name: 'Skills', path: '/settings/skills', icon: Zap },
        { name: 'Rules Engine', path: '/settings/rules', icon: Activity }
      ]
    },
    {
      title: 'System',
      items: [
        { name: 'Users', path: '/settings/users', icon: Users },
        { name: 'System Settings', path: '/settings/system', icon: SettingsIcon }
      ]
    }
  ]

  const isActive = (path: string) => route.path === path || route.path.startsWith(path + '/')
</script>

<template>
  <nav class="flex-1 overflow-y-auto py-4 px-3 space-y-8">
    <div v-for="(group, idx) in menuGroups" :key="idx">
      <div
        class="px-3 mb-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-widest font-mono"
      >
        {{ group.title }}
      </div>
      <div class="space-y-0.5">
        <router-link
          v-for="item in group.items"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-all duration-200 group relative border border-transparent"
          :class="[
            isActive(item.path)
              ? 'bg-accent text-accent-foreground font-medium shadow-sm'
              : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground'
          ]"
        >
          <component
            :is="item.icon"
            class="w-4 h-4 shrink-0 transition-colors"
            :class="
              isActive(item.path)
                ? 'text-primary'
                : 'text-muted-foreground group-hover:text-foreground'
            "
            :stroke-width="1.5"
          />
          {{ item.name }}
          <div
            v-if="isActive(item.path)"
            class="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-4 bg-primary rounded-r-full"
          ></div>
        </router-link>
      </div>
    </div>
  </nav>
</template>
