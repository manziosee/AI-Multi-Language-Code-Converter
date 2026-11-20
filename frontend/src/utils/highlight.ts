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

const HLJS_LANG: Record<string, string> = {
  python: 'python',
  javascript: 'javascript',
  nodejs: 'javascript',
  typescript: 'typescript',
  drizzle: 'typescript',
  java: 'java',
  php: 'php',
  golang: 'go',
  c: 'c',
  cpp: 'cpp',
  csharp: 'csharp',
  rust: 'rust',
  sql: 'sql',
  prisma: 'javascript',
};

export const escapeHtml = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

/** Returns safe HTML for v-html: highlighted, or escaped plain text. */
export function highlightCode(code: string, lang: string): string {
  if (!code) return '';
  const language = HLJS_LANG[lang];
  if (language) {
    try {
      return hljs.highlight(code, { language, ignoreIllegals: true }).value;
    } catch {
      /* fall through */
    }
  }
  return escapeHtml(code);
}
