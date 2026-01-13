// SysML v2 Parser

import { tokenize, Token, TokenType } from './lexer';
import {
  SysMLModel,
  SysMLElement,
  PartDef,
  Part,
  PortDef,
  Port,
  ItemDef,
  RequirementDef,
  StateDef,
  State,
  Transition,
  Connection,
  Bind,
} from './types';

export class SysMLParser {
  private tokens: Token[] = [];
  private pos = 0;
  private model: SysMLModel = { elements: new Map() };
  private idCounter = 0;

  parse(source: string): SysMLModel {
    this.tokens = tokenize(source).filter(t => t.type !== 'COMMENT');
    this.pos = 0;
    this.model = { elements: new Map() };
    this.idCounter = 0;

    // Parse top-level package
    if (this.check('KEYWORD', 'package')) {
      this.parsePackage();
    }

    return this.model;
  }

  private generateId(): string {
    return `elem_${++this.idCounter}`;
  }

  private current(): Token {
    return this.tokens[this.pos] || { type: 'EOF', value: '', line: 0, column: 0 };
  }

  private advance(): Token {
    const token = this.current();
    this.pos++;
    return token;
  }

  private check(type: TokenType, value?: string): boolean {
    const token = this.current();
    if (token.type !== type) return false;
    if (value !== undefined && token.value !== value) return false;
    return true;
  }

  private match(type: TokenType, value?: string): boolean {
    if (this.check(type, value)) {
      this.advance();
      return true;
    }
    return false;
  }

  private expect(type: TokenType, value?: string): Token {
    if (!this.check(type, value)) {
      const token = this.current();
      throw new Error(
        `Expected ${type}${value ? ` '${value}'` : ''} but got ${token.type} '${token.value}' at line ${token.line}`
      );
    }
    return this.advance();
  }

  private parsePackage(parent?: string): void {
    this.expect('KEYWORD', 'package');
    const name = this.expect('IDENTIFIER').value;
    const id = this.generateId();

    const pkg: SysMLElement = {
      type: 'package',
      name,
      id,
      parent,
      children: [],
      metadata: {},
    };

    this.model.elements.set(id, pkg);
    if (!parent) {
      this.model.rootPackage = id;
    }

    this.expect('LBRACE');
    this.parsePackageBody(id);
    this.expect('RBRACE');
  }

  private parsePackageBody(parentId: string): void {
    const parent = this.model.elements.get(parentId)!;

    while (!this.check('RBRACE') && !this.check('EOF')) {
      if (this.check('KEYWORD', 'item') && this.lookAhead('KEYWORD', 'def')) {
        const elemId = this.parseItemDef(parentId);
        parent.children.push(elemId);
      } else if (this.check('KEYWORD', 'port') && this.lookAhead('KEYWORD', 'def')) {
        const elemId = this.parsePortDef(parentId);
        parent.children.push(elemId);
      } else if (this.check('KEYWORD', 'part') && this.lookAhead('KEYWORD', 'def')) {
        const elemId = this.parsePartDef(parentId);
        parent.children.push(elemId);
      } else if (this.check('KEYWORD', 'part')) {
        const elemId = this.parsePart(parentId);
        parent.children.push(elemId);
      } else if (this.check('KEYWORD', 'requirement') && this.lookAhead('KEYWORD', 'def')) {
        const elemId = this.parseRequirementDef(parentId);
        parent.children.push(elemId);
      } else if (this.check('KEYWORD', 'state') && this.lookAhead('KEYWORD', 'def')) {
        const elemId = this.parseStateDef(parentId);
        parent.children.push(elemId);
      } else if (this.check('KEYWORD', 'interface')) {
        const elemId = this.parseConnection(parentId);
        if (elemId) parent.children.push(elemId);
      } else if (this.check('KEYWORD', 'bind')) {
        const elemId = this.parseBind(parentId);
        parent.children.push(elemId);
      } else {
        // Skip unknown constructs
        this.advance();
      }
    }
  }

  private lookAhead(type: TokenType, value?: string): boolean {
    const nextToken = this.tokens[this.pos + 1];
    if (!nextToken) return false;
    if (nextToken.type !== type) return false;
    if (value !== undefined && nextToken.value !== value) return false;
    return true;
  }

  private parseItemDef(parent: string): string {
    this.expect('KEYWORD', 'item');
    this.expect('KEYWORD', 'def');
    const name = this.expect('IDENTIFIER').value;
    const id = this.generateId();

    const item: ItemDef = {
      type: 'item_def',
      name,
      id,
      parent,
      children: [],
      metadata: {},
    };

    // Optional body
    if (this.match('LBRACE')) {
      while (!this.check('RBRACE') && !this.check('EOF')) {
        this.advance();
      }
      this.expect('RBRACE');
    } else {
      this.match('SEMICOLON');
    }

    this.model.elements.set(id, item);
    return id;
  }

  private parsePortDef(parent: string): string {
    this.expect('KEYWORD', 'port');
    this.expect('KEYWORD', 'def');
    const name = this.expect('IDENTIFIER').value;
    const id = this.generateId();

    const portDef: PortDef = {
      type: 'port_def',
      name,
      id,
      parent,
      children: [],
      items: [],
      metadata: {},
    };

    if (this.match('LBRACE')) {
      while (!this.check('RBRACE') && !this.check('EOF')) {
        // Parse inout item declarations
        if (this.check('KEYWORD', 'inout') || this.check('KEYWORD', 'in') || this.check('KEYWORD', 'out')) {
          const direction = this.advance().value;
          if (this.match('KEYWORD', 'item')) {
            const itemName = this.expect('IDENTIFIER').value;
            if (this.match('COLON')) {
              const itemType = this.expect('IDENTIFIER').value;
              portDef.items.push(`${direction} ${itemName}: ${itemType}`);
            }
            this.match('SEMICOLON');
          }
        } else {
          this.advance();
        }
      }
      this.expect('RBRACE');
    } else {
      this.match('SEMICOLON');
    }

    this.model.elements.set(id, portDef);
    return id;
  }

  private parsePartDef(parent: string): string {
    this.expect('KEYWORD', 'part');
    this.expect('KEYWORD', 'def');
    const name = this.expect('IDENTIFIER').value;
    const id = this.generateId();

    const partDef: PartDef = {
      type: 'part_def',
      name,
      id,
      parent,
      children: [],
      ports: [],
      parts: [],
      metadata: {},
    };

    if (this.match('LBRACE')) {
      this.parsePartDefBody(id, partDef);
      this.expect('RBRACE');
    } else {
      this.match('SEMICOLON');
    }

    this.model.elements.set(id, partDef);
    return id;
  }

  private parsePartDefBody(parentId: string, partDef: PartDef): void {
    while (!this.check('RBRACE') && !this.check('EOF')) {
      if (this.check('KEYWORD', 'port')) {
        const portId = this.parsePort(parentId);
        partDef.ports.push(portId);
        partDef.children.push(portId);
      } else if (this.check('KEYWORD', 'part')) {
        const childPartId = this.parsePart(parentId);
        partDef.parts.push(childPartId);
        partDef.children.push(childPartId);
      } else if (this.check('KEYWORD', 'state') && this.lookAhead('KEYWORD', 'def')) {
        const stateDefId = this.parseStateDef(parentId);
        partDef.children.push(stateDefId);
      } else if (this.check('KEYWORD', 'interface')) {
        const connId = this.parseConnection(parentId);
        if (connId) partDef.children.push(connId);
      } else if (this.check('KEYWORD', 'bind')) {
        const bindId = this.parseBind(parentId);
        partDef.children.push(bindId);
      } else {
        this.advance();
      }
    }
  }

  private parsePort(parent: string): string {
    this.expect('KEYWORD', 'port');
    const name = this.expect('IDENTIFIER').value;
    const id = this.generateId();

    let defRef: string | undefined;
    if (this.match('COLON')) {
      defRef = this.expect('IDENTIFIER').value;
    }

    const port: Port = {
      type: 'port',
      name,
      id,
      parent,
      children: [],
      defRef,
      metadata: {},
    };

    this.match('SEMICOLON');
    this.model.elements.set(id, port);
    return id;
  }

  private parsePart(parent: string): string {
    this.expect('KEYWORD', 'part');
    const name = this.expect('IDENTIFIER').value;
    const id = this.generateId();

    let defRef: string | undefined;
    let multiplicity: string | undefined;

    if (this.match('COLON')) {
      defRef = this.expect('IDENTIFIER').value;
      if (this.match('LBRACKET')) {
        multiplicity = this.expect('NUMBER').value;
        this.expect('RBRACKET');
      }
    }

    const part: Part = {
      type: 'part',
      name,
      id,
      parent,
      children: [],
      defRef,
      multiplicity,
      metadata: {},
    };

    this.match('SEMICOLON');
    this.model.elements.set(id, part);
    return id;
  }

  private parseRequirementDef(parent: string): string {
    this.expect('KEYWORD', 'requirement');
    this.expect('KEYWORD', 'def');
    const name = this.expect('IDENTIFIER').value;
    const id = this.generateId();

    const req: RequirementDef = {
      type: 'requirement_def',
      name,
      id,
      parent,
      children: [],
      metadata: {},
    };

    if (this.match('LBRACE')) {
      while (!this.check('RBRACE') && !this.check('EOF')) {
        if (this.check('KEYWORD', 'id')) {
          this.advance();
          this.expect('EQUALS');
          req.reqId = this.expect('STRING').value;
          this.match('SEMICOLON');
        } else if (this.check('KEYWORD', 'text')) {
          this.advance();
          this.expect('EQUALS');
          req.text = this.expect('STRING').value;
          this.match('SEMICOLON');
        } else {
          this.advance();
        }
      }
      this.expect('RBRACE');
    }

    this.model.elements.set(id, req);
    return id;
  }

  private parseStateDef(parent: string): string {
    this.expect('KEYWORD', 'state');
    this.expect('KEYWORD', 'def');
    const name = this.expect('IDENTIFIER').value;
    const id = this.generateId();

    const stateDef: StateDef = {
      type: 'state_def',
      name,
      id,
      parent,
      children: [],
      states: [],
      transitions: [],
      metadata: {},
    };

    if (this.match('LBRACE')) {
      this.parseStateDefBody(id, stateDef);
      this.expect('RBRACE');
    }

    this.model.elements.set(id, stateDef);
    return id;
  }

  private parseStateDefBody(parentId: string, stateDef: StateDef): void {
    while (!this.check('RBRACE') && !this.check('EOF')) {
      if (this.check('KEYWORD', 'state')) {
        const stateId = this.parseState(parentId);
        stateDef.states.push(stateId);
        stateDef.children.push(stateId);
      } else if (this.check('KEYWORD', 'transition')) {
        const transId = this.parseTransition(parentId);
        stateDef.transitions.push(transId);
        stateDef.children.push(transId);
      } else if (this.check('KEYWORD', 'entry')) {
        // Handle entry; then STATE pattern
        this.advance();
        this.match('SEMICOLON');
        if (this.match('KEYWORD', 'then')) {
          this.expect('IDENTIFIER'); // Initial state name
          this.match('SEMICOLON');
        }
      } else {
        this.advance();
      }
    }
  }

  private parseState(parent: string): string {
    this.expect('KEYWORD', 'state');
    const name = this.expect('IDENTIFIER').value;
    const id = this.generateId();

    const state: State = {
      type: 'state',
      name,
      id,
      parent,
      children: [],
      metadata: {},
    };

    if (this.match('LBRACE')) {
      while (!this.check('RBRACE') && !this.check('EOF')) {
        if (this.check('KEYWORD', 'entry')) {
          this.advance();
          if (this.match('KEYWORD', 'action')) {
            state.entryAction = this.expect('IDENTIFIER').value;
            if (this.match('LBRACE')) {
              while (!this.check('RBRACE')) this.advance();
              this.expect('RBRACE');
            }
          }
        } else {
          this.advance();
        }
      }
      this.expect('RBRACE');
    }

    this.model.elements.set(id, state);
    return id;
  }

  private parseTransition(parent: string): string {
    this.expect('KEYWORD', 'transition');
    const name = this.expect('IDENTIFIER').value;
    const id = this.generateId();

    let source = '';
    let target = '';
    let trigger: string | undefined;

    while (!this.check('SEMICOLON') && !this.check('RBRACE') && !this.check('EOF')) {
      if (this.match('KEYWORD', 'first')) {
        source = this.expect('IDENTIFIER').value;
      } else if (this.match('KEYWORD', 'accept')) {
        trigger = this.expect('IDENTIFIER').value;
      } else if (this.match('KEYWORD', 'then')) {
        target = this.expect('IDENTIFIER').value;
      } else {
        this.advance();
      }
    }
    this.match('SEMICOLON');

    const transition: Transition = {
      type: 'transition',
      name,
      id,
      parent,
      children: [],
      source,
      target,
      trigger,
      metadata: {},
    };

    this.model.elements.set(id, transition);
    return id;
  }

  private parseConnection(parent: string): string | null {
    this.expect('KEYWORD', 'interface');
    if (!this.match('KEYWORD', 'connect')) {
      // Skip non-connect interface statements
      while (!this.check('SEMICOLON') && !this.check('RBRACE') && !this.check('EOF')) {
        this.advance();
      }
      this.match('SEMICOLON');
      return null;
    }

    this.expect('LPAREN');
    const source = this.parseQualifiedName();
    this.expect('COMMA');
    const target = this.parseQualifiedName();
    this.expect('RPAREN');
    this.match('SEMICOLON');

    const id = this.generateId();
    const conn: Connection = {
      type: 'connection',
      name: `${source}->${target}`,
      id,
      parent,
      children: [],
      source,
      target,
      metadata: {},
    };

    this.model.elements.set(id, conn);
    return id;
  }

  private parseBind(parent: string): string {
    this.expect('KEYWORD', 'bind');
    const source = this.parseQualifiedName();
    this.expect('EQUALS');
    const target = this.parseQualifiedName();
    this.match('SEMICOLON');

    const id = this.generateId();
    const bind: Bind = {
      type: 'bind',
      name: `${source}=${target}`,
      id,
      parent,
      children: [],
      source,
      target,
      metadata: {},
    };

    this.model.elements.set(id, bind);
    return id;
  }

  private parseQualifiedName(): string {
    let name = this.expect('IDENTIFIER').value;
    while (this.match('DOT')) {
      name += '.' + this.expect('IDENTIFIER').value;
    }
    return name;
  }
}

export function parseSysML(source: string): SysMLModel {
  const parser = new SysMLParser();
  return parser.parse(source);
}
