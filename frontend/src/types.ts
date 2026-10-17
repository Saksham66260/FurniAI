export interface ScoreBreakdown {
  semantic: number;
  keyword: number;
  rating: number;
  price: number;
}

export interface Product {
  product_id: number;
  sku: string;
  name: string;
  category: string;
  subcategory: string;
  price: number;
  material: string;
  style: string;
  color: string;
  rating: number;
  review_count: number;
  description: string;
  dimensions: {
    width?: number;
    depth?: number;
    height?: number;
    unit?: string;
    [key: string]: any;
  };
  weight: number;
  features: string[];
  score?: number;
  score_breakdown?: ScoreBreakdown;
}

export interface KnowledgeChunk {
  chunk_id: number;
  product_id: number;
  document_type: string;
  content: string;
  similarity: number;
}

export interface CartItem {
  id: number;
  product_id: number;
  quantity: number;
  product?: Product;
}

export interface Cart {
  cart_id: number;
  user_id: number;
  items: CartItem[];
}

export interface OrderItem {
  order_item_id: number;
  product_id: number;
  quantity: number;
  unit_price: number;
}

export interface Order {
  id: number;
  user_id: number;
  status: string;
  total_amount: number;
  items: OrderItem[];
}

export interface AgentChatResponse {
  thread_id: string;
  status: 'COMPLETED' | 'APPROVAL_REQUIRED' | 'ERROR';
  reply: string;
  tool_calls: Array<{
    name: string;
    args: Record<string, any>;
  }>;
  approval_required: boolean;
  approval_prompt: string | null;
  checkout_result: {
    success: boolean;
    order_id?: number;
    status?: string;
    total_amount?: number;
    message?: string;
  } | null;
}
