import { API_CONFIG } from "@/config/api";
import type {
  ApiData,
  ApiDataList,
  FetchApiDataRequest,
  ApiError,
} from "@/types/api";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_CONFIG.BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const config: RequestInit = {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          (data as ApiError).detail || `HTTP error! status: ${response.status}`,
        );
      }

      return data as T;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error("Unknown error occurred");
    }
  }

  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>(API_CONFIG.ENDPOINTS.HEALTH);
  }

  async fetchData(request: FetchApiDataRequest): Promise<ApiData> {
    return this.request<ApiData>(API_CONFIG.ENDPOINTS.FETCH_DATA, {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  async getAllData(
    limit: number = 10,
    offset: number = 0,
  ): Promise<ApiDataList> {
    return this.request<ApiDataList>(
      `${API_CONFIG.ENDPOINTS.GET_ALL_DATA}?limit=${limit}&offset=${offset}`,
    );
  }

  async getDataById(id: string): Promise<ApiData> {
    return this.request<ApiData>(API_CONFIG.ENDPOINTS.GET_DATA_BY_ID(id));
  }
}

export const apiClient = new ApiClient();
