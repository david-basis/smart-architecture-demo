// SysML v2 Lexer

export type TokenType =
  | 'KEYWORD'
  | 'IDENTIFIER'
  | 'STRING'
  | 'NUMBER'
  | 'LBRACE'
  | 'RBRACE'
  | 'LBRACKET'
  | 'RBRACKET'
  | 'LPAREN'
  | 'RPAREN'
  | 'COLON'
  | 'SEMICOLON'
  | 'EQUALS'
  | 'COMMA'
  | 'DOT'
  | 'COMMENT'
  | 'EOF';

export interface Token {
  type: TokenType;
  value: string;
  line: number;
  column: number;
}

const KEYWORDS = new Set([
  'package',
  'part',
  'def',
  'port',
  'item',
  'requirement',
  'state',
  'transition',
  'attribute',
  'interface',
  'connect',
  'bind',
  'entry',
  'then',
  'first',
  'accept',
  'action',
  'inout',
  'in',
  'out',
  'id',
  'text',
]);

export function tokenize(source: string): Token[] {
  const tokens: Token[] = [];
  let pos = 0;
  let line = 1;
  let column = 1;

  while (pos < source.length) {
    const char = source[pos];

    // Skip whitespace
    if (/\s/.test(char)) {
      if (char === '\n') {
        line++;
        column = 1;
      } else {
        column++;
      }
      pos++;
      continue;
    }

    // Single-line comment
    if (char === '/' && source[pos + 1] === '/') {
      const start = pos;
      while (pos < source.length && source[pos] !== '\n') {
        pos++;
      }
      tokens.push({
        type: 'COMMENT',
        value: source.slice(start, pos),
        line,
        column,
      });
      continue;
    }

    // Multi-line comment
    if (char === '/' && source[pos + 1] === '*') {
      const start = pos;
      pos += 2;
      while (pos < source.length - 1 && !(source[pos] === '*' && source[pos + 1] === '/')) {
        if (source[pos] === '\n') {
          line++;
          column = 1;
        }
        pos++;
      }
      pos += 2;
      tokens.push({
        type: 'COMMENT',
        value: source.slice(start, pos),
        line,
        column,
      });
      continue;
    }

    // String literal
    if (char === '"') {
      const startCol = column;
      pos++;
      column++;
      const start = pos;
      while (pos < source.length && source[pos] !== '"') {
        if (source[pos] === '\n') {
          line++;
          column = 1;
        } else {
          column++;
        }
        pos++;
      }
      tokens.push({
        type: 'STRING',
        value: source.slice(start, pos),
        line,
        column: startCol,
      });
      pos++; // Skip closing quote
      column++;
      continue;
    }

    // Number
    if (/\d/.test(char) || (char === '.' && /\d/.test(source[pos + 1]))) {
      const startCol = column;
      const start = pos;
      while (pos < source.length && /[\d.]/.test(source[pos])) {
        pos++;
        column++;
      }
      tokens.push({
        type: 'NUMBER',
        value: source.slice(start, pos),
        line,
        column: startCol,
      });
      continue;
    }

    // Identifier or keyword
    if (/[a-zA-Z_]/.test(char)) {
      const startCol = column;
      const start = pos;
      while (pos < source.length && /[a-zA-Z0-9_]/.test(source[pos])) {
        pos++;
        column++;
      }
      const value = source.slice(start, pos);
      tokens.push({
        type: KEYWORDS.has(value) ? 'KEYWORD' : 'IDENTIFIER',
        value,
        line,
        column: startCol,
      });
      continue;
    }

    // Single-character tokens
    const singleTokens: Record<string, TokenType> = {
      '{': 'LBRACE',
      '}': 'RBRACE',
      '[': 'LBRACKET',
      ']': 'RBRACKET',
      '(': 'LPAREN',
      ')': 'RPAREN',
      ':': 'COLON',
      ';': 'SEMICOLON',
      '=': 'EQUALS',
      ',': 'COMMA',
      '.': 'DOT',
    };

    if (char in singleTokens) {
      tokens.push({
        type: singleTokens[char],
        value: char,
        line,
        column,
      });
      pos++;
      column++;
      continue;
    }

    // Unknown character - skip
    pos++;
    column++;
  }

  tokens.push({ type: 'EOF', value: '', line, column });
  return tokens;
}
