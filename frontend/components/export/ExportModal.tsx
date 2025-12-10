"use client";

import { useState, useEffect } from "react";
import {
  X,
  Download,
  Image as ImageIcon,
  Smartphone,
  ShoppingBag,
  Globe,
  Printer,
  Check,
  Loader2,
  Package,
} from "lucide-react";
import { exportApi, ExportPresetsResponse, ExportPreset } from "@/lib/api";

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  mockupId: string;
  mockupIds?: string[];
  mockupImageUrl: string;
}

type ExportFormat = "png" | "jpg" | "webp";
type ExportMode = "single" | "batch" | "multi-preset";

const categoryIcons: Record<string, React.ReactNode> = {
  social: <Smartphone className="w-4 h-4" />,
  ecommerce: <ShoppingBag className="w-4 h-4" />,
  website: <Globe className="w-4 h-4" />,
  print: <Printer className="w-4 h-4" />,
};

const categoryLabels: Record<string, string> = {
  social: "Social Media",
  ecommerce: "E-Commerce",
  website: "Website",
  print: "Print",
};

export default function ExportModal({
  isOpen,
  onClose,
  mockupId,
  mockupIds = [],
  mockupImageUrl,
}: ExportModalProps) {
  const [presetsData, setPresetsData] = useState<ExportPresetsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Export settings
  const [selectedPreset, setSelectedPreset] = useState<string | null>(null);
  const [selectedPresets, setSelectedPresets] = useState<string[]>([]);
  const [format, setFormat] = useState<ExportFormat>("png");
  const [quality, setQuality] = useState(95);
  const [exportMode, setExportMode] = useState<ExportMode>(
    mockupIds.length > 1 ? "batch" : "single"
  );
  const [activeCategory, setActiveCategory] = useState<string>("social");

  // Load presets on mount
  useEffect(() => {
    if (isOpen) {
      loadPresets();
    }
  }, [isOpen]);

  const loadPresets = async () => {
    try {
      setLoading(true);
      const data = await exportApi.getPresets();
      setPresetsData(data);
    } catch (err) {
      setError("Failed to load export presets");
    } finally {
      setLoading(false);
    }
  };

  const handlePresetToggle = (presetId: string) => {
    if (exportMode === "multi-preset") {
      setSelectedPresets((prev) =>
        prev.includes(presetId)
          ? prev.filter((p) => p !== presetId)
          : [...prev, presetId]
      );
    } else {
      setSelectedPreset(selectedPreset === presetId ? null : presetId);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    setError(null);

    try {
      let blob: Blob;
      let filename: string;

      if (exportMode === "multi-preset" && selectedPresets.length > 0) {
        // Export to multiple presets
        blob = await exportApi.exportMultiPreset({
          mockup_id: mockupId,
          preset_ids: selectedPresets,
        });
        filename = `mockup_all_formats.zip`;
      } else if (exportMode === "batch" && mockupIds.length > 1) {
        // Batch export
        blob = await exportApi.exportBatch({
          mockup_ids: mockupIds,
          preset_id: selectedPreset || undefined,
          format,
          quality,
        });
        filename = `mockups_batch.zip`;
      } else {
        // Single export
        blob = await exportApi.exportSingle({
          mockup_id: mockupId,
          preset_id: selectedPreset || undefined,
          format,
          quality,
        });
        const ext = format;
        filename = `mockup${selectedPreset ? `_${selectedPreset}` : ""}.${ext}`;
      }

      // Download the file
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      onClose();
    } catch (err) {
      setError("Export failed. Please try again.");
    } finally {
      setExporting(false);
    }
  };

  const getPresetDimensions = (preset: ExportPreset) => {
    return `${preset.width} x ${preset.height}`;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-background rounded-xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center gap-3">
            <Download className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-semibold">Export Mockup</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-muted rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-4">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <div className="space-y-6">
              {/* Preview */}
              <div className="flex gap-4">
                <div className="w-32 h-32 rounded-lg overflow-hidden bg-muted flex-shrink-0">
                  <img
                    src={mockupImageUrl}
                    alt="Mockup preview"
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium mb-2">Export Options</h3>
                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => setExportMode("single")}
                      className={`px-3 py-1.5 rounded-lg text-sm transition ${
                        exportMode === "single"
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted hover:bg-muted/80"
                      }`}
                    >
                      <ImageIcon className="w-4 h-4 inline mr-1.5" />
                      Single Export
                    </button>
                    <button
                      onClick={() => setExportMode("multi-preset")}
                      className={`px-3 py-1.5 rounded-lg text-sm transition ${
                        exportMode === "multi-preset"
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted hover:bg-muted/80"
                      }`}
                    >
                      <Package className="w-4 h-4 inline mr-1.5" />
                      All Sizes (ZIP)
                    </button>
                    {mockupIds.length > 1 && (
                      <button
                        onClick={() => setExportMode("batch")}
                        className={`px-3 py-1.5 rounded-lg text-sm transition ${
                          exportMode === "batch"
                            ? "bg-primary text-primary-foreground"
                            : "bg-muted hover:bg-muted/80"
                        }`}
                      >
                        <Package className="w-4 h-4 inline mr-1.5" />
                        Batch ({mockupIds.length})
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {/* Format & Quality */}
              {exportMode !== "multi-preset" && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Format
                    </label>
                    <div className="flex gap-2">
                      {(["png", "jpg", "webp"] as ExportFormat[]).map((f) => (
                        <button
                          key={f}
                          onClick={() => setFormat(f)}
                          className={`px-4 py-2 rounded-lg text-sm uppercase font-medium transition ${
                            format === f
                              ? "bg-primary text-primary-foreground"
                              : "bg-muted hover:bg-muted/80"
                          }`}
                        >
                          {f}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Quality: {quality}%
                    </label>
                    <input
                      type="range"
                      min="50"
                      max="100"
                      value={quality}
                      onChange={(e) => setQuality(Number(e.target.value))}
                      className="w-full"
                    />
                  </div>
                </div>
              )}

              {/* Preset Categories */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  {exportMode === "multi-preset"
                    ? "Select Sizes to Export"
                    : "Platform Preset (Optional)"}
                </label>

                {/* Category Tabs */}
                <div className="flex gap-2 mb-3 overflow-x-auto pb-2">
                  {presetsData &&
                    Object.keys(presetsData.categories).map((category) => (
                      <button
                        key={category}
                        onClick={() => setActiveCategory(category)}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm whitespace-nowrap transition ${
                          activeCategory === category
                            ? "bg-primary text-primary-foreground"
                            : "bg-muted hover:bg-muted/80"
                        }`}
                      >
                        {categoryIcons[category]}
                        {categoryLabels[category] || category}
                      </button>
                    ))}
                </div>

                {/* Preset Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {presetsData?.categories[activeCategory]?.map((preset) => {
                    const isSelected =
                      exportMode === "multi-preset"
                        ? selectedPresets.includes(preset.id)
                        : selectedPreset === preset.id;

                    return (
                      <button
                        key={preset.id}
                        onClick={() => handlePresetToggle(preset.id)}
                        className={`relative p-3 rounded-lg border text-left transition ${
                          isSelected
                            ? "border-primary bg-primary/5"
                            : "border-border hover:border-muted-foreground/50"
                        }`}
                      >
                        {isSelected && (
                          <div className="absolute top-2 right-2 w-5 h-5 bg-primary rounded-full flex items-center justify-center">
                            <Check className="w-3 h-3 text-primary-foreground" />
                          </div>
                        )}
                        <div className="font-medium text-sm">{preset.name}</div>
                        <div className="text-xs text-muted-foreground mt-1">
                          {getPresetDimensions(preset)}
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Error */}
              {error && (
                <div className="p-3 bg-destructive/10 text-destructive rounded-lg text-sm">
                  {error}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t p-4 flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            {exportMode === "multi-preset" && selectedPresets.length > 0 && (
              <span>{selectedPresets.length} sizes selected</span>
            )}
            {exportMode === "batch" && (
              <span>Exporting {mockupIds.length} mockups</span>
            )}
          </div>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg border hover:bg-muted transition"
            >
              Cancel
            </button>
            <button
              onClick={handleExport}
              disabled={
                exporting ||
                (exportMode === "multi-preset" && selectedPresets.length === 0)
              }
              className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {exporting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Exporting...
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  Export
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
