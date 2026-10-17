import type { Product, KnowledgeChunk, Cart, Order, AgentChatResponse } from '../types';

const API_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');

export async function hybridSearch(query: string, limit = 20): Promise<Product[]> {
  const res = await fetch(`${API_BASE}/products/hybrid-search?q=${encodeURIComponent(query)}&limit=${limit}`);
  if (!res.ok) {
    throw new Error(`Search failed: ${res.statusText}`);
  }
  return res.json();
}

export async function getProducts(limit = 20, offset = 0): Promise<Product[]> {
  const res = await fetch(`${API_BASE}/products/?limit=${limit}&offset=${offset}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch products: ${res.statusText}`);
  }
  return res.json();
}

export async function getProduct(productId: number): Promise<Product> {
  const res = await fetch(`${API_BASE}/products/${productId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch product ${productId}`);
  }
  return res.json();
}

export async function getProductKnowledge(productId: number, query: string): Promise<KnowledgeChunk[]> {
  const res = await fetch(`${API_BASE}/products/${productId}/knowledge?q=${encodeURIComponent(query)}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch knowledge chunks`);
  }
  return res.json();
}

export async function getCart(userId = 1): Promise<Cart> {
  const res = await fetch(`${API_BASE}/cart/${userId}`);
  if (!res.ok) {
    throw new Error(`Failed to load cart for user ${userId}`);
  }
  const data = await res.json();
  
  // Hydrate items with product details for display
  if (data.items && data.items.length > 0) {
    const enrichedItems = await Promise.all(
      data.items.map(async (item: any) => {
        try {
          const product = await getProduct(item.product_id);
          return { ...item, product };
        } catch {
          return item;
        }
      })
    );
    data.items = enrichedItems;
  }
  return data;
}

export async function addToCart(productId: number, quantity = 1, userId = 1): Promise<any> {
  const res = await fetch(`${API_BASE}/cart/items`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      product_id: productId,
      quantity,
    }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to add item to cart');
  }
  return res.json();
}

export async function updateCartItem(itemId: number, quantity: number): Promise<any> {
  const res = await fetch(`${API_BASE}/cart/items/${itemId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ quantity }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to update cart item');
  }
  return res.json();
}

export async function createOrder(idempotencyKey: string, userId = 1): Promise<Order> {
  const res = await fetch(`${API_BASE}/orders/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Idempotency-Key': idempotencyKey,
    },
    body: JSON.stringify({ user_id: userId }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Checkout failed');
  }
  return res.json();
}

export async function getOrder(orderId: number): Promise<Order> {
  const res = await fetch(`${API_BASE}/orders/${orderId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch order ${orderId}`);
  }
  return res.json();
}

export async function chatWithAgent(
  message: string,
  threadId?: string,
  resumeApproval?: boolean,
  userId = 1
): Promise<AgentChatResponse> {
  const res = await fetch(`${API_BASE}/agent/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      thread_id: threadId,
      resume_approval: resumeApproval,
      user_id: userId,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Agent chat error');
  }
  return res.json();
}
