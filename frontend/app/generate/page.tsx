"use client";

import { useState } from "react";
import Link from "next/link";
import { Upload, Sparkles, Download, ArrowLeft, AlertCircle } from "lucide-react";
import ProductUploader from "@/components/upload/ProductUploader";
import SceneSelector from "@/components/generation/SceneSelector";
import { mockupsApi, ProductResponse, MockupResponse, CustomizationOptions } from "@/lib/api";

type Step = "upload" | "scene" | "generate" | "result";

export default function GeneratePage() {
  const [currentStep, setCurrentStep] = useState<Step>("upload");
  const [product, setProduct] = useState<ProductResponse | null>(null);
  const [selectedScene, setSelectedScene] = useState<string | null>(null);
  const [customization, setCustomization] = useState<CustomizationOptions | undefined>(undefined);
  const [mockup, setMockup] = useState<MockupResponse | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
    setCustomization(undefined);
    setMockup(null);
    setError(null);
    setCurrentStep("upload");
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

            {/* Product Preview */}
            <div className="mb-6 p-4 bg-white rounded-lg border flex items-center gap-4">
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
          <div className="max-w-4xl mx-auto">
            <h1 className="text-2xl font-bold mb-6 text-center">
              Your Mockup is Ready!
            </h1>

            <div className="bg-white rounded-xl border overflow-hidden">
              <div className="aspect-video bg-gray-100 flex items-center justify-center">
                <img
                  src={mockup.image_url}
                  alt="Generated mockup"
                  className="max-w-full max-h-full object-contain"
                />
              </div>

              <div className="p-6 border-t">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Scene: {mockup.scene_template_id}</p>
                    <p className="text-xs text-gray-400">
                      Generated {new Date(mockup.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <a
                      href={mockup.image_url}
                      download={`mockup-${mockup.id}.png`}
                      className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition flex items-center gap-2"
                    >
                      <Download className="w-4 h-4" />
                      Download
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
