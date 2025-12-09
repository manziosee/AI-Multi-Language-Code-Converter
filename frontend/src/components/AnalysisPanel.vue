<template>
  <div class="analysis-panel">
    <h3>📊 Code Analysis</h3>
    
    <div v-if="analysis" class="analysis-content">
      <!-- Confidence Score -->
      <div v-if="analysis.confidence_score" class="analysis-section">
        <h4>🎯 Conversion Confidence</h4>
        <div class="confidence-bar">
          <div 
            class="confidence-fill" 
            :style="{ width: analysis.confidence_score + '%', backgroundColor: getConfidenceColor(analysis.confidence_score) }"
          ></div>
          <span class="confidence-text">{{ analysis.confidence_score }}%</span>
        </div>
      </div>

      <!-- Complexity Analysis -->
      <div v-if="analysis.complexity_analysis" class="analysis-section">
        <h4>🔄 Complexity Analysis</h4>
        <div class="metric">
          <span>Score:</span>
          <span class="value">{{ analysis.complexity_analysis.complexity_score }}</span>
          <span :class="'badge ' + analysis.complexity_analysis.rating.toLowerCase()">
            {{ analysis.complexity_analysis.rating }}
          </span>
        </div>
        <div v-if="analysis.complexity_analysis.complex_functions?.length" class="complex-functions">
          <p><strong>Complex Functions:</strong></p>
          <ul>
            <li v-for="func in analysis.complexity_analysis.complex_functions" :key="func.name">
              {{ func.name }} (line {{ func.line }}) - Complexity: {{ func.complexity }}
            </li>
          </ul>
        </div>
        <div v-if="analysis.complexity_analysis.suggestions?.length" class="suggestions">
          <p><strong>Suggestions:</strong></p>
          <ul>
            <li v-for="(suggestion, idx) in analysis.complexity_analysis.suggestions" :key="idx">
              {{ suggestion }}
            </li>
          </ul>
        </div>
      </div>

      <!-- Performance Analysis -->
      <div v-if="analysis.performance_analysis" class="analysis-section">
        <h4>⚡ Performance Analysis</h4>
        <div class="metric">
          <span>Score:</span>
          <span class="value">{{ analysis.performance_analysis.score }}/100</span>
        </div>
        <div v-if="analysis.performance_analysis.issues?.length" class="issues">
          <div v-for="(issue, idx) in analysis.performance_analysis.issues" :key="idx" class="issue">
            <span :class="'severity ' + issue.severity">{{ issue.severity.toUpperCase() }}</span>
            <p><strong>{{ issue.message }}</strong></p>
            <p class="suggestion">💡 {{ issue.suggestion }}</p>
          </div>
        </div>
        <p v-else class="no-issues">✅ No performance issues detected</p>
      </div>

      <!-- Security Analysis -->
      <div v-if="analysis.security_analysis" class="analysis-section">
        <h4>🔒 Security Analysis</h4>
        <div class="metric">
          <span>Score:</span>
          <span class="value">{{ analysis.security_analysis.score }}/100</span>
          <span v-if="analysis.security_analysis.is_secure" class="badge low">Secure</span>
          <span v-else class="badge high">Vulnerabilities Found</span>
        </div>
        <div v-if="analysis.security_analysis.vulnerabilities?.length" class="issues">
          <div v-for="(vuln, idx) in analysis.security_analysis.vulnerabilities" :key="idx" class="issue">
            <span :class="'severity ' + vuln.severity">{{ vuln.severity.toUpperCase() }}</span>
            <p><strong>{{ vuln.message }}</strong></p>
            <p class="suggestion">💡 {{ vuln.suggestion }}</p>
          </div>
        </div>
        <p v-else class="no-issues">✅ No security vulnerabilities detected</p>
      </div>

      <!-- Code Review -->
      <div v-if="analysis.code_review" class="analysis-section">
        <h4>📝 Code Review</h4>
        <div class="metric">
          <span>Score:</span>
          <span class="value">{{ analysis.code_review.score }}/100</span>
        </div>
        <div v-if="analysis.code_review.suggestions?.length" class="issues">
          <div v-for="(suggestion, idx) in analysis.code_review.suggestions" :key="idx" class="issue">
            <span :class="'severity ' + suggestion.priority">{{ suggestion.priority.toUpperCase() }}</span>
            <p><strong>{{ suggestion.category }}:</strong> {{ suggestion.message }}</p>
          </div>
        </div>
        <p v-else class="no-issues">✅ Code follows best practices</p>
      </div>
    </div>

    <div v-else class="no-analysis">
      <p>Convert code to see analysis results</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

defineProps<{
  analysis: any;
}>();

function getConfidenceColor(score: number): string {
  if (score >= 80) return '#4caf50';
  if (score >= 60) return '#ff9800';
  return '#f44336';
}
</script>

<style scoped>
.analysis-panel {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  margin-top: 20px;
}

.analysis-panel h3 {
  margin: 0 0 20px 0;
  color: #4a9eff;
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.analysis-section {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  padding: 15px;
}

.analysis-section h4 {
  margin: 0 0 15px 0;
  color: #fff;
  font-size: 16px;
}

.confidence-bar {
  position: relative;
  height: 30px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.confidence-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #fff;
  font-weight: bold;
}

.metric {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.metric .value {
  font-weight: bold;
  color: #4a9eff;
  font-size: 18px;
}

.badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.badge.low {
  background: #4caf50;
  color: #fff;
}

.badge.medium {
  background: #ff9800;
  color: #fff;
}

.badge.high {
  background: #f44336;
  color: #fff;
}

.issues, .complex-functions, .suggestions {
  margin-top: 10px;
}

.issue {
  background: rgba(255, 255, 255, 0.05);
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 10px;
}

.severity {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: bold;
  margin-bottom: 5px;
}

.severity.low {
  background: #4caf50;
  color: #fff;
}

.severity.medium {
  background: #ff9800;
  color: #fff;
}

.severity.high, .severity.critical {
  background: #f44336;
  color: #fff;
}

.suggestion {
  color: #aaa;
  font-size: 14px;
  margin-top: 5px;
}

.no-issues, .no-analysis {
  color: #aaa;
  text-align: center;
  padding: 20px;
}

ul {
  margin: 5px 0;
  padding-left: 20px;
}

li {
  color: #ccc;
  margin: 5px 0;
}
</style>
