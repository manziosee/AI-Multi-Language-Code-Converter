export type Language = 
  | 'python' 
  | 'nodejs' 
  | 'javascript'
  | 'php' 
  | 'golang' 
  | 'java' 
  | 'typescript' 
  | 'sql' 
  | 'prisma'
  | 'drizzle'
  | 'c'
  | 'cpp'
  | 'csharp'
  | 'rust';

export interface LanguageOption {
  value: Language;
  label: string;
  extension: string;
  monacoLanguage: string;
}

export interface ConversionRequest {
  source_language: Language;
  target_language: Language;
  code: string;
}

export interface ConversionResponse {
  converted_code: string;
  source_language: string;
  target_language: string;
  success: boolean;
}

export interface ErrorResponse {
  detail: string;
  success: false;
}

export interface ExplainRequest {
  language: Language;
  code: string;
}

export interface ExplainResponse {
  explanation: string;
  language: string;
  success: boolean;
}

export type ViewMode = 'single' | 'split';

export const SUPPORTED_LANGUAGES: LanguageOption[] = [
  { value: 'python', label: 'Python', extension: '.py', monacoLanguage: 'python' },
  { value: 'nodejs', label: 'Node.js', extension: '.js', monacoLanguage: 'javascript' },
  { value: 'javascript', label: 'JavaScript', extension: '.js', monacoLanguage: 'javascript' },
  { value: 'typescript', label: 'TypeScript', extension: '.ts', monacoLanguage: 'typescript' },
  { value: 'java', label: 'Java', extension: '.java', monacoLanguage: 'java' },
  { value: 'php', label: 'PHP', extension: '.php', monacoLanguage: 'php' },
  { value: 'golang', label: 'Go', extension: '.go', monacoLanguage: 'go' },
  { value: 'c', label: 'C', extension: '.c', monacoLanguage: 'c' },
  { value: 'cpp', label: 'C++', extension: '.cpp', monacoLanguage: 'cpp' },
  { value: 'csharp', label: 'C#', extension: '.cs', monacoLanguage: 'csharp' },
  { value: 'rust', label: 'Rust', extension: '.rs', monacoLanguage: 'rust' },
  { value: 'sql', label: 'SQL', extension: '.sql', monacoLanguage: 'sql' },
  { value: 'prisma', label: 'Prisma Schema', extension: '.prisma', monacoLanguage: 'prisma' },
  { value: 'drizzle', label: 'Drizzle ORM', extension: '.ts', monacoLanguage: 'typescript' },
];

// Valid conversion pairs
export const VALID_CONVERSIONS: Record<Language, Language[]> = {
  python: ['nodejs', 'javascript', 'typescript', 'java', 'php', 'golang', 'c', 'cpp', 'csharp', 'rust'],
  nodejs: ['python', 'javascript', 'typescript', 'java', 'php', 'golang', 'c', 'cpp', 'csharp', 'rust'],
  javascript: ['python', 'nodejs', 'typescript', 'java', 'php', 'golang', 'c', 'cpp', 'csharp', 'rust'],
  typescript: ['python', 'nodejs', 'javascript', 'java', 'php', 'golang', 'c', 'cpp', 'csharp', 'rust'],
  java: ['python', 'nodejs', 'javascript', 'typescript', 'php', 'golang', 'c', 'cpp', 'csharp', 'rust'],
  php: ['python', 'nodejs', 'javascript', 'typescript', 'java', 'golang', 'c', 'cpp', 'csharp', 'rust'],
  golang: ['python', 'nodejs', 'javascript', 'typescript', 'java', 'php', 'c', 'cpp', 'csharp', 'rust'],
  c: ['python', 'nodejs', 'javascript', 'typescript', 'java', 'php', 'golang', 'cpp', 'csharp', 'rust'],
  cpp: ['python', 'nodejs', 'javascript', 'typescript', 'java', 'php', 'golang', 'c', 'csharp', 'rust'],
  csharp: ['python', 'nodejs', 'javascript', 'typescript', 'java', 'php', 'golang', 'c', 'cpp', 'rust'],
  rust: ['python', 'nodejs', 'javascript', 'typescript', 'java', 'php', 'golang', 'c', 'cpp', 'csharp'],
  sql: ['prisma', 'drizzle'],
  prisma: ['sql', 'drizzle'],
  drizzle: ['sql', 'prisma'],
};
