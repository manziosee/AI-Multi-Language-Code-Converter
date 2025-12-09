<template>
  <div class="app">

    <header class="header">
      <div class="container">
        <div class="header-content">
          <h1><span class="emoji-icon">🚀</span> AI Code Converter</h1>
          <p class="text-secondary">Transform code between languages instantly</p>
        </div>
      </div>
    </header>

    <main class="main container">
      <div class="converter-layout">
        <!-- Control Panel -->
        <div class="control-panel glass-card">
          <h3 class="mb-md">Configuration</h3>
          
          <!-- File Upload -->
          <div class="mb-lg">
            <label class="label">Upload Code File</label>
            <div 
              class="file-upload-zone"
              :class="{ 'drag-over': isDragging }"
              @drop.prevent="handleFileDrop"
              @dragover.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
              @click="triggerFileInput"
            >
              <input 
                ref="fileInput"
                type="file" 
                @change="handleFileSelect"
                accept=".py,.js,.mjs,.cjs,.ts,.java,.php,.go,.sql,.prisma,.c,.cpp,.cc,.cs,.rs"
                style="display: none"
              />
              <div class="upload-content">
                <svg class="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p v-if="!uploadedFile" class="text-secondary">
                  <strong>Click to upload</strong> or drag and drop
                </p>
                <p v-else class="text-success">
                  ✓ {{ uploadedFile.name }}
                </p>
                <p class="text-muted text-sm">Supports: .py, .js, .ts, .java, .php, .go, .c, .cpp, .cs, .rs, .sql</p>
              </div>
            </div>
          </div>

          <!-- Language Selection -->
          <div class="language-selectors mb-lg">
            <div class="selector-group">
              <label class="label">From</label>
              <select v-model="sourceLanguage" class="select">
                <option value="" disabled>Select source language</option>
                <option v-for="lang in languages" :key="lang.value" :value="lang.value">
                  {{ lang.label }}
                </option>
              </select>
            </div>

            <div class="arrow-icon">→</div>

            <div class="selector-group">
              <label class="label">To</label>
              <select v-model="targetLanguage" class="select" :disabled="!sourceLanguage">
                <option value="" disabled>Select target language</option>
                <option v-for="lang in availableTargetLanguages" :key="lang.value" :value="lang.value">
                  {{ lang.label }}
                </option>
              </select>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="quick-actions mb-md">
            <button @click="showHistory = !showHistory" class="btn btn-sm btn-outline" style="width: 100%;">
              📜 History ({{ history.length }})
            </button>
          </div>

          <!-- Action Buttons -->
          <div class="button-group">
            <button 
              @click="convertCode"
              :disabled="!canConvert || isConverting"
              class="btn btn-primary btn-lg"
              title="Ctrl+Enter"
            >
              <span v-if="isConverting" class="spinner"></span>
              <span v-else>✨</span>
              {{ isConverting ? 'Converting...' : 'Convert' }}
            </button>
            
            <button 
              @click="explainCode"
              :disabled="!sourceLanguage || !sourceCode.trim() || isExplaining"
              class="btn btn-secondary btn-lg"
              title="Ctrl+E"
            >
              <span v-if="isExplaining" class="spinner"></span>
              <span v-else>💡</span>
              {{ isExplaining ? 'Explaining...' : 'Explain' }}
            </button>
          </div>
          
          <!-- View Mode Toggle -->
          <button 
            @click="toggleViewMode"
            class="btn btn-outline"
            style="width: 100%; margin-top: var(--spacing-md)"
          >
            {{ viewMode === 'single' ? '📊 Split View' : '📄 Single View' }}
          </button>

          <!-- Error Message -->
          <div v-if="errorMessage" class="error-message mt-md">
            {{ errorMessage }}
          </div>
        </div>

        <!-- Code Editors -->
        <div class="editors-container" :class="{ 'split-view': viewMode === 'split' }">
          <!-- Source Code -->
          <div class="editor-panel glass-card">
            <div class="editor-header">
              <h3>Source Code</h3>
              <div class="header-actions">
                <span v-if="sourceLanguage" class="language-badge">{{ getLanguageLabel(sourceLanguage) }}</span>
                <button 
                  v-if="sourceCode"
                  @click="copySource"
                  class="btn btn-sm btn-secondary"
                >
                  {{ copiedSource ? '✓ Copied!' : '📋 Copy' }}
                </button>
                <button 
                  v-if="sourceCode"
                  @click="clearSource"
                  class="btn btn-sm btn-secondary"
                >
                  🗑️ Clear
                </button>
              </div>
            </div>
            <div class="editor-wrapper">
              <div class="code-editor-container">
                <textarea 
                  v-model="sourceCode"
                  @input="updateSourceStats"
                  class="code-textarea"
                  placeholder="Paste your code here or upload a file..."
                  :disabled="isConverting"
                ></textarea>
              </div>
            </div>
            <div v-if="sourceStats" class="code-stats">
              <span>📊 {{ sourceStats.lines }} lines</span>
              <span>🔤 {{ sourceStats.characters }} chars</span>
              <span>📝 {{ sourceStats.nonEmptyLines }} non-empty</span>
            </div>
          </div>

          <!-- Converted Code -->
          <div class="editor-panel glass-card">
            <div class="editor-header">
              <h3>Converted Code</h3>
              <div class="header-actions">
                <span v-if="targetLanguage" class="language-badge">{{ getLanguageLabel(targetLanguage) }}</span>
                <button 
                  v-if="convertedCode"
                  @click="copyConverted"
                  class="btn btn-sm btn-secondary"
                >
                  {{ copiedConverted ? '✓ Copied!' : '📋 Copy' }}
                </button>
                <button 
                  v-if="convertedCode"
                  @click="downloadCode"
                  class="btn btn-sm btn-secondary"
                  title="Ctrl+D"
                >
                  📥 Download
                </button>
                <button 
                  v-if="targetLanguage"
                  @click="showSetupGuidePanel"
                  class="btn btn-sm btn-secondary"
                  title="Setup Guide"
                >
                  ⚙️ Setup
                </button>
              </div>
            </div>
            <div class="editor-wrapper">
              <div class="code-editor-container">
                <pre class="code-display" v-if="convertedCode"><code :class="getHighlightClass(targetLanguage)" v-html="highlightCode(convertedCode, targetLanguage)"></code></pre>
                <textarea 
                  v-model="convertedCode"
                  class="code-textarea code-textarea-hidden"
                  placeholder="Converted code will appear here..."
                  readonly
                ></textarea>
              </div>
            </div>
            <div v-if="convertedStats" class="code-stats">
              <span>📊 {{ convertedStats.lines }} lines</span>
              <span>🔤 {{ convertedStats.characters }} chars</span>
              <span>📝 {{ convertedStats.nonEmptyLines }} non-empty</span>
            </div>
          </div>
        </div>
        
        <!-- Side-by-side Panels Container -->
        <div class="side-panels-container">
          <!-- Code Explanation Panel -->
          <div v-if="explanation" class="explanation-panel glass-card">
            <div class="editor-header">
              <h3>💡 Code Explanation</h3>
              <button 
                @click="explanation = ''"
                class="btn btn-secondary"
              >
                ✕ Close
              </button>
            </div>
            <div class="explanation-content">
              <div v-html="formatExplanation(explanation)" class="explanation-text"></div>
            </div>
          </div>
          
          <!-- Setup Guide Panel -->
          <div v-if="showSetupGuide && setupGuide" class="setup-guide-panel glass-card">
          <div class="editor-header">
            <h3>⚙️ {{ setupGuide.language }} Setup Guide</h3>
            <button @click="showSetupGuide = false" class="btn btn-sm btn-secondary">
              ✕ Close
            </button>
          </div>
          <div class="setup-content">
            <div class="setup-section">
              <h4>📦 Dependencies</h4>
              <ul>
                <li v-for="dep in setupGuide.dependencies" :key="dep">{{ dep }}</li>
              </ul>
            </div>
            
            <div class="setup-section">
              <h4>💻 Installation</h4>
              <div class="code-block">
                <code>{{ setupGuide.installCommand }}</code>
                <button @click="copyToClipboard(setupGuide.installCommand)" class="copy-btn">📋</button>
              </div>
            </div>
            
            <div class="setup-section">
              <h4>▶️ Run Command</h4>
              <div class="code-block">
                <code>{{ setupGuide.runCommand }}</code>
                <button @click="copyToClipboard(setupGuide.runCommand)" class="copy-btn">📋</button>
              </div>
            </div>
            
            <div class="setup-section" v-if="setupGuide.configFiles.length">
              <h4>📄 Configuration Files</h4>
              <div v-for="file in setupGuide.configFiles" :key="file.name" class="config-file">
                <div class="file-header">
                  <strong>{{ file.name }}</strong>
                  <button @click="copyToClipboard(file.content)" class="copy-btn">📋 Copy</button>
                </div>
                <pre class="file-content">{{ file.content }}</pre>
              </div>
            </div>
            
            <div class="setup-section">
              <h4>💡 Quick Tips</h4>
              <ul>
                <li v-for="note in setupGuide.notes" :key="note">{{ note }}</li>
              </ul>
            </div>
          </div>
          </div>
        </div>
        
        <!-- History Panel -->
        <div v-if="showHistory" class="history-panel glass-card">
          <div class="editor-header">
            <h3>📜 Conversion History</h3>
            <div class="header-actions">
              <button @click="clearAllHistory" class="btn btn-sm btn-secondary" v-if="history.length">
                🗑️ Clear All
              </button>
              <button @click="showHistory = false" class="btn btn-sm btn-secondary">
                ✕ Close
              </button>
            </div>
          </div>
          <div class="history-content">
            <div v-if="!history.length" class="empty-state">
              <p>No conversion history yet</p>
            </div>
            <div v-else class="history-list">
              <div 
                v-for="item in history" 
                :key="item.id" 
                class="history-item"
                @click="loadFromHistory(item)"
              >
                <div class="history-header">
                  <span class="language-badge">{{ item.sourceLanguage }}</span>
                  <span>→</span>
                  <span class="language-badge">{{ item.targetLanguage }}</span>
                  <span class="history-time">{{ new Date(item.timestamp).toLocaleString() }}</span>
                </div>
                <div class="history-preview">{{ item.sourceCode.substring(0, 100) }}...</div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Keyboard Shortcuts Help -->
        <div class="shortcuts-hint glass-card">
          <h4>⌨️ Keyboard Shortcuts</h4>
          <div class="shortcuts-list">
            <div><kbd>Ctrl+Enter</kbd> Convert Code</div>
            <div><kbd>Ctrl+E</kbd> Explain Code</div>
            <div><kbd>Ctrl+D</kbd> Download</div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { converterApi } from '@/api/converter';
import { SUPPORTED_LANGUAGES, VALID_CONVERSIONS } from '@/types';
import type { Language, ViewMode } from '@/types';
import { CODE_EXAMPLES } from '@/utils/codeExamples';
import { saveToHistory, getHistory, clearHistory, type ConversionHistory } from '@/utils/localStorage';
import { copyToClipboard } from '@/utils/clipboard';
import { getCodeStats, type CodeStats } from '@/utils/codeStats';
import { SETUP_GUIDES, type SetupGuide } from '@/utils/setupGuides';
import { detectLanguage } from '@/utils/languageDetector';
import { validateSyntax } from '@/utils/syntaxValidator';
import hljs from 'highlight.js/lib/core';
import javascript from 'highlight.js/lib/languages/javascript';
import typescript from 'highlight.js/lib/languages/typescript';
import python from 'highlight.js/lib/languages/python';
import java from 'highlight.js/lib/languages/java';
import php from 'highlight.js/lib/languages/php';
import go from 'highlight.js/lib/languages/go';
import c from 'highlight.js/lib/languages/c';
import cpp from 'highlight.js/lib/languages/cpp';
import csharp from 'highlight.js/lib/languages/csharp';
import rust from 'highlight.js/lib/languages/rust';
import sql from 'highlight.js/lib/languages/sql';
import 'highlight.js/styles/vs2015.css';

hljs.registerLanguage('javascript', javascript);
hljs.registerLanguage('typescript', typescript);
hljs.registerLanguage('python', python);
hljs.registerLanguage('java', java);
hljs.registerLanguage('php', php);
hljs.registerLanguage('go', go);
hljs.registerLanguage('c', c);
hljs.registerLanguage('cpp', cpp);
hljs.registerLanguage('csharp', csharp);
hljs.registerLanguage('rust', rust);
hljs.registerLanguage('sql', sql);

const languages = SUPPORTED_LANGUAGES;

// Computed available target languages based on source
const availableTargetLanguages = computed(() => {
  if (!sourceLanguage.value) return languages;
  const validTargets = VALID_CONVERSIONS[sourceLanguage.value as Language] || [];
  return languages.filter(lang => validTargets.includes(lang.value));
});

// State
const sourceLanguage = ref<Language | ''>('');
const targetLanguage = ref<Language | ''>('');
const sourceCode = ref('');
const convertedCode = ref('');
const uploadedFile = ref<File | null>(null);
const isDragging = ref(false);
const isConverting = ref(false);
const errorMessage = ref('');
const fileInput = ref<HTMLInputElement | null>(null);
const viewMode = ref<ViewMode>('single');
const explanation = ref('');
const isExplaining = ref(false);
const showHistory = ref(false);
const history = ref<ConversionHistory[]>([]);
const copiedSource = ref(false);
const copiedConverted = ref(false);
const sourceStats = ref<CodeStats | null>(null);
const convertedStats = ref<CodeStats | null>(null);
const showSetupGuide = ref(false);
const setupGuide = ref<SetupGuide | null>(null);


// Computed
const canConvert = computed(() => {
  return sourceLanguage.value && 
         targetLanguage.value && 
         sourceCode.value.trim() &&
         sourceLanguage.value !== targetLanguage.value;
});

// Methods
const getLanguageLabel = (lang: Language | '') => {
  return languages.find(l => l.value === lang)?.label || '';
};

const getLanguageExtension = (lang: Language | '') => {
  return languages.find(l => l.value === lang)?.extension || '.txt';
};

const triggerFileInput = () => {
  fileInput.value?.click();
};

const getStarStyle = () => {
  const size = Math.random() * 2 + 1;
  return {
    top: `${Math.random() * 100}%`,
    left: `${Math.random() * 100}%`,
    width: `${size}px`,
    height: `${size}px`,
    '--duration': `${Math.random() * 3 + 2}s`,
    '--opacity': Math.random() * 0.7 + 0.3
  };
};

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    processFile(file);
  }
};

const handleFileDrop = (event: DragEvent) => {
  isDragging.value = false;
  const file = event.dataTransfer?.files[0];
  if (file) {
    processFile(file);
  }
};

const processFile = async (file: File) => {
  uploadedFile.value = file;
  errorMessage.value = '';
  
  // Validate file size (max 1MB)
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
    
    // Auto-detect source language from file extension
    const ext = file.name.split('.').pop()?.toLowerCase();
    const extMap: Record<string, Language> = {
      'py': 'python',
      'js': 'javascript',
      'mjs': 'javascript',
      'cjs': 'nodejs',
      'ts': 'typescript',
      'java': 'java',
      'php': 'php',
      'go': 'golang',
      'c': 'c',
      'cpp': 'cpp',
      'cc': 'cpp',
      'cs': 'csharp',
      'rs': 'rust',
      'sql': 'sql',
      'prisma': 'prisma'
    };
    
    if (ext && extMap[ext]) {
      sourceLanguage.value = extMap[ext];
    }
  } catch (error) {
    errorMessage.value = 'Failed to read file. Please ensure it is a valid text file.';
    uploadedFile.value = null;
  }
};

const convertCode = async () => {
  if (!canConvert.value) return;
  
  // Validate code length
  if (sourceCode.value.length > 50000) {
    errorMessage.value = 'Code is too large. Maximum 50,000 characters allowed.';
    return;
  }
  
  // Basic syntax validation
  const syntaxError = validateSyntax(sourceCode.value, sourceLanguage.value as Language);
  if (syntaxError) {
    errorMessage.value = `⚠️ Syntax Error Detected: ${syntaxError}\n\nPlease fix the error before converting. The conversion may produce incorrect results with syntax errors.`;
    
    // Ask user if they want to proceed anyway
    if (!confirm(`Syntax error detected:\n${syntaxError}\n\nDo you want to proceed with conversion anyway?`)) {
      return;
    }
    errorMessage.value = '';
  }
  
  isConverting.value = true;
  errorMessage.value = '';
  convertedCode.value = '';
  
  try {
    await converterApi.convertCodeStream({
      source_language: sourceLanguage.value as Language,
      target_language: targetLanguage.value as Language,
      code: sourceCode.value.trim()
    }, (chunk) => {
      convertedCode.value += chunk;
      updateConvertedStats();
    });
    
    if (!convertedCode.value.trim()) {
      errorMessage.value = 'No code was generated. Please try again.';
    } else {
      // Save to history
      saveToHistory({
        sourceLanguage: sourceLanguage.value,
        targetLanguage: targetLanguage.value,
        sourceCode: sourceCode.value,
        convertedCode: convertedCode.value
      });
      loadHistory();
    }
  } catch (error: any) {
    errorMessage.value = error.message || 'Conversion failed. Please try again.';
    console.error('Conversion error:', error);
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

const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'single' ? 'split' : 'single';
};

const explainCode = async () => {
  if (!sourceLanguage.value || !sourceCode.value.trim()) {
    errorMessage.value = 'Please provide code to explain';
    return;
  }
  
  isExplaining.value = true;
  errorMessage.value = '';
  explanation.value = '';
  
  try {
    const response = await converterApi.explainCode({
      language: sourceLanguage.value as Language,
      code: sourceCode.value.trim()
    });
    
    explanation.value = response.explanation;
  } catch (error: any) {
    errorMessage.value = error.message || 'Explanation failed. Please try again.';
    console.error('Explanation error:', error);
  } finally {
    isExplaining.value = false;
  }
};

const loadExample = () => {
  if (sourceLanguage.value) {
    sourceCode.value = CODE_EXAMPLES[sourceLanguage.value as Language];
    updateSourceStats();
  }
};

const copySource = async () => {
  const success = await copyToClipboard(sourceCode.value);
  if (success) {
    copiedSource.value = true;
    setTimeout(() => copiedSource.value = false, 2000);
  }
};

const copyConverted = async () => {
  const success = await copyToClipboard(convertedCode.value);
  if (success) {
    copiedConverted.value = true;
    setTimeout(() => copiedConverted.value = false, 2000);
  }
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
    
    // Auto-detect language if not already set
    if (!sourceLanguage.value && sourceCode.value.trim().length > 10) {
      const detected = detectLanguage(sourceCode.value);
      if (detected) {
        sourceLanguage.value = detected;
      }
    }
  } else {
    sourceStats.value = null;
    // Clear language selection when code is cleared
    sourceLanguage.value = '';
    targetLanguage.value = '';
  }
};

const updateConvertedStats = () => {
  if (convertedCode.value) {
    convertedStats.value = getCodeStats(convertedCode.value);
  } else {
    convertedStats.value = null;
  }
};

const loadHistory = () => {
  history.value = getHistory();
};

const loadFromHistory = (item: ConversionHistory) => {
  sourceLanguage.value = item.sourceLanguage as Language;
  targetLanguage.value = item.targetLanguage as Language;
  sourceCode.value = item.sourceCode;
  convertedCode.value = item.convertedCode;
  showHistory.value = false;
  updateSourceStats();
  updateConvertedStats();
};

const clearAllHistory = () => {
  if (confirm('Are you sure you want to clear all history?')) {
    clearHistory();
    loadHistory();
  }
};

const showSetupGuidePanel = () => {
  if (targetLanguage.value) {
    setupGuide.value = SETUP_GUIDES[targetLanguage.value as Language];
    showSetupGuide.value = true;
  }
};

const getHighlightClass = (lang: Language | '') => {
  const langMap: Record<string, string> = {
    'python': 'language-python',
    'javascript': 'language-javascript',
    'typescript': 'language-typescript',
    'nodejs': 'language-javascript',
    'java': 'language-java',
    'php': 'language-php',
    'go': 'language-go',
    'c': 'language-c',
    'cpp': 'language-cpp',
    'csharp': 'language-csharp',
    'rust': 'language-rust',
    'sql': 'language-sql',
    'prisma': 'language-javascript'
  };
  return langMap[lang as string] || 'language-plaintext';
};

const highlightCode = (code: string, lang: Language | '') => {
  if (!code) return '';
  const langMap: Record<string, string> = {
    'python': 'python',
    'javascript': 'javascript',
    'typescript': 'typescript',
    'nodejs': 'javascript',
    'java': 'java',
    'php': 'php',
    'go': 'go',
    'c': 'c',
    'cpp': 'cpp',
    'csharp': 'csharp',
    'rust': 'rust',
    'sql': 'sql',
    'prisma': 'javascript'
  };
  const language = langMap[lang as string];
  if (language) {
    try {
      return hljs.highlight(code, { language }).value;
    } catch (e) {
      return code;
    }
  }
  return code;
};

const formatExplanation = (text: string): string => {
  let counter = 1;
  return text
    .replace(/^###\s+(.+)$/gm, (_, title) => `<div class="section-title">${counter++}. ${title}</div>`)
    .replace(/^##\s+(.+)$/gm, '<div class="section-heading">$1</div>')
    .replace(/^\*\*(.+?)\*\*:?/gm, '<div class="bullet-point">• $1</div>')
    .replace(/^-\s+(.+)$/gm, '<div class="bullet-point">• $1</div>')
    .replace(/\n/g, '<br>');
};

const handleKeyboard = (e: KeyboardEvent) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault();
    convertCode();
  } else if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
    e.preventDefault();
    explainCode();
  } else if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
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
.app {
  min-height: 100vh;
  position: relative;
  background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
}

.header {
  position: sticky;
  top: 0;
  z-index: 100;
  padding: var(--spacing-2xl) 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(15, 20, 25, 0.95);
  backdrop-filter: blur(20px);
}

.header-content {
  text-align: center;
}

.header-content h1 {
  margin-bottom: var(--spacing-sm);
}

.main {
  padding: var(--spacing-2xl) var(--spacing-2xl);
  max-width: 1800px;
  margin: 0 auto;
}

.converter-layout {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: var(--spacing-2xl);
  align-items: start;
}

.control-panel {
  padding: var(--spacing-2xl);
}

.label {
  display: block;
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.file-upload-zone {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-xl);
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease;
  background: var(--color-bg-tertiary);
}

.file-upload-zone:hover,
.file-upload-zone.drag-over {
  border-color: #4a9eff;
  background: rgba(74, 158, 255, 0.05);
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
}

.upload-icon {
  width: 3rem;
  height: 3rem;
  color: #4a9eff;
}

.text-sm {
  font-size: 0.875rem;
}

.text-success {
  color: var(--color-success);
  font-weight: 600;
}

.language-selectors {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: var(--spacing-md);
  align-items: end;
}

.selector-group {
  display: flex;
  flex-direction: column;
}

.arrow-icon {
  font-size: 1.5rem;
  color: #4a9eff;
  padding-bottom: var(--spacing-sm);
}

.error-message {
  padding: var(--spacing-md);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: 0.875rem;
}

.button-group {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
  width: 100%;
}

.btn-outline {
  background: transparent;
  color: var(--color-text-primary);
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.btn-outline:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.4);
}

.editors-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-2xl);
}

.editors-container.split-view {
  grid-template-columns: 1fr 1fr;
}

.side-panels-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-xl);
  grid-column: 1 / -1;
  margin-top: var(--spacing-xl);
}

.explanation-panel,
.setup-guide-panel {
  margin-top: 0;
}

.explanation-content {
  padding: var(--spacing-xl);
  max-height: 700px;
  overflow-y: auto;
}

.explanation-text {
  line-height: 2;
  color: var(--color-text-secondary);
  font-size: 1rem;
}

.explanation-text .section-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-accent-primary);
  margin: var(--spacing-lg) 0 var(--spacing-md) 0;
}

.explanation-text .section-heading {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: var(--spacing-md) 0 var(--spacing-sm) 0;
}

.explanation-text .bullet-point {
  padding-left: var(--spacing-md);
  margin: var(--spacing-xs) 0;
  color: var(--color-text-secondary);
}

.quick-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.btn-sm {
  padding: var(--spacing-xs) var(--spacing-md);
  font-size: 0.875rem;
}

.code-stats {
  display: flex;
  gap: var(--spacing-lg);
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(0, 0, 0, 0.3);
  border-top: 1px solid var(--color-border);
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.history-panel {
  margin-top: var(--spacing-xl);
}

.history-content {
  max-height: 400px;
  overflow-y: auto;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.history-item {
  padding: var(--spacing-md);
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.history-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--color-border-hover);
}

.history-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-xs);
  font-size: 0.875rem;
}

.history-time {
  margin-left: auto;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.history-preview {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  font-family: 'Monaco', 'Menlo', monospace;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--color-text-muted);
}

.shortcuts-hint {
  margin-top: var(--spacing-xl);
  padding: var(--spacing-lg);
}

.shortcuts-hint h4 {
  margin-bottom: var(--spacing-md);
  font-size: 1rem;
}

.shortcuts-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-sm);
  font-size: 0.875rem;
}

kbd {
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.75rem;
  margin-right: var(--spacing-xs);
}



.setup-content {
  padding: var(--spacing-md);
  max-height: 700px;
  overflow-y: auto;
}

.setup-section {
  margin-bottom: var(--spacing-lg);
}

.setup-section h4 {
  margin-bottom: var(--spacing-sm);
  color: var(--color-accent-primary);
  font-size: 0.875rem;
}

.setup-section ul {
  list-style: none;
  padding: 0;
}

.setup-section li {
  padding: var(--spacing-xs) 0;
  padding-left: var(--spacing-lg);
  position: relative;
}

.setup-section li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: var(--color-accent-primary);
}

.code-block {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: #1e1e1e;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.875rem;
}

.code-block code {
  flex: 1;
  color: #d4d4d4;
}

.copy-btn {
  padding: var(--spacing-xs) var(--spacing-sm);
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-primary);
  cursor: pointer;
  font-size: 0.75rem;
  transition: all var(--transition-base);
}

.copy-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: var(--color-border-hover);
}

.config-file {
  margin-bottom: var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.file-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid var(--color-border);
}

.file-content {
  padding: var(--spacing-md);
  background: #1e1e1e;
  color: #d4d4d4;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.75rem;
  line-height: 1.6;
  overflow-x: auto;
  margin: 0;
}

.editor-panel {
  display: flex;
  flex-direction: column;
  min-height: 800px;
  padding: var(--spacing-xl);
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.language-badge {
  padding: var(--spacing-xs) var(--spacing-md);
  background: #ffffff;
  color: #000000;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.editor-wrapper {
  flex: 1;
  display: flex;
  position: relative;
}

.code-editor-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 700px;
}

.code-display {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  padding: var(--spacing-md);
  margin: 0;
  background: #1e1e1e;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: auto;
  pointer-events: auto;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.875rem;
  line-height: 1.6;
}

.code-display code {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.875rem;
  line-height: 1.6;
}

.code-textarea {
  width: 100%;
  height: 100%;
  min-height: 700px;
  padding: var(--spacing-md);
  background: #1e1e1e;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: #d4d4d4;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.875rem;
  line-height: 1.6;
  resize: vertical;
  transition: border-color 0.2s ease;
  caret-color: #d4d4d4;
}

.code-textarea-hidden {
  opacity: 0;
  pointer-events: none;
}

.code-textarea:focus {
  outline: none;
  border-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
}

.code-textarea::placeholder {
  color: var(--color-text-muted);
}

@media (max-width: 1200px) {
  .converter-layout {
    grid-template-columns: 1fr;
  }
  
  .control-panel {
    /* Already not sticky */
  }
  
  .editors-container,
  .editors-container.split-view {
    grid-template-columns: 1fr;
  }
  
  .button-group {
    grid-template-columns: 1fr;
  }
  
  .explanation-content {
    max-height: none;
  }
  
  .setup-content {
    max-height: none;
  }
  
  .header {
    position: relative;
  }
}
</style>
