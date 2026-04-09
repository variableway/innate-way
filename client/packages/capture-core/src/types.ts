export interface Category {
  name: string;
  display_name: string;
  count: number;
  created_at: string | null;
  last_entry: string | null;
  description: string;
}

export interface CategoryCreateInput {
  name: string;
  display_name?: string;
  description?: string;
}

export const MAX_CATEGORIES = 10;
