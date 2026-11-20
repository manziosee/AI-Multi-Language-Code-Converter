<template>
  <div class="guide">
    <div class="block">
      <h5><AppIcon name="package" /> Dependencies</h5>
      <div class="chips">
        <span v-for="dep in guide.dependencies" :key="dep" class="badge">{{ dep }}</span>
      </div>
    </div>

    <div class="block">
      <h5><AppIcon name="terminal" /> Install</h5>
      <div class="cmd">
        <code>{{ guide.installCommand }}</code>
        <button class="btn btn-ghost btn-sm btn-icon" @click="copy(guide.installCommand)" title="Copy">
          <AppIcon :name="copied === guide.installCommand ? 'check' : 'copy'" />
        </button>
      </div>
    </div>

    <div class="block">
      <h5><AppIcon name="play" /> Run</h5>
      <div class="cmd">
        <code>{{ guide.runCommand }}</code>
        <button class="btn btn-ghost btn-sm btn-icon" @click="copy(guide.runCommand)" title="Copy">
          <AppIcon :name="copied === guide.runCommand ? 'check' : 'copy'" />
        </button>
      </div>
    </div>

    <div v-if="guide.configFiles.length" class="block">
      <h5><AppIcon name="file" /> Configuration files</h5>
      <div v-for="file in guide.configFiles" :key="file.name" class="file">
        <div class="file-head">
          <span>{{ file.name }}</span>
          <button class="btn btn-ghost btn-sm" @click="copy(file.content)">
            <AppIcon :name="copied === file.content ? 'check' : 'copy'" /> Copy
          </button>
        </div>
        <pre>{{ file.content }}</pre>
      </div>
    </div>

    <div class="block">
      <h5><AppIcon name="bulb" /> Tips</h5>
      <ul>
        <li v-for="note in guide.notes" :key="note">{{ note }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import AppIcon from '@/components/AppIcon.vue';
import type { SetupGuide } from '@/utils/setupGuides';
import { copyToClipboard } from '@/utils/clipboard';

defineProps<{ guide: SetupGuide }>();

const copied = ref('');
async function copy(text: string) {
  if (await copyToClipboard(text)) {
    copied.value = text;
    setTimeout(() => (copied.value = ''), 1500);
  }
}
</script>

<style scoped>
.guide {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

h5 {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-3);
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.cmd {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 6px 6px 12px;
  border-radius: var(--radius);
  background: var(--code-bg);
  color: var(--code-text);
  font-size: 12.5px;
}

.cmd code {
  flex: 1;
  overflow-x: auto;
  white-space: nowrap;
}

.cmd .btn {
  color: var(--code-muted);
}

.file {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  margin-bottom: 8px;
}

.file-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 6px 4px 12px;
  background: var(--surface-2);
  border-bottom: 1px solid var(--border);
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 500;
}

.file pre {
  padding: 12px;
  margin: 0;
  background: var(--code-bg);
  color: var(--code-text);
  font-size: 12px;
  line-height: 1.6;
  overflow-x: auto;
}

ul {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: var(--text-2);
}

li {
  position: relative;
  padding-left: 16px;
}

li::before {
  content: '';
  position: absolute;
  left: 4px;
  top: 0.65em;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent);
}
</style>
