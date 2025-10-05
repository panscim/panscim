import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { 
  Home, 
  Trophy, 
  Gift, 
  User, 
  Settings,
  LogOut,
  Menu,
  X
} from 'lucide-react';

const Navbar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const navItems = [
    { path: '/dashboard', icon: Home, label: 'Dashboard' },
    { path: '/leaderboard', icon: Trophy, label: 'Classifica' },
    { path: '/prizes', icon: Gift, label: 'Premi' },
    { path: '/profile', icon: User, label: 'Profilo' }
  ];

  if (user?.is_admin) {
    navItems.push({ path: '/admin', icon: Settings, label: 'Admin' });
  }

  return (
    <nav className="bg-white mediterranean-shadow border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/dashboard" className="flex items-center space-x-3">
            <img 
              src="https://customer-assets.emergentagent.com/job_idea-showcase-6/artifacts/xc7s59ph_Progetto_senza_titolo__3_-removebg-preview.png" 
              alt="Desideri di Puglia Logo" 
              className="w-10 h-10"
            />
            <span className="font-cormorant text-xl font-semibold text-brand-dark">
              Desideri di Puglia Club
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-1 px-3 py-2 rounded-lg transition-colors ${
                    isActive 
                      ? 'bg-brand-accent text-white' 
                      : 'text-brand-dark hover:bg-gray-100'
                  }`}
                >
                  <Icon size={18} />
                  <span className="text-sm font-medium">{item.label}</span>
                </Link>
              );
            })}
            
            {/* User Profile & Logout */}
            <div className="flex items-center space-x-4 ml-6 pl-6 border-l border-gray-200">
              <div className="flex items-center space-x-2">
                {user?.avatar_url ? (
                  <img 
                    src={user.avatar_url} 
                    alt={user.name}
                    className="w-8 h-8 avatar-ring object-cover"
                  />
                ) : (
                  <div className="w-8 h-8 bg-gray-200 rounded-full avatar-ring flex items-center justify-center">
                    <User size={16} className="text-gray-500" />
                  </div>
                )}
                <div className="text-sm">
                  <div className="font-semibold text-brand-dark">{user?.name}</div>
                  <div className="text-xs text-brand-accent font-medium">
                    {user?.current_points} pts • {user?.level}
                  </div>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="text-gray-500 hover:text-red-500 transition-colors"
              >
                <LogOut size={18} />
              </button>
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-deep-sea-blue"
            >
              {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-100">
            <div className="space-y-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setIsMenuOpen(false)}
                    className={`flex items-center space-x-2 px-4 py-3 rounded-lg transition-colors ${
                      isActive 
                        ? 'bg-matte-gold text-white' 
                        : 'text-deep-sea-blue hover:bg-gray-100'
                    }`}
                  >
                    <Icon size={20} />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                );
              })}
              
              <div className="pt-4 mt-4 border-t border-gray-200">
                <div className="flex items-center space-x-3 px-4 py-2">
                  {user?.avatar_url ? (
                    <img 
                      src={user.avatar_url} 
                      alt={user.name}
                      className="w-10 h-10 avatar-ring object-cover"
                    />
                  ) : (
                    <div className="w-10 h-10 bg-gray-200 rounded-full avatar-ring flex items-center justify-center">
                      <User size={20} className="text-gray-500" />
                    </div>
                  )}
                  <div>
                    <div className="font-semibold text-deep-sea-blue">{user?.name}</div>
                    <div className="text-sm text-matte-gold font-medium">
                      {user?.current_points} pts • {user?.level}
                    </div>
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-2 px-4 py-3 text-red-500 hover:bg-red-50 rounded-lg w-full text-left transition-colors"
                >
                  <LogOut size={20} />
                  <span className="font-medium">Logout</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;