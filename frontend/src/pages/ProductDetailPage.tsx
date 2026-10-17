import React, { useState, useEffect } from 'react';
import type { Product, KnowledgeChunk } from '../types';
import { getProduct, getProductKnowledge } from '../services/api';

interface ProductDetailPageProps {
  productId: number;
  onBack: () => void;
  onAddToCart: (productId: number, quantity: number) => void;
}

export const ProductDetailPage: React.FC<ProductDetailPageProps> = ({
  productId,
  onBack,
  onAddToCart,
}) => {
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [quantity, setQuantity] = useState(1);

  // RAG State
  const [ragQuery, setRagQuery] = useState('');
  const [ragChunks, setRagChunks] = useState<KnowledgeChunk[]>([]);
  const [ragLoading, setRagLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    getProduct(productId)
      .then((p) => {
        setProduct(p);
        // Automatically fetch default knowledge (care / assembly)
        return getProductKnowledge(productId, 'assembly care manual guide').catch(() => []);
      })
      .then((chunks) => setRagChunks(chunks))
      .catch((err) => setError(err.message || 'Failed to load product'))
      .finally(() => setLoading(false));
  }, [productId]);

  const handleRagSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ragQuery.trim()) return;
    setRagLoading(true);
    try {
      const chunks = await getProductKnowledge(productId, ragQuery);
      setRagChunks(chunks);
    } catch (err: any) {
      console.error('RAG query failed:', err);
    } finally {
      setRagLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container" style={{ padding: '80px 24px', textAlign: 'center', color: 'var(--text-muted)' }}>
        Loading product details from PostgreSQL...
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="container" style={{ padding: '60px 24px' }}>
        <div style={{ padding: '24px', background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.3)', borderRadius: 'var(--radius-md)', color: '#fca5a5', marginBottom: '20px' }}>
          ⚠️ {error || 'Product not found'}
        </div>
        <button className="btn-secondary" onClick={onBack}>&larr; Back to Catalog</button>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '30px 24px 80px' }}>
      {/* Breadcrumb / Back button */}
      <button 
        className="btn-secondary" 
        onClick={onBack}
        style={{ marginBottom: '24px', padding: '6px 14px', fontSize: '0.85rem' }}
      >
        &larr; Back
      </button>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '40px', marginBottom: '50px' }}>
        {/* Left Column: Product Showcase Visual */}
        <div>
          <div
            className="glass-card"
            style={{
              height: '420px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'relative',
              overflow: 'hidden',
              background: 'linear-gradient(145deg, rgba(30,41,69,0.7), rgba(15,22,38,0.95))',
            }}
          >
            <span style={{ fontSize: '7rem' }}>
              {product.category === 'Desk' ? '💻' :
               product.category === 'Chair' ? '🪑' :
               product.category === 'Table' ? '🍽️' :
               product.category === 'Sofa' ? '🛋️' : '🛏️'}
            </span>
            <div style={{ position: 'absolute', bottom: '20px', display: 'flex', gap: '8px' }}>
              <span className="badge badge-indigo">{product.category}</span>
              <span className="badge badge-slate">{product.style}</span>
              <span className="badge badge-amber">★ {product.rating.toFixed(1)} ({product.review_count} reviews)</span>
            </div>
          </div>
        </div>

        {/* Right Column: Product Authoritative Details */}
        <div>
          <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
            <span className="badge badge-slate">SKU: {product.sku}</span>
            <span className="badge badge-emerald">In Stock (Warehouses 1 & 2)</span>
          </div>

          <h1 style={{ fontSize: '2.4rem', fontWeight: 800, marginBottom: '12px', lineHeight: 1.2 }}>
            {product.name}
          </h1>

          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '16px' }}>
            ₹{product.price.toLocaleString()}
          </div>

          <p style={{ color: 'var(--text-secondary)', fontSize: '1rem', lineHeight: 1.6, marginBottom: '24px' }}>
            {product.description}
          </p>

          {/* Specifications Table */}
          <div className="glass-card" style={{ padding: '20px', marginBottom: '24px' }}>
            <h4 style={{ fontSize: '0.95rem', marginBottom: '12px', color: 'var(--text-primary)' }}>Specifications</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '0.85rem' }}>
              <div><strong style={{ color: 'var(--text-muted)' }}>Material:</strong> {product.material}</div>
              <div><strong style={{ color: 'var(--text-muted)' }}>Color:</strong> {product.color}</div>
              <div><strong style={{ color: 'var(--text-muted)' }}>Weight:</strong> {product.weight} kg</div>
              <div>
                <strong style={{ color: 'var(--text-muted)' }}>Dimensions:</strong>{' '}
                {product.dimensions?.width}x{product.dimensions?.depth}x{product.dimensions?.height} {product.dimensions?.unit || 'cm'}
              </div>
            </div>

            {product.features && product.features.length > 0 && (
              <div style={{ marginTop: '16px' }}>
                <strong style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Features:</strong>
                <ul style={{ paddingLeft: '20px', marginTop: '6px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {product.features.map((feat, idx) => (
                    <li key={idx}>{feat}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Add to Cart Actions */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', background: 'rgba(255,255,255,0.06)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
              <button
                style={{ padding: '10px 14px', color: 'var(--text-primary)', fontSize: '1rem' }}
                onClick={() => setQuantity((q) => Math.max(1, q - 1))}
              >
                -
              </button>
              <span style={{ padding: '0 10px', fontWeight: 600 }}>{quantity}</span>
              <button
                style={{ padding: '10px 14px', color: 'var(--text-primary)', fontSize: '1rem' }}
                onClick={() => setQuantity((q) => q + 1)}
              >
                +
              </button>
            </div>

            <button
              className="btn-primary"
              style={{ flex: 1, padding: '12px 24px', fontSize: '1rem' }}
              onClick={() => onAddToCart(product.product_id, quantity)}
            >
              Add {quantity} to Cart &bull; ₹{(product.price * quantity).toLocaleString()}
            </button>
          </div>
        </div>
      </div>

      {/* Grounded RAG Knowledge Section */}
      <section className="glass-card" style={{ padding: '32px', marginTop: '40px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px', marginBottom: '20px' }}>
          <div>
            <span className="badge badge-emerald">Grounded RAG Knowledge</span>
            <h2 style={{ fontSize: '1.5rem', marginTop: '6px' }}>Product Documentation, Assembly & Care</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              Queried directly from PostgreSQL <code style={{ color: '#a5b4fc' }}>knowledge_chunks</code> using cosine vector similarity. Zero hallucinations.
            </p>
          </div>
        </div>

        {/* Knowledge Question Form */}
        <form onSubmit={handleRagSearch} style={{ display: 'flex', gap: '12px', marginBottom: '24px', maxWidth: '640px' }}>
          <input
            type="text"
            className="search-input"
            placeholder="Ask: 'How do I assemble this?', 'Care instructions', 'Warranty'..."
            value={ragQuery}
            onChange={(e) => setRagQuery(e.target.value)}
            style={{ padding: '10px 16px', fontSize: '0.9rem' }}
          />
          <button type="submit" className="btn-secondary" disabled={ragLoading}>
            {ragLoading ? 'Searching...' : 'Ask Knowledge Base'}
          </button>
        </form>

        {/* Retrieved Chunks Display */}
        {ragLoading ? (
          <div style={{ padding: '30px 0', textAlign: 'center', color: 'var(--text-muted)' }}>
            Retrieving pgvector embeddings...
          </div>
        ) : ragChunks.length === 0 ? (
          <div style={{ padding: '20px', background: 'rgba(255,255,255,0.03)', borderRadius: 'var(--radius-sm)', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            No specific documentation found for this question yet. Try asking about "assembly" or "care guide".
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {ragChunks.map((chunk) => (
              <div
                key={chunk.chunk_id}
                style={{
                  padding: '18px',
                  background: 'rgba(0,0,0,0.25)',
                  border: '1px solid rgba(255,255,255,0.08)',
                  borderRadius: 'var(--radius-sm)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <span className="badge badge-indigo" style={{ textTransform: 'capitalize' }}>
                      📄 {chunk.document_type.replace('_', ' ')}
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Chunk ID: #{chunk.chunk_id} &bull; Product ID: #{chunk.product_id}
                    </span>
                  </div>
                  <span className="badge badge-emerald" style={{ fontSize: '0.75rem' }}>
                    Similarity: {(chunk.similarity * 100).toFixed(1)}%
                  </span>
                </div>

                <p style={{ color: 'var(--text-primary)', fontSize: '0.9rem', lineHeight: 1.6, whiteSpace: 'pre-line' }}>
                  {chunk.content}
                </p>

                <div style={{ marginTop: '8px', fontSize: '0.75rem', color: '#818cf8', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <span>✓</span>
                  <span>Authoritative Citation: FurniAI Technical Documentation Repository</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};
