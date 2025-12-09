import type { Language } from '@/types';

export function detectLanguage(code: string): Language | null {
  if (!code.trim()) return null;

  // Python
  if (/^(def|class|import|from|if __name__|print\()/m.test(code)) return 'python';
  
  // TypeScript (check before JavaScript)
  if (/:\s*(string|number|boolean|any|void|interface|type\s+\w+\s*=)/m.test(code)) return 'typescript';
  
  // JavaScript/Node.js
  if (/(const|let|var|function|=>|console\.log|require\(|module\.exports)/m.test(code)) {
    if (/require\(|module\.exports|exports\./m.test(code)) return 'nodejs';
    return 'javascript';
  }
  
  // Java
  if (/(public\s+class|public\s+static\s+void\s+main|System\.out\.println)/m.test(code)) return 'java';
  
  // PHP
  if (/^<\?php/m.test(code)) return 'php';
  
  // Go
  if (/(package\s+main|func\s+main\(\)|import\s+\(|fmt\.Print)/m.test(code)) return 'golang';
  
  // C#
  if (/(using\s+System|namespace\s+\w+|public\s+class\s+\w+\s*:\s*\w+|Console\.WriteLine)/m.test(code)) return 'csharp';
  
  // Rust
  if (/(fn\s+main\(\)|let\s+mut|pub\s+fn|println!|use\s+std::)/m.test(code)) return 'rust';
  
  // C++
  if (/(#include\s+<iostream>|std::|cout\s*<<|namespace\s+std)/m.test(code)) return 'cpp';
  
  // C
  if (/(#include\s+<stdio\.h>|printf\(|int\s+main\()/m.test(code)) return 'c';
  
  // SQL
  if (/(SELECT|INSERT|UPDATE|DELETE|CREATE\s+TABLE|DROP\s+TABLE|ALTER\s+TABLE)\s+/i.test(code)) return 'sql';
  
  // Prisma
  if (/(model\s+\w+\s*{|datasource\s+db|generator\s+client|@id|@default|@relation)/m.test(code)) return 'prisma';
  
  // Drizzle
  if (/(pgTable|mysqlTable|sqliteTable|serial\(|varchar\(|integer\(|from\s+['"]drizzle-orm)/m.test(code)) return 'drizzle';

  return null;
}
