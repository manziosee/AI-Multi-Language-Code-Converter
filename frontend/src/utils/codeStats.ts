export interface CodeStats {
  lines: number;
  characters: number;
  words: number;
  nonEmptyLines: number;
}

export const getCodeStats = (code: string): CodeStats => {
  const lines = code.split('\n');
  const nonEmptyLines = lines.filter(line => line.trim().length > 0);
  
  return {
    lines: lines.length,
    characters: code.length,
    words: code.split(/\s+/).filter(word => word.length > 0).length,
    nonEmptyLines: nonEmptyLines.length
  };
};
