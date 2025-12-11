import { useCallback, useRef, useState } from 'react';
import { fabric } from 'fabric';

export function useCanvasHistory(canvas: fabric.Canvas | null) {
  const [canUndo, setCanUndo] = useState(false);
  const [canRedo, setCanRedo] = useState(false);

  const historyRef = useRef<string[]>([]);
  const historyStepRef = useRef<number>(-1);

  const saveState = useCallback(() => {
    if (!canvas) return;

    const json = JSON.stringify(canvas.toJSON());

    // Remove any states after current step
    historyRef.current = historyRef.current.slice(0, historyStepRef.current + 1);

    // Add new state
    historyRef.current.push(json);
    historyStepRef.current++;

    // Limit history to 50 states
    if (historyRef.current.length > 50) {
      historyRef.current.shift();
      historyStepRef.current--;
    }

    setCanUndo(historyStepRef.current > 0);
    setCanRedo(false);
  }, [canvas]);

  const undo = useCallback(() => {
    if (!canvas || historyStepRef.current <= 0) return;

    historyStepRef.current--;

    const state = historyRef.current[historyStepRef.current];
    canvas.loadFromJSON(state, () => {
      canvas.renderAll();
      setCanUndo(historyStepRef.current > 0);
      setCanRedo(true);
    });
  }, [canvas]);

  const redo = useCallback(() => {
    if (!canvas || historyStepRef.current >= historyRef.current.length - 1) return;

    historyStepRef.current++;

    const state = historyRef.current[historyStepRef.current];
    canvas.loadFromJSON(state, () => {
      canvas.renderAll();
      setCanUndo(true);
      setCanRedo(historyStepRef.current < historyRef.current.length - 1);
    });
  }, [canvas]);

  const initHistory = useCallback(() => {
    if (!canvas) return;

    // Save initial state
    saveState();

    // Add event listeners for history tracking
    const events = [
      'object:added',
      'object:removed',
      'object:modified',
      'object:skewing',
    ];

    const handler = () => {
      saveState();
    };

    events.forEach((event) => {
      canvas.on(event, handler);
    });

    return () => {
      events.forEach((event) => {
        canvas.off(event, handler);
      });
    };
  }, [canvas, saveState]);

  return {
    undo,
    redo,
    canUndo,
    canRedo,
    saveState,
    initHistory,
  };
}
