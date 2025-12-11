'use client';

import { fabric } from 'fabric';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import {
  MousePointer2,
  Type,
  Square,
  Circle,
  Trash2,
  RotateCcw,
  RotateCw,
  Download,
  ZoomIn,
  ZoomOut,
  Move,
} from 'lucide-react';

interface ToolBarProps {
  canvas: fabric.Canvas | null;
  onUndo?: () => void;
  onRedo?: () => void;
  onSave?: () => void;
  canUndo?: boolean;
  canRedo?: boolean;
}

export default function ToolBar({
  canvas,
  onUndo,
  onRedo,
  onSave,
  canUndo = false,
  canRedo = false,
}: ToolBarProps) {
  const addText = () => {
    if (!canvas) return;

    const text = new fabric.IText('Click to edit', {
      left: canvas.width! / 2,
      top: canvas.height! / 2,
      fontFamily: 'Arial',
      fontSize: 24,
      fill: '#000000',
      originX: 'center',
      originY: 'center',
    });

    canvas.add(text);
    canvas.setActiveObject(text);
    canvas.renderAll();
  };

  const addRectangle = () => {
    if (!canvas) return;

    const rect = new fabric.Rect({
      left: canvas.width! / 2,
      top: canvas.height! / 2,
      width: 100,
      height: 100,
      fill: '#3b82f6',
      originX: 'center',
      originY: 'center',
    });

    canvas.add(rect);
    canvas.setActiveObject(rect);
    canvas.renderAll();
  };

  const addCircle = () => {
    if (!canvas) return;

    const circle = new fabric.Circle({
      left: canvas.width! / 2,
      top: canvas.height! / 2,
      radius: 50,
      fill: '#10b981',
      originX: 'center',
      originY: 'center',
    });

    canvas.add(circle);
    canvas.setActiveObject(circle);
    canvas.renderAll();
  };

  const deleteSelected = () => {
    if (!canvas) return;

    const activeObject = canvas.getActiveObject();
    if (activeObject) {
      canvas.remove(activeObject);
      canvas.renderAll();
    }
  };

  const zoomIn = () => {
    if (!canvas) return;

    const zoom = canvas.getZoom();
    canvas.setZoom(Math.min(zoom * 1.1, 3));
    canvas.renderAll();
  };

  const zoomOut = () => {
    if (!canvas) return;

    const zoom = canvas.getZoom();
    canvas.setZoom(Math.max(zoom * 0.9, 0.5));
    canvas.renderAll();
  };

  const resetZoom = () => {
    if (!canvas) return;

    canvas.setZoom(1);
    canvas.viewportTransform = [1, 0, 0, 1, 0, 0];
    canvas.renderAll();
  };

  const enablePan = () => {
    if (!canvas) return;

    let isDragging = false;
    let lastPosX = 0;
    let lastPosY = 0;

    canvas.on('mouse:down', (opt) => {
      const evt = opt.e;
      if (evt.altKey === true) {
        isDragging = true;
        canvas.selection = false;
        lastPosX = evt.clientX;
        lastPosY = evt.clientY;
      }
    });

    canvas.on('mouse:move', (opt) => {
      if (isDragging) {
        const evt = opt.e;
        const vpt = canvas.viewportTransform;
        if (vpt) {
          vpt[4] += evt.clientX - lastPosX;
          vpt[5] += evt.clientY - lastPosY;
          canvas.requestRenderAll();
          lastPosX = evt.clientX;
          lastPosY = evt.clientY;
        }
      }
    });

    canvas.on('mouse:up', () => {
      isDragging = false;
      canvas.selection = true;
    });
  };

  return (
    <div className="flex items-center gap-3 p-4 bg-background border-b-3 border-foreground shadow-brutal-sm">
      {/* Selection Tools */}
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" title="Select (V)">
          <MousePointer2 className="w-5 h-5" />
        </Button>
        <Button variant="ghost" size="icon" title="Pan (Hold Alt)" onClick={enablePan}>
          <Move className="w-5 h-5" />
        </Button>
      </div>

      <Separator orientation="vertical" className="h-10" />

      {/* Add Elements */}
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" onClick={addText} title="Add Text (T)">
          <Type className="w-5 h-5" />
        </Button>
        <Button variant="ghost" size="icon" onClick={addRectangle} title="Add Rectangle (R)">
          <Square className="w-5 h-5" />
        </Button>
        <Button variant="ghost" size="icon" onClick={addCircle} title="Add Circle (C)">
          <Circle className="w-5 h-5" />
        </Button>
      </div>

      <Separator orientation="vertical" className="h-10" />

      {/* Actions */}
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={onUndo}
          disabled={!canUndo}
          title="Undo (Ctrl+Z)"
        >
          <RotateCcw className="w-5 h-5" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={onRedo}
          disabled={!canRedo}
          title="Redo (Ctrl+Y)"
        >
          <RotateCw className="w-5 h-5" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={deleteSelected}
          title="Delete (Del)"
        >
          <Trash2 className="w-5 h-5" />
        </Button>
      </div>

      <Separator orientation="vertical" className="h-10" />

      {/* Zoom Controls */}
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" onClick={zoomOut} title="Zoom Out (-)">
          <ZoomOut className="w-5 h-5" />
        </Button>
        <Button variant="ghost" size="icon" onClick={resetZoom} title="Reset Zoom (0)">
          <span className="text-xs font-black uppercase">100%</span>
        </Button>
        <Button variant="ghost" size="icon" onClick={zoomIn} title="Zoom In (+)">
          <ZoomIn className="w-5 h-5" />
        </Button>
      </div>

      <div className="flex-1" />

      {/* Save/Export */}
      <Button onClick={onSave} className="gap-2">
        <Download className="w-5 h-5" />
        Save Changes
      </Button>
    </div>
  );
}
