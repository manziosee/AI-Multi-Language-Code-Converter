<template>
  <div class="page">
    <div class="page-head">
      <div>
        <h1>History</h1>
        <p class="muted">Your last {{ MAX }} conversions, stored only in this browser.</p>
      </div>
      <div class="head-actions">
        <button class="btn" :disabled="!history.length" @click="clearAll">
          <AppIcon name="trash" /> Clear all
        </button>
        <a :href="hrefFor('convert')" class="btn btn-primary">
          <AppIcon name="sparkles" /> New conversion
        </a>
      </div>
    </div>

    <div class="stats">
      <div class="stat">
        <span class="stat-label">Conversions saved</span>
        <strong>{{ history.length }}</strong>
        <span class="stat-foot"><span class="badge">max {{ MAX }}</span></span>
      </div>
      <div class="stat">
        <span class="stat-label">Lines generated</span>
        <strong>{{ totalLinesConverted.toLocaleString() }}</strong>
        <span class="stat-foot muted">across all saved items</span>
      </div>
      <div class="stat">
        <span class="stat-label">Most used target</span>
        <strong>{{ topTarget ? labelOf(topTarget[0]) : '—' }}</strong>
        <span class="stat-foot">
          <span v-if="topTarget" class="badge badge-green">{{ topTarget[1] }}× used</span>
        </span>
      </div>
      <div class="stat">
        <span class="stat-label">Last conversion</span>
        <strong>{{ history[0] ? relative(history[0].timestamp) : '—' }}</strong>
        <span class="stat-foot muted">{{ history[0] ? new Date(history[0].timestamp).toLocaleDateString() : 'Nothing yet' }}</span>
      </div>
    </div>

    <div class="card table-card">
      <div class="table-tools">
        <div class="search">
          <AppIcon name="search" class="muted" />
          <input v-model="query" class="input" placeholder="Search code or language…" aria-label="Search history" />
        </div>
        <select v-model="targetFilter" class="select" aria-label="Filter by target">
          <option value="">All targets</option>
          <option v-for="t in targetsUsed" :key="t" :value="t">{{ labelOf(t) }}</option>
        </select>
      </div>

      <div class="table-scroll">
        <table v-if="filtered.length">
          <thead>
            <tr>
              <th>Conversion</th>
              <th>Preview</th>
              <th class="num">Lines in</th>
              <th class="num">Lines out</th>
              <th>Date</th>
              <th class="actions-col"><span class="sr-only">Actions</span></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filtered" :key="item.id" @click="open(item)">
              <td>
                <div class="pair">
                  <span class="badge">{{ labelOf(item.sourceLanguage) }}</span>
                  <AppIcon name="arrowRight" :size="13" class="muted" />
                  <span class="badge badge-accent">{{ labelOf(item.targetLanguage) }}</span>
                </div>
              </td>
              <td class="preview"><code>{{ firstLine(item.sourceCode) }}</code></td>
              <td class="num">{{ linesOf(item.sourceCode) }}</td>
              <td class="num">{{ linesOf(item.convertedCode) }}</td>
              <td class="date">{{ new Date(item.timestamp).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' }) }}</td>
              <td class="actions-col" @click.stop>
                <button class="btn btn-sm" @click="open(item)">Open</button>
                <button class="btn btn-ghost btn-sm btn-icon" @click="remove(item.id)" title="Delete" aria-label="Delete">
                  <AppIcon name="trash" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-else class="empty">
          <AppIcon name="history" :size="28" />
          <p>{{ history.length ? 'No conversions match your filter' : 'No conversions yet' }}</p>
          <a v-if="!history.length" :href="hrefFor('convert')" class="btn btn-sm">Start converting</a>
        </div>
      </div>

      <div class="table-foot">
        Showing {{ filtered.length }} of {{ history.length }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import AppIcon from '@/components/AppIcon.vue';
import { hrefFor, navigate } from '@/router';
import { SUPPORTED_LANGUAGES, type Language } from '@/types';
import { clearHistory, deleteHistoryItem, type ConversionHistory } from '@/utils/localStorage';
import {
  history,
  loadHistory,
  linesOf,
  totalLinesConverted,
  sourceLanguage,
  targetLanguage,
  sourceCode,
  convertedCode,
} from '@/stores/workspace';

const MAX = 10;
const query = ref('');
const targetFilter = ref('');

const labelOf = (v: string) => SUPPORTED_LANGUAGES.find((l) => l.value === v)?.label || v;
const firstLine = (code: string) => code.split('\n').find((l) => l.trim())?.trim().slice(0, 90) || '';

const targetsUsed = computed(() => [...new Set(history.value.map((h) => h.targetLanguage))]);

const topTarget = computed(() => {
  const counts: Record<string, number> = {};
  history.value.forEach((h) => (counts[h.targetLanguage] = (counts[h.targetLanguage] || 0) + 1));
  return Object.entries(counts).sort((a, b) => b[1] - a[1])[0];
});

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase();
  return history.value.filter(
    (h) =>
      (!targetFilter.value || h.targetLanguage === targetFilter.value) &&
      (!q ||
        h.sourceCode.toLowerCase().includes(q) ||
        labelOf(h.sourceLanguage).toLowerCase().includes(q) ||
        labelOf(h.targetLanguage).toLowerCase().includes(q))
  );
});

function relative(ts: number) {
  const s = Math.round((Date.now() - ts) / 1000);
  if (s < 60) return 'Just now';
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`;
  return `${Math.floor(s / 86400)}d ago`;
}

function open(item: ConversionHistory) {
  sourceLanguage.value = item.sourceLanguage as Language;
  targetLanguage.value = item.targetLanguage as Language;
  sourceCode.value = item.sourceCode;
  convertedCode.value = item.convertedCode;
  navigate('convert');
}

function remove(id: string) {
  deleteHistoryItem(id);
  loadHistory();
}

function clearAll() {
  if (confirm('Are you sure you want to clear all history?')) {
    clearHistory();
    loadHistory();
  }
}
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
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stat-foot {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  min-height: 22px;
}

.table-card {
  overflow: hidden;
}

.table-tools {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-bottom: 1px solid var(--border);
}

.search {
  position: relative;
  flex: 1;
  max-width: 360px;
}

.search svg {
  position: absolute;
  left: 11px;
  top: 50%;
  transform: translateY(-50%);
}

.search .input {
  width: 100%;
  padding-left: 34px;
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
  white-space: nowrap;
}

td {
  height: 52px;
  padding: 0 16px;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}

tbody tr {
  cursor: pointer;
  transition: background 0.12s;
}

tbody tr:hover {
  background: var(--surface-2);
}

tbody tr:last-child td {
  border-bottom: 0;
}

.num {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.pair {
  display: flex;
  align-items: center;
  gap: 6px;
}

.preview {
  max-width: 340px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.preview code {
  font-size: 12px;
  color: var(--text-2);
}

.date {
  color: var(--text-2);
}

.actions-col {
  text-align: right;
  width: 1%;
}

.actions-col .btn + .btn {
  margin-left: 4px;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 56px 16px;
  color: var(--text-3);
}

.empty p {
  color: var(--text-2);
  font-weight: 500;
}

.table-foot {
  padding: 12px 16px;
  border-top: 1px solid var(--border);
  font-size: 12.5px;
  color: var(--text-3);
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
}

@media (max-width: 640px) {
  .head-actions,
  .head-actions .btn {
    flex: 1;
  }

  .table-tools {
    flex-direction: column;
  }

  .search {
    max-width: none;
  }
}
</style>
