import { memo } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { SysMLElement, Port, Part } from '../../parser';

interface SimplifiedPartNodeData {
  element: SysMLElement;
  ports: SysMLElement[];
  parts: SysMLElement[];
  isSelected: boolean;
}

// Color mapping for different part types
function getPartColor(name: string): { bg: string; border: string; text: string } {
  const nameLower = name.toLowerCase();

  if (nameLower.includes('meter')) {
    return { bg: 'bg-blue-100', border: 'border-blue-400', text: 'text-blue-700' };
  }
  if (nameLower.includes('relay') || nameLower.includes('switch')) {
    return { bg: 'bg-orange-100', border: 'border-orange-400', text: 'text-orange-700' };
  }
  if (nameLower.includes('power') || nameLower.includes('psu')) {
    return { bg: 'bg-yellow-100', border: 'border-yellow-400', text: 'text-yellow-700' };
  }
  if (nameLower.includes('surge') || nameLower.includes('spd')) {
    return { bg: 'bg-red-100', border: 'border-red-400', text: 'text-red-700' };
  }
  if (nameLower.includes('circuit')) {
    return { bg: 'bg-green-100', border: 'border-green-400', text: 'text-green-700' };
  }
  if (nameLower.includes('terminal') || nameLower.includes('busbar')) {
    return { bg: 'bg-gray-100', border: 'border-gray-400', text: 'text-gray-700' };
  }
  if (nameLower.includes('manager') || nameLower.includes('system')) {
    return { bg: 'bg-purple-100', border: 'border-purple-400', text: 'text-purple-700' };
  }
  if (nameLower.includes('backplane')) {
    return { bg: 'bg-cyan-100', border: 'border-cyan-400', text: 'text-cyan-700' };
  }

  return { bg: 'bg-slate-100', border: 'border-slate-400', text: 'text-slate-700' };
}

export const SimplifiedPartNode = memo(({ data }: NodeProps) => {
  const { element, ports, parts, isSelected } = data as unknown as SimplifiedPartNodeData;
  const colors = getPartColor(element.name);

  // Format name for display (split camelCase)
  const displayName = element.name
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, str => str.toUpperCase())
    .trim();

  return (
    <div
      className={`rounded-lg shadow-lg min-w-[160px] ${colors.bg} border-2 ${
        isSelected ? 'border-blue-500 ring-2 ring-blue-300' : colors.border
      }`}
    >
      {/* Main content */}
      <div className="px-4 py-3">
        <div className={`font-semibold text-center ${colors.text}`}>
          {displayName}
        </div>

        {/* Show port/part count as small badges */}
        <div className="flex justify-center gap-2 mt-2">
          {ports.length > 0 && (
            <span className="text-xs bg-white/60 px-2 py-0.5 rounded-full">
              {ports.length} ports
            </span>
          )}
          {parts.length > 0 && (
            <span className="text-xs bg-white/60 px-2 py-0.5 rounded-full">
              {parts.length} parts
            </span>
          )}
        </div>
      </div>

      {/* Ports as small circles on edges */}
      {ports.length > 0 && (
        <div className="absolute -left-2 top-1/2 transform -translate-y-1/2 flex flex-col gap-1">
          {ports.slice(0, 3).map((port, i) => (
            <div
              key={port.id}
              className="w-3 h-3 rounded-full bg-green-400 border-2 border-green-600"
              title={port.name}
            />
          ))}
        </div>
      )}

      {/* Connection handles */}
      <Handle
        type="target"
        position={Position.Left}
        className="w-2 h-2 bg-green-500 opacity-0"
      />
      <Handle
        type="source"
        position={Position.Right}
        className="w-2 h-2 bg-green-500 opacity-0"
      />
      <Handle
        type="target"
        position={Position.Top}
        id="top"
        className="w-2 h-2 bg-green-500 opacity-0"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="bottom"
        className="w-2 h-2 bg-green-500 opacity-0"
      />
    </div>
  );
});

SimplifiedPartNode.displayName = 'SimplifiedPartNode';
