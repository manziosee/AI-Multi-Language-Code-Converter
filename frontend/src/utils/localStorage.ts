export interface ConversionHistory {
  id: string;
  sourceLanguage: string;
  targetLanguage: string;
  sourceCode: string;
  convertedCode: string;
  timestamp: number;
}

const HISTORY_KEY = 'code_conversion_history';
const MAX_HISTORY = 10;

export const saveToHistory = (item: Omit<ConversionHistory, 'id' | 'timestamp'>) => {
  const history = getHistory();
  const newItem: ConversionHistory = {
    ...item,
    id: Date.now().toString(),
    timestamp: Date.now()
  };
  
  history.unshift(newItem);
  
  if (history.length > MAX_HISTORY) {
    history.pop();
  }
  
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
};

export const getHistory = (): ConversionHistory[] => {
  try {
    const data = localStorage.getItem(HISTORY_KEY);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
};

export const clearHistory = () => {
  localStorage.removeItem(HISTORY_KEY);
};

export const deleteHistoryItem = (id: string) => {
  const history = getHistory().filter(item => item.id !== id);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
};
