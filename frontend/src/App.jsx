import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './Dashboard';
import VideoReview from './VideoReview';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-background">
        <nav className="bg-surface-container-low p-4 shadow-md flex items-center justify-between">
          <Link to="/" className="text-2xl font-manrope font-bold text-primary">The Kinetic Curator</Link>
          <div>
            <Link to="/" className="text-primary hover:text-primary-dim px-4 py-2">Dashboard</Link>
          </div>
        </nav>
        <main className="p-8">
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
