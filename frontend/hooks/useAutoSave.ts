import { useEffect, useRef, useCallback } from 'react';
import { fabric } from 'fabric';

interface UseAutoSaveOptions {
  canvas: fabric.Canvas | null;
  mockupId: string;
  onSave: (data: string) => Promise<void>;
  interval?: number; // in milliseconds
}

export function useAutoSave({ canvas, mockupId, onSave, interval = 30000 }: UseAutoSaveOptions) {
  const lastSavedRef = useRef<string>('');
  const timeoutRef = useRef<NodeJS.Timeout>();
  const isSavingRef = useRef(false);

  const saveCanvas = useCallback(async () => {
    if (!canvas || isSavingRef.current) return;

    const currentState = JSON.stringify(canvas.toJSON());

    // Only save if state has changed
    if (currentState === lastSavedRef.current) return;

    try {
      isSavingRef.current = true;
      await onSave(currentState);
      lastSavedRef.current = currentState;
      console.log('Canvas auto-saved');
    } catch (error) {
      console.error('Auto-save failed:', error);
    } finally {
      isSavingRef.current = false;
    }
  }, [canvas, onSave]);

  const scheduleAutoSave = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      saveCanvas();
    }, interval);
  }, [saveCanvas, interval]);

  useEffect(() => {
    if (!canvas) return;

    // Save on modifications
    const handleModification = () => {
      scheduleAutoSave();
    };

    canvas.on('object:modified', handleModification);
    canvas.on('object:added', handleModification);
    canvas.on('object:removed', handleModification);

    return () => {
      canvas.off('object:modified', handleModification);
      canvas.off('object:added', handleModification);
      canvas.off('object:removed', handleModification);

      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [canvas, scheduleAutoSave]);

  // Save on unmount
  useEffect(() => {
    return () => {
      if (canvas) {
        saveCanvas();
      }
    };
  }, [canvas, saveCanvas]);

  return { saveCanvas };
}
