'use client';

import { useState, useEffect } from 'react';
import { fabric } from 'fabric';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Button } from '@/components/ui/button';

interface AdjustmentPanelProps {
  canvas: fabric.Canvas | null;
}

interface Adjustments {
  brightness: number;
  contrast: number;
  saturation: number;
  blur: number;
  opacity: number;
}

export default function AdjustmentPanel({ canvas }: AdjustmentPanelProps) {
  const [adjustments, setAdjustments] = useState<Adjustments>({
    brightness: 0,
    contrast: 0,
    saturation: 0,
    blur: 0,
    opacity: 100,
  });
  const [activeObject, setActiveObject] = useState<fabric.Object | null>(null);

  useEffect(() => {
    if (!canvas) return;

    const handleSelection = () => {
      const obj = canvas.getActiveObject();
      setActiveObject(obj || null);

      if (obj && obj.type === 'image') {
        // Get existing filter values
        const filters = (obj as fabric.Image).filters || [];
        const brightness = filters.find((f: any) => f?.type === 'Brightness') as any;
        const contrast = filters.find((f: any) => f?.type === 'Contrast') as any;
        const saturation = filters.find((f: any) => f?.type === 'Saturation') as any;
        const blur = filters.find((f: any) => f?.type === 'Blur') as any;

        setAdjustments({
          brightness: brightness ? brightness.brightness * 100 : 0,
          contrast: contrast ? contrast.contrast * 100 : 0,
          saturation: saturation ? saturation.saturation * 100 : 0,
          blur: blur ? blur.blur * 10 : 0,
          opacity: (obj.opacity || 1) * 100,
        });
      } else {
        setAdjustments({
          brightness: 0,
          contrast: 0,
          saturation: 0,
          blur: 0,
          opacity: (obj?.opacity || 1) * 100,
        });
      }
    };

    canvas.on('selection:created', handleSelection);
    canvas.on('selection:updated', handleSelection);
    canvas.on('selection:cleared', () => {
      setActiveObject(null);
      setAdjustments({
        brightness: 0,
        contrast: 0,
        saturation: 0,
        blur: 0,
        opacity: 100,
      });
    });

    return () => {
      canvas.off('selection:created', handleSelection);
      canvas.off('selection:updated', handleSelection);
      canvas.off('selection:cleared');
    };
  }, [canvas]);

  const applyFilter = (filterType: string, value: number) => {
    if (!canvas || !activeObject) return;

    if (activeObject.type === 'image') {
      const img = activeObject as fabric.Image;
      let filters = (img.filters || []) as any[];

      // Remove existing filter of this type
      filters = filters.filter((f: any) => f?.type !== filterType);

      // Add new filter based on type
      switch (filterType) {
        case 'Brightness':
          if (value !== 0) {
            filters.push(new (fabric.Image.filters as any).Brightness({ brightness: value / 100 }));
          }
          break;
        case 'Contrast':
          if (value !== 0) {
            filters.push(new (fabric.Image.filters as any).Contrast({ contrast: value / 100 }));
          }
          break;
        case 'Saturation':
          if (value !== 0) {
            filters.push(new (fabric.Image.filters as any).Saturation({ saturation: value / 100 }));
          }
          break;
        case 'Blur':
          if (value !== 0) {
            filters.push(new (fabric.Image.filters as any).Blur({ blur: value / 10 }));
          }
          break;
      }

      img.filters = filters as any;
      img.applyFilters();
      canvas.renderAll();
    }
  };

  const handleBrightnessChange = (value: number[]) => {
    const newValue = value[0];
    setAdjustments((prev) => ({ ...prev, brightness: newValue }));
    applyFilter('Brightness', newValue);
  };

  const handleContrastChange = (value: number[]) => {
    const newValue = value[0];
    setAdjustments((prev) => ({ ...prev, contrast: newValue }));
    applyFilter('Contrast', newValue);
  };

  const handleSaturationChange = (value: number[]) => {
    const newValue = value[0];
    setAdjustments((prev) => ({ ...prev, saturation: newValue }));
    applyFilter('Saturation', newValue);
  };

  const handleBlurChange = (value: number[]) => {
    const newValue = value[0];
    setAdjustments((prev) => ({ ...prev, blur: newValue }));
    applyFilter('Blur', newValue);
  };

  const handleOpacityChange = (value: number[]) => {
    const newValue = value[0];
    setAdjustments((prev) => ({ ...prev, opacity: newValue }));

    if (activeObject && canvas) {
      activeObject.set('opacity', newValue / 100);
      canvas.renderAll();
    }
  };

  const resetAdjustments = () => {
    if (!canvas || !activeObject) return;

    if (activeObject.type === 'image') {
      const img = activeObject as fabric.Image;
      img.filters = [];
      img.applyFilters();
    }

    activeObject.set('opacity', 1);
    canvas.renderAll();

    setAdjustments({
      brightness: 0,
      contrast: 0,
      saturation: 0,
      blur: 0,
      opacity: 100,
    });
  };

  const isImage = activeObject?.type === 'image';

  return (
    <Card className="w-64">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm">Adjustments</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {!activeObject && (
          <div className="text-center text-gray-500 text-sm py-4">
            Select a layer to adjust
          </div>
        )}

        {activeObject && (
          <>
            {/* Opacity - works for all objects */}
            <div className="space-y-2">
              <div className="flex justify-between">
                <Label className="text-xs">Opacity</Label>
                <span className="text-xs text-gray-600">{adjustments.opacity}%</span>
              </div>
              <Slider
                value={[adjustments.opacity]}
                onValueChange={handleOpacityChange}
                min={0}
                max={100}
                step={1}
              />
            </div>

            {/* Image-specific adjustments */}
            {isImage && (
              <>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <Label className="text-xs">Brightness</Label>
                    <span className="text-xs text-gray-600">
                      {adjustments.brightness > 0 ? '+' : ''}
                      {adjustments.brightness}
                    </span>
                  </div>
                  <Slider
                    value={[adjustments.brightness]}
                    onValueChange={handleBrightnessChange}
                    min={-100}
                    max={100}
                    step={1}
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between">
                    <Label className="text-xs">Contrast</Label>
                    <span className="text-xs text-gray-600">
                      {adjustments.contrast > 0 ? '+' : ''}
                      {adjustments.contrast}
                    </span>
                  </div>
                  <Slider
                    value={[adjustments.contrast]}
                    onValueChange={handleContrastChange}
                    min={-100}
                    max={100}
                    step={1}
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between">
                    <Label className="text-xs">Saturation</Label>
                    <span className="text-xs text-gray-600">
                      {adjustments.saturation > 0 ? '+' : ''}
                      {adjustments.saturation}
                    </span>
                  </div>
                  <Slider
                    value={[adjustments.saturation]}
                    onValueChange={handleSaturationChange}
                    min={-100}
                    max={100}
                    step={1}
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between">
                    <Label className="text-xs">Blur</Label>
                    <span className="text-xs text-gray-600">{adjustments.blur}</span>
                  </div>
                  <Slider
                    value={[adjustments.blur]}
                    onValueChange={handleBlurChange}
                    min={0}
                    max={100}
                    step={1}
                  />
                </div>
              </>
            )}

            <Button
              variant="outline"
              size="sm"
              onClick={resetAdjustments}
              className="w-full"
            >
              Reset All
            </Button>
          </>
        )}
      </CardContent>
    </Card>
  );
}
