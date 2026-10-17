import React, { useState, useEffect } from 'react';
import type { Product } from '../types';
import { getProducts } from '../services/api';

interface HomePageProps {
  onSearch: (query: string) => void;
  onSelectProduct: (productId: number) => void;
  onAddToCart: (productId: number) => void;
}

export const HomePage: React.FC<HomePageProps> = ({
  onSearch,
  onSelectProduct,
  onAddToCart,
}) => {
  const [query, setQuery] = useState('');
  const [featuredProducts, setFeaturedProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getProducts(8, 0)
      .then((prods) => setFeaturedProducts(prods))
      .catch((err) => console.error('Failed to load featured products:', err))
      .finally(() => setLoading(false));
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  const categories = [
    { label: 'Work Desks', query: 'wooden study computer desk', icon: '💻' },
    { label: 'Ergonomic Chairs', query: 'ergonomic leather office chair', icon: '🪑' },
    { label: 'Dining Tables', query: 'round solid oak dining table', icon: '🍽️' },
    { label: 'Sofas & Couches', query: 'velvet fabric 2-seater sofa', icon: '🛋️' },
    { label: 'Platform Beds', query: 'wood platform king bed', icon: '🛏️' },
  ];

  return (
    <div className="container" style={{ paddingBottom: '60px' }}>
      {/* Hero Section */}
      <section style={{ textAlign: 'center', padding: '60px 0 40px', maxWidth: '840px', margin: '0 auto' }}>
        <div style={{ display: 'inline-flex', gap: '8px', marginBottom: '16px' }}>
          <span className="badge badge-indigo">PostgreSQL 16 + pgvector</span>
          <span className="badge badge-emerald">Deterministic Ranking</span>
          <span className="badge badge-amber">LangGraph Agent</span>
        </div>

        <h1 style={{ fontSize: '3.2rem', fontWeight: 800, letterSpacing: '-0.03em', marginBottom: '18px' }}>
          Intelligent Furniture Discovery Powered by AI
        </h1>

        <p style={{ fontSize: '1.15rem', color: 'var(--text-secondary)', marginBottom: '36px', lineHeight: 1.6 }}>
          Discover the perfect furniture pieces using natural language. FurniAI unites vector semantic retrieval, 
          lexical full-text indexing, deterministic scoring, and grounded RAG care guides.
        </p>

        {/* Big Search Bar */}
        <form onSubmit={handleSearchSubmit} style={{ position: 'relative', maxWidth: '640px', margin: '0 auto' }}>
          <input
            type="text"
            className="search-input"
            placeholder="Try: 'minimalist wooden desk for small room under ₹15,000'..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{
              padding: '18px 24px',
              paddingRight: '140px',
              fontSize: '1.05rem',
              boxShadow: '0 10px 30px rgba(0,0,0,0.4)',
            }}
          />
          <button
            type="submit"
            className="btn-primary"
            style={{
              position: 'absolute',
              right: '8px',
              top: '8px',
              bottom: '8px',
              padding: '0 22px',
            }}
          >
            Search
          </button>
        </form>

        {/* Quick Category Suggestions */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', flexWrap: 'wrap', marginTop: '20px' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', alignSelf: 'center' }}>Popular:</span>
          {categories.map((cat, idx) => (
            <button
              key={idx}
              className="badge badge-slate"
              style={{ cursor: 'pointer', padding: '6px 12px', fontSize: '0.8rem', textTransform: 'none' }}
              onClick={() => onSearch(cat.query)}
            >
              <span style={{ marginRight: '4px' }}>{cat.icon}</span> {cat.label}
            </button>
          ))}
        </div>
      </section>

      {/* Architecture Highlights Banner */}
      <section style={{ margin: '40px 0' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
          <div className="glass-card" style={{ padding: '24px' }}>
            <div style={{ fontSize: '2rem', marginBottom: '12px' }}>🎯</div>
            <h3 style={{ fontSize: '1.15rem', marginBottom: '8px' }}>Deterministic Ranking</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              Formula-driven Python ranking (0.50 × S_semantic + 0.20 × S_keyword + 0.15 × S_rating + 0.15 × S_price). Transparent and reproducible.
            </p>
          </div>

          <div className="glass-card" style={{ padding: '24px' }}>
            <div style={{ fontSize: '2rem', marginBottom: '12px' }}>📖</div>
            <h3 style={{ fontSize: '1.15rem', marginBottom: '8px' }}>Grounded RAG Knowledge</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              PostgreSQL vector retrieval of assembly manuals, care guides, and FAQs with strict chunk citations and zero hallucination.
            </p>
          </div>

          <div className="glass-card" style={{ padding: '24px' }}>
            <div style={{ fontSize: '2rem', marginBottom: '12px' }}>🛡️</div>
            <h3 style={{ fontSize: '1.15rem', marginBottom: '8px' }}>Human-in-the-Loop Safety</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              LangGraph interrupts execution before checkout. PostgreSQL orders are only placed upon explicit human confirmation.
            </p>
          </div>
        </div>
      </section>

      {/* Featured Catalog Products */}
      <section style={{ marginTop: '50px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '24px' }}>
          <div>
            <span className="badge badge-indigo">Catalog Showcase</span>
            <h2 style={{ fontSize: '1.8rem', marginTop: '6px' }}>Curated Furniture Collections</h2>
          </div>
          <button 
            className="btn-secondary" 
            onClick={() => onSearch('desk')}
          >
            Explore All 5,000 Products &rarr;
          </button>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
            Loading products from PostgreSQL...
          </div>
        ) : (
          <div className="products-grid">
            {featuredProducts.map((product) => (
              <div
                key={product.product_id}
                className="glass-card glass-card-interactive"
                style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}
              >
                {/* Visual placeholder with stylish gradient icon */}
                <div
                  style={{
                    height: '180px',
                    background: 'linear-gradient(135deg, rgba(30,41,69,0.9), rgba(15,22,38,0.95))',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    position: 'relative',
                    borderBottom: '1px solid var(--border-subtle)',
                  }}
                >
                  <span style={{ fontSize: '3.5rem', opacity: 0.85 }}>
                    {product.category === 'Desk' ? '💻' :
                     product.category === 'Chair' ? '🪑' :
                     product.category === 'Table' ? '🍽️' :
                     product.category === 'Sofa' ? '🛋️' : '🛏️'}
                  </span>
                  <div style={{ position: 'absolute', top: '12px', left: '12px' }}>
                    <span className="badge badge-slate">{product.category}</span>
                  </div>
                  <div style={{ position: 'absolute', top: '12px', right: '12px' }}>
                    <span className="badge badge-amber">★ {product.rating.toFixed(1)}</span>
                  </div>
                </div>

                <div style={{ padding: '20px', flex: 1, display: 'flex', flexDirection: 'column' }}>
                  <h3
                    style={{
                      fontSize: '1.05rem',
                      marginBottom: '8px',
                      cursor: 'pointer',
                      color: 'var(--text-primary)',
                    }}
                    onClick={() => onSelectProduct(product.product_id)}
                  >
                    {product.name}
                  </h3>

                  <p
                    style={{
                      fontSize: '0.85rem',
                      color: 'var(--text-secondary)',
                      marginBottom: '16px',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                      flex: 1,
                    }}
                  >
                    {product.description}
                  </p>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <div>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Price</span>
                      <span style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                        ₹{product.price.toLocaleString()}
                      </span>
                    </div>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      Material: {product.material}
                    </span>
                  </div>

                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      className="btn-secondary"
                      style={{ flex: 1, padding: '8px 12px', fontSize: '0.85rem' }}
                      onClick={() => onSelectProduct(product.product_id)}
                    >
                      Inspect Specs
                    </button>
                    <button
                      className="btn-primary"
                      style={{ padding: '8px 16px', fontSize: '0.85rem' }}
                      onClick={() => onAddToCart(product.product_id)}
                    >
                      + Cart
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};
