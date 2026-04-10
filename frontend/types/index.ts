export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface ApiError {
  detail?: string;
  message?: string;
}

export interface DocumentItem {
  _id: string;
  doc_id: string;
  user_id: string;
  filename: string;
  file_size: number;
  created_at: string;
  status: string;
}

export interface DocumentsResponse {
  user_id: string;
  documents: DocumentItem[];
  count: number;
}

export interface UploadResponse {
  message: string;
  doc_id: string;
  filename: string;
  outputs: string;
  chunks_file: string;
  index_dir: string;
  user_id: string;
}
