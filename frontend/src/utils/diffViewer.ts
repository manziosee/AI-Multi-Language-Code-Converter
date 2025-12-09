/**
 * Diff viewer utility for comparing source and converted code
 */

export interface DiffLine {
  type: 'added' | 'removed' | 'unchanged';
  content: string;
  lineNumber: number;
}

export function generateDiff(source: string, converted: string): DiffLine[] {
  const sourceLines = source.split('\n');
  const convertedLines = converted.split('\n');
  const diff: DiffLine[] = [];
  
  const maxLines = Math.max(sourceLines.length, convertedLines.length);
  
  for (let i = 0; i < maxLines; i++) {
    const sourceLine = sourceLines[i];
    const convertedLine = convertedLines[i];
    
    if (sourceLine === convertedLine) {
      diff.push({
        type: 'unchanged',
        content: sourceLine || '',
        lineNumber: i + 1
      });
    } else {
      if (sourceLine !== undefined) {
        diff.push({
          type: 'removed',
          content: sourceLine,
          lineNumber: i + 1
        });
      }
      if (convertedLine !== undefined) {
        diff.push({
          type: 'added',
          content: convertedLine,
          lineNumber: i + 1
        });
      }
    }
  }
  
  return diff;
}

export function calculateSimilarity(source: string, converted: string): number {
  const sourceLines = source.split('\n');
  const convertedLines = converted.split('\n');
  
  let matches = 0;
  const maxLines = Math.max(sourceLines.length, convertedLines.length);
  
  for (let i = 0; i < Math.min(sourceLines.length, convertedLines.length); i++) {
    if (sourceLines[i].trim() === convertedLines[i].trim()) {
      matches++;
    }
  }
  
  return Math.round((matches / maxLines) * 100);
}
