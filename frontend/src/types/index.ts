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
];
