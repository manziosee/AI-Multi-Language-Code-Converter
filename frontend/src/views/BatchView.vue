<template>
  <div class="page">
    <div class="page-head">
      <div>
        <h1>Batch convert</h1>
        <p class="muted">Convert up to 10 files in one go with the same language pair.</p>
      </div>
      <div class="head-actions">
        <button class="btn" :disabled="!files.length || isConverting" @click="reset">
          <AppIcon name="trash" /> Clear
        </button>
        <button class="btn btn-primary" :disabled="!canConvert" @click="convertBatch">
          <span v-if="isConverting" class="spinner" />
          <AppIcon v-else name="sparkles" />
          {{ isConverting ? `Converting ${files.length} files…` : `Convert ${files.length || ''} file${files.length === 1 ? '' : 's'}` }}
        </button>
      </div>
    </div>

    <div class="toolbar">
      <div class="lang-picker">
        <select v-model="source" class="select" aria-label="Source language">
          <option value="" disabled>Source language</option>
          <option v-for="l in SUPPORTED_LANGUAGES" :key="l.value" :value="l.value">{{ l.label }}</option>
        </select>
        <AppIcon name="arrowRight" class="muted" />
        <select v-model="target" class="select" :disabled="!source" aria-label="Target language">
          <option value="" disabled>Target language</option>
          <option v-for="l in targets" :key="l.value" :value="l.value">{{ l.label }}</option>
        </select>
      </div>
      <span class="badge" :class="files.length >= 10 ? 'badge-amber' : ''">{{ files.length }}/10 files</span>
    </div>

    <div v-if="error" class="alert" role="alert">
      <AppIcon name="alert" />
      <span>{{ error }}</span>
      <button class="btn btn-ghost btn-sm btn-icon" @click="error = ''" aria-label="Dismiss"><AppIcon name="x" /></button>
    </div>

    <!-- Drop zone -->
    <div
      class="drop card"
      :class="{ over: dragging, full: files.length >= 10 }"
      @click="files.length < 10 && fileInput?.click()"
      @drop.prevent="handleDrop"
      @dragover.prevent="dragging = true"
      @dragleave.prevent="dragging = false"
    >
      <input
        ref="fileInput"
        type="file"
        multiple
        hidden
        accept=".py,.js,.mjs,.cjs,.ts,.java,.php,.go,.c,.cpp,.cc,.cs,.rs,.sql,.prisma"
        @change="handleFileSelect"
      />
      <span class="drop-icon"><AppIcon name="upload" :size="20" /></span>
      <p><strong>Click to choose files</strong> or drag and drop</p>
      <span class="muted">.py .js .ts .java .php .go .c .cpp .cs .rs .sql · up to 10 files</span>
    </div>

    <!-- Files / results table -->
    <div v-if="files.length" class="card table-card">
      <div class="table-scroll">
        <table>
          <thead>
            <tr>
              <th>File</th>
              <th class="num">Size</th>
              <th>Status</th>
              <th class="actions-col"><span class="sr-only">Actions</span></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(file, idx) in files" :key="file.name + idx">
              <td>
                <div class="file-cell">
                  <span class="file-icon"><AppIcon name="file" /></span>
                  <span class="name">{{ file.name }}</span>
                </div>
              </td>
              <td class="num muted">{{ formatSize(file.size) }}</td>
              <td>
                <span v-if="isConverting" class="badge"><span class="spinner" /> Converting</span>
                <span v-else-if="resultFor(file.name)?.success" class="badge badge-green">Converted</span>
                <span v-else-if="resultFor(file.name)" class="badge badge-red" :title="resultFor(file.name)?.error">Failed</span>
                <span v-else class="badge">Ready</span>
              </td>
              <td class="actions-col">
                <button
                  v-if="resultFor(file.name)?.success"
                  class="btn btn-sm"
                  @click="downloadFile(file.name, resultFor(file.name)!.converted_code!)"
                >
                  <AppIcon name="download" /> Download
                </button>
                <button
                  class="btn btn-ghost btn-sm btn-icon"
                  :disabled="isConverting"
                  @click="removeFile(idx)"
                  aria-label="Remove"
                >
                  <AppIcon name="x" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="results.length" class="table-foot">
        <span>
          <span class="badge badge-green">{{ results.filter((r) => r.success).length }} succeeded</span>
          <span v-if="results.some((r) => !r.success)" class="badge badge-red">
            {{ results.filter((r) => !r.success).length }} failed
          </span>
        </span>
        <button class="btn btn-sm" @click="downloadAll" :disabled="!results.some((r) => r.success)">
          <AppIcon name="download" /> Download all
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import AppIcon from '@/components/AppIcon.vue';
import { converterApi } from '@/api/converter';
import { SUPPORTED_LANGUAGES, VALID_CONVERSIONS, type Language } from '@/types';
import { sourceLanguage, targetLanguage } from '@/stores/workspace';

interface BatchResult {
  name: string;
  success: boolean;
  converted_code?: string;
  error?: string;
}

const EXT_MAP: Record<string, Language> = {
  py: 'python', js: 'javascript', mjs: 'javascript', cjs: 'nodejs', ts: 'typescript',
  java: 'java', php: 'php', go: 'golang', c: 'c', cpp: 'cpp', cc: 'cpp', cs: 'csharp',
  rs: 'rust', sql: 'sql', prisma: 'prisma',
};

// Start from whatever pair the main converter has selected.
const source = ref<Language | ''>(sourceLanguage.value);
const target = ref<Language | ''>(targetLanguage.value);

const targets = computed(() => {
  if (!source.value) return SUPPORTED_LANGUAGES;
  const valid = VALID_CONVERSIONS[source.value] || [];
  return SUPPORTED_LANGUAGES.filter((l) => valid.includes(l.value));
});

watch(source, () => {
  if (target.value && !targets.value.some((l) => l.value === target.value)) target.value = '';
});

const fileInput = ref<HTMLInputElement | null>(null);
const files = ref<File[]>([]);
const results = ref<BatchResult[]>([]);
const isConverting = ref(false);
const dragging = ref(false);
const error = ref('');

const canConvert = computed(
  () => files.value.length > 0 && !!source.value && !!target.value && !isConverting.value
);

const resultFor = (name: string) => results.value.find((r) => r.name === name);

function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement;
  if (input.files) addFiles(Array.from(input.files));
  input.value = '';
}

function handleDrop(event: DragEvent) {
  dragging.value = false;
  if (event.dataTransfer?.files) addFiles(Array.from(event.dataTransfer.files));
}

function addFiles(newFiles: File[]) {
  error.value = '';
  const tooBig = newFiles.filter((f) => f.size > 1024 * 1024);
  if (tooBig.length) error.value = `Skipped files over 1MB: ${tooBig.map((f) => f.name).join(', ')}`;
  const remaining = 10 - files.value.length;
  const accepted = newFiles.filter((f) => f.size <= 1024 * 1024).slice(0, remaining);
  files.value.push(...accepted);
  results.value = [];

  if (!source.value && accepted[0]) {
    const ext = accepted[0].name.split('.').pop()?.toLowerCase();
    if (ext && EXT_MAP[ext]) source.value = EXT_MAP[ext];
  }
}

function removeFile(index: number) {
  files.value.splice(index, 1);
  results.value = [];
}

function reset() {
  files.value = [];
  results.value = [];
  error.value = '';
}

async function convertBatch() {
  if (!canConvert.value) return;
  isConverting.value = true;
  results.value = [];
  error.value = '';

  try {
    const fileData = await Promise.all(
      files.value.map(async (file) => ({ name: file.name, code: await file.text() }))
    );
    const response = await converterApi.batchConvert({
      files: fileData,
      source_language: source.value,
      target_language: target.value,
    });
    results.value = response.results;
  } catch (err: any) {
    error.value = 'Batch conversion failed: ' + (err.response?.data?.detail || err.message);
  } finally {
    isConverting.value = false;
  }
}

function outputName(filename: string) {
  const ext = SUPPORTED_LANGUAGES.find((l) => l.value === target.value)?.extension || '.txt';
  return filename.replace(/\.[^.]+$/, '') + '_converted' + ext;
}

function downloadFile(filename: string, content: string) {
  const blob = new Blob([content], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = outputName(filename);
  a.click();
  URL.revokeObjectURL(url);
}

function downloadAll() {
  results.value
    .filter((r) => r.success && r.converted_code)
    .forEach((r, i) => setTimeout(() => downloadFile(r.name, r.converted_code!), i * 250));
}

const formatSize = (b: number) => (b < 1024 ? `${b} B` : `${(b / 1024).toFixed(1)} KB`);
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 1100px;
  margin: 0 auto;
}

.page-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.page-head h1 {
  font-size: 24px;
  margin-bottom: 2px;
}

.head-actions {
  display: flex;
  gap: 8px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.lang-picker {
  display: flex;
  align-items: center;
  gap: 8px;
}

.lang-picker .select {
  min-width: 170px;
}

.alert {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius);
  background: var(--red-soft);
  color: var(--red);
  font-size: 13px;
}

.alert span {
  flex: 1;
}

.alert .btn {
  color: inherit;
}

.drop {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 36px 16px;
  border: 1.5px dashed var(--border-strong);
  background: var(--surface);
  text-align: center;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.drop:hover,
.drop.over {
  border-color: var(--accent);
  background: var(--accent-soft);
}

.drop.full {
  cursor: not-allowed;
  opacity: 0.6;
}

.drop-icon {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  margin-bottom: 6px;
  border-radius: 12px;
  background: var(--accent-soft);
  color: var(--accent-text);
}

.drop span.muted {
  font-size: 12px;
}

.table-card {
  overflow: hidden;
}

.table-scroll {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

th {
  height: 40px;
  padding: 0 16px;
  text-align: left;
  font-weight: 500;
  font-size: 12.5px;
  color: var(--text-2);
  background: var(--surface-2);
  border-bottom: 1px solid var(--border);
}

td {
  height: 52px;
  padding: 0 16px;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}

tbody tr:last-child td {
  border-bottom: 0;
}

.num {
  text-align: right;
}

.file-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-icon {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: var(--surface-hover);
  color: var(--text-2);
}

.name {
  font-weight: 500;
}

.badge .spinner {
  width: 10px;
  height: 10px;
  border-width: 1.5px;
}

.actions-col {
  text-align: right;
  width: 1%;
}

.actions-col .btn + .btn {
  margin-left: 4px;
}

.table-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 10px 16px;
  border-top: 1px solid var(--border);
}

.table-foot > span {
  display: flex;
  gap: 6px;
}

@media (max-width: 640px) {
  .head-actions,
  .head-actions .btn {
    flex: 1;
  }

  .lang-picker {
    width: 100%;
  }

  .lang-picker .select {
    flex: 1;
    min-width: 0;
  }
}
</style>
