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
}

export interface MockupResponse {
  id: string;
  product_id: string;
  image_url: string;
  scene_template_id: string | null;
  prompt_used: string | null;
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
