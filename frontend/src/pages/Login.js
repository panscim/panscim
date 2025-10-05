import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Eye, EyeOff, Mail, Lock, ArrowLeft } from 'lucide-react';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const result = await login(formData.email, formData.password);
      if (result.success) {
        navigate('/dashboard');
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Si è verificato un errore. Riprova.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-sand-white flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <Link to="/" className="inline-flex items-center text-deep-sea-blue hover:text-matte-gold transition-colors mb-8">
            <ArrowLeft size={20} className="mr-2" />
            Torna alla home
          </Link>
          
          <div className="flex items-center justify-center">
            <div className="w-16 h-16 bg-matte-gold rounded-full flex items-center justify-center mb-6 animate-float">
              <span className="text-2xl">🌿</span>
            </div>
          </div>
          
          <h1 className="text-3xl font-cormorant font-bold text-deep-sea-blue mb-2">
            Bentornato nel Club
          </h1>
          <p className="text-gray-600">
            Accedi per continuare la tua avventura pugliese
          </p>
        </div>

        {/* Login Form */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          <div className="space-y-4">
            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-deep-sea-blue mb-1">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className="pl-10 w-full px-4 py-3 border border-gray-200 rounded-[20px] focus:ring-2 focus:ring-matte-gold focus:border-transparent transition-colors"
                  placeholder="La tua email"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-deep-sea-blue mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="pl-10 pr-10 w-full px-4 py-3 border border-gray-200 rounded-[20px] focus:ring-2 focus:ring-matte-gold focus:border-transparent transition-colors"
                  placeholder="La tua password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full btn-primary flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            ) : (
              <>Accedi al Club 🌿</>
            )}
          </button>

          {/* Register Link */}
          <div className="text-center">
            <p className="text-gray-600">
              Non hai ancora un account?{' '}
              <Link to="/register" className="text-matte-gold hover:text-deep-sea-blue font-semibold transition-colors">
                Iscriviti ora
              </Link>
            </p>
          </div>
        </form>

        {/* Welcome Message */}
        <div className="mt-8 bg-white rounded-[20px] p-6 mediterranean-shadow">
          <p className="text-center text-gray-600 text-sm">
            <span className="text-matte-gold font-semibold">💡 Ricorda:</span> Ogni interazione sociale, ogni esperienza condivisa è un passo verso il tuo prossimo premio pugliese!
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;