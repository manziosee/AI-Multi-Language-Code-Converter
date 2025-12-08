<template>
  <div class="app">
    <!-- Space Background -->
    <div class="space-background">
      <div class="stars">
        <div v-for="n in 50" :key="n" class="star" :style="getStarStyle()"></div>
      </div>
      <div class="solar-system">
        <div class="sun"></div>
        
        <!-- Mercury -->
        <div class="orbit orbit-mercury">
          <div class="planet planet-mercury"></div>
        </div>
        
        <!-- Venus -->
        <div class="orbit orbit-venus">
          <div class="planet planet-venus"></div>
        </div>
        
        <!-- Earth -->
        <div class="orbit orbit-earth">
          <div class="planet planet-earth"></div>
        </div>
        
        <!-- Mars -->
        <div class="orbit orbit-mars">
          <div class="planet planet-mars"></div>
        </div>
        
        <!-- Jupiter -->
        <div class="orbit orbit-jupiter">
          <div class="planet planet-jupiter"></div>
        </div>
        
        <!-- Saturn -->
        <div class="orbit orbit-saturn">
          <div class="planet planet-saturn"></div>
        </div>
        
        <!-- Uranus -->
        <div class="orbit orbit-uranus">
          <div class="planet planet-uranus"></div>
        </div>
        
        <!-- Neptune -->
        <div class="orbit orbit-neptune">
          <div class="planet planet-neptune"></div>
        </div>
      </div>
    </div>

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
                accept=".py,.js,.ts,.java,.php,.go,.sql,.prisma,.c,.cpp,.cs,.rs"
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
              <select v-model="targetLanguage" class="select">
                <option value="" disabled>Select target language</option>
                <option v-for="lang in languages" :key="lang.value" :value="lang.value">
                  {{ lang.label }}
                </option>
              </select>
            </div>
          </div>

          <!-- Convert Button -->
          <button 
            @click="convertCode"
            :disabled="!canConvert || isConverting"
            class="btn btn-primary btn-lg"
            style="width: 100%"
          >
            <span v-if="isConverting" class="spinner"></span>
            <span v-else>✨</span>
            {{ isConverting ? 'Converting...' : 'Convert Code' }}
          </button>

          <!-- Error Message -->
          <div v-if="errorMessage" class="error-message mt-md">
            {{ errorMessage }}
          </div>
        </div>

        <!-- Code Editors -->
        <div class="editors-container">
          <!-- Source Code -->
          <div class="editor-panel glass-card">
            <div class="editor-header">
              <h3>Source Code</h3>
              <span v-if="sourceLanguage" class="language-badge">{{ getLanguageLabel(sourceLanguage) }}</span>
            </div>
            <div class="editor-wrapper">
              <textarea 
                v-model="sourceCode"
                class="code-textarea"
                placeholder="Paste your code here or upload a file..."
                :disabled="isConverting"
              ></textarea>
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
                  @click="downloadCode"
                  class="btn btn-secondary"
                >
                  📥 Download
                </button>
              </div>
            </div>
            <div class="editor-wrapper">
              <textarea 
                v-model="convertedCode"
                class="code-textarea"
                placeholder="Converted code will appear here..."
                readonly
              ></textarea>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { converterApi } from '@/api/converter';
import { SUPPORTED_LANGUAGES } from '@/types';
import type { Language } from '@/types';

const languages = SUPPORTED_LANGUAGES;

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
  
  try {
    const text = await file.text();
    sourceCode.value = text;
    
    // Auto-detect source language from file extension
    const ext = file.name.split('.').pop()?.toLowerCase();
    const detectedLang = languages.find(l => l.extension === `.${ext}`);
    if (detectedLang) {
      sourceLanguage.value = detectedLang.value;
    }
  } catch (error) {
    errorMessage.value = 'Failed to read file';
  }
};

const convertCode = async () => {
  if (!canConvert.value) return;
  
  isConverting.value = true;
  errorMessage.value = '';
  convertedCode.value = '';
  
  try {
    await converterApi.convertCodeStream({
      source_language: sourceLanguage.value as Language,
      target_language: targetLanguage.value as Language,
      code: sourceCode.value
    }, (chunk) => {
      convertedCode.value += chunk;
    });
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
</script>

<style scoped>
.app {
  min-height: 100vh;
  position: relative;
  z-index: 1;
}

.header {
  padding: var(--spacing-xl) 0;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg-glass);
  backdrop-filter: blur(20px);
}

.header-content {
  text-align: center;
}

.header-content h1 {
  margin-bottom: var(--spacing-sm);
}

.main {
  padding: var(--spacing-2xl) var(--spacing-lg);
}

.converter-layout {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: var(--spacing-xl);
  align-items: start;
}

.control-panel {
  position: sticky;
  top: var(--spacing-xl);
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
  transition: all var(--transition-base);
  background: var(--color-bg-tertiary);
}

.file-upload-zone:hover,
.file-upload-zone.drag-over {
  border-color: var(--color-accent-primary);
  background: rgba(255, 255, 255, 0.05);
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
  color: var(--color-accent-primary);
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
  color: var(--color-accent-primary);
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

.editors-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-xl);
}

.editor-panel {
  display: flex;
  flex-direction: column;
  min-height: 600px;
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
}

.code-textarea {
  width: 100%;
  height: 100%;
  min-height: 500px;
  padding: var(--spacing-md);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.875rem;
  line-height: 1.6;
  resize: vertical;
  transition: all var(--transition-base);
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
    position: static;
  }
  
  .editors-container {
    grid-template-columns: 1fr;
  }
}
</style>
