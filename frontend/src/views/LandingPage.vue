<template>
  <div class="landing">
    <!-- Nav -->
    <header class="nav">
      <div class="wrap nav-inner">
        <a href="#/" class="brand">
          <span class="brand-mark"><AppIcon name="logo" :size="16" :stroke="2.25" /></span>
          Code Converter
        </a>
        <nav class="nav-links">
          <a href="#features" @click.prevent="scrollTo('features')">Features</a>
          <a href="#how" @click.prevent="scrollTo('how')">How it works</a>
          <a href="#languages" @click.prevent="scrollTo('languages')">Languages</a>
        </nav>
        <div class="nav-cta">
          <a
            class="btn btn-ghost btn-icon hide-sm"
            href="https://github.com/manziosee/AI-Multi-Language-Code-Converter"
            target="_blank"
            rel="noopener"
            aria-label="GitHub"
          >
            <AppIcon name="github" :size="18" />
          </a>
          <a :href="hrefFor('convert')" class="btn btn-primary">Open app</a>
        </div>
      </div>
    </header>

    <!-- Hero -->
    <section class="hero">
      <div class="wrap hero-inner">
        <span class="eyebrow">
          <span class="pulse" />
          Streams from Groq, OpenAI or any OpenAI-compatible API
        </span>
        <h1>
          Translate code between
          <span class="hl">{{ SUPPORTED_LANGUAGES.length }} languages</span>
          in seconds.
        </h1>
        <p class="lead">
          Paste a snippet or drop a file, choose a target language, and watch idiomatic code stream in.
          It can also explain code, convert files in batches, and show you how to set up and run the result.
        </p>
        <div class="hero-cta">
          <a :href="hrefFor('convert')" class="btn btn-accent btn-lg">
            <AppIcon name="sparkles" /> Start converting
          </a>
          <a :href="hrefFor('batch')" class="btn btn-lg">
            <AppIcon name="layers" /> Batch convert files
          </a>
        </div>
        <ul class="trust">
          <li><AppIcon name="check" :size="14" /> Free to use</li>
          <li><AppIcon name="check" :size="14" /> No sign-up</li>
          <li><AppIcon name="check" :size="14" /> History stays in your browser</li>
        </ul>
      </div>

      <!-- Product preview -->
      <div class="wrap">
        <div class="preview">
          <div class="chrome">
            <span /><span /><span />
            <div class="url">code-converter.app/#/app/convert</div>
          </div>
          <div class="preview-body">
            <div class="preview-pane">
              <div class="preview-head">
                <span class="dot dot-src" /> Python
              </div>
              <pre><code class="hljs" v-html="highlightCode(demoSource, 'python')" /></pre>
            </div>
            <div class="preview-arrow"><AppIcon name="arrowRight" :size="16" /></div>
            <div class="preview-pane">
              <div class="preview-head">
                <span class="dot dot-out" /> Rust
                <span class="streaming"><span class="spinner" /> Streaming</span>
              </div>
              <pre><code class="hljs" v-html="highlightCode(demoTarget, 'rust')" /></pre>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section id="features" class="section">
      <div class="wrap">
        <div class="section-head">
          <span class="kicker">Features</span>
          <h2>Everything you need to move code between languages</h2>
          <p>The tools you need for migrating code, learning a new language, or prototyping.</p>
        </div>
        <div class="features">
          <article v-for="f in features" :key="f.title" class="feature card">
            <span class="f-icon"><AppIcon :name="f.icon" :size="18" /></span>
            <h3>{{ f.title }}</h3>
            <p>{{ f.body }}</p>
          </article>
        </div>
      </div>
    </section>

    <!-- How it works -->
    <section id="how" class="section alt">
      <div class="wrap">
        <div class="section-head">
          <span class="kicker">How it works</span>
          <h2>Three steps, no setup</h2>
        </div>
        <ol class="steps">
          <li v-for="(s, i) in steps" :key="s.title" class="card">
            <span class="step-n">{{ i + 1 }}</span>
            <h3>{{ s.title }}</h3>
            <p>{{ s.body }}</p>
          </li>
        </ol>
      </div>
    </section>

    <!-- Languages -->
    <section id="languages" class="section">
      <div class="wrap">
        <div class="section-head">
          <span class="kicker">Languages</span>
          <h2>{{ programming.length }} programming languages, plus your database schema</h2>
          <p>Convert between any pair of general-purpose languages, or move schemas between SQL, Prisma and Drizzle.</p>
        </div>
        <div class="langs">
          <span v-for="l in programming" :key="l.value" class="lang">
            <code>{{ l.extension }}</code>{{ l.label }}
          </span>
        </div>
        <div class="langs db">
          <span class="db-label"><AppIcon name="layers" :size="14" /> Schema</span>
          <span v-for="l in schema" :key="l.value" class="lang">
            <code>{{ l.extension }}</code>{{ l.label }}
          </span>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="section">
      <div class="wrap">
        <div class="cta">
          <div>
            <h2>Ready to convert your first file?</h2>
            <p>Open the converter and paste some code. Nothing to install.</p>
          </div>
          <div class="cta-actions">
            <a :href="hrefFor('convert')" class="btn btn-accent btn-lg">
              Open converter <AppIcon name="arrowRight" />
            </a>
            <a :href="hrefFor('guides')" class="btn btn-lg cta-ghost">Browse setup guides</a>
          </div>
        </div>
      </div>
    </section>

    <footer class="footer">
      <div class="wrap footer-inner">
        <span>© {{ new Date().getFullYear() }} AI Multi-Language Code Converter · MIT licensed</span>
        <div>
          <a :href="hrefFor('convert')">Converter</a>
          <a :href="hrefFor('batch')">Batch</a>
          <a :href="hrefFor('guides')">Guides</a>
          <a :href="`${API_BASE_URL}/docs`" target="_blank" rel="noopener">API</a>
          <a href="https://github.com/manziosee/AI-Multi-Language-Code-Converter" target="_blank" rel="noopener">GitHub</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import AppIcon from '@/components/AppIcon.vue';
import { hrefFor } from '@/router';
import { API_BASE_URL } from '@/api/converter';
import { SUPPORTED_LANGUAGES } from '@/types';
import { highlightCode } from '@/utils/highlight';

const schemaIds = ['sql', 'prisma', 'drizzle'];
const programming = SUPPORTED_LANGUAGES.filter((l) => !schemaIds.includes(l.value));
const schema = SUPPORTED_LANGUAGES.filter((l) => schemaIds.includes(l.value));

const demoSource = `def word_counts(text: str) -> dict[str, int]:
    counts = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return counts


print(word_counts("the cat and the hat"))`;

const demoTarget = `use std::collections::HashMap;

fn word_counts(text: &str) -> HashMap<String, usize> {
    let mut counts = HashMap::new();
    for word in text.to_lowercase().split_whitespace() {
        *counts.entry(word.to_string()).or_insert(0) += 1;
    }
    counts
}

fn main() {
    println!("{:?}", word_counts("the cat and the hat"));
}`;

const features = [
  {
    icon: 'zap',
    title: 'Real-time streaming',
    body: 'Converted code appears token by token as the model writes it, so you never stare at a spinner.',
  },
  {
    icon: 'bulb',
    title: 'Explain any snippet',
    body: 'Get a structured walkthrough: overview, key components, how it works and notable details.',
  },
  {
    icon: 'layers',
    title: 'Batch conversion',
    body: 'Drop up to 10 files at once and download each converted file, or all of them together.',
  },
  {
    icon: 'search',
    title: 'Language auto-detect',
    body: 'The source language is picked from the file extension or recognised from the code itself.',
  },
  {
    icon: 'package',
    title: 'Setup guides',
    body: 'Dependencies, install commands and config files for every target, so the output actually runs.',
  },
  {
    icon: 'shield',
    title: 'Private by default',
    body: 'No accounts. Your conversion history is stored only in your browser and you can clear it anytime.',
  },
];

const steps = [
  { title: 'Add your code', body: 'Paste it into the editor, drop a file, or load a built-in example.' },
  { title: 'Pick a target', body: 'Choose from the languages valid for your source. Swap direction with one click.' },
  { title: 'Convert & ship', body: 'Watch it stream, then copy, download, or open the setup guide to run it.' },
];

function scrollTo(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
</script>

<style scoped>
.landing {
  background: var(--surface);
  min-height: 100vh;
}

.wrap {
  width: 100%;
  max-width: 1160px;
  margin: 0 auto;
  padding: 0 24px;
}

/* Nav */
.nav {
  position: sticky;
  top: 12px;
  z-index: 20;
  height: 0; /* float over the hero instead of pushing it down */
}

.nav-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: calc(100% - 32px);
  max-width: 1112px;
  height: 56px;
  margin: 12px auto 0;
  padding: 0 8px 0 14px;
  border: 1px solid var(--border);
  border-radius: 14px;
  background: color-mix(in srgb, var(--surface) 82%, transparent);
  backdrop-filter: saturate(180%) blur(12px);
  box-shadow: var(--shadow-sm);
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  font-size: 15px;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: var(--ink);
  color: var(--ink-text);
}

.nav-links {
  display: flex;
  gap: 28px;
  font-size: 13.5px;
  color: var(--text-2);
}

.nav-links a:hover {
  color: var(--text);
}

.nav-cta {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Hero */
.hero {
  position: relative;
  padding: 136px 0 0;
  background:
    radial-gradient(60% 50% at 50% 0%, color-mix(in srgb, var(--accent) 10%, transparent), transparent 70%),
    var(--bg);
  border-bottom: 1px solid var(--border);
  overflow: hidden;
}

.hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(var(--border) 1px, transparent 1px),
    linear-gradient(90deg, var(--border) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(70% 60% at 50% 20%, #000 20%, transparent 75%);
  opacity: 0.55;
  pointer-events: none;
}

.hero-inner {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 30px;
  padding: 0 12px;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--surface);
  font-size: 12.5px;
  color: var(--text-2);
  box-shadow: var(--shadow-xs);
}

.pulse {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 25%, transparent);
}

.hero h1 {
  max-width: 820px;
  margin: 22px 0 18px;
  font-size: clamp(34px, 5.6vw, 60px);
  font-weight: 700;
  letter-spacing: -0.035em;
  line-height: 1.05;
}

.hl {
  color: var(--accent);
}

.lead {
  max-width: 620px;
  font-size: clamp(15px, 1.6vw, 17px);
  line-height: 1.65;
  color: var(--text-2);
}

.hero-cta {
  display: flex;
  gap: 10px;
  margin-top: 30px;
  flex-wrap: wrap;
  justify-content: center;
}

.trust {
  display: flex;
  gap: 20px;
  margin-top: 22px;
  list-style: none;
  font-size: 13px;
  color: var(--text-3);
  flex-wrap: wrap;
  justify-content: center;
}

.trust li {
  display: flex;
  align-items: center;
  gap: 6px;
}

.trust svg {
  color: var(--green);
}

/* Preview */
.preview {
  position: relative;
  margin: 56px auto -1px;
  max-width: 1040px;
  border: 1px solid var(--border);
  border-bottom: 0;
  border-radius: 16px 16px 0 0;
  background: var(--surface);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.chrome {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 40px;
  padding: 0 14px;
  border-bottom: 1px solid var(--border);
  background: var(--surface-2);
}

.chrome > span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--border-strong);
}

.url {
  flex: 1;
  max-width: 340px;
  margin: 0 auto;
  padding: 3px 12px;
  border-radius: 6px;
  background: var(--surface);
  border: 1px solid var(--border);
  font-size: 11.5px;
  color: var(--text-3);
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.preview-body {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  background: var(--code-bg);
}

.preview-pane {
  min-width: 0;
}

.preview-head {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 40px;
  padding: 0 16px;
  border-bottom: 1px solid var(--code-border);
  color: #c9ccd6;
  font-size: 12.5px;
  font-weight: 500;
}

.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.dot-src { background: #7c8193; }
.dot-out { background: var(--accent); }

.streaming {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #ff8a5c;
  font-size: 11.5px;
}

.streaming .spinner {
  width: 10px;
  height: 10px;
  border-width: 1.5px;
}

.preview pre {
  margin: 0;
  padding: 16px 18px 28px;
  font-size: 12.5px;
  line-height: 1.7;
  overflow-x: auto;
  color: var(--code-text);
}

.preview code.hljs {
  background: transparent;
  padding: 0;
}

.preview-arrow {
  display: grid;
  place-items: center;
  width: 36px;
  border-left: 1px solid var(--code-border);
  border-right: 1px solid var(--code-border);
  color: var(--accent);
}

/* Sections */
.section {
  padding: 88px 0;
}

.section.alt {
  background: var(--bg);
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}

.section-head {
  max-width: 640px;
  margin: 0 auto 44px;
  text-align: center;
}

.kicker {
  display: inline-block;
  margin-bottom: 10px;
  font-size: 12.5px;
  font-weight: 600;
  color: var(--accent-text);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.section-head h2 {
  font-size: clamp(26px, 3.4vw, 36px);
  font-weight: 700;
  letter-spacing: -0.03em;
}

.section-head p {
  margin-top: 12px;
  color: var(--text-2);
  font-size: 15.5px;
}

.features {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.feature {
  padding: 22px;
  transition: border-color 0.15s, transform 0.15s;
}

.feature:hover {
  border-color: var(--border-strong);
  transform: translateY(-2px);
}

.f-icon {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  margin-bottom: 16px;
  border-radius: 10px;
  background: var(--accent-soft);
  color: var(--accent-text);
}

.feature h3 {
  font-size: 15px;
  margin-bottom: 6px;
}

.feature p {
  color: var(--text-2);
  font-size: 13.5px;
  line-height: 1.6;
}

.steps {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  list-style: none;
}

.steps li {
  padding: 24px;
}

.step-n {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  margin-bottom: 18px;
  border-radius: 50%;
  background: var(--ink);
  color: var(--ink-text);
  font-weight: 600;
  font-size: 13px;
}

.steps h3 {
  font-size: 15.5px;
  margin-bottom: 6px;
}

.steps p {
  color: var(--text-2);
  font-size: 13.5px;
}

.langs {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
}

.langs.db {
  margin-top: 18px;
  padding-top: 18px;
  border-top: 1px dashed var(--border);
  align-items: center;
}

.db-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-right: 4px;
  font-size: 12.5px;
  color: var(--text-3);
}

.lang {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 40px;
  padding: 0 16px 0 8px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--surface);
  font-weight: 500;
  box-shadow: var(--shadow-xs);
}

.lang code {
  padding: 3px 6px;
  border-radius: 6px;
  background: var(--surface-hover);
  color: var(--text-3);
  font-size: 11px;
}

.cta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  flex-wrap: wrap;
  padding: 40px 44px;
  border-radius: var(--radius-xl);
  background: #18181b;
  color: #fff;
  position: relative;
  overflow: hidden;
}

.cta::after {
  content: '';
  position: absolute;
  right: -80px;
  top: -120px;
  width: 360px;
  height: 360px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(242, 86, 29, 0.45), transparent 65%);
  pointer-events: none;
}

.cta h2 {
  color: #fff;
  font-size: clamp(22px, 2.8vw, 28px);
  letter-spacing: -0.025em;
}

.cta p {
  margin-top: 6px;
  color: #a1a1aa;
}

.cta-actions {
  position: relative;
  z-index: 1;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.cta-ghost {
  background: transparent;
  color: #fff;
  border-color: #3f3f46;
}

.cta-ghost:hover:not(:disabled) {
  background: #27272a;
  border-color: #52525b;
}

.footer {
  border-top: 1px solid var(--border);
  padding: 24px 0;
  font-size: 13px;
  color: var(--text-3);
}

.footer-inner {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.footer-inner div {
  display: flex;
  gap: 20px;
}

.footer a:hover {
  color: var(--text);
}

@media (max-width: 900px) {
  .nav-links {
    display: none;
  }

  .features,
  .steps {
    grid-template-columns: 1fr 1fr;
  }

  .preview-body {
    grid-template-columns: 1fr;
  }

  .preview-arrow {
    display: none;
  }

  .preview-pane + .preview-arrow + .preview-pane {
    border-top: 1px solid var(--code-border);
  }

  .preview-pane:first-child {
    display: none;
  }
}

@media (max-width: 600px) {
  .wrap {
    padding: 0 16px;
  }

  .hide-sm {
    display: none;
  }

  .hero {
    padding-top: 108px;
  }

  .nav-inner {
    width: calc(100% - 24px);
    margin-top: 8px;
    height: 52px;
    padding: 0 6px 0 12px;
  }

  .hero-cta {
    width: 100%;
    flex-direction: column;
  }

  .hero-cta .btn {
    width: 100%;
  }

  .features,
  .steps {
    grid-template-columns: 1fr;
  }

  .section {
    padding: 64px 0;
  }

  .cta {
    padding: 28px 22px;
  }

  .cta-actions,
  .cta-actions .btn {
    width: 100%;
  }
}
</style>
