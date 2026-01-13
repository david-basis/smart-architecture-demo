import { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import { SysMLModel, SysMLElement, parseSysML } from '../parser';

interface ModelContextType {
  model: SysMLModel | null;
  selectedElement: string | null;
  viewMode: 'sysml' | 'simplified';
  loadModel: (source: string) => void;
  selectElement: (id: string | null) => void;
  setViewMode: (mode: 'sysml' | 'simplified') => void;
  getElement: (id: string) => SysMLElement | undefined;
  getChildren: (id: string) => SysMLElement[];
  getRootElements: () => SysMLElement[];
  getPartDefs: () => SysMLElement[];
  getConnections: () => SysMLElement[];
}

const ModelContext = createContext<ModelContextType | null>(null);

export function ModelProvider({ children }: { children: ReactNode }) {
  const [model, setModel] = useState<SysMLModel | null>(null);
  const [selectedElement, setSelectedElement] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'sysml' | 'simplified'>('simplified');

  const loadModel = useCallback((source: string) => {
    try {
      const parsed = parseSysML(source);
      setModel(parsed);
      setSelectedElement(null);
    } catch (error) {
      console.error('Failed to parse SysML:', error);
    }
  }, []);

  const selectElement = useCallback((id: string | null) => {
    setSelectedElement(id);
  }, []);

  const getElement = useCallback((id: string): SysMLElement | undefined => {
    return model?.elements.get(id);
  }, [model]);

  const getChildren = useCallback((id: string): SysMLElement[] => {
    const element = model?.elements.get(id);
    if (!element) return [];
    return element.children
      .map(childId => model?.elements.get(childId))
      .filter((e): e is SysMLElement => e !== undefined);
  }, [model]);

  const getRootElements = useCallback((): SysMLElement[] => {
    if (!model?.rootPackage) return [];
    return getChildren(model.rootPackage);
  }, [model, getChildren]);

  const getPartDefs = useCallback((): SysMLElement[] => {
    if (!model) return [];
    return Array.from(model.elements.values()).filter(e => e.type === 'part_def');
  }, [model]);

  const getConnections = useCallback((): SysMLElement[] => {
    if (!model) return [];
    return Array.from(model.elements.values()).filter(
      e => e.type === 'connection' || e.type === 'bind'
    );
  }, [model]);

  return (
    <ModelContext.Provider
      value={{
        model,
        selectedElement,
        viewMode,
        loadModel,
        selectElement,
        setViewMode,
        getElement,
        getChildren,
        getRootElements,
        getPartDefs,
        getConnections,
      }}
    >
      {children}
    </ModelContext.Provider>
  );
}

export function useModel() {
  const context = useContext(ModelContext);
  if (!context) {
    throw new Error('useModel must be used within a ModelProvider');
  }
  return context;
}
