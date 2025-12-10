/**
 * API client for MockupAI backend.
 * KISS: Simple fetch-based client, no heavy dependencies.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_URL}/api/v1${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new ApiError(response.status, error.detail || "Request failed");
  }

  return response.json();
}

// Products API
export const productsApi = {
  upload: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    return request<ProductResponse>("/products/upload", {
      method: "POST",
      body: formData,
    });
  },

  list: () => request<ProductResponse[]>("/products/"),

  get: (id: string) => request<ProductResponse>(`/products/${id}`),

  delete: (id: string) =>
    request<{ message: string }>(`/products/${id}`, { method: "DELETE" }),
};

// Mockups API
export const mockupsApi = {
  generate: (data: MockupGenerateRequest) =>
    request<MockupResponse>("/mockups/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }),

  list: (productId?: string) => {
    const params = productId ? `?product_id=${productId}` : "";
    return request<MockupResponse[]>(`/mockups/${params}`);
  },

  get: (id: string) => request<MockupResponse>(`/mockups/${id}`),

  delete: (id: string) =>
    request<{ message: string }>(`/mockups/${id}`, { method: "DELETE" }),
};

// Scenes API
export const scenesApi = {
  getTemplates: (params?: {
    category?: string;
    search?: string;
    tags?: string;
    premium_only?: boolean;
    limit?: number;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.category) searchParams.set("category", params.category);
    if (params?.search) searchParams.set("search", params.search);
    if (params?.tags) searchParams.set("tags", params.tags);
    if (params?.premium_only) searchParams.set("premium_only", "true");
    if (params?.limit) searchParams.set("limit", params.limit.toString());
    const queryString = searchParams.toString();
    return request<{ templates: SceneTemplate[]; total: number }>(
      `/scenes/templates${queryString ? `?${queryString}` : ""}`
    );
  },

  getTemplate: (id: string) =>
    request<SceneTemplate>(`/scenes/templates/${id}`),

  getCategories: () =>
    request<{ categories: string[]; counts: Record<string, number> }>("/scenes/categories"),

  getTags: () =>
    request<{ tags: Array<{ name: string; count: number }> }>("/scenes/tags"),

  customize: (data: CustomizeRequest) =>
    request<CustomizeResponse>("/scenes/customize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }),

  getSuggestions: (productCategory?: string) => {
    const params = productCategory ? `?product_category=${productCategory}` : "";
    return request<SceneSuggestionsResponse>(`/scenes/suggestions${params}`);
  },
};

// Types
export interface ProductResponse {
  id: string;
  original_image_url: string;
  processed_image_url: string | null;
  category: string | null;
  attributes: Record<string, string> | null;
  created_at: string;
}

export interface CustomizationOptions {
  color?: string;
  surface?: string;
  lighting?: string;
  angle?: string;
}

export interface MockupGenerateRequest {
  product_id: string;
  scene_template_id?: string;
  custom_prompt?: string;
  customization?: CustomizationOptions;
  brand_id?: string;  // Apply brand styling
}

export interface MockupResponse {
  id: string;
  product_id: string;
  image_url: string;
  scene_template_id: string | null;
  prompt_used: string | null;
  brand_id: string | null;
  brand_applied: Record<string, string> | null;
  created_at: string;
}

export interface SceneCustomizationOptions {
  colors: string[];
  surfaces: string[];
  lighting: string[];
  angles: string[];
}

export interface SceneTemplate {
  id: string;
  name: string;
  category: string;
  description: string;
  tags: string[];
  is_premium: boolean;
  popularity: number;
  customization: SceneCustomizationOptions;
}

export interface CustomizeRequest {
  template_id: string;
  color?: string;
  surface?: string;
  lighting?: string;
  angle?: string;
}

export interface CustomizeResponse {
  template_id: string;
  original_prompt: string;
  customized_prompt: string;
  customizations_applied: Record<string, string>;
}

export interface SceneSuggestion {
  template: SceneTemplate;
  relevance: number;
  reason: string;
}

export interface SceneSuggestionsResponse {
  product_category: string | null;
  suggestions: SceneSuggestion[];
}

// Chat Types
export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  image_url: string | null;
  refinement_type: string | null;
  created_at: string;
}

export interface ChatSession {
  id: string;
  mockup_id: string;
  current_image_url: string;
  messages: ChatMessage[];
  created_at: string;
  updated_at: string;
}

export interface RefinementSuggestion {
  label: string;
  prompt: string;
  category: string;
}

// Export Types
export interface ExportPreset {
  id: string;
  name: string;
  width: number;
  height: number;
  format: string;
}

export interface ExportPresetsResponse {
  presets: Record<string, Omit<ExportPreset, "id">>;
  categories: Record<string, ExportPreset[]>;
}

export interface ExportRequest {
  mockup_id: string;
  preset_id?: string;
  width?: number;
  height?: number;
  format?: string;
  quality?: number;
  background_color?: string;
}

export interface BatchExportRequest {
  mockup_ids: string[];
  preset_id?: string;
  format?: string;
  quality?: number;
}

export interface MultiPresetExportRequest {
  mockup_id: string;
  preset_ids: string[];
}

// Batch Generation Types
export interface VariationCustomization {
  template_id: string;
  customization?: Record<string, string>;
}

export interface BatchGenerateRequest {
  product_id: string;
  scene_template_ids?: string[];
  variation_preset?: "quick" | "standard" | "comprehensive";
  max_variations?: number;
  custom_variations?: VariationCustomization[];
}

export interface BatchGenerateResponse {
  job_id: string;
  status: string;
  total_variations: number;
  message: string;
}

export interface JobStatusResponse {
  id: string;
  job_type: string;
  status: "pending" | "in_progress" | "completed" | "failed" | "cancelled";
  total_items: number;
  completed_items: number;
  failed_items: number;
  progress: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  error: string | null;
  results: Array<{
    item_id: string;
    success: boolean;
    result: Record<string, unknown> | null;
    error: string | null;
  }>;
}

export interface MockupVariation {
  id: string;
  image_url: string;
  scene_template_id: string | null;
  customization: Record<string, string> | null;
}

export interface BatchResultResponse {
  job_id: string;
  status: string;
  mockups: MockupVariation[];
  failed_count: number;
}

export interface VariationPresetsResponse {
  presets: Record<
    string,
    {
      angles: string[];
      lighting: string[];
      backgrounds: string[];
      styles: string[];
      estimated_count: number;
    }
  >;
}

// Export API
export const exportApi = {
  getPresets: () => request<ExportPresetsResponse>("/export/presets"),

  exportSingle: async (data: ExportRequest): Promise<Blob> => {
    const url = `${API_URL}/api/v1/export/single`;
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new ApiError(response.status, "Export failed");
    }
    return response.blob();
  },

  exportBatch: async (data: BatchExportRequest): Promise<Blob> => {
    const url = `${API_URL}/api/v1/export/batch`;
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new ApiError(response.status, "Batch export failed");
    }
    return response.blob();
  },

  exportMultiPreset: async (data: MultiPresetExportRequest): Promise<Blob> => {
    const url = `${API_URL}/api/v1/export/multi-preset`;
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new ApiError(response.status, "Multi-preset export failed");
    }
    return response.blob();
  },

  downloadUrl: (mockupId: string, presetId?: string, format: string = "png") => {
    let url = `${API_URL}/api/v1/export/download/${mockupId}?format=${format}`;
    if (presetId) url += `&preset_id=${presetId}`;
    return url;
  },
};

// Batch Generation API
export const batchApi = {
  startGeneration: (data: BatchGenerateRequest) =>
    request<BatchGenerateResponse>("/batch/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }),

  getJobStatus: (jobId: string) =>
    request<JobStatusResponse>(`/batch/status/${jobId}`),

  cancelJob: (jobId: string) =>
    request<{ message: string; job_id: string }>(`/batch/status/${jobId}/cancel`, {
      method: "POST",
    }),

  getResults: (jobId: string, saveToDb: boolean = true) =>
    request<BatchResultResponse>(`/batch/results/${jobId}?save_to_db=${saveToDb}`),

  getPresets: () => request<VariationPresetsResponse>("/batch/presets"),

  listJobs: (status?: string, limit: number = 20) => {
    const params = new URLSearchParams();
    if (status) params.set("status", status);
    params.set("limit", limit.toString());
    return request<JobStatusResponse[]>(`/batch/jobs?${params.toString()}`);
  },
};

// Chat API
export const chatApi = {
  createSession: (mockupId: string) =>
    request<ChatSession>("/chat/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mockup_id: mockupId }),
    }),

  getSession: (sessionId: string) =>
    request<ChatSession>(`/chat/sessions/${sessionId}`),

  sendMessage: (sessionId: string, content: string) =>
    request<ChatMessage>(`/chat/sessions/${sessionId}/message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content }),
    }),

  undo: (sessionId: string) =>
    request<ChatMessage>(`/chat/sessions/${sessionId}/undo`),

  getSuggestions: () =>
    request<{ suggestions: RefinementSuggestion[] }>("/chat/suggestions"),

  listSessions: (mockupId?: string) => {
    const params = mockupId ? `?mockup_id=${mockupId}` : "";
    return request<ChatSession[]>(`/chat/sessions${params}`);
  },
};

// Brand Types
export interface Brand {
  id: string;
  name: string;
  description: string | null;
  logo_url: string | null;
  website_url: string | null;
  primary_color: string | null;
  secondary_color: string | null;
  accent_color: string | null;
  background_color: string | null;
  color_palette: string[] | null;
  primary_font: string | null;
  secondary_font: string | null;
  font_style: string | null;
  mood: string | null;
  style: string | null;
  industry: string | null;
  target_audience: string | null;
  prompt_description: string | null;
  suggested_scenes: string[] | null;
  preferred_lighting: string | null;
  is_default: boolean;
  is_extracted: boolean;
  created_at: string;
  updated_at: string;
}

export interface BrandCreate {
  name: string;
  description?: string;
  website_url?: string;
  primary_color?: string;
  secondary_color?: string;
  accent_color?: string;
  background_color?: string;
  color_palette?: string[];
  primary_font?: string;
  secondary_font?: string;
  font_style?: string;
  mood?: string;
  style?: string;
  industry?: string;
  target_audience?: string;
  preferred_lighting?: string;
  is_default?: boolean;
}

export interface BrandUpdate {
  name?: string;
  description?: string;
  website_url?: string;
  logo_url?: string;
  primary_color?: string;
  secondary_color?: string;
  accent_color?: string;
  background_color?: string;
  color_palette?: string[];
  primary_font?: string;
  secondary_font?: string;
  font_style?: string;
  mood?: string;
  style?: string;
  industry?: string;
  target_audience?: string;
  preferred_lighting?: string;
  is_default?: boolean;
}

export interface BrandExtractResponse {
  extracted: {
    primary_color?: string;
    secondary_color?: string;
    accent_color?: string;
    color_palette?: string[];
    mood?: string;
    style?: string;
    industry?: string;
  };
  confidence: number;
  suggestions: string[];
}

export interface BrandSuggestedScene {
  template_id: string;
  name: string;
  description: string;
  reason: string;
  relevance: number;
}

export interface BrandScenesResponse {
  brand_id: string;
  brand_mood: string | null;
  brand_style: string | null;
  suggested_scenes: BrandSuggestedScene[];
}

// Brands API
export const brandsApi = {
  create: (data: BrandCreate) =>
    request<Brand>("/brands/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }),

  list: () => request<Brand[]>("/brands/"),

  getDefault: () => request<Brand | null>("/brands/default"),

  get: (id: string) => request<Brand>(`/brands/${id}`),

  update: (id: string, data: BrandUpdate) =>
    request<Brand>(`/brands/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }),

  delete: (id: string) =>
    request<{ message: string; id: string }>(`/brands/${id}`, {
      method: "DELETE",
    }),

  setDefault: (id: string) =>
    request<Brand>(`/brands/${id}/set-default`, {
      method: "POST",
    }),

  uploadLogo: async (id: string, file: File): Promise<Brand> => {
    const formData = new FormData();
    formData.append("file", file);
    return request<Brand>(`/brands/${id}/upload-logo`, {
      method: "POST",
      body: formData,
    });
  },

  extract: async (logo?: File, websiteUrl?: string, brandName?: string): Promise<BrandExtractResponse> => {
    const formData = new FormData();
    if (logo) formData.append("logo", logo);
    if (websiteUrl) formData.append("website_url", websiteUrl);
    if (brandName) formData.append("brand_name", brandName);
    
    const url = `${API_URL}/api/v1/brands/extract`;
    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });
    if (!response.ok) {
      throw new ApiError(response.status, "Brand extraction failed");
    }
    return response.json();
  },

  extractAndCreate: async (
    name: string,
    logo?: File,
    websiteUrl?: string,
    isDefault?: boolean
  ): Promise<Brand> => {
    const formData = new FormData();
    formData.append("name", name);
    if (logo) formData.append("logo", logo);
    if (websiteUrl) formData.append("website_url", websiteUrl);
    if (isDefault) formData.append("is_default", "true");

    const url = `${API_URL}/api/v1/brands/extract-and-create`;
    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });
    if (!response.ok) {
      throw new ApiError(response.status, "Brand extraction and creation failed");
    }
    return response.json();
  },

  getSuggestedScenes: (id: string) =>
    request<BrandScenesResponse>(`/brands/${id}/suggested-scenes`),
};
