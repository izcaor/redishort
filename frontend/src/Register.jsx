import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function Register({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('/api/auth/register', { email, password });
      localStorage.setItem('token', res.data.access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${res.data.access_token}`;
      onLogin();
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="bg-surface-container-lowest rounded-xl p-8 shadow-md w-full max-w-md">
        <h1 className="text-display-lg font-manrope font-bold text-primary mb-6 text-center">Register</h1>
        {error && <p className="text-tertiary mb-4 text-center">{error}</p>}
        <form onSubmit={handleRegister} className="space-y-6">
          <div>
            <label className="block text-sm font-bold text-on-surface mb-2">Email</label>
            <input
              type="email"
              required
              className="w-full p-4 rounded-xl bg-surface-container-high text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/40"
              value={email}
              onChange={e => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-bold text-on-surface mb-2">Password</label>
            <input
              type="password"
              required
              className="w-full p-4 rounded-xl bg-surface-container-high text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/40"
              value={password}
              onChange={e => setPassword(e.target.value)}
            />
          </div>
          <button type="submit" className="w-full py-4 rounded-full font-bold text-on-primary bg-gradient-to-r from-primary-dim to-primary">
            Create Account
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-on-surface-variant">
          Already have an account? <span className="text-primary cursor-pointer hover:underline" onClick={() => navigate('/login')}>Sign In</span>
        </p>
      </div>
    </div>
  );
}

export default Register;
