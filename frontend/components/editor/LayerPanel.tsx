'use client';

import { useState, useEffect } from 'react';
import { fabric } from 'fabric';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Eye, EyeOff, Lock, Unlock, Trash2, ChevronUp, ChevronDown } from 'lucide-react';

interface LayerPanelProps {
  canvas: fabric.Canvas | null;
}

interface LayerInfo {
  id: string;
  name: string;
  type: string;
  visible: boolean;
  locked: boolean;
  object: fabric.Object;
}

export default function LayerPanel({ canvas }: LayerPanelProps) {
  const [layers, setLayers] = useState<LayerInfo[]>([]);
  const [selectedLayerId, setSelectedLayerId] = useState<string | null>(null);

  useEffect(() => {
    if (!canvas) return;

    const updateLayers = () => {
      const objects = canvas.getObjects();
      const layerList: LayerInfo[] = objects.map((obj, index) => ({
        id: `layer-${index}`,
        name: getLayerName(obj, index),
        type: obj.type || 'object',
        visible: obj.visible !== false,
        locked: obj.selectable === false,
        object: obj,
      })).reverse(); // Reverse to show top layers first

      setLayers(layerList);
    };

    updateLayers();

    canvas.on('object:added', updateLayers);
    canvas.on('object:removed', updateLayers);
    canvas.on('object:modified', updateLayers);
    canvas.on('selection:created', (e) => {
      const obj = e.selected?.[0];
      if (obj) {
        const index = canvas.getObjects().indexOf(obj);
        setSelectedLayerId(`layer-${index}`);
      }
    });
    canvas.on('selection:cleared', () => {
      setSelectedLayerId(null);
    });

    return () => {
      canvas.off('object:added', updateLayers);
      canvas.off('object:removed', updateLayers);
      canvas.off('object:modified', updateLayers);
    };
  }, [canvas]);

  const getLayerName = (obj: fabric.Object, index: number): string => {
    if (obj.type === 'i-text' || obj.type === 'text') {
      return `Text Layer ${index + 1}`;
    }
    if (obj.type === 'image') {
      return `Image Layer ${index + 1}`;
    }
    return `${obj.type?.charAt(0).toUpperCase()}${obj.type?.slice(1)} ${index + 1}`;
  };

  const selectLayer = (layer: LayerInfo) => {
    if (!canvas) return;
    canvas.setActiveObject(layer.object);
    canvas.renderAll();
  };

  const toggleVisibility = (layer: LayerInfo) => {
    if (!canvas) return;
    layer.object.set('visible', !layer.visible);
    canvas.renderAll();
  };

  const toggleLock = (layer: LayerInfo) => {
    if (!canvas) return;
    layer.object.set('selectable', layer.locked);
    layer.object.set('evented', layer.locked);
    canvas.renderAll();
  };

  const deleteLayer = (layer: LayerInfo) => {
    if (!canvas) return;
    canvas.remove(layer.object);
    canvas.renderAll();
  };

  const moveLayerUp = (layer: LayerInfo) => {
    if (!canvas) return;
    canvas.bringForward(layer.object);
    canvas.renderAll();
  };

  const moveLayerDown = (layer: LayerInfo) => {
    if (!canvas) return;
    canvas.sendBackwards(layer.object);
    canvas.renderAll();
  };

  return (
    <Card className="w-64 h-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm">Layers</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="space-y-1 max-h-[calc(100vh-200px)] overflow-y-auto">
          {layers.map((layer) => (
            <div
              key={layer.id}
              className={`flex items-center gap-2 px-3 py-2 hover:bg-gray-100 cursor-pointer ${
                selectedLayerId === layer.id ? 'bg-blue-50 border-l-2 border-blue-500' : ''
              }`}
              onClick={() => selectLayer(layer)}
            >
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate">{layer.name}</div>
                <div className="text-xs text-gray-500">{layer.type}</div>
              </div>

              <div className="flex items-center gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleVisibility(layer);
                  }}
                  title={layer.visible ? 'Hide' : 'Show'}
                >
                  {layer.visible ? (
                    <Eye className="w-3 h-3" />
                  ) : (
                    <EyeOff className="w-3 h-3 text-gray-400" />
                  )}
                </Button>

                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleLock(layer);
                  }}
                  title={layer.locked ? 'Unlock' : 'Lock'}
                >
                  {layer.locked ? (
                    <Lock className="w-3 h-3" />
                  ) : (
                    <Unlock className="w-3 h-3 text-gray-400" />
                  )}
                </Button>

                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                  onClick={(e) => {
                    e.stopPropagation();
                    moveLayerUp(layer);
                  }}
                  title="Move Up"
                >
                  <ChevronUp className="w-3 h-3" />
                </Button>

                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                  onClick={(e) => {
                    e.stopPropagation();
                    moveLayerDown(layer);
                  }}
                  title="Move Down"
                >
                  <ChevronDown className="w-3 h-3" />
                </Button>

                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 text-red-600 hover:text-red-700 hover:bg-red-50"
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteLayer(layer);
                  }}
                  title="Delete"
                >
                  <Trash2 className="w-3 h-3" />
                </Button>
              </div>
            </div>
          ))}

          {layers.length === 0 && (
            <div className="text-center text-gray-500 text-sm py-8">
              No layers yet
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
