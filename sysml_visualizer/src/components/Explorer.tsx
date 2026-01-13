import { useState } from 'react';
import { ChevronRight, ChevronDown, Box, Circle, FileText, Workflow, Plug } from 'lucide-react';
import { useModel } from '../model/ModelContext';
import { SysMLElement } from '../parser';

interface TreeNodeProps {
  element: SysMLElement;
  depth: number;
}

function getIcon(type: string) {
  switch (type) {
    case 'package':
      return <Box size={14} />;
    case 'part_def':
    case 'part':
      return <Box size={14} className="text-blue-500" />;
    case 'port_def':
    case 'port':
      return <Circle size={14} className="text-green-500" />;
    case 'item_def':
      return <Circle size={14} className="text-gray-500" />;
    case 'requirement_def':
      return <FileText size={14} className="text-purple-500" />;
    case 'state_def':
    case 'state':
      return <Workflow size={14} className="text-orange-500" />;
    case 'connection':
    case 'bind':
      return <Plug size={14} className="text-cyan-500" />;
    default:
      return <Box size={14} />;
  }
}

function TreeNode({ element, depth }: TreeNodeProps) {
  const { selectedElement, selectElement, getChildren } = useModel();
  const [expanded, setExpanded] = useState(depth < 2);

  const children = getChildren(element.id);
  const hasChildren = children.length > 0;
  const isSelected = selectedElement === element.id;

  // Filter to show meaningful children
  const visibleChildren = children.filter(
    c => !['connection', 'bind', 'transition'].includes(c.type)
  );

  return (
    <div>
      <div
        className={`flex items-center gap-1 py-1 px-2 cursor-pointer hover:bg-gray-100 rounded ${
          isSelected ? 'bg-blue-100' : ''
        }`}
        style={{ paddingLeft: `${depth * 16 + 8}px` }}
        onClick={() => selectElement(element.id)}
      >
        {hasChildren ? (
          <button
            onClick={(e) => {
              e.stopPropagation();
              setExpanded(!expanded);
            }}
            className="p-0.5 hover:bg-gray-200 rounded"
          >
            {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          </button>
        ) : (
          <span className="w-5" />
        )}
        {getIcon(element.type)}
        <span className="text-sm truncate">
          {element.name}
          <span className="text-gray-400 text-xs ml-1">
            {element.type.replace('_', ' ')}
          </span>
        </span>
      </div>
      {expanded && visibleChildren.map(child => (
        <TreeNode key={child.id} element={child} depth={depth + 1} />
      ))}
    </div>
  );
}

export function Explorer() {
  const { model, getRootElements } = useModel();

  if (!model) {
    return (
      <div className="p-4 text-gray-500 text-sm">
        No model loaded. Drop a .sysml file or click "Load Demo".
      </div>
    );
  }

  const rootElements = getRootElements();

  return (
    <div className="h-full overflow-auto">
      <div className="p-2 border-b bg-gray-50 font-medium text-sm">
        Model Explorer
      </div>
      <div className="py-2">
        {model.rootPackage && (
          <TreeNode
            element={model.elements.get(model.rootPackage)!}
            depth={0}
          />
        )}
        {rootElements.length === 0 && !model.rootPackage && (
          <div className="p-4 text-gray-500 text-sm">Empty model</div>
        )}
      </div>
    </div>
  );
}
