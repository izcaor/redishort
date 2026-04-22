import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, Navigate } from 'react-router-dom';
import axios from 'axios';
import Dashboard from './Dashboard';
import VideoReview from './VideoReview';
import Login from './Login';
import Register from './Register';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = () => setIsAuthenticated(true);

  const handleLogout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setIsAuthenticated(false);
  };

  return (
    <BrowserRouter>
      {isAuthenticated ? (
        <div className="min-h-screen bg-background">
          <nav className="bg-surface-container-low p-4 shadow-md flex items-center justify-between">
            <Link to="/" className="text-2xl font-manrope font-bold text-primary">The Kinetic Curator</Link>
            <div>
              <Link to="/" className="text-primary hover:text-primary-dim px-4 py-2 font-bold">Dashboard</Link>
              <button onClick={handleLogout} className="text-tertiary hover:text-tertiary-dim px-4 py-2 font-bold">Logout</button>
            </div>
          </nav>
          <main className="p-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/review/:id" element={<VideoReview />} />
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </main>
        </div>
      ) : (
        <Routes>
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route path="/register" element={<Register onLogin={handleLogin} />} />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      )}
    </BrowserRouter>
  );
}

export default App;
