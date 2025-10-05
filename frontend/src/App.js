import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import '@/App.css';

// Components
import Navbar from '@/components/Navbar';
import Home from '@/pages/Home';
import Login from '@/pages/Login';
import Register from '@/pages/Register';
import Dashboard from '@/pages/Dashboard';
import Leaderboard from '@/pages/Leaderboard';
import Prizes from '@/pages/Prizes';
import Profile from '@/pages/Profile';
import AdminPanel from '@/pages/AdminPanel';
import PublicProfile from '@/pages/PublicProfile';

// Context
import { AuthProvider, useAuth } from '@/context/AuthContext';
import { LanguageProvider } from '@/context/LanguageContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Configure axios defaults
axios.defaults.baseURL = API;

function AppContent() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-sand-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-deep-sea-blue"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-sand-white font-poppins">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route 
            path="/login" 
            element={user ? <Navigate to="/dashboard" /> : <Login />} 
          />
          <Route 
            path="/register" 
            element={user ? <Navigate to="/dashboard" /> : <Register />} 
          />
          <Route 
            path="/dashboard" 
            element={user ? <><Navbar /><Dashboard /></> : <Navigate to="/login" />} 
          />
          <Route 
            path="/leaderboard" 
            element={user ? <><Navbar /><Leaderboard /></> : <Navigate to="/login" />} 
          />
          <Route 
            path="/prizes" 
            element={user ? <><Navbar /><Prizes /></> : <Navigate to="/login" />} 
          />
          <Route 
            path="/profile" 
            element={user ? <><Navbar /><Profile /></> : <Navigate to="/login" />} 
          />
          <Route 
            path="/admin" 
            element={user && user.is_admin ? <><Navbar /><AdminPanel /></> : <Navigate to="/dashboard" />} 
          />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <LanguageProvider>
        <AppContent />
      </LanguageProvider>
    </AuthProvider>
  );
}

export default App;