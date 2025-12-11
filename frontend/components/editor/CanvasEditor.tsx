'use client';

import { useEffect, useRef, useState } from 'react';
import { fabric } from 'fabric';

interface CanvasEditorProps {
  mockupUrl: string;
  onSave?: (canvas: fabric.Canvas) => void;
  onChange?: (canvas: fabric.Canvas) => void;
}

export default function CanvasEditor({ mockupUrl, onSave, onChange }: CanvasEditorProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fabricCanvasRef = useRef<fabric.Canvas | null>(null);
  const [activeObject, setActiveObject] = useState<fabric.Object | null>(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    // Initialize Fabric canvas
    const canvas = new fabric.Canvas(canvasRef.current, {
      width: 800,
      height: 600,
      backgroundColor: '#f0f0f0',
      preserveObjectStacking: true,
    });

    fabricCanvasRef.current = canvas;

    // Load the mockup image
    fabric.Image.fromURL(
      mockupUrl,
      (img) => {
        if (!img) return;

        // Scale image to fit canvas
        const scale = Math.min(
          canvas.width! / (img.width || 1),
          canvas.height! / (img.height || 1)
        ) * 0.9;

        img.scale(scale);
        img.set({
          left: canvas.width! / 2,
          top: canvas.height! / 2,
          originX: 'center',
          originY: 'center',
          selectable: true,
        });

        canvas.add(img);
        canvas.renderAll();
      },
      { crossOrigin: 'anonymous' }
    );

    // Event listeners
    canvas.on('selection:created', (e) => {
      setActiveObject(e.selected?.[0] || null);
    });

    canvas.on('selection:updated', (e) => {
      setActiveObject(e.selected?.[0] || null);
    });

    canvas.on('selection:cleared', () => {
      setActiveObject(null);
    });

    canvas.on('object:modified', () => {
      onChange?.(canvas);
    });

    // Cleanup
    return () => {
      canvas.dispose();
    };
  }, [mockupUrl, onChange]);

  // Expose canvas instance
  useEffect(() => {
    if (fabricCanvasRef.current && onChange) {
      onChange(fabricCanvasRef.current);
    }
  }, [onChange]);

  return (
    <div className="flex items-center justify-center w-full h-full bg-gray-100 rounded-lg">
      <canvas ref={canvasRef} />
    </div>
  );
}
