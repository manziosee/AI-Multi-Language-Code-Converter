import type { Language } from '@/types';

export function validateSyntax(code: string, language: Language): string | null {
  if (!code.trim()) return null;

  const trimmed = code.trim();

  switch (language) {
    case 'python':
      return validatePython(trimmed);
    case 'javascript':
    case 'nodejs':
      return validateJavaScript(trimmed);
    case 'typescript':
      return validateTypeScript(trimmed);
    case 'java':
      return validateJava(trimmed);
    case 'golang':
      return validateGo(trimmed);
    case 'c':
    case 'cpp':
      return validateC(trimmed);
    case 'csharp':
      return validateCSharp(trimmed);
    case 'rust':
      return validateRust(trimmed);
    case 'php':
      return validatePHP(trimmed);
    case 'sql':
      return validateSQL(trimmed);
    default:
      return null;
  }
}

function validateSQL(code: string): string | null {
  const statements = code.split(';').filter(s => s.trim());
  
  for (const stmt of statements) {
    const upper = stmt.trim().toUpperCase();
    
    if (upper.startsWith('SELECT') && !upper.includes('FROM')) {
      return 'SELECT statement without FROM clause';
    }
    
    if (upper.startsWith('INSERT INTO') && !upper.includes('VALUES') && !upper.includes('SELECT')) {
      return 'INSERT statement without VALUES or SELECT';
    }
    
    if (upper.startsWith('UPDATE') && !upper.includes('SET')) {
      return 'UPDATE statement without SET clause';
    }
  }
  
  return null;
}

function validatePython(code: string): string | null {
  const lines = code.split('\n');
  
  // Check for unmatched parentheses, brackets, braces
  const openParen = (code.match(/\(/g) || []).length;
  const closeParen = (code.match(/\)/g) || []).length;
  if (openParen !== closeParen) return 'Unmatched parentheses ()';
  
  const openBracket = (code.match(/\[/g) || []).length;
  const closeBracket = (code.match(/\]/g) || []).length;
  if (openBracket !== closeBracket) return 'Unmatched brackets []';
  
  const openBrace = (code.match(/\{/g) || []).length;
  const closeBrace = (code.match(/\}/g) || []).length;
  if (openBrace !== closeBrace) return 'Unmatched braces {}';
  
  // Check for def without colon
  if (/def\s+\w+\([^)]*\)\s*$/m.test(code)) return 'Missing colon after function definition';
  
  // Check for if/for/while without colon
  if (/(if|for|while|elif|else|try|except|finally|with|class)\s+[^:]*$/m.test(code)) {
    return 'Missing colon after control statement';
  }
  
  // Check for try without except
  if (/\btry\s*:/.test(code) && !/\bexcept\b/.test(code)) {
    return 'try block without except clause';
  }
  
  // Check for unreachable code after return
  for (let i = 0; i < lines.length - 1; i++) {
    const line = lines[i];
    const nextLine = lines[i + 1];
    if (line.trim().startsWith('return ')) {
      const currentIndent = line.match(/^\s*/)?.[0].length || 0;
      const nextIndent = nextLine.match(/^\s*/)?.[0].length || 0;
      if (nextLine.trim() && nextIndent > currentIndent) {
        return `Unreachable code after return (line ${i + 2})`;
      }
    }
  }
  
  // Check for undefined variables in function parameters vs usage
  const funcMatches = code.matchAll(/def\s+(\w+)\(([^)]*)\):/g);
  for (const match of funcMatches) {
    const params = match[2].split(',').map(p => p.trim().split('=')[0].trim()).filter(Boolean);
    const funcStart = match.index || 0;
    const funcBody = code.slice(funcStart).split(/\ndef\s/)[0];
    
    // Find variables used in return statements
    const returnMatches = funcBody.matchAll(/return\s+([a-zA-Z_]\w*)(?:\s|\+|\-|\*|\/|$)/g);
    for (const ret of returnMatches) {
      const varName = ret[1];
      if (!params.includes(varName) && !funcBody.includes(`${varName} =`)) {
        return `Variable '${varName}' used but not defined (check function parameters)`;
      }
    }
  }
  
  // Check for except without variable but using one
  if (/except[^:]*:/.test(code) && !/except[^:]+as\s+\w+:/.test(code)) {
    const exceptBlocks = code.split(/except[^:]*:/);
    for (let i = 1; i < exceptBlocks.length; i++) {
      const block = exceptBlocks[i].split(/\n(?!\s)/)[0];
      if (/print\([^)]*,\s*\w+\)/.test(block)) {
        return 'Exception variable used but not defined (missing "as variable")';
      }
    }
  }
  
  return null;
}

function validateJavaScript(code: string): string | null {
  const openBrace = (code.match(/\{/g) || []).length;
  const closeBrace = (code.match(/\}/g) || []).length;
  if (openBrace !== closeBrace) return 'Unmatched braces {}';
  
  const openParen = (code.match(/\(/g) || []).length;
  const closeParen = (code.match(/\)/g) || []).length;
  if (openParen !== closeParen) return 'Unmatched parentheses ()';
  
  const openBracket = (code.match(/\[/g) || []).length;
  const closeBracket = (code.match(/\]/g) || []).length;
  if (openBracket !== closeBracket) return 'Unmatched brackets []';
  
  // Check for try without catch
  if (/\btry\s*\{/.test(code) && !/\bcatch\s*\(/.test(code) && !/\bfinally\s*\{/.test(code)) {
    return 'try block without catch or finally clause';
  }
  
  // Check for catch without error parameter but using one
  const catchMatches = code.matchAll(/catch\s*\(([^)]*)\)\s*\{([^}]+)\}/g);
  for (const match of catchMatches) {
    const param = match[1].trim();
    const body = match[2];
    if (!param && /console\.(log|error)\([^)]*\w+/.test(body)) {
      return 'Error variable used in catch but not defined in catch(error)';
    }
  }
  
  // Check for undefined variables in function
  const funcMatches = code.matchAll(/function\s+\w+\(([^)]*)\)\s*\{([^}]+)\}/g);
  for (const match of funcMatches) {
    const params = match[1].split(',').map(p => p.trim()).filter(Boolean);
    const body = match[2];
    const returnMatches = body.matchAll(/return\s+([a-zA-Z_]\w*)(?:\s|;|\+|\-|\*|\/|$)/g);
    for (const ret of returnMatches) {
      const varName = ret[1];
      if (!params.includes(varName) && !body.includes(`${varName} =`) && !body.includes(`let ${varName}`) && !body.includes(`const ${varName}`) && !body.includes(`var ${varName}`)) {
        return `Variable '${varName}' used but not defined`;
      }
    }
  }
  
  return null;
}

function validateTypeScript(code: string): string | null {
  return validateJavaScript(code);
}

function validateJava(code: string): string | null {
  // Check for unmatched braces
  const openBrace = (code.match(/\{/g) || []).length;
  const closeBrace = (code.match(/\}/g) || []).length;
  if (openBrace !== closeBrace) return 'Unmatched braces {}';
  
  const openParen = (code.match(/\(/g) || []).length;
  const closeParen = (code.match(/\)/g) || []).length;
  if (openParen !== closeParen) return 'Unmatched parentheses ()';
  
  // Check for class without braces
  if (/class\s+\w+[^{]*$/m.test(code)) return 'Class definition missing opening brace';
  
  // Check for method without braces
  if (/(public|private|protected)\s+\w+\s+\w+\([^)]*\)\s*$/m.test(code)) {
    return 'Method definition missing opening brace';
  }
  
  return null;
}

function validateGo(code: string): string | null {
  const openBrace = (code.match(/\{/g) || []).length;
  const closeBrace = (code.match(/\}/g) || []).length;
  if (openBrace !== closeBrace) return 'Unmatched braces {}';
  
  const openParen = (code.match(/\(/g) || []).length;
  const closeParen = (code.match(/\)/g) || []).length;
  if (openParen !== closeParen) return 'Unmatched parentheses ()';
  
  // Check for func without braces
  if (/func\s+\w+\([^)]*\)[^{]*$/m.test(code)) return 'Function missing opening brace';
  
  return null;
}

function validateC(code: string): string | null {
  const openBrace = (code.match(/\{/g) || []).length;
  const closeBrace = (code.match(/\}/g) || []).length;
  if (openBrace !== closeBrace) return 'Unmatched braces {}';
  
  const openParen = (code.match(/\(/g) || []).length;
  const closeParen = (code.match(/\)/g) || []).length;
  if (openParen !== closeParen) return 'Unmatched parentheses ()';
  
  // Check for missing semicolons
  if (/\)\s*\n\s*[a-z]/i.test(code) && !/{/.test(code)) {
    return 'Possible missing semicolons';
  }
  
  return null;
}

function validateCSharp(code: string): string | null {
  return validateJava(code);
}

function validateRust(code: string): string | null {
  const openBrace = (code.match(/\{/g) || []).length;
  const closeBrace = (code.match(/\}/g) || []).length;
  if (openBrace !== closeBrace) return 'Unmatched braces {}';
  
  const openParen = (code.match(/\(/g) || []).length;
  const closeParen = (code.match(/\)/g) || []).length;
  if (openParen !== closeParen) return 'Unmatched parentheses ()';
  
  return null;
}

function validatePHP(code: string): string | null {
  if (!code.includes('<?php')) return 'Missing <?php opening tag';
  
  const openBrace = (code.match(/\{/g) || []).length;
  const closeBrace = (code.match(/\}/g) || []).length;
  if (openBrace !== closeBrace) return 'Unmatched braces {}';
  
  const openParen = (code.match(/\(/g) || []).length;
  const closeParen = (code.match(/\)/g) || []).length;
  if (openParen !== closeParen) return 'Unmatched parentheses ()';
  
  // Check for try without catch
  if (/\btry\s*\{/.test(code) && !/\bcatch\s*\(/.test(code)) {
    return 'try block without catch clause';
  }
  
  // Check for variables without $ prefix
  const funcMatches = code.matchAll(/function\s+\w+\(([^)]*)\)/g);
  for (const match of funcMatches) {
    const params = match[1];
    if (params && !/\$/.test(params)) {
      return 'PHP function parameters must start with $ (e.g., $param)';
    }
  }
  
  return null;
}
