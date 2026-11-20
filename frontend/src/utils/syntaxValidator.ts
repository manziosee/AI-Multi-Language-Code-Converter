import type { Language } from '@/types';

/**
 * Lightweight pre-flight checks run before conversion. They only flag
 * mistakes that are almost certainly real, because a false alarm interrupts
 * the user with a confirm dialog. Comments and string contents are blanked
 * out first so brackets or keywords inside them are never counted.
 */
export function validateSyntax(code: string, language: Language): string | null {
  if (!code.trim()) return null;

  switch (language) {
    case 'python':
      return validatePython(stripCode(code, PYTHON));
    case 'javascript':
    case 'nodejs':
    case 'typescript':
      return validateJavaScript(stripCode(code, JS));
    case 'java':
    case 'csharp':
      return validateJavaLike(stripCode(code, C_LIKE));
    case 'golang':
      return validateGo(stripCode(code, GO));
    case 'c':
    case 'cpp':
      return checkBrackets(stripCode(code, C_LIKE));
    case 'rust':
      return checkBrackets(stripCode(code, RUST));
    case 'php':
      return validatePHP(stripCode(code, PHP));
    case 'sql':
      return validateSQL(stripCode(code, SQL));
    default:
      return null;
  }
}

// ---------------------------------------------------------------------------
// Comment / string stripping
// ---------------------------------------------------------------------------

interface Syntax {
  lineComments: string[];
  blockComment?: [string, string];
  quotes: string[];          // quote characters that open a string
  tripleQuotes?: boolean;    // Python ''' and """
  regexLiterals?: boolean;   // JavaScript /.../
  charLiterals?: boolean;    // Rust: ' only when it closes like 'x' or '\n' (else lifetime)
}

const PYTHON: Syntax = { lineComments: ['#'], quotes: ['"', "'"], tripleQuotes: true };
const JS: Syntax = { lineComments: ['//'], blockComment: ['/*', '*/'], quotes: ['"', "'", '`'], regexLiterals: true };
const C_LIKE: Syntax = { lineComments: ['//'], blockComment: ['/*', '*/'], quotes: ['"', "'"] };
const GO: Syntax = { lineComments: ['//'], blockComment: ['/*', '*/'], quotes: ['"', "'", '`'] };
const RUST: Syntax = { lineComments: ['//'], blockComment: ['/*', '*/'], quotes: ['"'], charLiterals: true };
const PHP: Syntax = { lineComments: ['//', '#'], blockComment: ['/*', '*/'], quotes: ['"', "'"] };
const SQL: Syntax = { lineComments: ['--'], blockComment: ['/*', '*/'], quotes: ["'"] };

/**
 * Replace the contents of comments and strings with spaces, keeping quotes
 * and newlines so line numbers and token positions stay the same.
 */
export function stripCode(code: string, syntax: Syntax): string {
  let out = '';
  let i = 0;
  const n = code.length;
  const blank = (s: string) => s.replace(/[^\n]/g, ' ');

  while (i < n) {
    const rest = code.startsWith.bind(code);

    // Line comments
    const lc = syntax.lineComments.find((t) => rest(t, i));
    if (lc) {
      const end = code.indexOf('\n', i);
      const stop = end === -1 ? n : end;
      out += blank(code.slice(i, stop));
      i = stop;
      continue;
    }

    // Block comments
    if (syntax.blockComment && rest(syntax.blockComment[0], i)) {
      const end = code.indexOf(syntax.blockComment[1], i + syntax.blockComment[0].length);
      const stop = end === -1 ? n : end + syntax.blockComment[1].length;
      out += blank(code.slice(i, stop));
      i = stop;
      continue;
    }

    const ch = code[i];

    // Python triple-quoted strings
    if (syntax.tripleQuotes && (rest('"""', i) || rest("'''", i))) {
      const q = code.slice(i, i + 3);
      let j = i + 3;
      while (j < n && !code.startsWith(q, j)) j += code[j] === '\\' ? 2 : 1;
      const stop = Math.min(n, j + 3);
      out += q + blank(code.slice(i + 3, Math.max(i + 3, stop - 3))) + (j < n ? q : '');
      i = stop;
      continue;
    }

    // Rust char literals vs lifetimes ('a)
    if (syntax.charLiterals && ch === "'") {
      const m = /^'(?:\\(?:x[0-9a-fA-F]{2}|u\{[0-9a-fA-F]+\}|.)|[^\\'\n])'/.exec(code.slice(i, i + 14));
      if (m) {
        out += "'" + blank(m[0].slice(1, -1)) + "'";
        i += m[0].length;
        continue;
      }
    }

    // Regular strings
    if (syntax.quotes.includes(ch)) {
      let j = i + 1;
      while (j < n && code[j] !== ch) {
        if (code[j] === '\n' && ch !== '`') break; // unterminated: stop at line end
        j += code[j] === '\\' ? 2 : 1;
      }
      const closed = j < n && code[j] === ch;
      out += ch + blank(code.slice(i + 1, Math.min(j, n))) + (closed ? ch : '');
      i = closed ? j + 1 : j;
      continue;
    }

    // JavaScript regex literals: a "/" where an operand is expected
    if (syntax.regexLiterals && ch === '/' && regexAllowedAfter(out)) {
      let j = i + 1;
      let inClass = false;
      while (j < n && code[j] !== '\n') {
        if (code[j] === '\\') { j += 2; continue; }
        if (code[j] === '[') inClass = true;
        else if (code[j] === ']') inClass = false;
        else if (code[j] === '/' && !inClass) break;
        j++;
      }
      if (j < n && code[j] === '/') {
        out += '/' + blank(code.slice(i + 1, j)) + '/';
        i = j + 1;
        continue;
      }
    }

    out += ch;
    i++;
  }
  return out;
}

function regexAllowedAfter(before: string): boolean {
  const trimmed = before.replace(/\s+$/, '');
  if (!trimmed) return true;
  if (/(?:^|[^\w$])(?:return|typeof|case|do|else|in|of|new|delete|void|throw|yield|await)$/.test(trimmed)) return true;
  return /[(,=:[!&|?{};+\-*%<>~^]$/.test(trimmed);
}

// ---------------------------------------------------------------------------
// Shared checks
// ---------------------------------------------------------------------------

const PAIRS: Record<string, string> = { ')': '(', ']': '[', '}': '{' };
const NAMES: Record<string, string> = { '(': 'parentheses ()', '[': 'brackets []', '{': 'braces {}' };

const lineAt = (code: string, index: number) => code.slice(0, index).split('\n').length;

/** Bracket matching with a stack, reporting where the problem is. */
export function checkBrackets(code: string): string | null {
  const stack: { ch: string; at: number }[] = [];
  for (let i = 0; i < code.length; i++) {
    const ch = code[i];
    if (ch === '(' || ch === '[' || ch === '{') {
      stack.push({ ch, at: i });
    } else if (ch in PAIRS) {
      const top = stack.pop();
      if (!top) return `Unmatched ${NAMES[PAIRS[ch]]}: extra "${ch}" on line ${lineAt(code, i)}`;
      if (top.ch !== PAIRS[ch]) {
        return `Unmatched ${NAMES[top.ch]}: "${top.ch}" on line ${lineAt(code, top.at)} is closed by "${ch}" on line ${lineAt(code, i)}`;
      }
    }
  }
  const open = stack.pop();
  if (open) return `Unmatched ${NAMES[open.ch]}: "${open.ch}" on line ${lineAt(code, open.at)} is never closed`;
  return null;
}

/**
 * Join physical lines into logical lines: a line continues while brackets
 * are open (or, for Python, when it ends with a backslash).
 */
function logicalLines(code: string, backslashContinues = false): { text: string; line: number }[] {
  const result: { text: string; line: number }[] = [];
  let depth = 0;
  let buf = '';
  let start = 1;
  code.split('\n').forEach((raw, idx) => {
    if (!buf) start = idx + 1;
    buf += (buf ? ' ' : '') + raw;
    for (const ch of raw) {
      if (ch === '(' || ch === '[' || ch === '{') depth++;
      else if (ch === ')' || ch === ']' || ch === '}') depth = Math.max(0, depth - 1);
    }
    const continues = depth > 0 || (backslashContinues && /\\\s*$/.test(raw));
    if (!continues) {
      result.push({ text: buf, line: start });
      buf = '';
    }
  });
  if (buf) result.push({ text: buf, line: start });
  return result;
}


// ---------------------------------------------------------------------------
// Languages
// ---------------------------------------------------------------------------

function validatePython(code: string): string | null {
  const brackets = checkBrackets(code);
  if (brackets) return brackets;

  const lines = logicalLines(code, true);

  for (const { text, line } of lines) {
    const t = text.trim();
    if (/^(?:async\s+)?def\s+\w+\s*\(.*\)(?:\s*->\s*[^:]+)?\s*$/.test(t)) {
      return `Missing colon after function definition (line ${line})`;
    }
    if (/^(?:if|elif|while|for|with|class|except|async\s+for|async\s+with)\b/.test(t) && !/:/.test(t)) {
      return `Missing colon after "${t.split(/[\s(:]/)[0]}" statement (line ${line})`;
    }
    if (/^(?:else|try|finally)\s*$/.test(t)) {
      return `Missing colon after "${t}" (line ${line})`;
    }
  }

  // try needs except or finally at the same indentation
  const physical = code.split('\n');
  for (let i = 0; i < physical.length; i++) {
    const m = /^(\s*)try\s*:/.exec(physical[i]);
    if (!m) continue;
    const indent = m[1].length;
    let handled = false;
    for (let j = i + 1; j < physical.length; j++) {
      const l = physical[j];
      if (!l.trim()) continue;
      const ind = l.length - l.trimStart().length;
      if (ind < indent) break;
      if (ind === indent) {
        handled = /^\s*(except|finally)\b/.test(l);
        if (handled || !/^\s*(else|elif)\b/.test(l)) break;
      }
    }
    if (!handled) return `try block without except or finally (line ${i + 1})`;
  }

  return null;
}

function validateJavaScript(code: string): string | null {
  const brackets = checkBrackets(code);
  if (brackets) return brackets;

  // A try block must be followed by catch or finally
  const re = /\btry\s*\{/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(code))) {
    let depth = 0;
    let i = m.index + m[0].length - 1;
    for (; i < code.length; i++) {
      if (code[i] === '{') depth++;
      else if (code[i] === '}' && --depth === 0) break;
    }
    if (!/^\s*(catch|finally)\b/.test(code.slice(i + 1))) {
      return `try block without catch or finally (line ${lineAt(code, m.index)})`;
    }
  }
  return null;
}

function validateJavaLike(code: string): string | null {
  const brackets = checkBrackets(code);
  if (brackets) return brackets;

  // After "class Foo ..." the next "{" or ";" must be a "{". The brace may sit
  // on a later line (Allman style is standard in C#), and the header may wrap.
  const decl = /^[ \t]*(?:[\w@]+[ \t]+)*(class|interface|enum|record|struct)[ \t]+\w+/gm;
  let m: RegExpExecArray | null;
  while ((m = decl.exec(code))) {
    const after = code.slice(m.index + m[0].length);
    const stop = after.search(/[{;}]/);
    const terminator = stop === -1 ? '' : after[stop];
    // C# positional records may end with ";" (record Person(string Name);)
    if (terminator === '{' || (terminator === ';' && m[1] === 'record')) continue;
    return `Type declaration missing opening brace (line ${lineAt(code, m.index)})`;
  }
  return null;
}

function validateGo(code: string): string | null {
  const brackets = checkBrackets(code);
  if (brackets) return brackets;

  // Go requires the opening brace on the same (logical) line as func
  for (const { text, line } of logicalLines(code)) {
    const t = text.trim();
    if (/^func\b/.test(t) && !t.includes('{')) {
      return `Function missing opening brace on the same line (line ${line})`;
    }
  }
  return null;
}

function validatePHP(code: string): string | null {
  const brackets = checkBrackets(code);
  if (brackets) return brackets;

  const re = /\bfunction\s+&?\w+\s*\(([^)]*)\)/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(code))) {
    const params = m[1].split(',').map((p) => p.trim()).filter(Boolean);
    const bad = params.find((p) => !/\$\w+/.test(p));
    if (bad) {
      return `PHP function parameters must start with $ (got "${bad}" on line ${lineAt(code, m.index)})`;
    }
  }

  const tries = /\btry\s*\{/g;
  while ((m = tries.exec(code))) {
    let depth = 0;
    let i = m.index + m[0].length - 1;
    for (; i < code.length; i++) {
      if (code[i] === '{') depth++;
      else if (code[i] === '}' && --depth === 0) break;
    }
    if (!/^\s*(catch|finally)\b/.test(code.slice(i + 1))) {
      return `try block without catch or finally (line ${lineAt(code, m.index)})`;
    }
  }
  return null;
}

function validateSQL(code: string): string | null {
  const brackets = checkBrackets(code);
  if (brackets) return brackets;

  for (const stmt of code.split(';')) {
    const upper = stmt.trim().replace(/\s+/g, ' ').toUpperCase();
    if (/^UPDATE\b/.test(upper) && !/\bSET\b/.test(upper)) {
      return 'UPDATE statement without SET clause';
    }
    if (/^INSERT INTO\b/.test(upper) && !/\b(VALUES|SELECT|DEFAULT VALUES)\b/.test(upper)) {
      return 'INSERT statement without VALUES or SELECT';
    }
  }
  return null;
}
