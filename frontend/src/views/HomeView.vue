<script setup lang="ts">
  import { Bot, Sparkles, Zap, Database, ArrowRight } from 'lucide-vue-next'
  import { RouterLink } from 'vue-router'

  const features = [
    {
      icon: Bot,
      title: 'AI Agents',
      description: 'Intelligent agents with ReAct reasoning and tool integration'
    },
    {
      icon: Zap,
      title: 'MCP Integration',
      description: 'Connect to any MCP server for extended capabilities'
    },
    {
      icon: Database,
      title: 'RAG Knowledge Base',
      description: 'Build and query vector-based knowledge repositories'
    },
    {
      icon: Sparkles,
      title: 'SKILL Engine',
      description: 'Create reusable skills with natural language definitions'
    }
  ]
</script>

<template>
  <div class="home-view">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <div class="hero-badge">
          <Sparkles class="w-4 h-4" />
          <span>AI Agent Platform</span>
        </div>

        <h1 class="hero-title">
          Welcome to
          <span class="text-gradient">Agentex</span>
        </h1>

        <p class="hero-description">
          A powerful Web AI Agent platform with MCP integration, RAG knowledge bases, SKILL
          management, and an intelligent rule engine.
        </p>

        <div class="hero-actions">
          <RouterLink to="/chat" class="btn btn-primary">
            <span>Start Chat</span>
            <ArrowRight class="w-4 h-4" />
          </RouterLink>
          <a
            href="https://github.com/agentex"
            target="_blank"
            rel="noopener noreferrer"
            class="btn btn-secondary"
          >
            View on GitHub
          </a>
        </div>
      </div>

      <!-- Decorative Grid -->
      <div class="hero-grid"></div>
    </section>

    <!-- Features Section -->
    <section class="features">
      <h2 class="section-title">Core Features</h2>
      <div class="features-grid">
        <div v-for="feature in features" :key="feature.title" class="feature-card">
          <div class="feature-icon">
            <component :is="feature.icon" class="w-5 h-5" />
          </div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-description">{{ feature.description }}</p>
        </div>
      </div>
    </section>

    <!-- Status Section -->
    <section class="status">
      <div class="status-card">
        <div class="status-indicator"></div>
        <span class="status-text">System Online</span>
        <span class="status-version">v0.1.0</span>
      </div>
    </section>
  </div>
</template>

<style scoped>
  .home-view {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: var(--spacing-8) var(--spacing-4);
  }

  /* Hero Section */
  .hero {
    position: relative;
    max-width: 800px;
    width: 100%;
    text-align: center;
    padding: var(--spacing-16) 0;
  }

  .hero-content {
    position: relative;
    z-index: 1;
  }

  .hero-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-2);
    padding: var(--spacing-2) var(--spacing-4);
    background: var(--color-bg-secondary);
    border: var(--border-width) solid var(--color-border-default);
    border-radius: var(--radius-full);
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    margin-bottom: var(--spacing-6);
  }

  .hero-title {
    font-size: clamp(2.5rem, 8vw, 4rem);
    font-weight: var(--font-bold);
    line-height: 1.1;
    margin-bottom: var(--spacing-6);
    letter-spacing: -0.02em;
  }

  .hero-description {
    font-size: var(--text-lg);
    color: var(--color-text-secondary);
    max-width: 600px;
    margin: 0 auto var(--spacing-8);
    line-height: var(--leading-relaxed);
  }

  .hero-actions {
    display: flex;
    gap: var(--spacing-4);
    justify-content: center;
    flex-wrap: wrap;
  }

  /* Buttons */
  .btn {
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-2);
    padding: var(--spacing-3) var(--spacing-6);
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    border-radius: var(--radius-md);
    border: var(--border-width) solid transparent;
    cursor: pointer;
    transition:
      background var(--transition-fast),
      border-color var(--transition-fast);
    text-decoration: none;
  }

  .btn-primary {
    background: var(--color-accent-primary);
    color: var(--color-text-primary);
    border-color: var(--color-accent-primary);
  }

  .btn-primary:hover {
    background: var(--color-accent-hover);
    border-color: var(--color-accent-hover);
  }

  .btn-secondary {
    background: transparent;
    color: var(--color-text-primary);
    border-color: var(--color-border-default);
  }

  .btn-secondary:hover {
    background: var(--color-bg-hover);
    border-color: var(--color-text-tertiary);
  }

  /* Hero Grid */
  .hero-grid {
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    max-width: 1200px;
    height: 100%;
    background-image:
      linear-gradient(var(--color-border-muted) 1px, transparent 1px),
      linear-gradient(90deg, var(--color-border-muted) 1px, transparent 1px);
    background-size: 60px 60px;
    opacity: 0.3;
    mask-image: radial-gradient(ellipse at center, black 0%, transparent 70%);
    -webkit-mask-image: radial-gradient(ellipse at center, black 0%, transparent 70%);
  }

  /* Features Section */
  .features {
    max-width: 1000px;
    width: 100%;
    padding: var(--spacing-16) 0;
  }

  .section-title {
    font-size: var(--text-xl);
    font-weight: var(--font-semibold);
    text-align: center;
    margin-bottom: var(--spacing-8);
    color: var(--color-text-secondary);
  }

  .features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: var(--spacing-4);
  }

  .feature-card {
    padding: var(--spacing-6);
    background: var(--color-bg-secondary);
    border: var(--border-width) solid var(--color-border-default);
    border-radius: var(--radius-lg);
    transition:
      border-color var(--transition-fast),
      background var(--transition-fast);
  }

  .feature-card:hover {
    border-color: var(--color-border-focus);
    background: var(--color-bg-tertiary);
  }

  .feature-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    background: var(--color-accent-bg);
    border: var(--border-width) solid var(--color-border-default);
    border-radius: var(--radius-md);
    color: var(--color-accent-primary);
    margin-bottom: var(--spacing-4);
  }

  .feature-title {
    font-size: var(--text-base);
    font-weight: var(--font-semibold);
    margin-bottom: var(--spacing-2);
  }

  .feature-description {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    line-height: var(--leading-relaxed);
  }

  /* Status Section */
  .status {
    padding: var(--spacing-8) 0;
  }

  .status-card {
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-3);
    padding: var(--spacing-3) var(--spacing-5);
    background: var(--color-bg-secondary);
    border: var(--border-width) solid var(--color-border-default);
    border-radius: var(--radius-full);
  }

  .status-indicator {
    width: 8px;
    height: 8px;
    background: var(--color-success);
    border-radius: var(--radius-full);
    animation: pulse-status 2s ease-in-out infinite;
  }

  @keyframes pulse-status {
    0%,
    100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }

  .status-text {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
  }

  .status-version {
    font-size: var(--text-xs);
    color: var(--color-text-tertiary);
    font-family: var(--font-mono);
  }
</style>
