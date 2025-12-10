"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, X, Image as ImageIcon, AlertCircle } from "lucide-react";
import { productsApi, ProductResponse } from "@/lib/api";

interface ProductUploaderProps {
  onUpload: (product: ProductResponse) => void;
}

export default function ProductUploader({ onUpload }: ProductUploaderProps) {
  const [preview, setPreview] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (!file) return;

      setError(null);

      // Show preview immediately
      const previewUrl = URL.createObjectURL(file);
      setPreview(previewUrl);
      setIsUploading(true);

      try {
        const product = await productsApi.upload(file);
        onUpload(product);
      } catch (err) {
        console.error("Upload failed:", err);
        setError(err instanceof Error ? err.message : "Upload failed");
        setPreview(null);
      } finally {
        setIsUploading(false);
      }
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".png", ".jpg", ".jpeg", ".webp"],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  });

  const clearPreview = () => {
    setPreview(null);
    setError(null);
  };

  if (preview) {
    return (
      <div className="relative">
        <div className="aspect-square bg-gray-100 rounded-xl overflow-hidden">
          <img
            src={preview}
            alt="Product preview"
            className="w-full h-full object-contain"
          />
        </div>
        {isUploading && (
          <div className="absolute inset-0 bg-black/50 flex items-center justify-center rounded-xl">
            <div className="text-white text-center">
              <div className="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
              <p>Processing image...</p>
              <p className="text-sm text-gray-300 mt-1">Removing background & analyzing</p>
            </div>
          </div>
        )}
        {!isUploading && (
          <button
            onClick={clearPreview}
            className="absolute top-2 right-2 p-2 bg-white rounded-full shadow-lg hover:bg-gray-100"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    );
  }

  return (
    <div>
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
          <AlertCircle className="w-5 h-5" />
          {error}
        </div>
      )}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition
          ${
            isDragActive
              ? "border-primary bg-primary/5"
              : "border-gray-300 hover:border-primary hover:bg-gray-50"
          }
        `}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
            {isDragActive ? (
              <ImageIcon className="w-8 h-8 text-primary" />
            ) : (
              <Upload className="w-8 h-8 text-gray-400" />
            )}
          </div>
          <div>
            <p className="font-medium text-lg">
              {isDragActive ? "Drop your image here" : "Drag & drop your product image"}
            </p>
            <p className="text-gray-500 mt-1">or click to browse</p>
          </div>
          <p className="text-sm text-gray-400">PNG, JPG, WEBP up to 10MB</p>
        </div>
      </div>
    </div>
  );
}
