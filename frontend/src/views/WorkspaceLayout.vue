<template>
  <div class="shell">
    <!-- Mobile top bar -->
    <header class="mobile-bar">
      <button class="btn btn-ghost btn-icon" @click="menuOpen = true" aria-label="Open menu">
        <AppIcon name="menu" :size="18" />
      </button>
      <a :href="hrefFor('landing')" class="brand-mini">
        <span class="brand-mark"><AppIcon name="logo" :size="14" :stroke="2.25" /></span>
        Code Converter
      </a>
      <span style="width: 36px" />
    </header>

    <div v-if="menuOpen" class="scrim" @click="menuOpen = false" />

    <aside class="sidebar" :class="{ open: menuOpen }">
      <div class="brand">
        <span class="brand-mark"><AppIcon name="logo" :size="16" :stroke="2.25" /></span>
        <div class="brand-text">
          <strong>Code Converter</strong>
          <span>AI · multi-language</span>
        </div>
        <a :href="hrefFor('landing')" class="btn btn-ghost btn-sm btn-icon collapse" title="Back to home">
          <AppIcon name="chevronLeft" />
        </a>
      </div>

      <nav class="nav">
        <p class="nav-label">Main menu</p>
        <a
          v-for="item in mainNav"
          :key="item.id"
          :href="hrefFor(item.id)"
          class="nav-item"
          :class="{ active: section === item.id }"
          @click="menuOpen = false"
        >
          <AppIcon :name="item.icon" />
          {{ item.label }}
          <span v-if="item.count" class="nav-count">{{ item.count }}</span>
        </a>

        <p class="nav-label">Resources</p>
        <a
          :href="hrefFor('guides')"
          class="nav-item"
          :class="{ active: section === 'guides' }"
          @click="menuOpen = false"
        >
          <AppIcon name="book" />
          Setup guides
        </a>
        <a :href="hrefFor('landing')" class="nav-item">
          <AppIcon name="home" />
          Home page
        </a>
        <a :href="`${API_BASE_URL}/docs`" target="_blank" rel="noopener" class="nav-item">
          <AppIcon name="code" />
          API docs
        </a>
        <a
          href="https://github.com/manziosee/AI-Multi-Language-Code-Converter"
          target="_blank"
          rel="noopener"
          class="nav-item"
        >
          <AppIcon name="github" />
          Source code
        </a>
      </nav>

      <div class="sidebar-foot">
        <button class="nav-item" @click="toggleTheme">
          <AppIcon :name="isDark ? 'sun' : 'moon'" />
          {{ isDark ? 'Light mode' : 'Dark mode' }}
        </button>

        <div class="provider-card">
          <span class="status-dot" :class="statusClass" />
          <div>
            <strong>{{ statusTitle }}</strong>
            <span>{{ statusDetail }}</span>
          </div>
        </div>
      </div>
    </aside>

    <main class="main">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import AppIcon from '@/components/AppIcon.vue';
import { hrefFor, type AppSection } from '@/router';
import { API_BASE_URL } from '@/api/converter';
import { history, backendOnline, providerLabel, providerModel, checkBackend } from '@/stores/workspace';

defineProps<{ section: AppSection }>();

const menuOpen = ref(false);

const mainNav = computed(() => [
  { id: 'convert' as const, label: 'Converter', icon: 'convert', count: 0 },
  { id: 'batch' as const, label: 'Batch convert', icon: 'layers', count: 0 },
  { id: 'history' as const, label: 'History', icon: 'history', count: history.value.length },
]);

const statusClass = computed(() =>
  backendOnline.value === null ? 'pending' : backendOnline.value ? 'online' : 'offline'
);
const statusTitle = computed(() =>
  backendOnline.value === null
    ? 'Connecting…'
    : backendOnline.value
      ? `${providerLabel.value || 'AI'} connected`
      : 'Backend offline'
);
const statusDetail = computed(() =>
  backendOnline.value ? providerModel.value || 'Ready' : backendOnline.value === false ? 'Check VITE_API_URL' : 'Checking API'
);

// Theme
const isDark = ref(false);
function applyTheme(theme: 'light' | 'dark') {
  document.documentElement.dataset.theme = theme;
  isDark.value = theme === 'dark';
  try {
    localStorage.setItem('theme', theme);
  } catch {
    /* storage unavailable */
  }
}
function toggleTheme() {
  applyTheme(isDark.value ? 'light' : 'dark');
}

onMounted(() => {
  const explicit = document.documentElement.dataset.theme;
  isDark.value = explicit
    ? explicit === 'dark'
    : window.matchMedia('(prefers-color-scheme: dark)').matches;
  checkBackend();
});
</script>

<style scoped>
.shell {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  width: var(--sidebar-w);
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px 12px;
  background: var(--surface-2);
  border-right: 1px solid var(--border);
  overflow-y: auto;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 8px 16px;
  border-bottom: 1px solid var(--border);
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 9px;
  background: var(--ink);
  color: var(--ink-text);
  flex-shrink: 0;
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
  min-width: 0;
  flex: 1;
}

.brand-text strong {
  font-size: 14px;
}

.brand-text span {
  font-size: 12px;
  color: var(--text-3);
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding-top: 8px;
}

.nav-label {
  padding: 14px 10px 6px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-3);
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  height: 34px;
  padding: 0 10px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: var(--text-2);
  font-size: 13.5px;
  font-weight: 500;
  text-align: left;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.nav-item:hover {
  background: var(--surface-hover);
  color: var(--text);
}

.nav-item.active {
  background: var(--surface);
  color: var(--text);
  box-shadow: var(--shadow-sm);
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: -12px;
  top: 7px;
  bottom: 7px;
  width: 3px;
  border-radius: 0 3px 3px 0;
  background: var(--accent);
}

.nav-count {
  margin-left: auto;
  min-width: 22px;
  height: 20px;
  padding: 0 6px;
  border-radius: 6px;
  background: var(--surface-hover);
  border: 1px solid var(--border);
  font-size: 11px;
  display: grid;
  place-items: center;
  color: var(--text-3);
}

.sidebar-foot {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

.provider-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: var(--radius);
  background: var(--surface);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-xs);
}

.provider-card div {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
  min-width: 0;
}

.provider-card strong {
  font-size: 12.5px;
}

.provider-card span {
  font-size: 11.5px;
  color: var(--text-3);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  background: var(--text-3);
}

.status-dot.online {
  background: #22c55e;
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.18);
}

.status-dot.offline {
  background: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.18);
}

.status-dot.pending {
  animation: pulse 1.2s ease-in-out infinite;
}

@keyframes pulse {
  50% { opacity: 0.3; }
}

.main {
  flex: 1;
  min-width: 0;
  padding: 28px 32px 48px;
}

.mobile-bar,
.scrim {
  display: none;
}

@media (max-width: 960px) {
  .shell {
    flex-direction: column;
  }

  .mobile-bar {
    position: sticky;
    top: 0;
    z-index: 30;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
  }

  .brand-mini {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
  }

  .brand-mini .brand-mark {
    width: 26px;
    height: 26px;
    border-radius: 7px;
  }

  .sidebar {
    position: fixed;
    z-index: 50;
    left: 0;
    top: 0;
    transform: translateX(-100%);
    transition: transform 0.2s ease;
    box-shadow: var(--shadow-lg);
  }

  .sidebar.open {
    transform: none;
  }

  .scrim {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 40;
    background: rgba(0, 0, 0, 0.35);
  }

  .main {
    padding: 20px 16px 40px;
  }
}
</style>
