"use client";

import { useState } from "react";
import { Download, Maximize2, Heart } from "lucide-react";

interface ResultsGridProps {
  mockups: string[];
}

export default function ResultsGrid({ mockups }: ResultsGridProps) {
  const [selectedMockup, setSelectedMockup] = useState<string | null>(
    mockups[0] || null
  );

  if (mockups.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        No mockups generated yet
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Main Preview */}
      {selectedMockup && (
        <div className="relative aspect-square bg-gray-100 rounded-xl overflow-hidden">
          <div className="w-full h-full bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center text-gray-400">
            Generated Mockup Preview
          </div>

          {/* Action Buttons */}
          <div className="absolute top-4 right-4 flex gap-2">
            <button className="p-2 bg-white rounded-lg shadow hover:bg-gray-50">
              <Heart className="w-5 h-5" />
            </button>
            <button className="p-2 bg-white rounded-lg shadow hover:bg-gray-50">
              <Maximize2 className="w-5 h-5" />
            </button>
            <button className="p-2 bg-primary text-white rounded-lg shadow hover:opacity-90">
              <Download className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}

      {/* Thumbnail Grid */}
      {mockups.length > 1 && (
        <div className="grid grid-cols-4 gap-2">
          {mockups.map((mockup, index) => (
            <button
              key={index}
              onClick={() => setSelectedMockup(mockup)}
              className={`aspect-square bg-gray-100 rounded-lg overflow-hidden border-2 transition ${
                selectedMockup === mockup
                  ? "border-primary"
                  : "border-transparent hover:border-gray-300"
              }`}
            >
              <div className="w-full h-full bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center text-xs text-gray-400">
                {index + 1}
              </div>
            </button>
          ))}
        </div>
      )}

      {/* Export Button */}
      <button className="w-full py-3 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition flex items-center justify-center gap-2">
        <Download className="w-5 h-5" />
        Export All Mockups
      </button>
    </div>
  );
}
