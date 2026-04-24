import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Sparkles } from 'lucide-react';
import Dashboard from './Dashboard';
import VideoReview from './VideoReview';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-transparent text-on-surface">
        <nav className="sticky top-0 z-10 border-b border-outline-variant/40 bg-surface-container-low/90 backdrop-blur-md">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <Link to="/" className="flex items-center gap-3 text-2xl font-manrope font-extrabold tracking-tight text-on-surface">
              <span className="inline-flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-primary-dim to-primary text-on-primary shadow-brand">
                <Sparkles className="w-5 h-5" />
              </span>
              RediShort Studio
            </Link>
            <div>
              <Link
                to="/"
                className="text-sm font-semibold text-on-surface hover:text-secondary-container px-4 py-2 rounded-full transition-colors"
              >
                Dashboard
              </Link>
            </div>
          </div>
        </nav>
        <main className="p-6 md:p-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/review/:id" element={<VideoReview />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
