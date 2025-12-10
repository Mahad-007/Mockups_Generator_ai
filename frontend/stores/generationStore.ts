import { create } from "zustand";

interface GenerationState {
  // Product
  productId: string | null;
  productImageUrl: string | null;

  // Scene
  selectedSceneId: string | null;
  customPrompt: string | null;

  // Brand
  selectedBrandId: string | null;

  // Generation
  isGenerating: boolean;
  generatedMockups: string[];

  // Chat
  chatSessionId: string | null;

  // Actions
  setProduct: (id: string, imageUrl: string) => void;
  setScene: (sceneId: string) => void;
  setCustomPrompt: (prompt: string) => void;
  setBrand: (brandId: string | null) => void;
  setGenerating: (isGenerating: boolean) => void;
  setMockups: (mockups: string[]) => void;
  addMockup: (mockup: string) => void;
  setChatSession: (sessionId: string) => void;
  reset: () => void;
}

const initialState = {
  productId: null,
  productImageUrl: null,
  selectedSceneId: null,
  customPrompt: null,
  selectedBrandId: null,
  isGenerating: false,
  generatedMockups: [],
  chatSessionId: null,
};

export const useGenerationStore = create<GenerationState>((set) => ({
  ...initialState,

  setProduct: (id, imageUrl) =>
    set({ productId: id, productImageUrl: imageUrl }),

  setScene: (sceneId) => set({ selectedSceneId: sceneId }),

  setCustomPrompt: (prompt) => set({ customPrompt: prompt }),

  setBrand: (brandId) => set({ selectedBrandId: brandId }),

  setGenerating: (isGenerating) => set({ isGenerating }),

  setMockups: (mockups) => set({ generatedMockups: mockups }),

  addMockup: (mockup) =>
    set((state) => ({
      generatedMockups: [...state.generatedMockups, mockup],
    })),

  setChatSession: (sessionId) => set({ chatSessionId: sessionId }),

  reset: () => set(initialState),
}));
