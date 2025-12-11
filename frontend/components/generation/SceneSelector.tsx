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
        <Loader2 className="w-8 h-8 animate-spin text-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="SEARCH SCENES..."
          className="w-full pl-12 pr-12 py-3 border-3 border-foreground bg-background font-bold uppercase tracking-wide text-sm shadow-brutal-sm focus:outline-none focus:shadow-brutal focus:-translate-x-0.5 focus:-translate-y-0.5 transition-all placeholder:text-muted-foreground placeholder:font-bold"
        />
        {(searchQuery || selectedTags.length > 0) && (
          <button
            onClick={clearFilters}
            className="absolute right-4 top-1/2 -translate-y-1/2 text-foreground hover:text-accent-foreground hover:bg-accent p-1 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Category Tabs */}
      <div className="flex gap-3 overflow-x-auto pb-2">
        {categories.map((category) => (
          <button
            key={category}
            onClick={() => setActiveCategory(category)}
            className={`px-5 py-2.5 whitespace-nowrap transition-all flex items-center gap-2 font-bold uppercase text-xs tracking-wide border-3 border-foreground ${
              activeCategory === category
                ? "bg-primary text-primary-foreground shadow-brutal"
                : "bg-secondary text-secondary-foreground shadow-brutal-sm hover:shadow-brutal hover:-translate-x-0.5 hover:-translate-y-0.5"
            }`}
          >
            {category === "favorites" && <Heart className="w-4 h-4" />}
            {CATEGORY_LABELS[category] || category}
            {category !== "all" && category !== "favorites" && categoryCounts[category] && (
              <span className="text-[10px] opacity-70">({categoryCounts[category]})</span>
            )}
            {category === "favorites" && (
              <span className="text-[10px] opacity-70">({favorites.length})</span>
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
              className={`px-3 py-1.5 text-xs font-bold uppercase tracking-wide border-3 border-foreground transition-all ${
                selectedTags.includes(tag.name)
                  ? "bg-accent text-accent-foreground shadow-brutal"
                  : "bg-background text-foreground shadow-brutal-sm hover:shadow-brutal hover:-translate-x-0.5 hover:-translate-y-0.5"
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
              className={`w-full relative overflow-hidden border-3 transition-all ${
                selectedScene === scene.id
                  ? "border-foreground shadow-brutal-lg -translate-x-0.5 -translate-y-0.5"
                  : "border-foreground shadow-brutal hover:shadow-brutal-lg hover:-translate-x-0.5 hover:-translate-y-0.5"
              }`}
            >
              <div className="aspect-square bg-gradient-to-br from-secondary to-muted flex items-center justify-center">
                <span className="text-foreground text-sm font-bold uppercase text-center px-2">
                  {scene.name}
                </span>
              </div>

              {/* Premium Badge */}
              {scene.is_premium && (
                <div className="absolute top-3 left-3 px-3 py-1 bg-brutal-yellow border-3 border-foreground text-foreground text-xs font-black uppercase flex items-center gap-1.5 shadow-brutal-sm">
                  <Star className="w-3 h-3 fill-current" />
                  Premium
                </div>
              )}

              {/* Selected Check */}
              {selectedScene === scene.id && (
                <div className="absolute top-3 right-3 w-8 h-8 bg-primary border-3 border-foreground text-primary-foreground flex items-center justify-center shadow-brutal-sm">
                  <Check className="w-5 h-5 stroke-[3]" />
                </div>
              )}

              {/* Scene Info */}
              <div className="absolute bottom-0 left-0 right-0 p-3 bg-black/80 border-t-3 border-foreground">
                <p className="text-white text-sm font-black uppercase">{scene.name}</p>
                <p className="text-white/80 text-xs font-bold uppercase">{scene.category}</p>
              </div>
            </button>

            {/* Favorite Button */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                toggleFavorite(scene.id);
              }}
              className={`absolute top-3 right-3 p-2 transition-all z-10 border-3 border-foreground shadow-brutal-sm ${
                selectedScene === scene.id ? "right-14" : ""
              } ${
                isFavorite(scene.id)
                  ? "bg-brutal-pink text-white"
                  : "bg-white text-foreground opacity-0 group-hover:opacity-100 hover:shadow-brutal hover:-translate-x-0.5 hover:-translate-y-0.5"
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
        <div className="text-center py-8 px-6 border-3 border-foreground bg-muted shadow-brutal">
          <p className="text-foreground font-bold uppercase tracking-wide">
            {activeCategory === "favorites"
              ? "No favorites yet. Click the heart icon on scenes to add them!"
              : "No scenes match your filters"}
          </p>
          {(searchQuery || selectedTags.length > 0) && (
            <button
              onClick={clearFilters}
              className="mt-4 px-4 py-2 bg-primary text-primary-foreground border-3 border-foreground shadow-brutal hover:shadow-brutal-lg hover:-translate-x-0.5 hover:-translate-y-0.5 font-bold uppercase text-xs transition-all"
            >
              Clear filters
            </button>
          )}
        </div>
      )}

      {/* Customization Panel */}
      {selectedTemplate && (
        <div className="mt-6 p-6 border-3 border-foreground bg-secondary shadow-brutal">
          <button
            onClick={() => setShowCustomization(!showCustomization)}
            className="flex items-center justify-between w-full"
          >
            <div className="flex items-center gap-3">
              <SlidersHorizontal className="w-5 h-5 text-foreground" />
              <span className="font-black uppercase tracking-wide text-sm">Customize Scene</span>
            </div>
            <span className="text-xs font-bold uppercase text-muted-foreground">
              {showCustomization ? "Hide" : "Show"} options
            </span>
          </button>

          {showCustomization && (
            <div className="mt-6 grid grid-cols-2 gap-4">
              {/* Color Options */}
              {selectedTemplate.customization.colors.length > 0 && (
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wide mb-2">Color</label>
                  <select
                    value={customization.color || ""}
                    onChange={(e) =>
                      setCustomization((prev) => ({
                        ...prev,
                        color: e.target.value || undefined,
                      }))
                    }
                    className="w-full p-3 border-3 border-foreground bg-background font-bold text-sm shadow-brutal-sm focus:outline-none focus:shadow-brutal focus:-translate-x-0.5 focus:-translate-y-0.5 transition-all"
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
                  <label className="block text-xs font-bold uppercase tracking-wide mb-2">Surface</label>
                  <select
                    value={customization.surface || ""}
                    onChange={(e) =>
                      setCustomization((prev) => ({
                        ...prev,
                        surface: e.target.value || undefined,
                      }))
                    }
                    className="w-full p-3 border-3 border-foreground bg-background font-bold text-sm shadow-brutal-sm focus:outline-none focus:shadow-brutal focus:-translate-x-0.5 focus:-translate-y-0.5 transition-all"
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
                  <label className="block text-xs font-bold uppercase tracking-wide mb-2">Lighting</label>
                  <select
                    value={customization.lighting || ""}
                    onChange={(e) =>
                      setCustomization((prev) => ({
                        ...prev,
                        lighting: e.target.value || undefined,
                      }))
                    }
                    className="w-full p-3 border-3 border-foreground bg-background font-bold text-sm shadow-brutal-sm focus:outline-none focus:shadow-brutal focus:-translate-x-0.5 focus:-translate-y-0.5 transition-all"
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
                  <label className="block text-xs font-bold uppercase tracking-wide mb-2">Angle</label>
                  <select
                    value={customization.angle || ""}
                    onChange={(e) =>
                      setCustomization((prev) => ({
                        ...prev,
                        angle: e.target.value || undefined,
                      }))
                    }
                    className="w-full p-3 border-3 border-foreground bg-background font-bold text-sm shadow-brutal-sm focus:outline-none focus:shadow-brutal focus:-translate-x-0.5 focus:-translate-y-0.5 transition-all"
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
