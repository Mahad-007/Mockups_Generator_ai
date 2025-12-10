"use client";

import { useState, useEffect, useMemo } from "react";
import {
  Check,
  Loader2,
  Search,
  Heart,
  Star,
  SlidersHorizontal,
  X,
} from "lucide-react";
import { scenesApi, SceneTemplate, CustomizationOptions } from "@/lib/api";
import { useFavorites } from "@/hooks/useFavorites";

interface SceneSelectorProps {
  selectedScene: string | null;
  onSelect: (sceneId: string, customization?: CustomizationOptions) => void;
}

const CATEGORY_LABELS: Record<string, string> = {
  all: "All",
  favorites: "Favorites",
  studio: "Studio",
  lifestyle: "Lifestyle",
  outdoor: "Outdoor",
  "e-commerce": "E-commerce",
  premium: "Premium",
  seasonal: "Seasonal",
  social: "Social",
};

export default function SceneSelector({
  selectedScene,
  onSelect,
}: SceneSelectorProps) {
  const [activeCategory, setActiveCategory] = useState("all");
  const [templates, setTemplates] = useState<SceneTemplate[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [categoryCounts, setCategoryCounts] = useState<Record<string, number>>({});
  const [tags, setTags] = useState<Array<{ name: string; count: number }>>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [showCustomization, setShowCustomization] = useState(false);
  const [customization, setCustomization] = useState<CustomizationOptions>({});

  const { favorites, toggleFavorite, isFavorite } = useFavorites();

  // Get selected template for customization panel
  const selectedTemplate = useMemo(
    () => templates.find((t) => t.id === selectedScene),
    [templates, selectedScene]
  );

  useEffect(() => {
    async function loadData() {
      try {
        const [templatesRes, categoriesRes, tagsRes] = await Promise.all([
          scenesApi.getTemplates(),
          scenesApi.getCategories(),
          scenesApi.getTags(),
        ]);
        setTemplates(templatesRes.templates);
        setCategories(["all", "favorites", ...categoriesRes.categories]);
        setCategoryCounts(categoriesRes.counts);
        setTags(tagsRes.tags);
      } catch (err) {
        console.error("Failed to load scenes:", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  // Filter templates based on category, search, and tags
  const filteredTemplates = useMemo(() => {
    let result = templates;

    // Category filter
    if (activeCategory === "favorites") {
      result = result.filter((t) => favorites.includes(t.id));
    } else if (activeCategory !== "all") {
      result = result.filter((t) => t.category === activeCategory);
    }

    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (t) =>
          t.name.toLowerCase().includes(query) ||
          t.description.toLowerCase().includes(query) ||
          t.tags.some((tag) => tag.includes(query))
      );
    }

    // Tag filter
    if (selectedTags.length > 0) {
      result = result.filter((t) =>
        selectedTags.some((tag) => t.tags.includes(tag))
      );
    }

    return result;
  }, [templates, activeCategory, searchQuery, selectedTags, favorites]);

  const handleSelect = (sceneId: string) => {
    onSelect(sceneId, Object.keys(customization).length > 0 ? customization : undefined);
  };

  const toggleTag = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  const clearFilters = () => {
    setSearchQuery("");
    setSelectedTags([]);
    setActiveCategory("all");
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search scenes..."
          className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
        />
        {(searchQuery || selectedTags.length > 0) && (
          <button
            onClick={clearFilters}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Category Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {categories.map((category) => (
          <button
            key={category}
            onClick={() => setActiveCategory(category)}
            className={`px-4 py-2 rounded-full whitespace-nowrap transition flex items-center gap-2 ${
              activeCategory === category
                ? "bg-primary text-primary-foreground"
                : "bg-gray-100 hover:bg-gray-200"
            }`}
          >
            {category === "favorites" && <Heart className="w-4 h-4" />}
            {CATEGORY_LABELS[category] || category}
            {category !== "all" && category !== "favorites" && categoryCounts[category] && (
              <span className="text-xs opacity-70">({categoryCounts[category]})</span>
            )}
            {category === "favorites" && (
              <span className="text-xs opacity-70">({favorites.length})</span>
            )}
          </button>
        ))}
      </div>

      {/* Tag Filters */}
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {tags.slice(0, 10).map((tag) => (
            <button
              key={tag.name}
              onClick={() => toggleTag(tag.name)}
              className={`px-3 py-1 text-xs rounded-full transition ${
                selectedTags.includes(tag.name)
                  ? "bg-primary text-white"
                  : "bg-gray-100 hover:bg-gray-200"
              }`}
            >
              {tag.name}
            </button>
          ))}
        </div>
      )}

      {/* Scene Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {filteredTemplates.map((scene) => (
          <div key={scene.id} className="relative group">
            <button
              onClick={() => handleSelect(scene.id)}
              className={`w-full relative rounded-xl overflow-hidden border-2 transition ${
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

              {/* Premium Badge */}
              {scene.is_premium && (
                <div className="absolute top-2 left-2 px-2 py-0.5 bg-yellow-400 text-yellow-900 text-xs rounded-full flex items-center gap-1">
                  <Star className="w-3 h-3" />
                  Premium
                </div>
              )}

              {/* Selected Check */}
              {selectedScene === scene.id && (
                <div className="absolute top-2 right-2 w-6 h-6 bg-primary text-white rounded-full flex items-center justify-center">
                  <Check className="w-4 h-4" />
                </div>
              )}

              {/* Scene Info */}
              <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/60 to-transparent">
                <p className="text-white text-sm font-medium">{scene.name}</p>
                <p className="text-white/70 text-xs">{scene.category}</p>
              </div>
            </button>

            {/* Favorite Button */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                toggleFavorite(scene.id);
              }}
              className={`absolute top-2 right-2 p-1.5 rounded-full transition z-10 ${
                selectedScene === scene.id ? "right-10" : ""
              } ${
                isFavorite(scene.id)
                  ? "bg-red-500 text-white"
                  : "bg-white/80 text-gray-600 opacity-0 group-hover:opacity-100"
              }`}
            >
              <Heart
                className={`w-4 h-4 ${isFavorite(scene.id) ? "fill-current" : ""}`}
              />
            </button>
          </div>
        ))}
      </div>

      {filteredTemplates.length === 0 && (
        <div className="text-center py-8">
          <p className="text-gray-500">
            {activeCategory === "favorites"
              ? "No favorites yet. Click the heart icon on scenes to add them!"
              : "No scenes match your filters"}
          </p>
          {(searchQuery || selectedTags.length > 0) && (
            <button
              onClick={clearFilters}
              className="mt-2 text-primary hover:underline"
            >
              Clear filters
            </button>
          )}
        </div>
      )}

      {/* Customization Panel */}
      {selectedTemplate && (
        <div className="mt-6 p-4 border rounded-xl bg-gray-50">
          <button
            onClick={() => setShowCustomization(!showCustomization)}
            className="flex items-center justify-between w-full"
          >
            <div className="flex items-center gap-2">
              <SlidersHorizontal className="w-5 h-5" />
              <span className="font-medium">Customize Scene</span>
            </div>
            <span className="text-sm text-gray-500">
              {showCustomization ? "Hide" : "Show"} options
            </span>
          </button>

          {showCustomization && (
            <div className="mt-4 grid grid-cols-2 gap-4">
              {/* Color Options */}
              {selectedTemplate.customization.colors.length > 0 && (
                <div>
                  <label className="block text-sm font-medium mb-2">Color</label>
                  <select
                    value={customization.color || ""}
                    onChange={(e) =>
                      setCustomization((prev) => ({
                        ...prev,
                        color: e.target.value || undefined,
                      }))
                    }
                    className="w-full p-2 border rounded-lg"
                  >
                    <option value="">Default</option>
                    {selectedTemplate.customization.colors.map((color) => (
                      <option key={color} value={color}>
                        {color}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Surface Options */}
              {selectedTemplate.customization.surfaces.length > 0 && (
                <div>
                  <label className="block text-sm font-medium mb-2">Surface</label>
                  <select
                    value={customization.surface || ""}
                    onChange={(e) =>
                      setCustomization((prev) => ({
                        ...prev,
                        surface: e.target.value || undefined,
                      }))
                    }
                    className="w-full p-2 border rounded-lg"
                  >
                    <option value="">Default</option>
                    {selectedTemplate.customization.surfaces.map((surface) => (
                      <option key={surface} value={surface}>
                        {surface}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Lighting Options */}
              {selectedTemplate.customization.lighting.length > 0 && (
                <div>
                  <label className="block text-sm font-medium mb-2">Lighting</label>
                  <select
                    value={customization.lighting || ""}
                    onChange={(e) =>
                      setCustomization((prev) => ({
                        ...prev,
                        lighting: e.target.value || undefined,
                      }))
                    }
                    className="w-full p-2 border rounded-lg"
                  >
                    <option value="">Default</option>
                    {selectedTemplate.customization.lighting.map((light) => (
                      <option key={light} value={light}>
                        {light}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Angle Options */}
              {selectedTemplate.customization.angles.length > 0 && (
                <div>
                  <label className="block text-sm font-medium mb-2">Angle</label>
                  <select
                    value={customization.angle || ""}
                    onChange={(e) =>
                      setCustomization((prev) => ({
                        ...prev,
                        angle: e.target.value || undefined,
                      }))
                    }
                    className="w-full p-2 border rounded-lg"
                  >
                    <option value="">Default</option>
                    {selectedTemplate.customization.angles.map((angle) => (
                      <option key={angle} value={angle}>
                        {angle}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
