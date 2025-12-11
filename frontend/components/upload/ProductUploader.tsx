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
        <div className="aspect-square bg-secondary border-3 border-foreground shadow-brutal overflow-hidden">
          <img
            src={preview}
            alt="Product preview"
            className="w-full h-full object-contain"
          />
        </div>
        {isUploading && (
          <div className="absolute inset-0 bg-black/80 flex items-center justify-center">
            <div className="text-white text-center">
              <div className="w-10 h-10 border-3 border-white border-t-transparent animate-spin mx-auto mb-3"></div>
              <p className="font-bold uppercase tracking-wide">Processing image...</p>
              <p className="text-sm font-medium mt-2">Removing background & analyzing</p>
            </div>
          </div>
        )}
        {!isUploading && (
          <button
            onClick={clearPreview}
            className="absolute top-4 right-4 p-2 bg-white border-3 border-foreground shadow-brutal hover:shadow-brutal-lg hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-1 active:translate-y-1 active:shadow-none transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>
    );
  }

  return (
    <div>
      {error && (
        <div className="mb-4 p-4 bg-destructive/10 border-3 border-destructive shadow-brutal-sm flex items-center gap-3 text-destructive">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span className="font-bold">{error}</span>
        </div>
      )}
      <div
        {...getRootProps()}
        className={`
          border-3 p-12 text-center cursor-pointer transition-all
          ${
            isDragActive
              ? "border-foreground bg-accent shadow-brutal-lg -translate-x-0.5 -translate-y-0.5"
              : "border-foreground bg-background shadow-brutal hover:shadow-brutal-lg hover:-translate-x-0.5 hover:-translate-y-0.5"
          }
        `}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center gap-6">
          <div className="w-20 h-20 bg-secondary border-3 border-foreground shadow-brutal-sm flex items-center justify-center">
            {isDragActive ? (
              <ImageIcon className="w-10 h-10 text-foreground" />
            ) : (
              <Upload className="w-10 h-10 text-foreground" />
            )}
          </div>
          <div>
            <p className="font-black uppercase text-xl tracking-wide">
              {isDragActive ? "Drop your image here" : "Drag & drop your product image"}
            </p>
            <p className="text-muted-foreground font-bold mt-2 uppercase text-sm">or click to browse</p>
          </div>
          <p className="text-xs font-bold uppercase tracking-wide text-muted-foreground px-4 py-2 bg-secondary border-3 border-foreground">
            PNG, JPG, WEBP up to 10MB
          </p>
        </div>
      </div>
    </div>
  );
}
