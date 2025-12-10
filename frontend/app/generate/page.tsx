"use client";

import { useState } from "react";
import Link from "next/link";
import { Upload, Sparkles, Download, ArrowLeft, AlertCircle, MessageSquare, Settings2, Palette } from "lucide-react";
import ProductUploader from "@/components/upload/ProductUploader";
import SceneSelector from "@/components/generation/SceneSelector";
import BrandSelector from "@/components/generation/BrandSelector";
import ChatInterface from "@/components/chat/ChatInterface";
import ExportModal from "@/components/export/ExportModal";
import BatchGenerator from "@/components/generation/BatchGenerator";
import { SceneSuggestions } from "@/components/generation/SceneSuggestions";
import { mockupsApi, ProductResponse, MockupResponse, CustomizationOptions, MockupVariation } from "@/lib/api";

type Step = "upload" | "scene" | "generate" | "result";

export default function GeneratePage() {
  const [currentStep, setCurrentStep] = useState<Step>("upload");
  const [product, setProduct] = useState<ProductResponse | null>(null);
  const [selectedScene, setSelectedScene] = useState<string | null>(null);
  const [selectedBrandId, setSelectedBrandId] = useState<string | null>(null);
  const [customization, setCustomization] = useState<CustomizationOptions | undefined>(undefined);
  const [mockup, setMockup] = useState<MockupResponse | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showRefinement, setShowRefinement] = useState(false);
  const [currentImageUrl, setCurrentImageUrl] = useState<string | null>(null);
  const [showExportModal, setShowExportModal] = useState(false);
  const [batchMockups, setBatchMockups] = useState<MockupVariation[]>([]);

  const handleProductUpload = (uploadedProduct: ProductResponse) => {
    setProduct(uploadedProduct);
    setCurrentStep("scene");
  };

  const handleSceneSelect = (sceneId: string, options?: CustomizationOptions) => {
    setSelectedScene(sceneId);
    setCustomization(options);
  };

  const handleGenerate = async () => {
    if (!product || !selectedScene) return;

    setError(null);
    setIsGenerating(true);
    setCurrentStep("generate");

    try {
      const result = await mockupsApi.generate({
        product_id: product.id,
        scene_template_id: selectedScene,
        customization,
        brand_id: selectedBrandId || undefined,
      });
      setMockup(result);
      setCurrentStep("result");
    } catch (err) {
      console.error("Generation failed:", err);
      setError(err instanceof Error ? err.message : "Generation failed");
      setCurrentStep("scene");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleStartOver = () => {
    setProduct(null);
    setSelectedScene(null);
    setSelectedBrandId(null);
    setCustomization(undefined);
    setMockup(null);
    setError(null);
    setShowRefinement(false);
    setCurrentImageUrl(null);
    setBatchMockups([]);
    setCurrentStep("upload");
  };

  const handleBatchComplete = (mockups: MockupVariation[]) => {
    setBatchMockups(mockups);
  };

  // Get all mockup IDs for batch export
  const getAllMockupIds = () => {
    const ids = mockup ? [mockup.id] : [];
    return [...ids, ...batchMockups.map(m => m.id)];
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-primary" />
            <span className="font-bold text-xl">MockupAI</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link
              href="/brands"
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
            >
              <Palette className="w-4 h-4" />
              Brands
            </Link>
            {currentStep !== "upload" && (
              <button
                onClick={handleStartOver}
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="w-4 h-4" />
                Start Over
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Progress Steps */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-center gap-4">
            <StepIndicator
              number={1}
              label="Upload"
              active={currentStep === "upload"}
              completed={!!product}
            />
            <StepConnector completed={!!product} />
            <StepIndicator
              number={2}
              label="Choose Scene"
              active={currentStep === "scene"}
              completed={!!mockup}
            />
            <StepConnector completed={!!mockup} />
            <StepIndicator
              number={3}
              label="Result"
              active={currentStep === "result"}
              completed={false}
            />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {error && (
          <div className="max-w-2xl mx-auto mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            {error}
          </div>
        )}

        {currentStep === "upload" && (
          <div className="max-w-2xl mx-auto">
            <h1 className="text-2xl font-bold mb-6 text-center">
              Upload Your Product
            </h1>
            <ProductUploader onUpload={handleProductUpload} />
          </div>
        )}

        {currentStep === "scene" && product && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-2xl font-bold">Choose a Scene</h1>
                <p className="text-gray-600">Select a scene template for your mockup</p>
              </div>
              <button
                onClick={handleGenerate}
                disabled={!selectedScene}
                className="px-6 py-2 bg-primary text-primary-foreground rounded-lg disabled:opacity-50 hover:opacity-90 transition flex items-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                Generate Mockup
              </button>
            </div>

            {/* Product Preview and Brand Selector */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
              {/* Product Preview */}
              <div className="p-4 bg-white rounded-lg border flex items-center gap-4">
                <img
                  src={product.processed_image_url || product.original_image_url}
                  alt="Product"
                  className="w-20 h-20 object-contain rounded bg-gray-50"
                />
                <div>
                  <p className="font-medium">Your Product</p>
                  <p className="text-sm text-gray-500">
                    Category: {product.category || "Detected automatically"}
                  </p>
                </div>
              </div>

              {/* Brand Selector */}
              <BrandSelector
                selectedBrandId={selectedBrandId}
                onSelect={setSelectedBrandId}
              />
            </div>

            <SceneSuggestions
              product={product}
              brandId={selectedBrandId}
              selectedScene={selectedScene}
              onSelect={handleSceneSelect}
            />

            <SceneSelector
              selectedScene={selectedScene}
              onSelect={handleSceneSelect}
            />
          </div>
        )}

        {currentStep === "generate" && isGenerating && (
          <div className="text-center py-20">
            <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <h2 className="text-xl font-semibold mb-2">Generating Your Mockup</h2>
            <p className="text-gray-600">This usually takes 10-30 seconds...</p>
            <p className="text-sm text-gray-400 mt-2">
              AI is placing your product in the scene
            </p>
          </div>
        )}

        {currentStep === "result" && mockup && (
          <div className="max-w-6xl mx-auto">
            <h1 className="text-2xl font-bold mb-6 text-center">
              Your Mockup is Ready!
            </h1>

            <div className={`grid gap-6 ${showRefinement ? "lg:grid-cols-2" : ""}`}>
              {/* Mockup Display */}
              <div className="space-y-4">
                <div className="bg-white rounded-xl border overflow-hidden">
                  <div className="aspect-video bg-gray-100 flex items-center justify-center">
                    <img
                      src={currentImageUrl || mockup.image_url}
                      alt="Generated mockup"
                      className="max-w-full max-h-full object-contain"
                    />
                  </div>

                  <div className="p-6 border-t">
                    <div className="flex items-center justify-between flex-wrap gap-4">
                      <div>
                        <p className="text-sm text-gray-500">Scene: {mockup.scene_template_id}</p>
                        {mockup.brand_applied && (
                          <p className="text-sm text-violet-600 flex items-center gap-1">
                            <Palette className="w-3 h-3" />
                            Brand styling applied
                            {mockup.brand_applied.mood && (
                              <span className="text-xs text-gray-500">
                                ({mockup.brand_applied.mood})
                              </span>
                            )}
                          </p>
                        )}
                        <p className="text-xs text-gray-400">
                          Generated {new Date(mockup.created_at).toLocaleString()}
                        </p>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        <button
                          onClick={() => setShowRefinement(!showRefinement)}
                          className={`px-4 py-2 rounded-lg transition flex items-center gap-2 ${
                            showRefinement
                              ? "bg-gray-200 text-gray-700"
                              : "bg-purple-600 text-white hover:bg-purple-700"
                          }`}
                        >
                          <MessageSquare className="w-4 h-4" />
                          {showRefinement ? "Hide Refinement" : "Refine with AI"}
                        </button>
                        <button
                          onClick={() => setShowExportModal(true)}
                          className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition flex items-center gap-2"
                        >
                          <Settings2 className="w-4 h-4" />
                          Export Options
                        </button>
                        <a
                          href={currentImageUrl || mockup.image_url}
                          download={`mockup-${mockup.id}.png`}
                          className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition flex items-center gap-2"
                        >
                          <Download className="w-4 h-4" />
                          Quick Download
                        </a>
                        <button
                          onClick={handleStartOver}
                          className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                        >
                          Create Another
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Batch Generator */}
                {product && (
                  <BatchGenerator
                    productId={product.id}
                    productImageUrl={product.processed_image_url || product.original_image_url}
                    onComplete={handleBatchComplete}
                  />
                )}

                {/* Batch Mockups Grid */}
                {batchMockups.length > 0 && (
                  <div className="bg-white rounded-xl border p-4">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-medium">
                        Generated Variations ({batchMockups.length})
                      </h3>
                      <button
                        onClick={() => setShowExportModal(true)}
                        className="text-sm text-primary hover:underline"
                      >
                        Export All
                      </button>
                    </div>
                    <div className="grid grid-cols-4 sm:grid-cols-5 md:grid-cols-6 gap-2">
                      {batchMockups.map((m, i) => (
                        <div
                          key={m.id}
                          className="aspect-square rounded-lg overflow-hidden bg-muted cursor-pointer hover:ring-2 ring-primary transition"
                          onClick={() => setCurrentImageUrl(m.image_url)}
                        >
                          <img
                            src={m.image_url}
                            alt={`Variation ${i + 1}`}
                            className="w-full h-full object-cover"
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Chat Interface */}
              {showRefinement && (
                <div className="lg:h-[600px]">
                  <ChatInterface
                    mockupId={mockup.id}
                    initialImageUrl={mockup.image_url}
                    onImageUpdate={setCurrentImageUrl}
                  />
                </div>
              )}
            </div>

            {/* Export Modal */}
            <ExportModal
              isOpen={showExportModal}
              onClose={() => setShowExportModal(false)}
              mockupId={mockup.id}
              mockupIds={getAllMockupIds()}
              mockupImageUrl={currentImageUrl || mockup.image_url}
            />
          </div>
        )}
      </main>
    </div>
  );
}

function StepIndicator({
  number,
  label,
  active,
  completed,
}: {
  number: number;
  label: string;
  active: boolean;
  completed: boolean;
}) {
  return (
    <div
      className={`flex items-center gap-2 ${
        active ? "text-primary" : completed ? "text-green-600" : "text-gray-400"
      }`}
    >
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
          active
            ? "bg-primary text-white"
            : completed
            ? "bg-green-600 text-white"
            : "bg-gray-200"
        }`}
      >
        {completed ? "✓" : number}
      </div>
      <span className="font-medium">{label}</span>
    </div>
  );
}

function StepConnector({ completed }: { completed: boolean }) {
  return (
    <div
      className={`w-12 h-0.5 ${completed ? "bg-green-600" : "bg-gray-200"}`}
    ></div>
  );
}
