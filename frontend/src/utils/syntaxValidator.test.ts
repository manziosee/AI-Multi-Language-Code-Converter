import { describe, it, expect } from 'vitest';
import { validateSyntax, stripCode, checkBrackets } from './syntaxValidator';
import { CODE_EXAMPLES } from './codeExamples';
import type { Language } from '@/types';

const ok = (lang: Language, code: string) => expect(validateSyntax(code, lang)).toBeNull();
const bad = (lang: Language, code: string, msg: RegExp) => expect(validateSyntax(code, lang)).toMatch(msg);

describe('built-in examples', () => {
  for (const [lang, code] of Object.entries(CODE_EXAMPLES)) {
    it(`${lang} example passes`, () => ok(lang as Language, code));
  }
});

describe('stripCode', () => {
  it('keeps line count and blanks comment/string contents', () => {
    const src = 'x = "a(b" # call(\ny = 1';
    const out = stripCode(src, { lineComments: ['#'], quotes: ['"'] });
    expect(out.split('\n')).toHaveLength(2);
    expect(out).not.toContain('(');
    expect(out.length).toBe(src.length);
  });
});

describe('checkBrackets', () => {
  it('reports mismatched pair with lines', () => {
    expect(checkBrackets('foo(\n  [1, 2)\n]')).toMatch(/"\[" on line 2 is closed by "\)"/);
  });
  it('reports unclosed opener', () => {
    expect(checkBrackets('a = {\n')).toMatch(/never closed/);
  });
});

describe('python', () => {
  it('ignores keywords in comments (the reported false alarm)', () => {
    ok('python', '# loop for each item\nitems = [1, 2]\nprint(items)');
  });
  it('ignores brackets and keywords inside strings', () => {
    ok('python', 'print("(")\nmsg = "if you wait for it"\ndoc = """\nclass Foo\n  ((\n"""');
  });
  it('allows multi-line conditions and signatures', () => {
    ok('python', 'if (a and\n        b):\n    pass\ndef f(\n    x,\n    y,\n) -> int:\n    return x');
  });
  it('allows inline if/for expressions', () => {
    ok('python', 'x = 1 if y else 2\nsquares = [n * n for n in range(5)]');
  });
  it('allows try/finally and loop variables in return', () => {
    ok('python', 'def f(items):\n    try:\n        for x in items:\n            return x\n    finally:\n        pass');
  });
  it('allows return spanning lines', () => {
    ok('python', 'def f(a, b):\n    return (\n        a + b\n    )');
  });
  it('catches unmatched parentheses', () => bad('python', 'print((1)', /Unmatched parentheses/));
  it('catches def without colon', () => bad('python', 'def foo(x)\n    return x', /Missing colon after function definition \(line 1\)/));
  it('catches if without colon', () => bad('python', 'x = 1\nif x > 0\n    print(x)', /Missing colon after "if" statement \(line 2\)/));
  it('catches bare else without colon', () => bad('python', 'if x:\n    pass\nelse\n    pass', /"else"/));
  it('catches try without handler', () => bad('python', 'try:\n    x = 1\nprint(x)', /try block without except or finally/));
});

describe('javascript / typescript', () => {
  it('ignores brackets in strings, templates, comments and regex', () => {
    ok('javascript', 'const a = "(";\nconst b = `${"{"} )`;\n// call(\n/* { */\nconst re = /\\(+[)]/g;\nconst d = x / 2 / (y);');
  });
  it('accepts try/catch and try/finally', () => {
    ok('typescript', 'try { a(); } catch (e: unknown) { log(e); }\ntry { b(); } finally { c(); }');
  });
  it('catches try without catch', () => bad('javascript', 'try {\n  run();\n}\nnext();', /try block without catch or finally \(line 1\)/));
  it('catches unmatched braces', () => bad('nodejs', 'function f() {\n  return 1;\n', /Unmatched braces/));
});

describe('java / c#', () => {
  it('accepts Allman braces (standard C# style)', () => {
    ok('csharp', 'public class Foo\n{\n    public void Bar()\n    {\n    }\n}');
  });
  it('accepts wrapped headers and generic constraints', () => {
    ok('java', 'public class Foo\n    extends Bar\n    implements Baz {\n}');
    ok('csharp', 'class Box<T> where T : class\n{\n}');
  });
  it('accepts C# positional records', () => ok('csharp', 'public record Person(string Name, int Age);'));
  it('ignores "class" in strings and Foo.class', () => {
    ok('java', 'class A {\n  String s = "class X";\n  Class<?> c = A.class;\n}');
  });
  it('catches class without brace', () => bad('java', 'public class Foo\n    int x;\n', /Type declaration missing opening brace \(line 1\)/));
});

describe('go', () => {
  it('accepts multi-line signatures', () => {
    ok('golang', 'func f(\n\ta int,\n\tb int,\n) (int, error) {\n\treturn a + b, nil\n}');
  });
  it('ignores braces in raw strings', () => ok('golang', 'var s = `{{ ( `'));
  it('catches brace on next line', () => bad('golang', 'func main()\n{\n}', /Function missing opening brace/));
});

describe('rust', () => {
  it('handles lifetimes and char literals', () => {
    ok('rust', "fn first<'a>(s: &'a str) -> &'a str {\n    let c = '{';\n    let d = '\\'';\n    s\n}");
  });
  it('catches unclosed brace', () => bad('rust', 'fn main() {\n', /Unmatched braces/));
});

describe('c / c++', () => {
  it('ignores brackets in strings and comments', () => ok('c', 'printf("%d)\\n", x); // )\n/* { */'));
});

describe('php', () => {
  it('does not require an opening tag for snippets', () => ok('php', '$x = 1;\necho $x;'));
  it('accepts typed and by-ref parameters', () => ok('php', '<?php\nfunction f(int $a, array &$b = []) { return $a; }'));
  it('catches parameter without $', () => bad('php', '<?php\nfunction f(a) { return 1; }', /must start with \$/));
});

describe('sql', () => {
  it('accepts SELECT without FROM (valid in most databases)', () => ok('sql', 'SELECT NOW();\nSELECT 1;'));
  it('ignores keywords in comments and strings', () => ok('sql', "-- update later\nINSERT INTO t (a) VALUES ('UPDATE x');"));
  it('catches UPDATE without SET', () => bad('sql', 'UPDATE users WHERE id = 1;', /UPDATE statement without SET/));
});
