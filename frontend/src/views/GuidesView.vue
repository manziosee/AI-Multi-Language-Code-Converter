<template>
  <div class="page">
    <div class="page-head">
      <div>
        <h1>Setup guides</h1>
        <p class="muted">Dependencies, install and run commands for every target language.</p>
      </div>
    </div>

    <div class="layout">
      <nav class="card lang-list" aria-label="Languages">
        <button
          v-for="l in SUPPORTED_LANGUAGES"
          :key="l.value"
          :class="{ active: selected === l.value }"
          @click="selected = l.value"
        >
          <span class="ext">{{ l.extension }}</span>
          {{ l.label }}
        </button>
      </nav>

      <section class="card guide-card">
        <header>
          <h3>{{ guide.language }}</h3>
          <span class="badge">{{ guide.packageManager }}</span>
        </header>
        <div class="body">
          <SetupGuideBody :guide="guide" />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import SetupGuideBody from '@/components/SetupGuideBody.vue';
import { SUPPORTED_LANGUAGES, type Language } from '@/types';
import { SETUP_GUIDES } from '@/utils/setupGuides';
import { targetLanguage } from '@/stores/workspace';

const selected = ref<Language>((targetLanguage.value as Language) || 'python');
const guide = computed(() => SETUP_GUIDES[selected.value]);
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 1100px;
  margin: 0 auto;
}

.page-head h1 {
  font-size: 24px;
  margin-bottom: 2px;
}

.layout {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 16px;
  align-items: start;
}

.lang-list {
  display: flex;
  flex-direction: column;
  padding: 6px;
  gap: 2px;
  position: sticky;
  top: 20px;
}

.lang-list button {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 34px;
  padding: 0 10px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: var(--text-2);
  font-weight: 500;
  font-size: 13px;
  text-align: left;
  cursor: pointer;
}

.lang-list button:hover {
  background: var(--surface-hover);
  color: var(--text);
}

.lang-list button.active {
  background: var(--accent-soft);
  color: var(--accent-text);
}

.ext {
  width: 52px;
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text-3);
}

.active .ext {
  color: inherit;
  opacity: 0.75;
}

.guide-card header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  border-bottom: 1px solid var(--border);
}

.guide-card header h3 {
  font-size: 15px;
}

.body {
  padding: 18px;
}

@media (max-width: 760px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .lang-list {
    position: static;
    flex-direction: row;
    overflow-x: auto;
  }

  .lang-list button {
    flex-shrink: 0;
  }

  .ext {
    display: none;
  }
}
</style>
