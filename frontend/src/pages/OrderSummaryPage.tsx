import React, { useState, useEffect } from 'react';
import type { Order } from '../types';
import { getOrder } from '../services/api';

interface OrderSummaryPageProps {
  orderId: number;
  onContinueShopping: () => void;
}

export const OrderSummaryPage: React.FC<OrderSummaryPageProps> = ({
  orderId,
  onContinueShopping,
}) => {
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getOrder(orderId)
      .then((ord) => setOrder(ord))
      .catch((err) => setError(err.message || 'Failed to load order'))
      .finally(() => setLoading(false));
  }, [orderId]);

  if (loading) {
    return (
      <div className="container" style={{ padding: '80px 24px', textAlign: 'center', color: 'var(--text-muted)' }}>
        Retrieving order #{orderId} from PostgreSQL...
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="container" style={{ padding: '60px 24px', maxWidth: '640px' }}>
        <div style={{ padding: '24px', background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.3)', borderRadius: 'var(--radius-md)', color: '#fca5a5', marginBottom: '20px' }}>
          ⚠️ {error || 'Order not found'}
        </div>
        <button className="btn-secondary" onClick={onContinueShopping}>&larr; Back to Catalog</button>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '40px 24px 80px', maxWidth: '760px' }}>
      {/* Success Badge */}
      <div className="glass-card" style={{ padding: '36px', textAlign: 'center', marginBottom: '32px' }}>
        <div
          style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            background: 'rgba(16,185,129,0.15)',
            border: '2px solid var(--accent-emerald)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '2rem',
            color: 'var(--accent-emerald)',
            marginBottom: '16px',
          }}
        >
          ✓
        </div>

        <span className="badge badge-emerald" style={{ marginBottom: '8px' }}>
          Transaction Committed & Reserved
        </span>

        <h1 style={{ fontSize: '2.2rem', marginBottom: '8px' }}>Order #{order.id} Confirmed!</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1rem', maxWidth: '540px', margin: '0 auto 24px' }}>
          Your furniture order was authoritatively created in PostgreSQL with transactional inventory reservation and Redis idempotency verification.
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <span className="badge badge-slate">Status: {order.status}</span>
          <span className="badge badge-slate">User ID: #{order.user_id}</span>
          <span className="badge badge-indigo">Total: ₹{Number(order.total_amount).toLocaleString()}</span>
        </div>
      </div>

      {/* Items Breakdown */}
      <div className="glass-card" style={{ padding: '28px', marginBottom: '32px' }}>
        <h3 style={{ fontSize: '1.2rem', marginBottom: '20px' }}>Purchased Order Items</h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {order.items.map((item) => (
            <div
              key={item.order_item_id}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '12px 16px',
                background: 'rgba(0,0,0,0.25)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <div>
                <strong style={{ fontSize: '0.95rem' }}>Product ID #{item.product_id}</strong>
                <span style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Quantity: {item.quantity} &bull; Unit Price Snapshot: ₹{Number(item.unit_price).toLocaleString()}
                </span>
              </div>
              <div style={{ fontWeight: 700, fontSize: '1.05rem' }}>
                ₹{(Number(item.unit_price) * item.quantity).toLocaleString()}
              </div>
            </div>
          ))}
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '24px', paddingTop: '16px', borderTop: '1px solid var(--border-subtle)' }}>
          <span style={{ fontSize: '1.1rem', fontWeight: 600 }}>Grand Total</span>
          <span style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-emerald)' }}>
            ₹{Number(order.total_amount).toLocaleString()}
          </span>
        </div>
      </div>

      {/* Action */}
      <div style={{ textAlign: 'center' }}>
        <button className="btn-primary" onClick={onContinueShopping} style={{ padding: '12px 28px' }}>
          Continue Shopping &rarr;
        </button>
      </div>
    </div>
  );
};
