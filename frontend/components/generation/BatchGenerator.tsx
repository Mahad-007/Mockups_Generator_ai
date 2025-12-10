"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Layers,
  Play,
  Loader2,
  CheckCircle,
  XCircle,
  RefreshCw,
  StopCircle,
  Download,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import {
  batchApi,
  BatchGenerateRequest,
  JobStatusResponse,
  MockupVariation,
} from "@/lib/api";

interface BatchGeneratorProps {
  productId: string;
  productImageUrl: string;
  onComplete?: (mockups: MockupVariation[]) => void;
}

type VariationPreset = "quick" | "standard" | "comprehensive";

const presetInfo: Record<
  VariationPreset,
  { name: string; description: string; count: string }
> = {
  quick: {
    name: "Quick",
    description: "2-3 variations, fast generation",
    count: "~3",
  },
  standard: {
    name: "Standard",
    description: "5-6 variations, balanced coverage",
    count: "~6",
  },
  comprehensive: {
    name: "Comprehensive",
    description: "10+ variations, full coverage",
    count: "~10",
  },
};

export default function BatchGenerator({
  productId,
  productImageUrl,
  onComplete,
}: BatchGeneratorProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [preset, setPreset] = useState<VariationPreset>("standard");
  const [maxVariations, setMaxVariations] = useState(6);
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatusResponse | null>(null);
  const [results, setResults] = useState<MockupVariation[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isStarting, setIsStarting] = useState(false);

  // Poll for job status
  useEffect(() => {
    if (!jobId) return;

    const pollInterval = setInterval(async () => {
      try {
        const status = await batchApi.getJobStatus(jobId);
        setJobStatus(status);

        // Check if job is complete
        if (status.status === "completed" || status.status === "failed") {
          clearInterval(pollInterval);

          if (status.status === "completed") {
            // Fetch results
            const resultsData = await batchApi.getResults(jobId);
            setResults(resultsData.mockups);
            onComplete?.(resultsData.mockups);
          }
        }
      } catch (err) {
        console.error("Failed to poll job status:", err);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }, [jobId, onComplete]);

  const handleStart = async () => {
    setIsStarting(true);
    setError(null);

    try {
      const request: BatchGenerateRequest = {
        product_id: productId,
        variation_preset: preset,
        max_variations: maxVariations,
      };

      const response = await batchApi.startGeneration(request);
      setJobId(response.job_id);
      setJobStatus({
        id: response.job_id,
        job_type: "batch_generation",
        status: "pending",
        total_items: response.total_variations,
        completed_items: 0,
        failed_items: 0,
        progress: 0,
        created_at: new Date().toISOString(),
        started_at: null,
        completed_at: null,
        error: null,
        results: [],
      });
    } catch (err: any) {
      setError(err.message || "Failed to start batch generation");
    } finally {
      setIsStarting(false);
    }
  };

  const handleCancel = async () => {
    if (!jobId) return;

    try {
      await batchApi.cancelJob(jobId);
      setJobStatus((prev) =>
        prev ? { ...prev, status: "cancelled" } : null
      );
    } catch (err) {
      console.error("Failed to cancel job:", err);
    }
  };

  const handleReset = () => {
    setJobId(null);
    setJobStatus(null);
    setResults([]);
    setError(null);
  };

  const isRunning =
    jobStatus?.status === "pending" || jobStatus?.status === "in_progress";
  const isComplete = jobStatus?.status === "completed";
  const isFailed =
    jobStatus?.status === "failed" || jobStatus?.status === "cancelled";

  return (
    <div className="border rounded-xl overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 hover:bg-muted/50 transition"
      >
        <div className="flex items-center gap-3">
          <Layers className="w-5 h-5 text-primary" />
          <div className="text-left">
            <h3 className="font-medium">Batch Generate Variations</h3>
            <p className="text-sm text-muted-foreground">
              Create multiple mockup variations automatically
            </p>
          </div>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-5 h-5 text-muted-foreground" />
        ) : (
          <ChevronDown className="w-5 h-5 text-muted-foreground" />
        )}
      </button>

      {/* Content */}
      {isExpanded && (
        <div className="border-t p-4 space-y-4">
          {!jobId ? (
            // Configuration
            <>
              {/* Preset Selection */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Generation Preset
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(Object.keys(presetInfo) as VariationPreset[]).map((p) => (
                    <button
                      key={p}
                      onClick={() => {
                        setPreset(p);
                        setMaxVariations(
                          p === "quick" ? 3 : p === "standard" ? 6 : 10
                        );
                      }}
                      className={`p-3 rounded-lg border text-left transition ${
                        preset === p
                          ? "border-primary bg-primary/5"
                          : "border-border hover:border-muted-foreground/50"
                      }`}
                    >
                      <div className="font-medium text-sm">
                        {presetInfo[p].name}
                      </div>
                      <div className="text-xs text-muted-foreground mt-0.5">
                        {presetInfo[p].description}
                      </div>
                      <div className="text-xs text-primary mt-1">
                        {presetInfo[p].count} variations
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Max Variations Slider */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Max Variations: {maxVariations}
                </label>
                <input
                  type="range"
                  min="2"
                  max="20"
                  value={maxVariations}
                  onChange={(e) => setMaxVariations(Number(e.target.value))}
                  className="w-full"
                />
              </div>

              {/* Error */}
              {error && (
                <div className="p-3 bg-destructive/10 text-destructive rounded-lg text-sm">
                  {error}
                </div>
              )}

              {/* Start Button */}
              <button
                onClick={handleStart}
                disabled={isStarting}
                className="w-full py-3 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isStarting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Starting...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    Generate {maxVariations} Variations
                  </>
                )}
              </button>
            </>
          ) : (
            // Progress & Results
            <>
              {/* Progress */}
              {jobStatus && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {isRunning && (
                        <Loader2 className="w-4 h-4 animate-spin text-primary" />
                      )}
                      {isComplete && (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      )}
                      {isFailed && (
                        <XCircle className="w-4 h-4 text-destructive" />
                      )}
                      <span className="font-medium capitalize">
                        {jobStatus.status.replace("_", " ")}
                      </span>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {jobStatus.completed_items} / {jobStatus.total_items}
                    </span>
                  </div>

                  {/* Progress Bar */}
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-500 ${
                        isFailed ? "bg-destructive" : "bg-primary"
                      }`}
                      style={{ width: `${jobStatus.progress}%` }}
                    />
                  </div>

                  {jobStatus.error && (
                    <p className="text-sm text-destructive">{jobStatus.error}</p>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2">
                    {isRunning && (
                      <button
                        onClick={handleCancel}
                        className="flex-1 py-2 border rounded-lg hover:bg-muted transition flex items-center justify-center gap-2"
                      >
                        <StopCircle className="w-4 h-4" />
                        Cancel
                      </button>
                    )}
                    {(isComplete || isFailed) && (
                      <button
                        onClick={handleReset}
                        className="flex-1 py-2 border rounded-lg hover:bg-muted transition flex items-center justify-center gap-2"
                      >
                        <RefreshCw className="w-4 h-4" />
                        Generate More
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* Results Grid */}
              {results.length > 0 && (
                <div className="space-y-3">
                  <h4 className="font-medium">Generated Variations</h4>
                  <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
                    {results.map((mockup, index) => (
                      <div
                        key={mockup.id}
                        className="relative aspect-square rounded-lg overflow-hidden bg-muted group"
                      >
                        <img
                          src={mockup.image_url}
                          alt={`Variation ${index + 1}`}
                          className="w-full h-full object-cover"
                        />
                        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition flex items-center justify-center">
                          <a
                            href={mockup.image_url}
                            download
                            className="p-2 bg-white rounded-full"
                          >
                            <Download className="w-4 h-4 text-black" />
                          </a>
                        </div>
                        <div className="absolute bottom-1 left-1 px-1.5 py-0.5 bg-black/60 rounded text-xs text-white">
                          #{index + 1}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
