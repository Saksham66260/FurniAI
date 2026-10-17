import React, { useState, useEffect } from 'react';
import type { Product } from '../types';
import { hybridSearch } from '../services/api';
import { ScoreBreakdownModal } from '../components/ScoreBreakdownModal';

interface SearchResultsPageProps {
  initialQuery: string;
  onSelectProduct: (productId: number) => void;
  onAddToCart: (productId: number) => void;
}

export const SearchResultsPage: React.FC<SearchResultsPageProps> = ({
  initialQuery,
  onSelectProduct,
  onAddToCart,
}) => {
  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedProductForBreakdown, setSelectedProductForBreakdown] = useState<Product | null>(null);

  // Filters
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [maxPrice, setMaxPrice] = useState<number>(100000);

  const performSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await hybridSearch(searchQuery, 30);
      setResults(data);
    } catch (err: any) {
      setError(err.message || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialQuery) {
      setQuery(initialQuery);
      performSearch(initialQuery);
    }
  }, [initialQuery]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    performSearch(query);
  };

  // Filtered results
  const filteredResults = results.filter((product) => {
    const matchesCategory =
      categoryFilter === 'all' || product.category.toLowerCase() === categoryFilter.toLowerCase();
    const matchesPrice = product.price <= maxPrice;
    return matchesCategory && matchesPrice;
  });

  const categories = ['all', 'Desk', 'Chair', 'Table', 'Sofa', 'Bed'];

  return (
    <div className="container" style={{ padding: '30px 24px 60px' }}>
      {/* Search Header */}
      <div style={{ marginBottom: '32px' }}>
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '12px', maxWidth: '720px', marginBottom: '16px' }}>
          <input
            type="text"
            className="search-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search catalog with natural language or keywords..."
            style={{ fontSize: '1rem', padding: '14px 20px' }}
          />
          <button type="submit" className="btn-primary" style={{ padding: '0 24px' }}>
            Search
          </button>
        </form>

        {/* Demo Spec Query Button */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Specification Demo Query:</span>
          <button
            className="badge badge-amber"
            style={{ cursor: 'pointer', padding: '4px 10px', textTransform: 'none' }}
            onClick={() => {
              const q = 'minimalist wooden desk for small room under ₹15,000';
              setQuery(q);
              performSearch(q);
            }}
          >
            "minimalist wooden desk for small room under ₹15,000"
          </button>
          <button
            className="badge badge-indigo"
            style={{ cursor: 'pointer', padding: '4px 10px', textTransform: 'none' }}
            onClick={() => {
              const q = 'ergonomic leather chair';
              setQuery(q);
              performSearch(q);
            }}
          >
            "ergonomic leather chair"
          </button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div
        className="glass-card"
        style={{
          padding: '16px 20px',
          marginBottom: '28px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Category:</span>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className="badge"
              style={{
                background: categoryFilter === cat ? 'var(--accent-primary)' : 'rgba(255,255,255,0.06)',
                color: categoryFilter === cat ? '#fff' : 'var(--text-secondary)',
                cursor: 'pointer',
                padding: '5px 12px',
              }}
            >
              {cat === 'all' ? 'All Categories' : cat}
            </button>
          ))}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Max Price: ₹{maxPrice.toLocaleString()}</span>
          <input
            type="range"
            min="5000"
            max="150000"
            step="5000"
            value={maxPrice}
            onChange={(e) => setMaxPrice(Number(e.target.value))}
            style={{ accentColor: 'var(--accent-primary)', cursor: 'pointer' }}
          />
        </div>
      </div>

      {/* Results Section */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '80px 0', color: 'var(--text-muted)' }}>
          <div style={{ fontSize: '2rem', marginBottom: '12px' }}>⚡</div>
          Executing hybrid retrieval (pgvector cosine + tsvector GIN) & deterministic ranking...
        </div>
      ) : error ? (
        <div style={{ padding: '24px', background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.3)', borderRadius: 'var(--radius-md)', color: '#fca5a5' }}>
          ⚠️ {error}
        </div>
      ) : filteredResults.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
          No products matched your search or filters. Try adjusting your query.
        </div>
      ) : (
        <div>
          <div style={{ marginBottom: '16px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Found <strong style={{ color: 'var(--text-primary)' }}>{filteredResults.length}</strong> ranked products:
          </div>

          <div className="products-grid">
            {filteredResults.map((product, rankIdx) => (
              <div
                key={product.product_id}
                className="glass-card glass-card-interactive"
                style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}
              >
                {/* Product Header / Visual */}
                <div
                  style={{
                    height: '170px',
                    background: 'linear-gradient(135deg, rgba(30,41,69,0.8), rgba(15,22,38,0.9))',
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

                  {/* Rank badge */}
                  <div style={{ position: 'absolute', top: '12px', left: '12px' }}>
                    <span className="badge badge-slate" style={{ fontWeight: 700 }}>
                      #{rankIdx + 1}
                    </span>
                  </div>

                  {/* Deterministic Score Badge */}
                  {product.score !== undefined && (
                    <div style={{ position: 'absolute', top: '12px', right: '12px' }}>
                      <span 
                        className="badge badge-indigo"
                        style={{ cursor: 'pointer' }}
                        title="Click to see score breakdown"
                        onClick={() => setSelectedProductForBreakdown(product)}
                      >
                        Score: {(product.score * 100).toFixed(1)} ℹ️
                      </span>
                    </div>
                  )}
                </div>

                {/* Details */}
                <div style={{ padding: '18px', flex: 1, display: 'flex', flexDirection: 'column' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{product.category} &bull; {product.material}</span>
                    <span style={{ fontSize: '0.8rem', color: 'var(--accent-secondary)' }}>★ {product.rating.toFixed(1)}</span>
                  </div>

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
                      fontSize: '0.82rem',
                      color: 'var(--text-secondary)',
                      marginBottom: '14px',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                      flex: 1,
                    }}
                  >
                    {product.description}
                  </p>

                  {/* Price & Action */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '14px' }}>
                    <div>
                      <span style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                        ₹{product.price.toLocaleString()}
                      </span>
                    </div>
                    {product.score_breakdown && (
                      <button
                        style={{ fontSize: '0.75rem', color: '#818cf8', textDecoration: 'underline' }}
                        onClick={() => setSelectedProductForBreakdown(product)}
                      >
                        Breakdown
                      </button>
                    )}
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
                      style={{ padding: '8px 14px', fontSize: '0.85rem' }}
                      onClick={() => onAddToCart(product.product_id)}
                    >
                      + Cart
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Score Breakdown Modal */}
      <ScoreBreakdownModal
        product={selectedProductForBreakdown}
        onClose={() => setSelectedProductForBreakdown(null)}
      />
    </div>
  );
};
