"use client";

import { useEffect, useState, useMemo } from "react";
import { Flame, Info, Sparkles, ThumbsDown, ThumbsUp } from "lucide-react";
import { scenesApi, SceneSuggestion, ProductResponse, SceneSuggestionFeedback } from "@/lib/api";

interface SceneSuggestionsProps {
  product: ProductResponse | null;
  brandId: string | null;
  selectedScene: string | null;
  onSelect: (sceneId: string) => void;
}

type FeedbackState = Record<string, "helpful" | "not_helpful">;

export function SceneSuggestions({
  product,
  brandId,
  selectedScene,
  onSelect,
}: SceneSuggestionsProps) {
  const [suggestions, setSuggestions] = useState<SceneSuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<FeedbackState>({});

  const productCategoryLabel = useMemo(
    () => product?.category || "auto-detected",
    [product?.category]
  );

  useEffect(() => {
    let cancelled = false;

    async function loadSuggestions() {
      if (!product) return;
      setIsLoading(true);
      setError(null);

      try {
        const res = await scenesApi.getSuggestions({
          product_id: product.id,
          brand_id: brandId || undefined,
        });

        if (cancelled) return;
        setSuggestions(res.suggestions);

        // Pre-select top suggestion if none chosen yet
        if (!selectedScene && res.suggestions.length > 0) {
          onSelect(res.suggestions[0].template.id);
        }
      } catch (err) {
        if (!cancelled) {
          console.error("Failed to load scene suggestions", err);
          setError(err instanceof Error ? err.message : "Unable to load suggestions");
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    loadSuggestions();
    return () => {
      cancelled = true;
    };
  }, [product?.id, brandId]);

  const submitFeedback = async (scene: SceneSuggestion, helpful: boolean) => {
    if (!product) return;
    const key = `${scene.template.id}-${helpful ? "helpful" : "not_helpful"}`;

    setFeedback((prev) => ({ ...prev, [scene.template.id]: helpful ? "helpful" : "not_helpful" }));

    const payload: SceneSuggestionFeedback = {
      feedback_token: scene.feedback_token,
      scene_id: scene.template.id,
      helpful,
      product_id: product.id,
      brand_id: brandId || undefined,
    };

    try {
      await scenesApi.sendSuggestionFeedback(payload);
    } catch (err) {
      console.warn("Failed to submit feedback", err);
      // revert on failure
      setFeedback((prev) => {
        const next = { ...prev };
        delete next[scene.template.id];
        return next;
      });
    }

    return key;
  };

  if (!product) return null;

  return (
    <div className="mb-6">
      <div className="flex items-center gap-2 mb-3">
        <Sparkles className="w-5 h-5 text-primary" />
        <div>
          <p className="font-semibold">AI Scene Suggestions</p>
          <p className="text-sm text-gray-500">
            Based on your product {productCategoryLabel}
            {brandId ? " and brand styling" : ""}
          </p>
        </div>
      </div>

      <div className="bg-white border rounded-xl p-4">
        {error && (
          <div className="mb-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-3">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-36 rounded-lg bg-gradient-to-r from-gray-100 to-gray-200 animate-pulse"
              />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {suggestions.map((scene) => {
              const selected = scene.template.id === selectedScene;
              const topReason = scene.reasons[0]?.detail || "Great contextual fit";
              const feedbackState = feedback[scene.template.id];

              return (
                <div
                  key={scene.template.id}
                  className={`border rounded-lg p-4 h-full flex flex-col gap-3 transition ${
                    selected ? "border-primary shadow-sm" : "border-gray-200 hover:border-primary/50"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="font-semibold">{scene.template.name}</p>
                      <p className="text-xs uppercase text-gray-500">{scene.template.category}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      {scene.trending && (
                        <span className="flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-orange-100 text-orange-700">
                          <Flame className="w-3 h-3" />
                          Trending
                        </span>
                      )}
                      {scene.seasonal && (
                        <span className="text-xs px-2 py-1 rounded-full bg-blue-50 text-blue-700">
                          {scene.seasonal} pick
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary rounded-full"
                        style={{ width: `${Math.round(scene.relevance * 100)}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-600 w-10 text-right">
                      {Math.round(scene.relevance * 100)}%
                    </span>
                  </div>

                  <div className="flex items-start gap-2 text-sm text-gray-700">
                    <Info className="w-4 h-4 text-gray-400 mt-0.5" />
                    <div>
                      <p className="font-medium">Why this scene</p>
                      <p className="text-gray-600">{topReason}</p>
                      {scene.reasons.length > 1 && (
                        <ul className="mt-2 space-y-1 text-gray-600">
                          {scene.reasons.slice(1, 3).map((reason, idx) => (
                            <li key={idx} className="text-xs">
                              • {reason.detail}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2 mt-auto">
                    <button
                      onClick={() => onSelect(scene.template.id)}
                      className={`px-3 py-2 rounded-md text-sm font-medium transition ${
                        selected
                          ? "bg-primary text-white"
                          : "bg-gray-100 text-gray-800 hover:bg-gray-200"
                      }`}
                    >
                      {selected ? "Selected" : "Use this scene"}
                    </button>
                    <button
                      onClick={() => submitFeedback(scene, true)}
                      disabled={feedbackState === "helpful"}
                      className={`px-3 py-2 rounded-md text-xs border flex items-center gap-1 transition ${
                        feedbackState === "helpful"
                          ? "border-green-200 bg-green-50 text-green-700"
                          : "border-gray-200 text-gray-700 hover:border-green-300"
                      }`}
                    >
                      <ThumbsUp className="w-4 h-4" />
                      Helpful
                    </button>
                    <button
                      onClick={() => submitFeedback(scene, false)}
                      disabled={feedbackState === "not_helpful"}
                      className={`px-3 py-2 rounded-md text-xs border flex items-center gap-1 transition ${
                        feedbackState === "not_helpful"
                          ? "border-red-200 bg-red-50 text-red-700"
                          : "border-gray-200 text-gray-700 hover:border-red-300"
                      }`}
                    >
                      <ThumbsDown className="w-4 h-4" />
                      Not helpful
                    </button>
                  </div>
                </div>
              );
            })}

            {suggestions.length === 0 && (
              <div className="col-span-full text-center text-sm text-gray-500">
                No tailored suggestions yet. Try re-uploading the product.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

