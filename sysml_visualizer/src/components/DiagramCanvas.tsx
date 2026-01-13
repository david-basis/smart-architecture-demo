import { useCallback, useEffect } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
} from '@xyflow/react';
import type { Node, Edge, ReactFlowInstance } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { useModel } from '../model/ModelContext';
import type { SysMLElement, PartDef, Connection } from '../parser';
import { SysMLPartNode } from '../views/sysml/SysMLPartNode';
import { SimplifiedPartNode } from '../views/simplified/SimplifiedPartNode';

const nodeTypes = {
  sysmlPart: SysMLPartNode,
  simplifiedPart: SimplifiedPartNode,
};

interface DiagramCanvasProps {
  flowInstance: ReactFlowInstance | null;
  setFlowInstance: (instance: ReactFlowInstance) => void;
}

export function DiagramCanvas({ setFlowInstance }: DiagramCanvasProps) {
  const { model, selectedElement, selectElement, viewMode, getElement, getPartDefs } = useModel();
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  // Generate nodes and edges from model
  useEffect(() => {
    if (!model) {
      setNodes([]);
      setEdges([]);
      return;
    }

    const partDefs = getPartDefs();
    const newNodes: Node[] = [];
    const newEdges: Edge[] = [];

    // Layout configuration
    const nodeWidth = viewMode === 'sysml' ? 280 : 200;
    const nodeHeight = viewMode === 'sysml' ? 200 : 120;
    const horizontalGap = 60;
    const verticalGap = 40;
    const cols = 4;

    // Create nodes for part definitions
    partDefs.forEach((partDef, index) => {
      const col = index % cols;
      const row = Math.floor(index / cols);
      const x = col * (nodeWidth + horizontalGap) + 50;
      const y = row * (nodeHeight + verticalGap) + 50;

      const pd = partDef as PartDef;
      const ports = pd.ports?.map(pid => getElement(pid)).filter((p): p is SysMLElement => !!p) || [];
      const parts = pd.parts?.map(pid => getElement(pid)).filter((p): p is SysMLElement => !!p) || [];

      newNodes.push({
        id: partDef.id,
        type: viewMode === 'sysml' ? 'sysmlPart' : 'simplifiedPart',
        position: { x, y },
        data: {
          element: partDef,
          ports,
          parts,
          isSelected: selectedElement === partDef.id,
        },
      });
    });

    // Create edges for connections within selected part or root
    const allElements = Array.from(model.elements.values());
    const connections = allElements.filter(
      (e): e is Connection => e.type === 'connection'
    );

    // For simplified view, create edges between related parts
    if (viewMode === 'simplified') {
      // Create edges based on connections
      connections.forEach((conn) => {
        // Parse connection source/target to find related part defs
        const sourceParts = conn.source.split('.');
        const targetParts = conn.target.split('.');

        // Find source and target nodes by name
        const sourceNode = newNodes.find(n => {
          const elem = n.data.element as SysMLElement;
          return sourceParts.some(sp => elem.name.toLowerCase().includes(sp.toLowerCase()));
        });
        const targetNode = newNodes.find(n => {
          const elem = n.data.element as SysMLElement;
          return targetParts.some(tp => elem.name.toLowerCase().includes(tp.toLowerCase()));
        });

        if (sourceNode && targetNode && sourceNode.id !== targetNode.id) {
          const edgeId = `edge-${conn.id}`;
          if (!newEdges.find(e => e.id === edgeId)) {
            newEdges.push({
              id: edgeId,
              source: sourceNode.id,
              target: targetNode.id,
              style: { stroke: '#64748b', strokeWidth: 2 },
              animated: true,
            });
          }
        }
      });
    }

    setNodes(newNodes);
    setEdges(newEdges);
  }, [model, viewMode, selectedElement, getPartDefs, getElement, setNodes, setEdges]);

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      selectElement(node.id);
    },
    [selectElement]
  );

  const onPaneClick = useCallback(() => {
    selectElement(null);
  }, [selectElement]);

  if (!model) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50 text-gray-500">
        <div className="text-center">
          <p className="text-lg mb-2">No model loaded</p>
          <p className="text-sm">Load a SysML file or click "Load Demo" to get started</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        onInit={setFlowInstance as any}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.1}
        maxZoom={2}
      >
        <Background color="#e2e8f0" gap={20} />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            if (node.data?.isSelected) return '#3b82f6';
            return '#94a3b8';
          }}
          maskColor="rgba(0, 0, 0, 0.1)"
        />
      </ReactFlow>
    </div>
  );
}
