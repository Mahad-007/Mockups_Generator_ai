"use client";

import { useState, useEffect } from "react";
import { Palette, Plus, Check, X, ChevronDown, Sparkles } from "lucide-react";
import Link from "next/link";
import { brandsApi, Brand } from "@/lib/api";

interface BrandSelectorProps {
  selectedBrandId: string | null;
  onSelect: (brandId: string | null) => void;
}

export default function BrandSelector({
  selectedBrandId,
  onSelect,
}: BrandSelectorProps) {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [loading, setLoading] = useState(true);
  const [isOpen, setIsOpen] = useState(false);
  const [selectedBrand, setSelectedBrand] = useState<Brand | null>(null);

  useEffect(() => {
    loadBrands();
  }, []);

  useEffect(() => {
    if (selectedBrandId && brands.length > 0) {
      const brand = brands.find((b) => b.id === selectedBrandId);
      setSelectedBrand(brand || null);
    } else {
      setSelectedBrand(null);
    }
  }, [selectedBrandId, brands]);

  const loadBrands = async () => {
    try {
      const data = await brandsApi.list();
      setBrands(data);
      
      // Auto-select default brand
      const defaultBrand = data.find((b) => b.is_default);
      if (defaultBrand && !selectedBrandId) {
        onSelect(defaultBrand.id);
      }
    } catch (error) {
      console.error("Failed to load brands:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (brand: Brand | null) => {
    setSelectedBrand(brand);
    onSelect(brand?.id || null);
    setIsOpen(false);
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg border p-4 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-32 mb-2"></div>
        <div className="h-10 bg-gray-200 rounded"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Palette className="w-5 h-5 text-violet-600" />
          <span className="font-medium text-gray-900">Brand Styling</span>
        </div>
        {brands.length > 0 && (
          <Link
            href="/brands"
            className="text-sm text-violet-600 hover:text-violet-700"
          >
            Manage Brands
          </Link>
        )}
      </div>

      {brands.length === 0 ? (
        <div className="text-center py-4">
          <Palette className="w-8 h-8 text-gray-300 mx-auto mb-2" />
          <p className="text-sm text-gray-500 mb-3">
            No brands created yet
          </p>
          <Link
            href="/brands"
            className="inline-flex items-center gap-1 text-sm text-violet-600 hover:text-violet-700"
          >
            <Plus className="w-4 h-4" />
            Create a Brand
          </Link>
        </div>
      ) : (
        <div className="relative">
          <button
            onClick={() => setIsOpen(!isOpen)}
            className={`w-full flex items-center justify-between px-3 py-2 border rounded-lg transition ${
              isOpen
                ? "border-violet-500 ring-2 ring-violet-200"
                : "border-gray-200 hover:border-gray-300"
            }`}
          >
            {selectedBrand ? (
              <div className="flex items-center gap-3">
                {/* Brand Color Indicator */}
                <div className="flex -space-x-1">
                  {[
                    selectedBrand.primary_color,
                    selectedBrand.secondary_color,
                    selectedBrand.accent_color,
                  ]
                    .filter(Boolean)
                    .slice(0, 3)
                    .map((color, i) => (
                      <div
                        key={i}
                        className="w-5 h-5 rounded-full border-2 border-white"
                        style={{ backgroundColor: color! }}
                      />
                    ))}
                </div>
                <div className="text-left">
                  <p className="font-medium text-sm">{selectedBrand.name}</p>
                  {selectedBrand.mood && (
                    <p className="text-xs text-gray-500 capitalize">
                      {selectedBrand.mood} • {selectedBrand.style || "default"}
                    </p>
                  )}
                </div>
              </div>
            ) : (
              <span className="text-gray-500">No brand selected</span>
            )}
            <ChevronDown
              className={`w-5 h-5 text-gray-400 transition-transform ${
                isOpen ? "rotate-180" : ""
              }`}
            />
          </button>

          {/* Dropdown */}
          {isOpen && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-white border rounded-lg shadow-lg z-10 max-h-60 overflow-y-auto">
              {/* No brand option */}
              <button
                onClick={() => handleSelect(null)}
                className={`w-full flex items-center justify-between px-3 py-2 hover:bg-gray-50 transition ${
                  !selectedBrand ? "bg-violet-50" : ""
                }`}
              >
                <span className="text-gray-500">No brand styling</span>
                {!selectedBrand && (
                  <Check className="w-4 h-4 text-violet-600" />
                )}
              </button>

              <div className="border-t" />

              {/* Brand options */}
              {brands.map((brand) => (
                <button
                  key={brand.id}
                  onClick={() => handleSelect(brand)}
                  className={`w-full flex items-center justify-between px-3 py-2 hover:bg-gray-50 transition ${
                    selectedBrand?.id === brand.id ? "bg-violet-50" : ""
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="flex -space-x-1">
                      {[
                        brand.primary_color,
                        brand.secondary_color,
                        brand.accent_color,
                      ]
                        .filter(Boolean)
                        .slice(0, 3)
                        .map((color, i) => (
                          <div
                            key={i}
                            className="w-5 h-5 rounded-full border-2 border-white shadow-sm"
                            style={{ backgroundColor: color! }}
                          />
                        ))}
                      {!brand.primary_color && (
                        <div className="w-5 h-5 rounded-full bg-gray-200" />
                      )}
                    </div>
                    <div className="text-left">
                      <p className="font-medium text-sm flex items-center gap-1">
                        {brand.name}
                        {brand.is_default && (
                          <span className="px-1.5 py-0.5 text-xs bg-violet-100 text-violet-700 rounded">
                            Default
                          </span>
                        )}
                      </p>
                      {brand.mood && (
                        <p className="text-xs text-gray-500 capitalize">
                          {brand.mood}
                        </p>
                      )}
                    </div>
                  </div>
                  {selectedBrand?.id === brand.id && (
                    <Check className="w-4 h-4 text-violet-600" />
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Selected Brand Preview */}
      {selectedBrand && (
        <div className="mt-3 p-3 bg-gradient-to-r from-violet-50 to-indigo-50 rounded-lg">
          <div className="flex items-center gap-2 text-sm text-violet-700 mb-2">
            <Sparkles className="w-4 h-4" />
            <span className="font-medium">Brand styling will be applied</span>
          </div>
          <div className="text-xs text-gray-600 space-y-1">
            {selectedBrand.mood && (
              <p>
                Mood: <span className="capitalize">{selectedBrand.mood}</span>
              </p>
            )}
            {selectedBrand.preferred_lighting && (
              <p>
                Lighting:{" "}
                <span className="capitalize">
                  {selectedBrand.preferred_lighting}
                </span>
              </p>
            )}
            {selectedBrand.primary_color && (
              <p>
                Colors will influence scene palette
              </p>
            )}
          </div>
          <button
            onClick={() => handleSelect(null)}
            className="mt-2 text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
          >
            <X className="w-3 h-3" />
            Remove brand styling
          </button>
        </div>
      )}
    </div>
  );
}


