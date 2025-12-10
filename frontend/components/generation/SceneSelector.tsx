"use client";

import { useState, useEffect } from "react";
import { Check, Loader2 } from "lucide-react";
import { scenesApi, SceneTemplate } from "@/lib/api";

interface SceneSelectorProps {
  selectedScene: string | null;
  onSelect: (sceneId: string) => void;
}

const CATEGORY_LABELS: Record<string, string> = {
  all: "All",
  studio: "Studio",
  lifestyle: "Lifestyle",
  outdoor: "Outdoor",
  "e-commerce": "E-commerce",
  premium: "Premium",
  seasonal: "Seasonal",
};

export default function SceneSelector({
  selectedScene,
  onSelect,
}: SceneSelectorProps) {
  const [activeCategory, setActiveCategory] = useState("all");
  const [templates, setTemplates] = useState<SceneTemplate[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [templatesRes, categoriesRes] = await Promise.all([
          scenesApi.getTemplates(),
          scenesApi.getCategories(),
        ]);
        setTemplates(templatesRes.templates);
        setCategories(["all", ...categoriesRes.categories]);
      } catch (err) {
        console.error("Failed to load scenes:", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  const filteredTemplates =
    activeCategory === "all"
      ? templates
      : templates.filter((t) => t.category === activeCategory);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
      </div>
    );
  }

  return (
    <div>
      {/* Category Tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {categories.map((category) => (
          <button
            key={category}
            onClick={() => setActiveCategory(category)}
            className={`px-4 py-2 rounded-full whitespace-nowrap transition ${
              activeCategory === category
                ? "bg-primary text-primary-foreground"
                : "bg-gray-100 hover:bg-gray-200"
            }`}
          >
            {CATEGORY_LABELS[category] || category}
          </button>
        ))}
      </div>

      {/* Scene Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {filteredTemplates.map((scene) => (
          <button
            key={scene.id}
            onClick={() => onSelect(scene.id)}
            className={`relative group rounded-xl overflow-hidden border-2 transition ${
              selectedScene === scene.id
                ? "border-primary ring-2 ring-primary/20"
                : "border-transparent hover:border-gray-300"
            }`}
          >
            <div className="aspect-square bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
              <span className="text-gray-500 text-sm text-center px-2">
                {scene.name}
              </span>
            </div>

            {/* Selected Check */}
            {selectedScene === scene.id && (
              <div className="absolute top-2 right-2 w-6 h-6 bg-primary text-white rounded-full flex items-center justify-center">
                <Check className="w-4 h-4" />
              </div>
            )}

            {/* Scene Name */}
            <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/60 to-transparent">
              <p className="text-white text-sm font-medium">{scene.name}</p>
              <p className="text-white/70 text-xs">{scene.category}</p>
            </div>
          </button>
        ))}
      </div>

      {filteredTemplates.length === 0 && (
        <p className="text-center text-gray-500 py-8">
          No scenes in this category
        </p>
      )}
    </div>
  );
}
