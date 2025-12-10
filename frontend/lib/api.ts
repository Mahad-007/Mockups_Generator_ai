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
  getTemplates: (category?: string) => {
    const params = category ? `?category=${category}` : "";
    return request<{ templates: SceneTemplate[] }>(`/scenes/templates${params}`);
  },

  getCategories: () =>
    request<{ categories: string[] }>("/scenes/categories"),
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

export interface MockupGenerateRequest {
  product_id: string;
  scene_template_id?: string;
  custom_prompt?: string;
}

export interface MockupResponse {
  id: string;
  product_id: string;
  image_url: string;
  scene_template_id: string | null;
  prompt_used: string | null;
  created_at: string;
}

export interface SceneTemplate {
  id: string;
  name: string;
  category: string;
  tags: string[];
}
