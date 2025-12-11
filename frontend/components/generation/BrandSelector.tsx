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
      <div className="bg-card border-3 border-foreground p-6 animate-pulse shadow-brutal">
        <div className="h-6 bg-secondary w-32 mb-3"></div>
        <div className="h-12 bg-secondary border-3 border-foreground"></div>
      </div>
    );
  }

  return (
    <div className="bg-card border-3 border-foreground p-6 shadow-brutal">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Palette className="w-6 h-6 text-foreground" />
          <span className="font-black uppercase tracking-wide text-sm">Brand Styling</span>
        </div>
        {brands.length > 0 && (
          <Link
            href="/brands"
            className="text-xs font-bold uppercase tracking-wide px-3 py-1.5 bg-accent text-accent-foreground border-3 border-foreground shadow-brutal-sm hover:shadow-brutal hover:-translate-x-0.5 hover:-translate-y-0.5 transition-all"
          >
            Manage Brands
          </Link>
        )}
      </div>

      {brands.length === 0 ? (
        <div className="text-center py-8 px-4 bg-muted border-3 border-foreground">
          <Palette className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
          <p className="text-sm font-bold uppercase text-muted-foreground mb-4">
            No brands created yet
          </p>
          <Link
            href="/brands"
            className="inline-flex items-center gap-2 text-xs font-black uppercase tracking-wide px-4 py-2.5 bg-primary text-primary-foreground border-3 border-foreground shadow-brutal hover:shadow-brutal-lg hover:-translate-x-0.5 hover:-translate-y-0.5 transition-all"
          >
            <Plus className="w-4 h-4" />
            Create a Brand
          </Link>
        </div>
      ) : (
        <div className="relative">
          <button
            onClick={() => setIsOpen(!isOpen)}
            className={`w-full flex items-center justify-between px-4 py-3 border-3 border-foreground transition-all font-bold ${
              isOpen
                ? "bg-accent shadow-brutal-lg -translate-x-0.5 -translate-y-0.5"
                : "bg-background shadow-brutal hover:shadow-brutal-lg hover:-translate-x-0.5 hover:-translate-y-0.5"
            }`}
          >
            {selectedBrand ? (
              <div className="flex items-center gap-3">
                {/* Brand Color Indicator */}
                <div className="flex -space-x-1.5">
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
                        className="w-6 h-6 border-3 border-foreground shadow-brutal-sm"
                        style={{ backgroundColor: color! }}
                      />
                    ))}
                </div>
                <div className="text-left">
                  <p className="font-black uppercase text-sm tracking-wide">{selectedBrand.name}</p>
                  {selectedBrand.mood && (
                    <p className="text-xs text-muted-foreground font-bold uppercase">
                      {selectedBrand.mood} • {selectedBrand.style || "default"}
                    </p>
                  )}
                </div>
              </div>
            ) : (
              <span className="text-muted-foreground uppercase text-sm">No brand selected</span>
            )}
            <ChevronDown
              className={`w-5 h-5 text-foreground transition-transform ${
                isOpen ? "rotate-180" : ""
              }`}
            />
          </button>

          {/* Dropdown */}
          {isOpen && (
            <div className="absolute top-full left-0 right-0 mt-2 bg-background border-3 border-foreground shadow-brutal-lg z-10 max-h-60 overflow-y-auto">
              {/* No brand option */}
              <button
                onClick={() => handleSelect(null)}
                className={`w-full flex items-center justify-between px-4 py-3 hover:bg-muted transition-colors border-b-3 border-foreground ${
                  !selectedBrand ? "bg-accent" : "bg-background"
                }`}
              >
                <span className="text-muted-foreground font-bold uppercase text-xs">No brand styling</span>
                {!selectedBrand && (
                  <Check className="w-5 h-5 text-foreground stroke-[3]" />
                )}
              </button>

              {/* Brand options */}
              {brands.map((brand) => (
                <button
                  key={brand.id}
                  onClick={() => handleSelect(brand)}
                  className={`w-full flex items-center justify-between px-4 py-3 hover:bg-muted transition-colors border-b-3 border-foreground last:border-b-0 ${
                    selectedBrand?.id === brand.id ? "bg-accent" : "bg-background"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="flex -space-x-1.5">
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
                            className="w-6 h-6 border-3 border-foreground shadow-brutal-sm"
                            style={{ backgroundColor: color! }}
                          />
                        ))}
                      {!brand.primary_color && (
                        <div className="w-6 h-6 bg-secondary border-3 border-foreground" />
                      )}
                    </div>
                    <div className="text-left">
                      <p className="font-black uppercase text-xs tracking-wide flex items-center gap-2">
                        {brand.name}
                        {brand.is_default && (
                          <span className="px-2 py-0.5 text-[10px] bg-brutal-yellow border-2 border-foreground font-black uppercase">
                            Default
                          </span>
                        )}
                      </p>
                      {brand.mood && (
                        <p className="text-xs text-muted-foreground font-bold uppercase mt-0.5">
                          {brand.mood}
                        </p>
                      )}
                    </div>
                  </div>
                  {selectedBrand?.id === brand.id && (
                    <Check className="w-5 h-5 text-foreground stroke-[3]" />
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Selected Brand Preview */}
      {selectedBrand && (
        <div className="mt-4 p-4 bg-brutal-cyan/20 border-3 border-foreground shadow-brutal-sm">
          <div className="flex items-center gap-2 text-sm text-foreground mb-3">
            <Sparkles className="w-5 h-5" />
            <span className="font-black uppercase tracking-wide">Brand styling will be applied</span>
          </div>
          <div className="text-xs font-bold space-y-1.5">
            {selectedBrand.mood && (
              <p className="uppercase">
                Mood: <span className="capitalize font-black">{selectedBrand.mood}</span>
              </p>
            )}
            {selectedBrand.preferred_lighting && (
              <p className="uppercase">
                Lighting:{" "}
                <span className="capitalize font-black">
                  {selectedBrand.preferred_lighting}
                </span>
              </p>
            )}
            {selectedBrand.primary_color && (
              <p className="uppercase">
                Colors will influence scene palette
              </p>
            )}
          </div>
          <button
            onClick={() => handleSelect(null)}
            className="mt-3 text-xs font-bold uppercase text-foreground hover:text-destructive flex items-center gap-1.5 px-2 py-1 hover:bg-background transition-colors"
          >
            <X className="w-4 h-4" />
            Remove brand styling
          </button>
        </div>
      )}
    </div>
  );
}


