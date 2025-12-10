"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  Sparkles,
  Plus,
  Trash2,
  Edit2,
  Star,
  Upload,
  Palette,
  Globe,
  Loader2,
  Check,
  X,
  ChevronRight,
  Wand2,
} from "lucide-react";
import { brandsApi, Brand, BrandCreate, BrandExtractResponse } from "@/lib/api";

// Mood and style options
const MOOD_OPTIONS = [
  { value: "professional", label: "Professional", emoji: "💼" },
  { value: "playful", label: "Playful", emoji: "🎨" },
  { value: "luxury", label: "Luxury", emoji: "✨" },
  { value: "minimal", label: "Minimal", emoji: "◻️" },
  { value: "bold", label: "Bold", emoji: "🔥" },
  { value: "elegant", label: "Elegant", emoji: "🌸" },
  { value: "casual", label: "Casual", emoji: "☀️" },
  { value: "tech", label: "Tech", emoji: "⚡" },
  { value: "organic", label: "Organic", emoji: "🌿" },
  { value: "vintage", label: "Vintage", emoji: "📻" },
];

const STYLE_OPTIONS = [
  { value: "modern", label: "Modern" },
  { value: "classic", label: "Classic" },
  { value: "minimalist", label: "Minimalist" },
  { value: "industrial", label: "Industrial" },
  { value: "bohemian", label: "Bohemian" },
  { value: "scandinavian", label: "Scandinavian" },
];

const INDUSTRY_OPTIONS = [
  { value: "tech", label: "Technology" },
  { value: "beauty", label: "Beauty & Cosmetics" },
  { value: "food", label: "Food & Beverage" },
  { value: "fashion", label: "Fashion & Apparel" },
  { value: "home", label: "Home & Living" },
  { value: "fitness", label: "Health & Fitness" },
  { value: "jewelry", label: "Jewelry & Accessories" },
  { value: "electronics", label: "Electronics" },
  { value: "lifestyle", label: "Lifestyle" },
  { value: "other", label: "Other" },
];

const LIGHTING_OPTIONS = [
  { value: "natural", label: "Natural Daylight" },
  { value: "soft", label: "Soft & Diffused" },
  { value: "dramatic", label: "Dramatic Shadows" },
  { value: "studio", label: "Studio Lighting" },
  { value: "bright", label: "Bright & Even" },
  { value: "warm", label: "Warm Golden Hour" },
];

export default function BrandsPage() {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingBrand, setEditingBrand] = useState<Brand | null>(null);

  const loadBrands = useCallback(async () => {
    try {
      setLoading(true);
      const data = await brandsApi.list();
      setBrands(data);
    } catch (error) {
      console.error("Failed to load brands:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadBrands();
  }, [loadBrands]);

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this brand?")) return;
    try {
      await brandsApi.delete(id);
      setBrands(brands.filter((b) => b.id !== id));
    } catch (error) {
      console.error("Failed to delete brand:", error);
    }
  };

  const handleSetDefault = async (id: string) => {
    try {
      await brandsApi.setDefault(id);
      setBrands(
        brands.map((b) => ({
          ...b,
          is_default: b.id === id,
        }))
      );
    } catch (error) {
      console.error("Failed to set default:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-violet-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-violet-600" />
            <span className="font-bold text-xl bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
              MockupAI
            </span>
          </Link>
          <nav className="flex items-center gap-4">
            <Link
              href="/generate"
              className="text-gray-600 hover:text-gray-900 transition"
            >
              Generate
            </Link>
            <Link
              href="/brands"
              className="text-violet-600 font-medium"
            >
              Brands
            </Link>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
              Brand DNA
            </h1>
            <p className="text-gray-600 mt-1">
              Create and manage your brand profiles for consistent mockup styling
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-violet-600 to-indigo-600 text-white rounded-lg hover:opacity-90 transition shadow-lg shadow-violet-200"
          >
            <Plus className="w-5 h-5" />
            Create Brand
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-violet-600" />
          </div>
        )}

        {/* Empty State */}
        {!loading && brands.length === 0 && (
          <div className="text-center py-20 bg-white rounded-2xl border-2 border-dashed border-gray-200">
            <Palette className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-700 mb-2">
              No brands yet
            </h2>
            <p className="text-gray-500 mb-6 max-w-md mx-auto">
              Create your first brand profile to maintain consistent styling
              across all your mockups.
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-violet-600 to-indigo-600 text-white rounded-lg hover:opacity-90 transition"
            >
              <Plus className="w-5 h-5" />
              Create Your First Brand
            </button>
          </div>
        )}

        {/* Brands Grid */}
        {!loading && brands.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {brands.map((brand) => (
              <BrandCard
                key={brand.id}
                brand={brand}
                onEdit={() => setEditingBrand(brand)}
                onDelete={() => handleDelete(brand.id)}
                onSetDefault={() => handleSetDefault(brand.id)}
              />
            ))}
          </div>
        )}
      </main>

      {/* Create Brand Modal */}
      {showCreateModal && (
        <CreateBrandModal
          onClose={() => setShowCreateModal(false)}
          onCreated={(brand) => {
            setBrands([brand, ...brands]);
            setShowCreateModal(false);
          }}
        />
      )}

      {/* Edit Brand Modal */}
      {editingBrand && (
        <EditBrandModal
          brand={editingBrand}
          onClose={() => setEditingBrand(null)}
          onUpdated={(updated) => {
            setBrands(brands.map((b) => (b.id === updated.id ? updated : b)));
            setEditingBrand(null);
          }}
        />
      )}
    </div>
  );
}

// Brand Card Component
function BrandCard({
  brand,
  onEdit,
  onDelete,
  onSetDefault,
}: {
  brand: Brand;
  onEdit: () => void;
  onDelete: () => void;
  onSetDefault: () => void;
}) {
  const colors = [
    brand.primary_color,
    brand.secondary_color,
    brand.accent_color,
    ...(brand.color_palette || []),
  ].filter(Boolean);

  return (
    <div className="bg-white rounded-xl border shadow-sm hover:shadow-md transition overflow-hidden group">
      {/* Color Bar */}
      <div className="h-2 flex">
        {colors.length > 0 ? (
          colors.slice(0, 5).map((color, i) => (
            <div
              key={i}
              className="flex-1"
              style={{ backgroundColor: color! }}
            />
          ))
        ) : (
          <div className="flex-1 bg-gradient-to-r from-gray-200 to-gray-300" />
        )}
      </div>

      <div className="p-5">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            {brand.logo_url ? (
              <img
                src={brand.logo_url}
                alt={brand.name}
                className="w-12 h-12 rounded-lg object-contain bg-gray-50"
              />
            ) : (
              <div
                className="w-12 h-12 rounded-lg flex items-center justify-center text-xl font-bold text-white"
                style={{
                  backgroundColor: brand.primary_color || "#6366f1",
                }}
              >
                {brand.name.charAt(0).toUpperCase()}
              </div>
            )}
            <div>
              <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                {brand.name}
                {brand.is_default && (
                  <span className="px-2 py-0.5 text-xs bg-violet-100 text-violet-700 rounded-full">
                    Default
                  </span>
                )}
              </h3>
              {brand.industry && (
                <p className="text-sm text-gray-500 capitalize">
                  {brand.industry}
                </p>
              )}
            </div>
          </div>
          {brand.is_extracted && (
            <span title="AI Extracted">
              <Wand2 className="w-4 h-4 text-violet-500" />
            </span>
          )}
        </div>

        {/* Description */}
        {brand.description && (
          <p className="text-sm text-gray-600 mb-4 line-clamp-2">
            {brand.description}
          </p>
        )}

        {/* Attributes */}
        <div className="flex flex-wrap gap-2 mb-4">
          {brand.mood && (
            <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full capitalize">
              {brand.mood}
            </span>
          )}
          {brand.style && (
            <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full capitalize">
              {brand.style}
            </span>
          )}
          {brand.preferred_lighting && (
            <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full capitalize">
              {brand.preferred_lighting} lighting
            </span>
          )}
        </div>

        {/* Colors Preview */}
        {colors.length > 0 && (
          <div className="flex gap-1 mb-4">
            {colors.slice(0, 6).map((color, i) => (
              <div
                key={i}
                className="w-6 h-6 rounded-full border-2 border-white shadow-sm"
                style={{ backgroundColor: color! }}
                title={color!}
              />
            ))}
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between pt-4 border-t">
          <div className="flex gap-2">
            <button
              onClick={onEdit}
              className="p-2 text-gray-500 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition"
              title="Edit"
            >
              <Edit2 className="w-4 h-4" />
            </button>
            <button
              onClick={onDelete}
              className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
              title="Delete"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
          {!brand.is_default && (
            <button
              onClick={onSetDefault}
              className="flex items-center gap-1 px-3 py-1.5 text-sm text-gray-600 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition"
            >
              <Star className="w-4 h-4" />
              Set Default
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// Create Brand Modal
function CreateBrandModal({
  onClose,
  onCreated,
}: {
  onClose: () => void;
  onCreated: (brand: Brand) => void;
}) {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [extracted, setExtracted] = useState<BrandExtractResponse | null>(null);

  // Form state
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [logoPreview, setLogoPreview] = useState<string | null>(null);

  // Brand attributes
  const [primaryColor, setPrimaryColor] = useState("#6366f1");
  const [secondaryColor, setSecondaryColor] = useState("#8b5cf6");
  const [accentColor, setAccentColor] = useState("#ec4899");
  const [mood, setMood] = useState("");
  const [style, setStyle] = useState("");
  const [industry, setIndustry] = useState("");
  const [lighting, setLighting] = useState("");
  const [isDefault, setIsDefault] = useState(false);

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setLogoFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setLogoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleExtract = async () => {
    if (!logoFile && !websiteUrl) return;

    setExtracting(true);
    try {
      const result = await brandsApi.extract(logoFile || undefined, websiteUrl || undefined, name || undefined);
      setExtracted(result);

      // Apply extracted values
      if (result.extracted.primary_color)
        setPrimaryColor(result.extracted.primary_color);
      if (result.extracted.secondary_color)
        setSecondaryColor(result.extracted.secondary_color);
      if (result.extracted.accent_color)
        setAccentColor(result.extracted.accent_color);
      if (result.extracted.mood) setMood(result.extracted.mood);
      if (result.extracted.style) setStyle(result.extracted.style);
      if (result.extracted.industry) setIndustry(result.extracted.industry);
    } catch (error) {
      console.error("Extraction failed:", error);
    } finally {
      setExtracting(false);
    }
  };

  const handleCreate = async () => {
    if (!name.trim()) return;

    setLoading(true);
    try {
      const brandData: BrandCreate = {
        name: name.trim(),
        description: description.trim() || undefined,
        website_url: websiteUrl.trim() || undefined,
        primary_color: primaryColor,
        secondary_color: secondaryColor,
        accent_color: accentColor,
        mood: mood || undefined,
        style: style || undefined,
        industry: industry || undefined,
        preferred_lighting: lighting || undefined,
        is_default: isDefault,
      };

      const brand = await brandsApi.create(brandData);

      // Upload logo if provided
      if (logoFile) {
        const updated = await brandsApi.uploadLogo(brand.id, logoFile);
        onCreated(updated);
      } else {
        onCreated(brand);
      }
    } catch (error) {
      console.error("Failed to create brand:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b bg-gradient-to-r from-violet-600 to-indigo-600">
          <h2 className="text-xl font-semibold text-white">Create Brand</h2>
          <button
            onClick={onClose}
            className="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Steps */}
        <div className="px-6 py-4 border-b bg-gray-50">
          <div className="flex items-center gap-4">
            {[1, 2, 3].map((s) => (
              <div key={s} className="flex items-center gap-2">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition ${
                    step >= s
                      ? "bg-violet-600 text-white"
                      : "bg-gray-200 text-gray-500"
                  }`}
                >
                  {step > s ? <Check className="w-4 h-4" /> : s}
                </div>
                <span
                  className={`text-sm ${
                    step >= s ? "text-gray-900" : "text-gray-500"
                  }`}
                >
                  {s === 1 ? "Basics" : s === 2 ? "Extract" : "Customize"}
                </span>
                {s < 3 && <ChevronRight className="w-4 h-4 text-gray-400" />}
              </div>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {/* Step 1: Basics */}
          {step === 1 && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Brand Name *
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Enter your brand name"
                  className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Briefly describe your brand"
                  rows={3}
                  className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent resize-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Logo
                </label>
                <div className="flex items-center gap-4">
                  {logoPreview ? (
                    <div className="relative">
                      <img
                        src={logoPreview}
                        alt="Logo preview"
                        className="w-20 h-20 rounded-lg object-contain bg-gray-50 border"
                      />
                      <button
                        onClick={() => {
                          setLogoFile(null);
                          setLogoPreview(null);
                        }}
                        className="absolute -top-2 -right-2 p-1 bg-red-500 text-white rounded-full"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ) : (
                    <label className="w-20 h-20 rounded-lg border-2 border-dashed border-gray-300 flex flex-col items-center justify-center cursor-pointer hover:border-violet-500 transition">
                      <Upload className="w-6 h-6 text-gray-400" />
                      <span className="text-xs text-gray-500 mt-1">Upload</span>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleLogoChange}
                        className="hidden"
                      />
                    </label>
                  )}
                  <div className="text-sm text-gray-500">
                    Upload your logo to extract brand colors automatically
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Website URL
                </label>
                <div className="flex items-center gap-2">
                  <Globe className="w-5 h-5 text-gray-400" />
                  <input
                    type="url"
                    value={websiteUrl}
                    onChange={(e) => setWebsiteUrl(e.target.value)}
                    placeholder="https://yourbrand.com"
                    className="flex-1 px-4 py-3 border rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Extract */}
          {step === 2 && (
            <div className="space-y-6">
              <div className="text-center py-6">
                <Wand2 className="w-12 h-12 text-violet-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">
                  AI Brand Extraction
                </h3>
                <p className="text-gray-600 mb-6">
                  {logoFile || websiteUrl
                    ? "Click below to analyze your logo and website to extract brand colors and style."
                    : "Go back to add a logo or website URL to enable AI extraction."}
                </p>
                <button
                  onClick={handleExtract}
                  disabled={(!logoFile && !websiteUrl) || extracting}
                  className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-violet-600 to-indigo-600 text-white rounded-lg hover:opacity-90 transition disabled:opacity-50"
                >
                  {extracting ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Wand2 className="w-5 h-5" />
                      Extract Brand DNA
                    </>
                  )}
                </button>
              </div>

              {extracted && (
                <div className="bg-violet-50 rounded-xl p-4 space-y-4">
                  <div className="flex items-center gap-2 text-violet-700">
                    <Check className="w-5 h-5" />
                    <span className="font-medium">
                      Extraction Complete ({Math.round(extracted.confidence * 100)}% confidence)
                    </span>
                  </div>

                  {extracted.extracted.primary_color && (
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-600">Colors found:</span>
                      <div className="flex gap-1">
                        {[
                          extracted.extracted.primary_color,
                          extracted.extracted.secondary_color,
                          extracted.extracted.accent_color,
                        ]
                          .filter(Boolean)
                          .map((c, i) => (
                            <div
                              key={i}
                              className="w-6 h-6 rounded-full border-2 border-white shadow"
                              style={{ backgroundColor: c }}
                            />
                          ))}
                      </div>
                    </div>
                  )}

                  {extracted.extracted.mood && (
                    <div className="text-sm">
                      <span className="text-gray-600">Detected mood:</span>{" "}
                      <span className="font-medium capitalize">
                        {extracted.extracted.mood}
                      </span>
                    </div>
                  )}

                  {extracted.suggestions.length > 0 && (
                    <div className="text-sm text-amber-700 bg-amber-50 p-2 rounded">
                      {extracted.suggestions.join(". ")}
                    </div>
                  )}
                </div>
              )}

              <p className="text-sm text-gray-500 text-center">
                You can skip this step and set colors manually in the next step.
              </p>
            </div>
          )}

          {/* Step 3: Customize */}
          {step === 3 && (
            <div className="space-y-6">
              {/* Colors */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">
                  Brand Colors
                </h3>
                <div className="grid grid-cols-3 gap-4">
                  <ColorPicker
                    label="Primary"
                    value={primaryColor}
                    onChange={setPrimaryColor}
                  />
                  <ColorPicker
                    label="Secondary"
                    value={secondaryColor}
                    onChange={setSecondaryColor}
                  />
                  <ColorPicker
                    label="Accent"
                    value={accentColor}
                    onChange={setAccentColor}
                  />
                </div>
              </div>

              {/* Mood */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Brand Mood
                </label>
                <div className="grid grid-cols-5 gap-2">
                  {MOOD_OPTIONS.map((option) => (
                    <button
                      key={option.value}
                      onClick={() =>
                        setMood(mood === option.value ? "" : option.value)
                      }
                      className={`p-2 rounded-lg border text-center transition ${
                        mood === option.value
                          ? "border-violet-500 bg-violet-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      <span className="text-lg">{option.emoji}</span>
                      <p className="text-xs mt-1">{option.label}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Style */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Visual Style
                </label>
                <div className="flex flex-wrap gap-2">
                  {STYLE_OPTIONS.map((option) => (
                    <button
                      key={option.value}
                      onClick={() =>
                        setStyle(style === option.value ? "" : option.value)
                      }
                      className={`px-4 py-2 rounded-full text-sm transition ${
                        style === option.value
                          ? "bg-violet-600 text-white"
                          : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                      }`}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Industry */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Industry
                </label>
                <select
                  value={industry}
                  onChange={(e) => setIndustry(e.target.value)}
                  className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                >
                  <option value="">Select industry</option>
                  {INDUSTRY_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Lighting */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Preferred Lighting
                </label>
                <select
                  value={lighting}
                  onChange={(e) => setLighting(e.target.value)}
                  className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                >
                  <option value="">Select lighting preference</option>
                  {LIGHTING_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Default */}
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={isDefault}
                  onChange={(e) => setIsDefault(e.target.checked)}
                  className="w-5 h-5 rounded border-gray-300 text-violet-600 focus:ring-violet-500"
                />
                <span className="text-sm text-gray-700">
                  Set as default brand for new mockups
                </span>
              </label>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t bg-gray-50 flex justify-between">
          <button
            onClick={() => (step > 1 ? setStep(step - 1) : onClose())}
            className="px-4 py-2 text-gray-600 hover:text-gray-900 transition"
          >
            {step > 1 ? "Back" : "Cancel"}
          </button>
          <button
            onClick={() => {
              if (step < 3) {
                setStep(step + 1);
              } else {
                handleCreate();
              }
            }}
            disabled={step === 1 && !name.trim()}
            className="px-6 py-2 bg-gradient-to-r from-violet-600 to-indigo-600 text-white rounded-lg hover:opacity-90 transition disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Creating...
              </>
            ) : step < 3 ? (
              <>
                Next
                <ChevronRight className="w-4 h-4" />
              </>
            ) : (
              "Create Brand"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

// Edit Brand Modal (simplified version)
function EditBrandModal({
  brand,
  onClose,
  onUpdated,
}: {
  brand: Brand;
  onClose: () => void;
  onUpdated: (brand: Brand) => void;
}) {
  const [loading, setLoading] = useState(false);
  const [name, setName] = useState(brand.name);
  const [description, setDescription] = useState(brand.description || "");
  const [primaryColor, setPrimaryColor] = useState(brand.primary_color || "#6366f1");
  const [secondaryColor, setSecondaryColor] = useState(brand.secondary_color || "#8b5cf6");
  const [accentColor, setAccentColor] = useState(brand.accent_color || "#ec4899");
  const [mood, setMood] = useState(brand.mood || "");
  const [style, setStyle] = useState(brand.style || "");
  const [industry, setIndustry] = useState(brand.industry || "");
  const [lighting, setLighting] = useState(brand.preferred_lighting || "");

  const handleSave = async () => {
    setLoading(true);
    try {
      const updated = await brandsApi.update(brand.id, {
        name,
        description: description || undefined,
        primary_color: primaryColor,
        secondary_color: secondaryColor,
        accent_color: accentColor,
        mood: mood || undefined,
        style: style || undefined,
        industry: industry || undefined,
        preferred_lighting: lighting || undefined,
      });
      onUpdated(updated);
    } catch (error) {
      console.error("Failed to update brand:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="text-lg font-semibold">Edit Brand</h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 overflow-y-auto max-h-[calc(90vh-150px)]">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Brand Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent resize-none"
            />
          </div>

          {/* Colors */}
          <div className="grid grid-cols-3 gap-4">
            <ColorPicker
              label="Primary"
              value={primaryColor}
              onChange={setPrimaryColor}
            />
            <ColorPicker
              label="Secondary"
              value={secondaryColor}
              onChange={setSecondaryColor}
            />
            <ColorPicker
              label="Accent"
              value={accentColor}
              onChange={setAccentColor}
            />
          </div>

          {/* Selects */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Mood
              </label>
              <select
                value={mood}
                onChange={(e) => setMood(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg"
              >
                <option value="">None</option>
                {MOOD_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Style
              </label>
              <select
                value={style}
                onChange={(e) => setStyle(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg"
              >
                <option value="">None</option>
                {STYLE_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Industry
              </label>
              <select
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg"
              >
                <option value="">None</option>
                {INDUSTRY_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Lighting
              </label>
              <select
                value={lighting}
                onChange={(e) => setLighting(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg"
              >
                <option value="">None</option>
                {LIGHTING_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t bg-gray-50 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:text-gray-900 transition"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={loading || !name.trim()}
            className="px-6 py-2 bg-gradient-to-r from-violet-600 to-indigo-600 text-white rounded-lg hover:opacity-90 transition disabled:opacity-50 flex items-center gap-2"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
}

// Color Picker Component
function ColorPicker({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div>
      <label className="block text-xs text-gray-500 mb-1">{label}</label>
      <div className="flex items-center gap-2">
        <input
          type="color"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-10 h-10 rounded-lg cursor-pointer border-0"
        />
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="flex-1 px-2 py-1.5 text-sm border rounded-lg font-mono uppercase"
          maxLength={7}
        />
      </div>
    </div>
  );
}

