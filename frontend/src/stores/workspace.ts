import { ref, computed } from 'vue';
import type { Language } from '@/types';
import { getHistory, type ConversionHistory } from '@/utils/localStorage';
import { converterApi } from '@/api/converter';

/** Converter state shared between the converter, history and guides views. */
export const sourceLanguage = ref<Language | ''>('');
export const targetLanguage = ref<Language | ''>('');
export const sourceCode = ref('');
export const convertedCode = ref('');

export const history = ref<ConversionHistory[]>(getHistory());
export const loadHistory = () => {
  history.value = getHistory();
};

/** Active backend provider, read from /health. */
export const providerLabel = ref('');
export const providerModel = ref('');
export const backendOnline = ref<boolean | null>(null);

let healthChecked = false;
export async function checkBackend() {
  if (healthChecked) return;
  healthChecked = true;
  try {
    const h: any = await converterApi.healthCheck();
    backendOnline.value = h.status === 'healthy';
    providerLabel.value = h.provider_label || '';
    providerModel.value = h.model || '';
  } catch {
    backendOnline.value = false;
  }
}

export const linesOf = (code: string) => (code ? code.split('\n').length : 0);
export const totalLinesConverted = computed(() =>
  history.value.reduce((n, h) => n + linesOf(h.convertedCode), 0)
);
