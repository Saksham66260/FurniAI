import React from 'react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  cartCount: number;
  openAgent: () => void;
  isAgentOpen: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  cartCount,
  openAgent,
  isAgentOpen,
}) => {
  return (
    <header className="navbar">
      <div className="container navbar-inner">
        <button
          className="brand-logo"
          type="button"
          aria-label="Return to FurniAI home"
          onClick={() => setActiveTab('home')}
        >
          <img className="brand-logo-image" src="/furniai-logo.png" alt="FurniAI" />
        </button>

        <nav style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            className={activeTab === 'home' ? 'btn-secondary' : 'btn-secondary'}
            style={{
              background: activeTab === 'home' ? 'rgba(99, 102, 241, 0.2)' : undefined,
              borderColor: activeTab === 'home' ? 'var(--accent-primary)' : undefined,
            }}
            onClick={() => setActiveTab('home')}
          >
            Discover
          </button>
          <button
            className="btn-secondary"
            style={{
              background: activeTab === 'search' ? 'rgba(99, 102, 241, 0.2)' : undefined,
              borderColor: activeTab === 'search' ? 'var(--accent-primary)' : undefined,
            }}
            onClick={() => setActiveTab('search')}
          >
            Hybrid Search
          </button>
          <button
            className="btn-secondary"
            style={{
              background: activeTab === 'cart' ? 'rgba(99, 102, 241, 0.2)' : undefined,
              borderColor: activeTab === 'cart' ? 'var(--accent-primary)' : undefined,
              position: 'relative',
            }}
            onClick={() => setActiveTab('cart')}
          >
            🛒 Cart
            {cartCount > 0 && (
              <span
                style={{
                  position: 'absolute',
                  top: '-6px',
                  right: '-6px',
                  background: 'var(--accent-primary)',
                  color: '#fff',
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  width: '20px',
                  height: '20px',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 2px 6px rgba(0,0,0,0.4)',
                }}
              >
                {cartCount}
              </span>
            )}
          </button>

          <button
            className="btn-primary"
            style={{
              boxShadow: isAgentOpen ? '0 0 20px rgba(99,102,241,0.8)' : undefined,
              marginLeft: '8px',
            }}
            onClick={openAgent}
          >
            ✨ AI Assistant
          </button>
        </nav>
      </div>
    </header>
  );
};
