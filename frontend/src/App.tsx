import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { AIAssistantDrawer } from './components/AIAssistantDrawer';
import { HomePage } from './pages/HomePage';
import { SearchResultsPage } from './pages/SearchResultsPage';
import { ProductDetailPage } from './pages/ProductDetailPage';
import { CartPage } from './pages/CartPage';
import { OrderSummaryPage } from './pages/OrderSummaryPage';
import { getCart, addToCart } from './services/api';

export function App() {
  const [activeTab, setActiveTab] = useState<'home' | 'search' | 'product' | 'cart' | 'order'>('home');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [confirmedOrderId, setConfirmedOrderId] = useState<number | null>(null);
  const [cartCount, setCartCount] = useState(0);
  const [isAgentOpen, setIsAgentOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const refreshCartCount = async () => {
    try {
      const c = await getCart(1);
      const count = c.items?.reduce((s, i) => s + i.quantity, 0) || 0;
      setCartCount(count);
    } catch {
      // Cart might be empty or fresh
    }
  };

  useEffect(() => {
    refreshCartCount();
  }, []);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleSearch = (q: string) => {
    setSearchQuery(q);
    setActiveTab('search');
  };

  const handleSelectProduct = (productId: number) => {
    setSelectedProductId(productId);
    setActiveTab('product');
  };

  const handleAddToCart = async (productId: number, quantity = 1) => {
    try {
      await addToCart(productId, quantity, 1);
      await refreshCartCount();
      showToast(`✓ Added ${quantity} item(s) to Cart!`);
    } catch (err: any) {
      alert(err.message || 'Failed to add item to cart');
    }
  };

  const handleOrderSuccess = (orderId: number) => {
    setConfirmedOrderId(orderId);
    refreshCartCount();
    setActiveTab('order');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Toast Notification */}
      {toastMessage && (
        <div
          style={{
            position: 'fixed',
            top: '84px',
            right: '24px',
            zIndex: 200,
            background: 'linear-gradient(135deg, #10b981, #059669)',
            color: '#fff',
            padding: '12px 20px',
            borderRadius: 'var(--radius-sm)',
            boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
            fontWeight: 600,
            fontSize: '0.9rem',
            animation: 'fadeIn 0.2s ease-out',
          }}
        >
          {toastMessage}
        </div>
      )}

      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={(tab) => setActiveTab(tab as any)}
        cartCount={cartCount}
        openAgent={() => setIsAgentOpen((prev) => !prev)}
        isAgentOpen={isAgentOpen}
      />

      {/* Main Pages */}
      <main style={{ flex: 1 }}>
        {activeTab === 'home' && (
          <HomePage
            onSearch={handleSearch}
            onSelectProduct={handleSelectProduct}
            onAddToCart={(pid) => handleAddToCart(pid, 1)}
          />
        )}

        {activeTab === 'search' && (
          <SearchResultsPage
            initialQuery={searchQuery}
            onSelectProduct={handleSelectProduct}
            onAddToCart={(pid) => handleAddToCart(pid, 1)}
          />
        )}

        {activeTab === 'product' && selectedProductId && (
          <ProductDetailPage
            productId={selectedProductId}
            onBack={() => setActiveTab('search')}
            onAddToCart={handleAddToCart}
          />
        )}

        {activeTab === 'cart' && (
          <CartPage
            onOrderSuccess={handleOrderSuccess}
            onExploreProducts={() => setActiveTab('home')}
          />
        )}

        {activeTab === 'order' && confirmedOrderId && (
          <OrderSummaryPage
            orderId={confirmedOrderId}
            onContinueShopping={() => setActiveTab('home')}
          />
        )}
      </main>

      {/* AI Assistant Floating Drawer */}
      <AIAssistantDrawer
        isOpen={isAgentOpen}
        onClose={() => setIsAgentOpen(false)}
        onOrderCreated={handleOrderSuccess}
      />

      {/* Footer */}
      <footer style={{ borderTop: '1px solid var(--border-subtle)', padding: '24px 0', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
        <div className="container">
          <p>FurniAI — Modular Monolith AI Architecture &bull; PostgreSQL 16 &bull; Redis 7 &bull; LangGraph &bull; Groq</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
