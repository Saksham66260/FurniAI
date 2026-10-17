import React, { useState, useEffect } from 'react';
import type { Cart } from '../types';
import { getCart, updateCartItem, createOrder } from '../services/api';

interface CartPageProps {
  onOrderSuccess: (orderId: number) => void;
  onExploreProducts: () => void;
}

export const CartPage: React.FC<CartPageProps> = ({
  onOrderSuccess,
  onExploreProducts,
}) => {
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Human-in-the-Loop Checkout Modal State
  const [isConfirmModalOpen, setIsConfirmModalOpen] = useState(false);
  const [processingOrder, setProcessingOrder] = useState(false);
  const [idempotencyKey, setIdempotencyKey] = useState('');

  const loadCart = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getCart(1);
      setCart(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load cart');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCart();
  }, []);

  const handleUpdateQuantity = async (itemId: number, newQty: number) => {
    if (newQty < 1) return;
    try {
      await updateCartItem(itemId, newQty);
      await loadCart();
    } catch (err: any) {
      alert(err.message || 'Failed to update quantity');
    }
  };

  const handleStartCheckout = () => {
    // Generate fresh idempotency key
    const newKey = `checkout-ui-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`;
    setIdempotencyKey(newKey);
    setIsConfirmModalOpen(true);
  };

  const handleConfirmCheckout = async () => {
    setProcessingOrder(true);
    try {
      const order = await createOrder(idempotencyKey, 1);
      setIsConfirmModalOpen(false);
      onOrderSuccess(order.id);
    } catch (err: any) {
      alert(`Checkout failed: ${err.message}`);
    } finally {
      setProcessingOrder(false);
    }
  };

  const calculateTotal = () => {
    if (!cart?.items) return 0;
    return cart.items.reduce((acc, item) => {
      const price = item.product?.price || 0;
      return acc + price * item.quantity;
    }, 0);
  };

  if (loading) {
    return (
      <div className="container" style={{ padding: '80px 24px', textAlign: 'center', color: 'var(--text-muted)' }}>
        Loading your cart from PostgreSQL...
      </div>
    );
  }

  const items = cart?.items || [];
  const total = calculateTotal();

  return (
    <div className="container" style={{ padding: '30px 24px 80px', maxWidth: '960px' }}>
      <h1 style={{ fontSize: '2.2rem', marginBottom: '8px' }}>Your Shopping Cart</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>
        Authenticated as <strong style={{ color: 'var(--text-primary)' }}>User #1</strong> &bull; PostgreSQL Cart #{cart?.cart_id || 1}
      </p>

      {error ? (
        <div style={{ padding: '20px', background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.3)', borderRadius: 'var(--radius-md)', color: '#fca5a5' }}>
          ⚠️ {error}
        </div>
      ) : items.length === 0 ? (
        <div className="glass-card" style={{ padding: '60px 20px', textAlign: 'center' }}>
          <span style={{ fontSize: '3rem', display: 'block', marginBottom: '16px' }}>🛒</span>
          <h3 style={{ fontSize: '1.25rem', marginBottom: '8px' }}>Your cart is empty</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
            Discover our catalog with hybrid semantic search.
          </p>
          <button className="btn-primary" onClick={onExploreProducts}>
            Explore Catalog
          </button>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '30px', alignItems: 'start' }}>
          {/* Cart Items List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {items.map((item) => (
              <div
                key={item.id}
                className="glass-card"
                style={{ padding: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
              >
                <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                  <div
                    style={{
                      width: '64px',
                      height: '64px',
                      borderRadius: 'var(--radius-sm)',
                      background: 'rgba(255,255,255,0.05)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '1.8rem',
                    }}
                  >
                    {item.product?.category === 'Desk' ? '💻' :
                     item.product?.category === 'Chair' ? '🪑' :
                     item.product?.category === 'Table' ? '🍽️' :
                     item.product?.category === 'Sofa' ? '🛋️' : '🛏️'}
                  </div>
                  <div>
                    <h4 style={{ fontSize: '1rem', marginBottom: '4px' }}>
                      {item.product?.name || `Product #${item.product_id}`}
                    </h4>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      SKU: {item.product?.sku || 'N/A'} &bull; Unit: ₹{(item.product?.price || 0).toLocaleString()}
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                  {/* Quantity controls */}
                  <div style={{ display: 'flex', alignItems: 'center', background: 'rgba(255,255,255,0.06)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                    <button
                      style={{ padding: '6px 10px', color: 'var(--text-primary)' }}
                      onClick={() => handleUpdateQuantity(item.id, item.quantity - 1)}
                    >
                      -
                    </button>
                    <span style={{ padding: '0 8px', fontWeight: 600, fontSize: '0.9rem' }}>
                      {item.quantity}
                    </span>
                    <button
                      style={{ padding: '6px 10px', color: 'var(--text-primary)' }}
                      onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                    >
                      +
                    </button>
                  </div>

                  <div style={{ minWidth: '90px', textAlign: 'right', fontWeight: 700, fontSize: '1.1rem' }}>
                    ₹{((item.product?.price || 0) * item.quantity).toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Order Summary Checkout Card */}
          <div className="glass-card" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '16px' }}>Order Summary</h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px', fontSize: '0.9rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                <span>Subtotal ({items.length} items)</span>
                <span>₹{total.toLocaleString()}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                <span>Fulfillment Allocation</span>
                <span style={{ color: 'var(--accent-emerald)' }}>Free Delivery</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                <span>Warehouse Scoring</span>
                <span>Automated Fit</span>
              </div>
              <div style={{ height: '1px', background: 'var(--border-subtle)', margin: '4px 0' }} />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '1.2rem', fontWeight: 800 }}>
                <span>Total</span>
                <span>₹{total.toLocaleString()}</span>
              </div>
            </div>

            <button
              className="btn-amber"
              style={{ width: '100%', padding: '14px', fontSize: '1rem', marginBottom: '12px' }}
              onClick={handleStartCheckout}
            >
              🛡️ Review & Place Order
            </button>

            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center', lineHeight: 1.4 }}>
              Human Approval Gate: You will be asked to confirm before inventory row locks are acquired.
            </p>
          </div>
        </div>
      )}

      {/* Human-in-the-Loop Confirmation Modal */}
      {isConfirmModalOpen && (
        <div className="modal-overlay" onClick={() => !processingOrder && setIsConfirmModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
              <span style={{ fontSize: '1.6rem' }}>🛡️</span>
              <div>
                <span className="badge badge-amber">Human-in-the-Loop Gate</span>
                <h3 style={{ fontSize: '1.25rem', marginTop: '4px' }}>Confirm Order Creation</h3>
              </div>
            </div>

            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '18px', lineHeight: 1.5 }}>
              In accordance with FurniAI's architectural constitution, checkout operations require explicit human approval. 
              Executing this will acquire transactional row-level locks (<code style={{ color: '#a5b4fc' }}>SELECT ... FOR UPDATE</code>), 
              verify inventory availability, create order items, and register an idempotency key.
            </p>

            <div style={{ background: 'rgba(0,0,0,0.3)', padding: '14px', borderRadius: 'var(--radius-sm)', marginBottom: '20px', fontSize: '0.85rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Target Total:</span>
                <strong style={{ color: 'var(--text-primary)', fontSize: '1.05rem' }}>₹{total.toLocaleString()}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Items to Reserve:</span>
                <span>{items.reduce((s, i) => s + i.quantity, 0)} units</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Idempotency Key:</span>
                <code style={{ fontSize: '0.75rem', color: '#fcd34d' }}>{idempotencyKey}</code>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                className="btn-primary"
                style={{ flex: 1, padding: '12px', background: 'linear-gradient(135deg, #10b981, #059669)' }}
                onClick={handleConfirmCheckout}
                disabled={processingOrder}
              >
                {processingOrder ? 'Reserving Inventory...' : '✓ Approve & Create Order'}
              </button>
              <button
                className="btn-secondary"
                style={{ padding: '12px 18px' }}
                onClick={() => setIsConfirmModalOpen(false)}
                disabled={processingOrder}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
