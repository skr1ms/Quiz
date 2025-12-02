export interface ApiData {
  id: string;
  source: string;
  title: string;
  content: string;
  external_id: string | null;
  fetched_at: string;
  created_at: string;
  updated_at: string | null;
}

export interface ApiDataList {
  items: ApiData[];
  total: number;
  limit: number;
  offset: number;
}

export interface FetchApiDataRequest {
  number?: number;
}

export interface ApiError {
  detail: string;
}
