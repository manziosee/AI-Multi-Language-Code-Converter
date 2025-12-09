import type { Language } from '@/types';

export function detectLanguage(code: string): Language | null {
  if (!code.trim()) return null;

  const trimmed = code.trim();
  
  // Prisma (check early - very specific syntax)
  if (/(model\s+\w+|datasource\s+db|generator\s+client)\s*\{|@(id|default|unique|relation|map)/.test(trimmed)) return 'prisma';
  
  // Drizzle (check early)
  if (/(pgTable|mysqlTable|sqliteTable)\(|from\s+['"]drizzle-orm/.test(trimmed)) return 'drizzle';
  
  // Go (check before SQL to avoid false positives)
  if (/(package\s+\w+|func\s+\w+\(|import\s+\(|fmt\.|:=|github\.com)/.test(trimmed)) return 'golang';
  
  // Python (check before SQL)
  if (/(^|\n)(def|class|import|from)\s+\w+|async\s+def|@app\.|FastAPI|asyncpg/.test(trimmed)) return 'python';
  
  // C# (check before C/C++)
  if (/(using\s+System|namespace\s+\w+|Console\.|class\s+\w+\s*:\s*\w+)/.test(trimmed)) return 'csharp';
  
  // C++ (check before C)
  if (/(#include\s*<iostream>|std::|cout|cin|namespace\s+std|class\s+\w+\s*\{)/.test(trimmed)) return 'cpp';
  
  // C
  if (/(#include\s*<stdio\.h>|#include\s*<stdlib\.h>|printf\(|scanf\(|int\s+main\s*\()/.test(trimmed)) return 'c';
  
  // PHP
  if (/<\?php|\$\w+\s*=/.test(trimmed)) return 'php';
  
  // TypeScript (check before JavaScript)
  if (/:\s*(string|number|boolean|any|void)|interface\s+\w+|type\s+\w+\s*=/.test(trimmed)) return 'typescript';
  
  // JavaScript/Node.js
  if (/(const|let|var|function|=>|console\.log)/.test(trimmed)) {
    if (/(require\(|module\.exports|exports\.|__dirname|__filename)/.test(trimmed)) return 'nodejs';
    return 'javascript';
  }
  
  // Java
  if (/(public\s+class|public\s+static\s+void\s+main|System\.out|import\s+java\.)/.test(trimmed)) return 'java';
  
  // Rust
  if (/(fn\s+\w+\(|let\s+mut|pub\s+fn|println!|use\s+std::)/.test(trimmed)) return 'rust';
  
  // SQL (check LAST - only if no other language matched)
  // Must have SQL-specific patterns: CREATE TABLE, CREATE FUNCTION, or start with SELECT/INSERT/UPDATE/DELETE
  if (/^\s*(CREATE\s+(TABLE|FUNCTION|PROCEDURE|INDEX|VIEW|DATABASE|SCHEMA|TRIGGER)|ALTER\s+TABLE|DROP\s+TABLE|--\s*.*\n\s*CREATE)/im.test(trimmed)) return 'sql';
  if (/^\s*(SELECT|INSERT|UPDATE|DELETE|WITH)\s+/im.test(trimmed) && !/^\s*(package|import|func|def|class|const|let|var|public)/im.test(trimmed)) return 'sql';

  return null;
}
