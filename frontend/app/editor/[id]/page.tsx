'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { fabric } from 'fabric';
import { toast } from 'sonner';
import CanvasEditor from '@/components/editor/CanvasEditor';
import ToolBar from '@/components/editor/ToolBar';
import LayerPanel from '@/components/editor/LayerPanel';
import AdjustmentPanel from '@/components/editor/AdjustmentPanel';
import { useCanvasHistory } from '@/hooks/useCanvasHistory';
import { useAutoSave } from '@/hooks/useAutoSave';
import { mockupsApi } from '@/lib/api';

interface Mockup {
  id: string;
  image_url: string;
  canvas_data?: Record<string, unknown> | null;
}

export default function EditorPage() {
  const params = useParams();
  const router = useRouter();
  const mockupId = params.id as string;

  const [mockup, setMockup] = useState<Mockup | null>(null);
  const [loading, setLoading] = useState(true);
  const [canvas, setCanvas] = useState<fabric.Canvas | null>(null);
  const canvasRef = useRef<fabric.Canvas | null>(null);

  const { undo, redo, canUndo, canRedo, initHistory } = useCanvasHistory(canvas);

  // Load mockup data
  useEffect(() => {
    const loadMockup = async () => {
      try {
        const data = await mockupsApi.get(mockupId);
        setMockup({
          id: data.id,
          image_url: data.image_url,
          canvas_data: data.canvas_data,
        });

        // If there's saved canvas data, we'll load it after canvas is initialized
      } catch (error) {
        console.error('Failed to load mockup:', error);
        toast.error('Failed to load mockup');
        router.push('/dashboard');
      } finally {
        setLoading(false);
      }
    };

    loadMockup();
  }, [mockupId, router]);

  // Handle canvas changes
  const handleCanvasChange = useCallback((fabricCanvas: fabric.Canvas) => {
    canvasRef.current = fabricCanvas;
    setCanvas(fabricCanvas);
  }, []);

  // Initialize history when canvas is ready
  useEffect(() => {
    if (canvas) {
      const cleanup = initHistory();
      return cleanup;
    }
  }, [canvas, initHistory]);

  // Auto-save handler
  const handleAutoSave = useCallback(
    async (canvasData: string) => {
      try {
        const parsedData = JSON.parse(canvasData);
        await mockupsApi.update(mockupId, { canvas_data: parsedData });
      } catch (error) {
        console.error('Auto-save failed:', error);
      }
    },
    [mockupId]
  );

  // Use auto-save hook
  useAutoSave({
    canvas,
    mockupId,
    onSave: handleAutoSave,
    interval: 30000, // 30 seconds
  });

  // Manual save
  const handleSave = async () => {
    if (!canvas) return;

    try {
      const canvasData = canvas.toJSON();
      await mockupsApi.update(mockupId, { canvas_data: canvasData });

      // Export as image
      const dataURL = canvas.toDataURL({
        format: 'png',
        quality: 1,
      });

      // Create download link
      const link = document.createElement('a');
      link.download = `mockup-${mockupId}-edited.png`;
      link.href = dataURL;
      link.click();

      toast.success('Mockup saved and downloaded!');
    } catch (error) {
      console.error('Save failed:', error);
      toast.error('Failed to save mockup');
    }
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + Z for undo
      if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        undo();
      }

      // Ctrl/Cmd + Shift + Z or Ctrl/Cmd + Y for redo
      if (
        ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'z') ||
        ((e.ctrlKey || e.metaKey) && e.key === 'y')
      ) {
        e.preventDefault();
        redo();
      }

      // Delete key
      if (e.key === 'Delete' || e.key === 'Backspace') {
        if (!canvas) return;

        const activeObject = canvas.getActiveObject();
        if (activeObject && document.activeElement?.tagName !== 'INPUT') {
          e.preventDefault();
          canvas.remove(activeObject);
          canvas.renderAll();
        }
      }

      // Ctrl/Cmd + S for save
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        handleSave();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [canvas, undo, redo, handleSave]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading editor...</p>
        </div>
      </div>
    );
  }

  if (!mockup) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-gray-600">Mockup not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Toolbar */}
      <ToolBar
        canvas={canvas}
        onUndo={undo}
        onRedo={redo}
        onSave={handleSave}
        canUndo={canUndo}
        canRedo={canRedo}
      />

      {/* Main Editor Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel - Layers */}
        <div className="w-64 border-r bg-white overflow-y-auto">
          <LayerPanel canvas={canvas} />
        </div>

        {/* Center - Canvas */}
        <div className="flex-1 p-4">
          <CanvasEditor mockupUrl={mockup.image_url} onChange={handleCanvasChange} />
        </div>

        {/* Right Panel - Adjustments */}
        <div className="w-64 border-l bg-white overflow-y-auto p-4">
          <AdjustmentPanel canvas={canvas} />
        </div>
      </div>

      {/* Status Bar */}
      <div className="h-8 bg-gray-800 text-white text-xs flex items-center px-4">
        <span className="text-gray-400">
          Auto-save enabled • Mockup ID: {mockupId}
        </span>
      </div>
    </div>
  );
}
