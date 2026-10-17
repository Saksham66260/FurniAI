import React from 'react';
import type { Product } from '../types';

interface ScoreBreakdownModalProps {
  product: Product | null;
  onClose: () => void;
}

export const ScoreBreakdownModal: React.FC<ScoreBreakdownModalProps> = ({ product, onClose }) => {
  if (!product || !product.score_breakdown) return null;

  const { semantic, keyword, rating, price } = product.score_breakdown;
  const totalScore = product.score ?? 0;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <span className="badge badge-indigo">Deterministic Ranking</span>
            <h3 style={{ marginTop: '8px', fontSize: '1.25rem' }}>{product.name}</h3>
          </div>
          <button 
            onClick={onClose}
            style={{ fontSize: '1.5rem', color: 'var(--text-muted)', lineHeight: 1 }}
          >
            &times;
          </button>
        </div>

        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '20px' }}>
          FurniAI calculates search rank deterministically in Python using normalized signals. 
          The LLM does not fabricate rankings.
        </p>

        <div style={{ background: 'rgba(0,0,0,0.3)', padding: '12px 16px', borderRadius: 'var(--radius-sm)', marginBottom: '20px', fontFamily: 'monospace', fontSize: '0.85rem', color: '#a5b4fc' }}>
          Score = 0.50 × S<sub>sem</sub> + 0.20 × S<sub>kw</sub> + 0.15 × S<sub>rate</sub> + 0.15 × S<sub>price</sub>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '24px' }}>
          {/* Semantic Score */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '4px' }}>
              <span style={{ color: 'var(--text-primary)' }}>Semantic Similarity (50% weight)</span>
              <span style={{ fontWeight: 600, color: '#818cf8' }}>{(semantic * 100).toFixed(1)}%</span>
            </div>
            <div style={{ height: '8px', background: 'rgba(255,255,255,0.08)', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{ width: `${Math.min(100, Math.max(0, semantic * 100))}%`, height: '100%', background: 'linear-gradient(90deg, #6366f1, #818cf8)' }} />
            </div>
          </div>

          {/* Keyword Score */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '4px' }}>
              <span style={{ color: 'var(--text-primary)' }}>Keyword / Lexical Match (20% weight)</span>
              <span style={{ fontWeight: 600, color: '#38bdf8' }}>{(keyword * 100).toFixed(1)}%</span>
            </div>
            <div style={{ height: '8px', background: 'rgba(255,255,255,0.08)', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{ width: `${Math.min(100, Math.max(0, keyword * 100))}%`, height: '100%', background: 'linear-gradient(90deg, #0284c7, #38bdf8)' }} />
            </div>
          </div>

          {/* Rating Score */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '4px' }}>
              <span style={{ color: 'var(--text-primary)' }}>Customer Rating (15% weight)</span>
              <span style={{ fontWeight: 600, color: '#f59e0b' }}>{(rating * 100).toFixed(1)}% ({product.rating}★)</span>
            </div>
            <div style={{ height: '8px', background: 'rgba(255,255,255,0.08)', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{ width: `${Math.min(100, Math.max(0, rating * 100))}%`, height: '100%', background: 'linear-gradient(90deg, #d97706, #f59e0b)' }} />
            </div>
          </div>

          {/* Price Score */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '4px' }}>
              <span style={{ color: 'var(--text-primary)' }}>Price Affinity (15% weight)</span>
              <span style={{ fontWeight: 600, color: '#10b981' }}>{(price * 100).toFixed(1)}% (₹{product.price.toLocaleString()})</span>
            </div>
            <div style={{ height: '8px', background: 'rgba(255,255,255,0.08)', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{ width: `${Math.min(100, Math.max(0, price * 100))}%`, height: '100%', background: 'linear-gradient(90deg, #059669, #10b981)' }} />
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--border-subtle)', paddingTop: '16px' }}>
          <div>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Final Weighted Score</span>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)' }}>
              {(totalScore * 100).toFixed(2)} / 100
            </div>
          </div>
          <button className="btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
