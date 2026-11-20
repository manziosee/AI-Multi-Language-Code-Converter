<template>
  <div class="page">
    <!-- Page header -->
    <div class="page-head">
      <div>
        <h1>Converter</h1>
        <p class="muted">Paste or upload code, pick a target language, and stream the translation.</p>
      </div>
      <div class="head-actions">
        <button
          class="btn"
          @click="explainCode"
          :disabled="!sourceLanguage || !sourceCode.trim() || isExplaining"
          title="Ctrl+E"
        >
          <span v-if="isExplaining" class="spinner" />
          <AppIcon v-else name="bulb" />
          {{ isExplaining ? 'Explaining…' : 'Explain' }}
        </button>
        <button
          class="btn btn-primary"
          @click="convertCode"
          :disabled="!canConvert || isConverting"
          title="Ctrl+Enter"
        >
          <span v-if="isConverting" class="spinner" />
          <AppIcon v-else name="sparkles" />
          {{ isConverting ? 'Converting…' : 'Convert' }}
          <kbd v-if="!isConverting" class="hide-sm">Ctrl ↵</kbd>
        </button>
      </div>
    </div>

    <!-- Toolbar -->
    <div class="toolbar">
      <div class="lang-picker">
        <label class="sr-only" for="src-lang">Source language</label>
        <select id="src-lang" v-model="sourceLanguage" class="select">
          <option value="" disabled>Source language</option>
          <option v-for="lang in languages" :key="lang.value" :value="lang.value">{{ lang.label }}</option>
        </select>
        <button
          class="btn btn-icon"
          :disabled="!canSwap"
          @click="swapLanguages"
          title="Swap languages"
          aria-label="Swap languages"
        >
          <AppIcon name="swap" />
        </button>
        <label class="sr-only" for="tgt-lang">Target language</label>
        <select id="tgt-lang" v-model="targetLanguage" class="select" :disabled="!sourceLanguage">
          <option value="" disabled>Target language</option>
          <option v-for="lang in availableTargetLanguages" :key="lang.value" :value="lang.value">
            {{ lang.label }}
          </option>
        </select>
      </div>

      <div class="toolbar-right">
        <input
          ref="fileInput"
          type="file"
          @change="handleFileSelect"
          accept=".py,.js,.mjs,.cjs,.ts,.java,.php,.go,.sql,.prisma,.c,.cpp,.cc,.cs,.rs"
          hidden
        />
        <button class="btn" @click="fileInput?.click()">
          <AppIcon name="upload" /> Upload file
        </button>
        <button class="btn" @click="loadExample" :disabled="!sourceLanguage" title="Load an example for the source language">
          <AppIcon name="file" /> Example
        </button>
        <div class="seg" role="group" aria-label="Layout">
          <button :class="{ on: viewMode === 'split' }" @click="viewMode = 'split'" title="Side by side">
            <AppIcon name="columns" />
          </button>
          <button :class="{ on: viewMode === 'single' }" @click="viewMode = 'single'" title="Stacked">
            <AppIcon name="rows" />
          </button>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="stats">
      <div class="stat">
        <span class="stat-label">Source lines</span>
        <strong>{{ sourceStats?.lines ?? 0 }}</strong>
        <span class="stat-foot">
          <span class="badge">{{ sourceStats?.characters ?? 0 }} chars</span>
          <span v-if="uploadedFile" class="trunc">{{ uploadedFile.name }}</span>
        </span>
      </div>
      <div class="stat">
        <span class="stat-label">Output lines</span>
        <strong>{{ convertedStats?.lines ?? 0 }}</strong>
        <span class="stat-foot">
          <span class="badge" :class="lineDelta >= 0 ? 'badge-green' : 'badge-amber'" v-if="convertedStats">
            {{ lineDelta >= 0 ? '+' : '' }}{{ lineDelta }} vs source
          </span>
          <span v-else class="muted">Waiting for conversion</span>
        </span>
      </div>
      <div class="stat">
        <span class="stat-label">Saved conversions</span>
        <strong>{{ history.length }}</strong>
        <span class="stat-foot">
          <a :href="hrefFor('history')" class="link">Open history <AppIcon name="arrowRight" :size="12" /></a>
        </span>
      </div>
      <div class="stat">
        <span class="stat-label">Language pair</span>
        <strong class="pair">
          {{ getLanguageLabel(sourceLanguage) || '—' }}
          <AppIcon name="arrowRight" :size="16" class="muted" />
          {{ getLanguageLabel(targetLanguage) || '—' }}
        </strong>
        <span class="stat-foot">
          <span class="badge badge-violet">{{ languages.length }} languages</span>
        </span>
      </div>
    </div>

    <!-- Error -->
    <div v-if="errorMessage" class="alert" role="alert">
      <AppIcon name="alert" />
      <span>{{ errorMessage }}</span>
      <button class="btn btn-ghost btn-sm btn-icon" @click="errorMessage = ''" aria-label="Dismiss">
        <AppIcon name="x" />
      </button>
    </div>

    <!-- Editors -->
    <div class="editors card" :class="viewMode">
      <section
        class="pane"
        :class="{ dragging: isDragging }"
        @drop.prevent="handleFileDrop"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
      >
        <header class="pane-head">
          <div class="pane-title">
            <span class="dot dot-src" />
            Source
            <span v-if="sourceLanguage" class="badge">{{ getLanguageLabel(sourceLanguage) }}</span>
          </div>
          <div class="pane-actions">
            <button v-if="sourceCode" class="btn btn-ghost btn-sm" @click="copySource">
              <AppIcon :name="copiedSource ? 'check' : 'copy'" /> {{ copiedSource ? 'Copied' : 'Copy' }}
            </button>
            <button v-if="sourceCode" class="btn btn-ghost btn-sm" @click="clearSource">
              <AppIcon name="trash" /> Clear
            </button>
          </div>
        </header>
        <div class="code-wrap">
          <textarea
            v-model="sourceCode"
            @input="updateSourceStats"
            class="code-area"
            spellcheck="false"
            placeholder="Paste your code here, or drop a file anywhere on this panel…"
            :disabled="isConverting"
          />
          <div v-if="isDragging" class="drop-hint">
            <AppIcon name="upload" :size="22" />
            Drop file to load
          </div>
        </div>
      </section>

      <section class="pane">
        <header class="pane-head">
          <div class="pane-title">
            <span class="dot dot-out" />
            Output
            <span v-if="targetLanguage" class="badge badge-accent">{{ getLanguageLabel(targetLanguage) }}</span>
            <span v-if="isConverting" class="streaming"><span class="spinner" /> Streaming</span>
          </div>
          <div class="pane-actions">
            <button v-if="convertedCode" class="btn btn-ghost btn-sm" @click="copyConverted">
              <AppIcon :name="copiedConverted ? 'check' : 'copy'" /> {{ copiedConverted ? 'Copied' : 'Copy' }}
            </button>
            <button v-if="convertedCode" class="btn btn-ghost btn-sm" @click="downloadCode" title="Ctrl+D">
              <AppIcon name="download" /> Download
            </button>
            <button v-if="targetLanguage" class="btn btn-ghost btn-sm" @click="showSetupGuidePanel">
              <AppIcon name="settings" /> Setup
            </button>
          </div>
        </header>
        <div class="code-wrap">
          <pre v-if="convertedCode" class="code-out"><code
            class="hljs"
            v-html="highlightCode(convertedCode, targetLanguage)"
          /></pre>
          <div v-else class="empty-out">
            <AppIcon name="code" :size="26" />
            <p>Converted code will appear here</p>
            <span>
              <kbd>Ctrl</kbd> <kbd>↵</kbd> convert ·
              <kbd>Ctrl</kbd> <kbd>E</kbd> explain ·
              <kbd>Ctrl</kbd> <kbd>D</kbd> download
            </span>
          </div>
        </div>
      </section>
    </div>

    <!-- Explanation + setup guide -->
    <div v-if="explanation || (showSetupGuide && setupGuide)" class="panels">
      <section v-if="explanation" class="card panel">
        <header class="panel-head">
          <h3><AppIcon name="bulb" /> Code explanation</h3>
          <button class="btn btn-ghost btn-sm btn-icon" @click="explanation = ''" aria-label="Close">
            <AppIcon name="x" />
          </button>
        </header>
        <div class="panel-body explanation" v-html="formatExplanation(explanation)" />
      </section>

      <section v-if="showSetupGuide && setupGuide" class="card panel">
        <header class="panel-head">
          <h3><AppIcon name="settings" /> {{ setupGuide.language }} setup</h3>
          <button class="btn btn-ghost btn-sm btn-icon" @click="showSetupGuide = false" aria-label="Close">
            <AppIcon name="x" />
          </button>
        </header>
        <div class="panel-body">
          <SetupGuideBody :guide="setupGuide" />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import AppIcon from '@/components/AppIcon.vue';
import SetupGuideBody from '@/components/SetupGuideBody.vue';
import { converterApi, StreamInterruptedError } from '@/api/converter';
import { SUPPORTED_LANGUAGES, VALID_CONVERSIONS } from '@/types';
import type { Language, ViewMode } from '@/types';
import { hrefFor } from '@/router';
import {
  sourceLanguage,
  targetLanguage,
  sourceCode,
  convertedCode,
  history,
  loadHistory,
} from '@/stores/workspace';
import { saveToHistory } from '@/utils/localStorage';
import { copyToClipboard } from '@/utils/clipboard';
import { getCodeStats, type CodeStats } from '@/utils/codeStats';
import { SETUP_GUIDES, type SetupGuide } from '@/utils/setupGuides';
import { CODE_EXAMPLES } from '@/utils/codeExamples';
import { detectLanguage } from '@/utils/languageDetector';
import { validateSyntax } from '@/utils/syntaxValidator';
import { highlightCode } from '@/utils/highlight';

const languages = SUPPORTED_LANGUAGES;

const availableTargetLanguages = computed(() => {
  if (!sourceLanguage.value) return languages;
  const validTargets = VALID_CONVERSIONS[sourceLanguage.value as Language] || [];
  return languages.filter((lang) => validTargets.includes(lang.value));
});

// Local UI state
const uploadedFile = ref<File | null>(null);
const isDragging = ref(false);
const isConverting = ref(false);
const errorMessage = ref('');
const fileInput = ref<HTMLInputElement | null>(null);
const viewMode = ref<ViewMode>('split');
const explanation = ref('');
const isExplaining = ref(false);
const copiedSource = ref(false);
const copiedConverted = ref(false);
const sourceStats = ref<CodeStats | null>(sourceCode.value ? getCodeStats(sourceCode.value) : null);
const convertedStats = ref<CodeStats | null>(convertedCode.value ? getCodeStats(convertedCode.value) : null);
const showSetupGuide = ref(false);
const setupGuide = ref<SetupGuide | null>(null);

const canConvert = computed(
  () =>
    sourceLanguage.value &&
    targetLanguage.value &&
    sourceCode.value.trim() &&
    sourceLanguage.value !== targetLanguage.value
);

const canSwap = computed(
  () =>
    !!sourceLanguage.value &&
    !!targetLanguage.value &&
    (VALID_CONVERSIONS[targetLanguage.value as Language] || []).includes(sourceLanguage.value as Language)
);

const lineDelta = computed(() => (convertedStats.value?.lines ?? 0) - (sourceStats.value?.lines ?? 0));

const getLanguageLabel = (lang: Language | '') => languages.find((l) => l.value === lang)?.label || '';
const getLanguageExtension = (lang: Language | '') =>
  languages.find((l) => l.value === lang)?.extension || '.txt';

// ---------------------------------------------------------------- files
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) processFile(file);
  target.value = '';
};

const handleFileDrop = (event: DragEvent) => {
  isDragging.value = false;
  const file = event.dataTransfer?.files[0];
  if (file) processFile(file);
};

const EXT_MAP: Record<string, Language> = {
  py: 'python',
  js: 'javascript',
  mjs: 'javascript',
  cjs: 'nodejs',
  ts: 'typescript',
  java: 'java',
  php: 'php',
  go: 'golang',
  c: 'c',
  cpp: 'cpp',
  cc: 'cpp',
  cs: 'csharp',
  rs: 'rust',
  sql: 'sql',
  prisma: 'prisma',
};

const processFile = async (file: File) => {
  uploadedFile.value = file;
  errorMessage.value = '';

  if (file.size > 1024 * 1024) {
    errorMessage.value = 'File is too large. Maximum size is 1MB.';
    uploadedFile.value = null;
    return;
  }

  try {
    const text = await file.text();
    if (!text.trim()) {
      errorMessage.value = 'File is empty.';
      uploadedFile.value = null;
      return;
    }
    sourceCode.value = text;
    updateSourceStats();

    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext && EXT_MAP[ext]) sourceLanguage.value = EXT_MAP[ext];
  } catch {
    errorMessage.value = 'Failed to read file. Please ensure it is a valid text file.';
    uploadedFile.value = null;
  }
};

const loadExample = () => {
  if (!sourceLanguage.value) return;
  sourceCode.value = CODE_EXAMPLES[sourceLanguage.value as Language] || '';
  uploadedFile.value = null;
  updateSourceStats();
};

const swapLanguages = () => {
  if (!canSwap.value) return;
  const from = sourceLanguage.value;
  sourceLanguage.value = targetLanguage.value;
  targetLanguage.value = from;
  if (convertedCode.value) {
    sourceCode.value = convertedCode.value;
    convertedCode.value = '';
    updateSourceStats();
    updateConvertedStats();
  }
};

// ------------------------------------------------------------ convert
const convertCode = async () => {
  if (!canConvert.value || isConverting.value) return;

  if (sourceCode.value.length > 50000) {
    errorMessage.value = 'Code is too large. Maximum 50,000 characters allowed.';
    return;
  }

  const syntaxError = validateSyntax(sourceCode.value, sourceLanguage.value as Language);
  if (syntaxError) {
    if (!confirm(`Syntax error detected:\n${syntaxError}\n\nDo you want to proceed with conversion anyway?`)) {
      errorMessage.value = `Syntax issue detected: ${syntaxError}`;
      return;
    }
  }

  isConverting.value = true;
  errorMessage.value = '';
  convertedCode.value = '';
  updateConvertedStats();

  try {
    await converterApi.convertCodeStream(
      {
        source_language: sourceLanguage.value as Language,
        target_language: targetLanguage.value as Language,
        code: sourceCode.value.trim(),
      },
      (chunk) => {
        convertedCode.value += chunk;
        updateConvertedStats();
      }
    );

    if (!convertedCode.value.trim()) {
      errorMessage.value = 'No code was generated. Please try again.';
    } else {
      saveToHistory({
        sourceLanguage: sourceLanguage.value,
        targetLanguage: targetLanguage.value,
        sourceCode: sourceCode.value,
        convertedCode: convertedCode.value,
      });
      loadHistory();
    }
  } catch (error: any) {
    if (error instanceof StreamInterruptedError) {
      // Keep the partial output visible, but don't save it to history.
      errorMessage.value = `${error.message}\nThe output below is incomplete.`;
    } else {
      errorMessage.value = error.message || 'Conversion failed. Please try again.';
    }
    console.warn('Conversion error:', error);
  } finally {
    isConverting.value = false;
  }
};

const downloadCode = () => {
  const blob = new Blob([convertedCode.value], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `converted${getLanguageExtension(targetLanguage.value)}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

const explainCode = async () => {
  if (!sourceLanguage.value || !sourceCode.value.trim()) {
    errorMessage.value = 'Please provide code to explain';
    return;
  }
  if (isExplaining.value) return;

  isExplaining.value = true;
  errorMessage.value = '';
  explanation.value = '';

  try {
    const response = await converterApi.explainCode({
      language: sourceLanguage.value as Language,
      code: sourceCode.value.trim(),
    });
    explanation.value = response.explanation;
  } catch (error: any) {
    errorMessage.value =
      error.response?.data?.detail || error.message || 'Explanation failed. Please try again.';
    console.warn('Explanation error:', error);
  } finally {
    isExplaining.value = false;
  }
};

// -------------------------------------------------------------- misc
const flash = (flag: typeof copiedSource) => {
  flag.value = true;
  setTimeout(() => (flag.value = false), 2000);
};

const copySource = async () => {
  if (await copyToClipboard(sourceCode.value)) flash(copiedSource);
};

const copyConverted = async () => {
  if (await copyToClipboard(convertedCode.value)) flash(copiedConverted);
};

const clearSource = () => {
  sourceCode.value = '';
  sourceStats.value = null;
  sourceLanguage.value = '';
  targetLanguage.value = '';
  uploadedFile.value = null;
};

const updateSourceStats = () => {
  if (sourceCode.value) {
    sourceStats.value = getCodeStats(sourceCode.value);
    if (!sourceLanguage.value && sourceCode.value.trim().length > 10) {
      const detected = detectLanguage(sourceCode.value);
      if (detected) sourceLanguage.value = detected;
    }
  } else {
    sourceStats.value = null;
    sourceLanguage.value = '';
    targetLanguage.value = '';
  }
};

const updateConvertedStats = () => {
  convertedStats.value = convertedCode.value ? getCodeStats(convertedCode.value) : null;
};

const showSetupGuidePanel = () => {
  if (targetLanguage.value) {
    setupGuide.value = SETUP_GUIDES[targetLanguage.value as Language];
    showSetupGuide.value = true;
  }
};

/** Light markdown → HTML for the explanation (HTML-escaped first). */
const escapeHtml = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

const formatExplanation = (text: string): string => {
  let counter = 1;
  return escapeHtml(text)
    .replace(/^###\s+(.+)$/gm, (_, title) => `<h4><span>${counter++}</span>${title}</h4>`)
    .replace(/^##\s+(.+)$/gm, '<h4>$1</h4>')
    .replace(/^\s*[-*]\s+(.+)$/gm, '<div class="li">$1</div>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\n{2,}/g, '<br>')
    .replace(/(<\/h4>|<\/div>)\n/g, '$1')
    .replace(/\n/g, '<br>');
};

const handleKeyboard = (e: KeyboardEvent) => {
  if (!(e.ctrlKey || e.metaKey)) return;
  if (e.key === 'Enter') {
    e.preventDefault();
    convertCode();
  } else if (e.key === 'e') {
    e.preventDefault();
    explainCode();
  } else if (e.key === 'd') {
    e.preventDefault();
    if (convertedCode.value) downloadCode();
  }
};

onMounted(() => {
  loadHistory();
  window.addEventListener('keydown', handleKeyboard);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyboard);
});
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 1480px;
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

/* Toolbar */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  padding-bottom: 4px;
}

.lang-picker {
  display: flex;
  align-items: center;
  gap: 8px;
}

.lang-picker .select {
  min-width: 170px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.seg {
  display: inline-flex;
  padding: 3px;
  gap: 2px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface-2);
}

.seg button {
  display: grid;
  place-items: center;
  width: 30px;
  height: 28px;
  border: 0;
  border-radius: 7px;
  background: transparent;
  color: var(--text-3);
  cursor: pointer;
}

.seg button.on {
  background: var(--surface);
  color: var(--text);
  box-shadow: var(--shadow-sm);
}

/* Stats */
.stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xs);
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 16px 18px;
  min-width: 0;
}

.stat + .stat {
  border-left: 1px solid var(--border);
}

.stat-label {
  font-size: 12.5px;
  color: var(--text-2);
}

.stat strong {
  font-size: 24px;
  font-weight: 600;
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
}

.stat strong.pair {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 17px;
  height: 36px;
  white-space: nowrap;
  overflow: hidden;
}

.stat-foot {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-3);
  min-width: 0;
}

.trunc {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--accent-text);
  font-weight: 500;
}

.link:hover {
  text-decoration: underline;
}

/* Alert */
.alert {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius);
  background: var(--red-soft);
  color: var(--red);
  font-size: 13px;
  border: 1px solid color-mix(in srgb, var(--red) 25%, transparent);
}

.alert span {
  flex: 1;
  white-space: pre-line;
}

.alert .btn {
  color: inherit;
}

/* Editors */
.editors {
  display: grid;
  grid-template-columns: 1fr 1fr;
  overflow: hidden;
}

.editors.single {
  grid-template-columns: 1fr;
}

.pane {
  display: flex;
  flex-direction: column;
  min-width: 0;
  position: relative;
}

.editors.split .pane + .pane {
  border-left: 1px solid var(--border);
}

.editors.single .pane + .pane {
  border-top: 1px solid var(--border);
}

.pane-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  height: 52px;
  padding: 0 10px 0 16px;
  border-bottom: 1px solid var(--border);
}

.pane-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 13.5px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot-src {
  background: var(--text-3);
}

.dot-out {
  background: var(--accent);
}

.streaming {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  color: var(--accent-text);
}

.streaming .spinner {
  width: 11px;
  height: 11px;
}

.pane-actions {
  display: flex;
  gap: 2px;
}

.code-wrap {
  position: relative;
  height: 560px;
  background: var(--code-bg);
}

.editors.single .code-wrap {
  height: 420px;
}

.code-area,
.code-out {
  width: 100%;
  height: 100%;
  padding: 16px 18px;
  border: 0;
  background: transparent;
  color: var(--code-text);
  font-family: var(--mono);
  font-size: 13px;
  line-height: 1.65;
  tab-size: 4;
  resize: none;
  overflow: auto;
}

.code-area {
  caret-color: var(--accent);
}

.code-area:focus {
  outline: none;
  box-shadow: inset 0 0 0 2px rgba(242, 86, 29, 0.35);
}

.code-area::placeholder {
  color: var(--code-muted);
}

.code-out code.hljs {
  background: transparent;
  padding: 0;
  font-family: inherit;
}

.drop-hint {
  position: absolute;
  inset: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: 2px dashed var(--accent);
  border-radius: var(--radius);
  background: rgba(22, 23, 29, 0.85);
  color: #fff;
  font-weight: 500;
  pointer-events: none;
}

.empty-out {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: var(--code-muted);
  text-align: center;
  padding: 24px;
}

.empty-out p {
  color: #9da2b3;
  font-weight: 500;
}

.empty-out span {
  font-size: 12px;
}

.empty-out kbd {
  background: var(--code-gutter);
  border-color: var(--code-border);
  color: #9da2b3;
}

/* Panels */
.panels {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
  gap: 16px;
}

.panel {
  display: flex;
  flex-direction: column;
  max-height: 640px;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 12px 12px 18px;
  border-bottom: 1px solid var(--border);
}

.panel-head h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.panel-body {
  padding: 16px 18px 20px;
  overflow-y: auto;
}

.explanation {
  color: var(--text-2);
  line-height: 1.7;
}

.explanation :deep(h4) {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 14px 0 6px;
  font-size: 14px;
  color: var(--text);
}

.explanation :deep(h4:first-child) {
  margin-top: 0;
}

.explanation :deep(h4 span) {
  display: grid;
  place-items: center;
  width: 20px;
  height: 20px;
  border-radius: 6px;
  background: var(--accent-soft);
  color: var(--accent-text);
  font-size: 11px;
}

.explanation :deep(.li) {
  position: relative;
  padding-left: 16px;
  margin: 3px 0;
}

.explanation :deep(.li)::before {
  content: '';
  position: absolute;
  left: 4px;
  top: 0.7em;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent);
}

.explanation :deep(code) {
  padding: 1px 5px;
  border-radius: 4px;
  background: var(--surface-hover);
  font-size: 12.5px;
}

.explanation :deep(strong) {
  color: var(--text);
}

@media (max-width: 1100px) {
  .stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .stat:nth-child(3) {
    border-left: 0;
  }

  .stat:nth-child(n + 3) {
    border-top: 1px solid var(--border);
  }

  .editors.split {
    grid-template-columns: 1fr;
  }

  .editors.split .pane + .pane {
    border-left: 0;
    border-top: 1px solid var(--border);
  }

  .code-wrap {
    height: 420px;
  }
}

@media (max-width: 640px) {
  .head-actions,
  .head-actions .btn {
    flex: 1;
  }

  .hide-sm {
    display: none;
  }

  .lang-picker {
    width: 100%;
  }

  .lang-picker .select {
    flex: 1;
    min-width: 0;
  }

  .seg {
    display: none;
  }

  .panels {
    grid-template-columns: 1fr;
  }

  .code-wrap,
  .editors.single .code-wrap {
    height: 340px;
  }

  .stat strong {
    font-size: 20px;
  }
}
</style>
