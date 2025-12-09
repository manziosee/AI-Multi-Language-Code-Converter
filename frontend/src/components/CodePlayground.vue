<template>
  <div class="playground">
    <div class="playground-header">
      <h3>🎮 Code Playground</h3>
      <button @click="runCode" :disabled="isRunning || !canExecute" class="run-button">
        {{ isRunning ? '⏳ Running...' : '▶️ Run Code' }}
      </button>
    </div>

    <div v-if="!canExecute" class="warning">
      ⚠️ Execution only supported for Python and JavaScript
    </div>

    <div v-if="output || error" class="output-section">
      <h4>Output:</h4>
      <pre v-if="output" class="output">{{ output }}</pre>
      <pre v-if="error" class="error">{{ error }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineProps } from 'vue';
import { converterApi } from '@/api/converter';

const props = defineProps<{
  code: string;
  language: string;
}>();

const isRunning = ref(false);
const output = ref('');
const error = ref('');

const canExecute = computed(() => {
  return ['python', 'javascript', 'nodejs'].includes(props.language);
});

async function runCode() {
  if (!canExecute.value || !props.code.trim()) return;

  isRunning.value = true;
  output.value = '';
  error.value = '';

  try {
    const result = await converterApi.executeCode({
      language: props.language,
      code: props.code
    });

    if (result.success) {
      output.value = result.output || '(No output)';
    } else {
      error.value = result.error;
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || 'Execution failed';
  } finally {
    isRunning.value = false;
  }
}
</script>

<style scoped>
.playground {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  margin-top: 20px;
}

.playground-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.playground-header h3 {
  margin: 0;
  color: #4a9eff;
}

.run-button {
  padding: 10px 20px;
  background: linear-gradient(135deg, #4a9eff 0%, #357abd 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.run-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(74, 158, 255, 0.4);
}

.run-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.warning {
  background: rgba(255, 152, 0, 0.1);
  border-left: 3px solid #ff9800;
  padding: 10px;
  border-radius: 4px;
  color: #ff9800;
  margin-bottom: 15px;
}

.output-section {
  margin-top: 15px;
}

.output-section h4 {
  margin: 0 0 10px 0;
  color: #fff;
}

.output, .error {
  background: rgba(0, 0, 0, 0.3);
  padding: 15px;
  border-radius: 8px;
  color: #fff;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 300px;
  overflow-y: auto;
}

.error {
  color: #f44336;
  border-left: 3px solid #f44336;
}
</style>
