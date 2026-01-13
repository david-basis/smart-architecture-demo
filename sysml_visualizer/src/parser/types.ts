// SysML v2 AST Types

export type ElementType =
  | 'package'
  | 'part_def'
  | 'part'
  | 'port_def'
  | 'port'
  | 'item_def'
  | 'item'
  | 'requirement_def'
  | 'requirement'
  | 'state_def'
  | 'state'
  | 'transition'
  | 'attribute'
  | 'connection'
  | 'bind';

export interface SysMLElement {
  type: ElementType;
  name: string;
  id: string;
  parent?: string;
  children: string[];
  metadata: Record<string, unknown>;
}

export interface Package extends SysMLElement {
  type: 'package';
}

export interface PartDef extends SysMLElement {
  type: 'part_def';
  ports: string[];
  parts: string[];
}

export interface Part extends SysMLElement {
  type: 'part';
  defRef?: string;  // Reference to part def
  multiplicity?: string;
}

export interface PortDef extends SysMLElement {
  type: 'port_def';
  items: string[];
  direction?: 'in' | 'out' | 'inout';
}

export interface Port extends SysMLElement {
  type: 'port';
  defRef?: string;  // Reference to port def
  direction?: 'in' | 'out' | 'inout';
}

export interface ItemDef extends SysMLElement {
  type: 'item_def';
}

export interface RequirementDef extends SysMLElement {
  type: 'requirement_def';
  reqId?: string;
  text?: string;
}

export interface StateDef extends SysMLElement {
  type: 'state_def';
  states: string[];
  transitions: string[];
}

export interface State extends SysMLElement {
  type: 'state';
  entryAction?: string;
}

export interface Transition extends SysMLElement {
  type: 'transition';
  source: string;
  target: string;
  trigger?: string;
}

export interface Connection extends SysMLElement {
  type: 'connection';
  source: string;
  target: string;
}

export interface Bind extends SysMLElement {
  type: 'bind';
  source: string;
  target: string;
}

export interface SysMLModel {
  elements: Map<string, SysMLElement>;
  rootPackage?: string;
}
