import { Upload, LayoutGrid, FileCode, ZoomIn, ZoomOut, Maximize } from 'lucide-react';
import { useModel } from '../model/ModelContext';

interface ToolbarProps {
  onLoadDemo: () => void;
  onFileSelect: (file: File) => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFitView: () => void;
}

export function Toolbar({ onLoadDemo, onFileSelect, onZoomIn, onZoomOut, onFitView }: ToolbarProps) {
  const { viewMode, setViewMode } = useModel();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileSelect(file);
    }
  };

  return (
    <div className="h-12 border-b bg-white flex items-center px-4 gap-2">
      <div className="flex items-center gap-2">
        <label className="flex items-center gap-1 px-3 py-1.5 bg-blue-500 text-white rounded hover:bg-blue-600 cursor-pointer text-sm">
          <Upload size={16} />
          Load File
          <input
            type="file"
            accept=".sysml"
            onChange={handleFileChange}
            className="hidden"
          />
        </label>

        <button
          onClick={onLoadDemo}
          className="flex items-center gap-1 px-3 py-1.5 bg-gray-100 rounded hover:bg-gray-200 text-sm"
        >
          <FileCode size={16} />
          Load Demo
        </button>
      </div>

      <div className="w-px h-6 bg-gray-200 mx-2" />

      <div className="flex items-center gap-1 bg-gray-100 rounded p-0.5">
        <button
          onClick={() => setViewMode('simplified')}
          className={`flex items-center gap-1 px-3 py-1 rounded text-sm ${
            viewMode === 'simplified' ? 'bg-white shadow' : 'hover:bg-gray-200'
          }`}
        >
          <LayoutGrid size={16} />
          Simplified
        </button>
        <button
          onClick={() => setViewMode('sysml')}
          className={`flex items-center gap-1 px-3 py-1 rounded text-sm ${
            viewMode === 'sysml' ? 'bg-white shadow' : 'hover:bg-gray-200'
          }`}
        >
          <FileCode size={16} />
          SysML
        </button>
      </div>

      <div className="w-px h-6 bg-gray-200 mx-2" />

      <div className="flex items-center gap-1">
        <button
          onClick={onZoomIn}
          className="p-1.5 hover:bg-gray-100 rounded"
          title="Zoom In"
        >
          <ZoomIn size={18} />
        </button>
        <button
          onClick={onZoomOut}
          className="p-1.5 hover:bg-gray-100 rounded"
          title="Zoom Out"
        >
          <ZoomOut size={18} />
        </button>
        <button
          onClick={onFitView}
          className="p-1.5 hover:bg-gray-100 rounded"
          title="Fit to View"
        >
          <Maximize size={18} />
        </button>
      </div>

      <div className="flex-1" />

      <div className="text-sm text-gray-500">
        SysML v2 Visualizer
      </div>
    </div>
  );
}
