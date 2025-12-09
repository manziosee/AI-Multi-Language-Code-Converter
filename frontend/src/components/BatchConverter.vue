<template>
  <div class="batch-converter">
    <h3>📦 Batch Conversion</h3>
    
    <div class="upload-area" @drop.prevent="handleDrop" @dragover.prevent>
      <input 
        type="file" 
        ref="fileInput" 
        multiple 
        @change="handleFileSelect" 
        accept=".py,.js,.ts,.java,.php,.go,.c,.cpp,.cs,.rs,.sql"
        style="display: none"
      />
      <button @click="$refs.fileInput.click()" class="upload-button">
        📁 Select Files (Max 10)
      </button>
      <p>or drag and drop files here</p>
    </div>

    <div v-if="files.length" class="files-list">
      <h4>Selected Files ({{ files.length }}/10):</h4>
      <div v-for="(file, idx) in files" :key="idx" class="file-item">
        <span>{{ file.name }}</span>
        <button @click="removeFile(idx)" class="remove-btn">✕</button>
      </div>
    </div>

    <button 
      v-if="files.length" 
      @click="convertBatch" 
      :disabled="isConverting"
      class="convert-button"
    >
      {{ isConverting ? '⏳ Converting...' : '🔄 Convert All' }}
    </button>

    <div v-if="results.length" class="results">
      <h4>Results:</h4>
      <div v-for="(result, idx) in results" :key="idx" class="result-item">
        <div class="result-header">
          <span>{{ result.name }}</span>
          <span :class="result.success ? 'success' : 'error'">
            {{ result.success ? '✅ Success' : '❌ Failed' }}
          </span>
        </div>
        <button 
          v-if="result.success" 
          @click="downloadFile(result.name, result.converted_code)"
          class="download-btn"
        >
          💾 Download
        </button>
        <p v-if="result.error" class="error-msg">{{ result.error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps } from 'vue';
import { converterApi } from '@/api/converter';

const props = defineProps<{
  sourceLanguage: string;
  targetLanguage: string;
}>();

const fileInput = ref<HTMLInputElement>();
const files = ref<File[]>([]);
const isConverting = ref(false);
const results = ref<any[]>([]);

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files) {
    addFiles(Array.from(target.files));
  }
}

function handleDrop(event: DragEvent) {
  if (event.dataTransfer?.files) {
    addFiles(Array.from(event.dataTransfer.files));
  }
}

function addFiles(newFiles: File[]) {
  const remaining = 10 - files.value.length;
  files.value.push(...newFiles.slice(0, remaining));
}

function removeFile(index: number) {
  files.value.splice(index, 1);
}

async function convertBatch() {
  if (!files.value.length) return;

  isConverting.value = true;
  results.value = [];

  try {
    const fileData = await Promise.all(
      files.value.map(async (file) => ({
        name: file.name,
        code: await file.text()
      }))
    );

    const response = await converterApi.batchConvert({
      files: fileData,
      source_language: props.sourceLanguage,
      target_language: props.targetLanguage
    });

    results.value = response.results;
  } catch (err: any) {
    alert('Batch conversion failed: ' + (err.response?.data?.detail || err.message));
  } finally {
    isConverting.value = false;
  }
}

function downloadFile(filename: string, content: string) {
  const blob = new Blob([content], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename.replace(/\.[^.]+$/, '_converted$&');
  a.click();
  URL.revokeObjectURL(url);
}
</script>

<style scoped>
.batch-converter {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  margin-top: 20px;
}

.batch-converter h3 {
  margin: 0 0 20px 0;
  color: #4a9eff;
}

.upload-area {
  border: 2px dashed rgba(74, 158, 255, 0.5);
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  transition: all 0.3s ease;
}

.upload-area:hover {
  border-color: #4a9eff;
  background: rgba(74, 158, 255, 0.05);
}

.upload-button {
  padding: 12px 24px;
  background: linear-gradient(135deg, #4a9eff 0%, #357abd 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  margin-bottom: 10px;
}

.files-list {
  margin-top: 20px;
}

.files-list h4 {
  color: #fff;
  margin-bottom: 10px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.05);
  padding: 10px 15px;
  border-radius: 6px;
  margin-bottom: 8px;
}

.remove-btn {
  background: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  cursor: pointer;
}

.convert-button {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  margin-top: 20px;
}

.convert-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.results {
  margin-top: 20px;
}

.result-item {
  background: rgba(255, 255, 255, 0.05);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 10px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.success {
  color: #4caf50;
}

.error {
  color: #f44336;
}

.error-msg {
  color: #f44336;
  font-size: 14px;
  margin-top: 5px;
}

.download-btn {
  padding: 8px 16px;
  background: #4a9eff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
</style>
