import { memo } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { SysMLElement, Port, Part } from '../../parser';

interface SysMLPartNodeData {
  element: SysMLElement;
  ports: SysMLElement[];
  parts: SysMLElement[];
  isSelected: boolean;
}

export const SysMLPartNode = memo(({ data }: NodeProps) => {
  const { element, ports, parts, isSelected } = data as unknown as SysMLPartNodeData;

  const leftPorts = ports.filter((_, i) => i % 2 === 0);
  const rightPorts = ports.filter((_, i) => i % 2 === 1);

  return (
    <div
      className={`bg-white border-2 rounded shadow-md min-w-[250px] ${
        isSelected ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-300'
      }`}
    >
      {/* Header with stereotype */}
      <div className="px-3 py-2 border-b bg-gray-50 rounded-t">
        <div className="text-xs text-gray-500 text-center">
          «part def»
        </div>
        <div className="font-bold text-center text-sm">
          {element.name}
        </div>
      </div>

      {/* Ports section */}
      {ports.length > 0 && (
        <div className="px-3 py-2 border-b">
          <div className="text-xs text-gray-500 uppercase mb-1">ports</div>
          <div className="space-y-1">
            {ports.slice(0, 6).map((port) => {
              const p = port as Port;
              return (
                <div key={p.id} className="flex items-center gap-1 text-xs">
                  <span className="w-2 h-2 rounded-full bg-green-400 border border-green-600" />
                  <span>{p.name}</span>
                  {p.defRef && (
                    <span className="text-gray-400">: {p.defRef}</span>
                  )}
                </div>
              );
            })}
            {ports.length > 6 && (
              <div className="text-xs text-gray-400">
                +{ports.length - 6} more...
              </div>
            )}
          </div>
        </div>
      )}

      {/* Parts section */}
      {parts.length > 0 && (
        <div className="px-3 py-2">
          <div className="text-xs text-gray-500 uppercase mb-1">parts</div>
          <div className="space-y-1">
            {parts.slice(0, 6).map((part) => {
              const pt = part as Part;
              return (
                <div key={pt.id} className="flex items-center gap-1 text-xs">
                  <span className="w-2 h-2 bg-blue-400 border border-blue-600" />
                  <span>{pt.name}</span>
                  {pt.defRef && (
                    <span className="text-gray-400">: {pt.defRef}</span>
                  )}
                  {pt.multiplicity && (
                    <span className="text-gray-400">[{pt.multiplicity}]</span>
                  )}
                </div>
              );
            })}
            {parts.length > 6 && (
              <div className="text-xs text-gray-400">
                +{parts.length - 6} more...
              </div>
            )}
          </div>
        </div>
      )}

      {/* Connection handles */}
      <Handle
        type="target"
        position={Position.Left}
        className="w-3 h-3 bg-blue-500"
      />
      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 bg-blue-500"
      />
    </div>
  );
});

SysMLPartNode.displayName = 'SysMLPartNode';
