import { useModel } from '../model/ModelContext';
import { PartDef, Port, RequirementDef, StateDef, State, Transition } from '../parser';

export function ElementDetails() {
  const { selectedElement, getElement, getChildren } = useModel();

  if (!selectedElement) {
    return (
      <div className="p-4 text-gray-500 text-sm">
        Select an element to view details
      </div>
    );
  }

  const element = getElement(selectedElement);
  if (!element) return null;

  const children = getChildren(selectedElement);

  return (
    <div className="h-full overflow-auto">
      <div className="p-2 border-b bg-gray-50 font-medium text-sm">
        Element Details
      </div>
      <div className="p-4 space-y-4">
        <div>
          <div className="text-xs text-gray-500 uppercase">Name</div>
          <div className="font-medium">{element.name}</div>
        </div>

        <div>
          <div className="text-xs text-gray-500 uppercase">Type</div>
          <div className="text-sm">{element.type.replace('_', ' ')}</div>
        </div>

        {element.type === 'part_def' && (
          <PartDefDetails element={element as PartDef} children={children} />
        )}

        {element.type === 'port' && (
          <PortDetails element={element as Port} />
        )}

        {element.type === 'requirement_def' && (
          <RequirementDetails element={element as RequirementDef} />
        )}

        {element.type === 'state_def' && (
          <StateDefDetails element={element as StateDef} children={children} />
        )}

        {element.type === 'state' && (
          <StateDetails element={element as State} />
        )}

        {element.type === 'transition' && (
          <TransitionDetails element={element as Transition} />
        )}
      </div>
    </div>
  );
}

function PartDefDetails({ element, children }: { element: PartDef; children: ReturnType<typeof useModel>['getChildren'] extends (id: string) => infer R ? R : never }) {
  const ports = children.filter(c => c.type === 'port');
  const parts = children.filter(c => c.type === 'part');

  return (
    <>
      {ports.length > 0 && (
        <div>
          <div className="text-xs text-gray-500 uppercase mb-1">Ports ({ports.length})</div>
          <div className="space-y-1">
            {ports.map(p => (
              <div key={p.id} className="text-sm bg-green-50 px-2 py-1 rounded">
                <span className="font-medium">{p.name}</span>
                {(p as Port).defRef && (
                  <span className="text-gray-500">: {(p as Port).defRef}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {parts.length > 0 && (
        <div>
          <div className="text-xs text-gray-500 uppercase mb-1">Parts ({parts.length})</div>
          <div className="space-y-1">
            {parts.map(p => (
              <div key={p.id} className="text-sm bg-blue-50 px-2 py-1 rounded">
                <span className="font-medium">{p.name}</span>
                {(p as any).defRef && (
                  <span className="text-gray-500">: {(p as any).defRef}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}

function PortDetails({ element }: { element: Port }) {
  return (
    <>
      {element.defRef && (
        <div>
          <div className="text-xs text-gray-500 uppercase">Port Type</div>
          <div className="text-sm">{element.defRef}</div>
        </div>
      )}
    </>
  );
}

function RequirementDetails({ element }: { element: RequirementDef }) {
  return (
    <>
      {element.reqId && (
        <div>
          <div className="text-xs text-gray-500 uppercase">ID</div>
          <div className="text-sm font-mono">{element.reqId}</div>
        </div>
      )}
      {element.text && (
        <div>
          <div className="text-xs text-gray-500 uppercase">Text</div>
          <div className="text-sm bg-purple-50 p-2 rounded">{element.text}</div>
        </div>
      )}
    </>
  );
}

function StateDefDetails({ element, children }: { element: StateDef; children: any[] }) {
  const states = children.filter(c => c.type === 'state');
  const transitions = children.filter(c => c.type === 'transition');

  return (
    <>
      {states.length > 0 && (
        <div>
          <div className="text-xs text-gray-500 uppercase mb-1">States ({states.length})</div>
          <div className="space-y-1">
            {states.map(s => (
              <div key={s.id} className="text-sm bg-orange-50 px-2 py-1 rounded">
                {s.name}
              </div>
            ))}
          </div>
        </div>
      )}

      {transitions.length > 0 && (
        <div>
          <div className="text-xs text-gray-500 uppercase mb-1">Transitions ({transitions.length})</div>
          <div className="space-y-1">
            {transitions.map(t => (
              <div key={t.id} className="text-sm bg-gray-50 px-2 py-1 rounded">
                {(t as Transition).source} → {(t as Transition).target}
                {(t as Transition).trigger && (
                  <span className="text-gray-500 ml-1">[{(t as Transition).trigger}]</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}

function StateDetails({ element }: { element: State }) {
  return (
    <>
      {element.entryAction && (
        <div>
          <div className="text-xs text-gray-500 uppercase">Entry Action</div>
          <div className="text-sm font-mono">{element.entryAction}</div>
        </div>
      )}
    </>
  );
}

function TransitionDetails({ element }: { element: Transition }) {
  return (
    <>
      <div>
        <div className="text-xs text-gray-500 uppercase">Source</div>
        <div className="text-sm">{element.source}</div>
      </div>
      <div>
        <div className="text-xs text-gray-500 uppercase">Target</div>
        <div className="text-sm">{element.target}</div>
      </div>
      {element.trigger && (
        <div>
          <div className="text-xs text-gray-500 uppercase">Trigger</div>
          <div className="text-sm">{element.trigger}</div>
        </div>
      )}
    </>
  );
}
