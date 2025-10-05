import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Eye, EyeOff, User, Mail, Lock, Globe, ArrowLeft } from 'lucide-react';

const Register = () => {
  const [formData, setFormData] = useState({
    name: '',
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    country: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const countries = [
    { code: 'IT', name: 'Italia' },
    { code: 'US', name: 'Stati Uniti' },
    { code: 'GB', name: 'Regno Unito' },
    { code: 'DE', name: 'Germania' },
    { code: 'FR', name: 'Francia' },
    { code: 'ES', name: 'Spagna' },
    { code: 'NL', name: 'Paesi Bassi' },
    { code: 'BE', name: 'Belgio' },
    { code: 'CH', name: 'Svizzera' },
    { code: 'AT', name: 'Austria' },
    { code: 'OTHER', name: 'Altro' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Le password non coincidono');
      return;
    }

    if (formData.password.length < 6) {
      setError('La password deve essere di almeno 6 caratteri');
      return;
    }

    if (formData.username.length < 3) {
      setError('Lo username deve essere di almeno 3 caratteri');
      return;
    }

    setIsLoading(true);

    try {
      const result = await register({
        name: formData.name,
        username: formData.username,
        email: formData.email,
        password: formData.password,
        country: formData.country
      });
      
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
    <div className="min-h-screen bg-sand-white py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
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
            Benvenuto nel Club
          </h1>
          <p className="text-gray-600">
            Inizia la tua avventura pugliese. Ogni storia condivisa è un passo verso il tuo prossimo premio.
          </p>
        </div>

        {/* Registration Form */}
        <form className="space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          <div className="space-y-4">
            {/* Name */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-deep-sea-blue mb-1">
                Nome completo
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  id="name"
                  name="name"
                  type="text"
                  required
                  value={formData.name}
                  onChange={handleChange}
                  className="pl-10 w-full px-4 py-3 border border-gray-200 rounded-[20px] focus:ring-2 focus:ring-matte-gold focus:border-transparent transition-colors"
                  placeholder="Il tuo nome completo"
                />
              </div>
            </div>

            {/* Username */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-deep-sea-blue mb-1">
                Username
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  id="username"
                  name="username"
                  type="text"
                  required
                  value={formData.username}
                  onChange={handleChange}
                  className="pl-10 w-full px-4 py-3 border border-gray-200 rounded-[20px] focus:ring-2 focus:ring-matte-gold focus:border-transparent transition-colors"
                  placeholder="Il tuo username unico"
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">Almeno 3 caratteri, sarà visibile agli altri utenti</p>
            </div>

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

            {/* Country */}
            <div>
              <label htmlFor="country" className="block text-sm font-medium text-deep-sea-blue mb-1">
                Paese
              </label>
              <div className="relative">
                <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 z-10" size={18} />
                <select
                  id="country"
                  name="country"
                  required
                  value={formData.country}
                  onChange={handleChange}
                  className="pl-12 pr-4 w-full py-3 border border-gray-200 rounded-[20px] focus:ring-2 focus:ring-matte-gold focus:border-transparent transition-colors appearance-none bg-white"
                  style={{ 
                    backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                    backgroundPosition: 'right 8px center',
                    backgroundRepeat: 'no-repeat',
                    backgroundSize: '16px'
                  }}
                >
                  <option value="">Seleziona il tuo paese</option>
                  {countries.map((country) => (
                    <option key={country.code} value={country.code}>
                      {country.name}
                    </option>
                  ))}
                </select>
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
              <p className="text-xs text-gray-500 mt-1">Almeno 6 caratteri</p>
            </div>

            {/* Confirm Password */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-deep-sea-blue mb-1">
                Conferma Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  required
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className="pl-10 pr-10 w-full px-4 py-3 border border-gray-200 rounded-[20px] focus:ring-2 focus:ring-matte-gold focus:border-transparent transition-colors"
                  placeholder="Conferma la tua password"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
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
              <>Entra nel Club 🌿</>
            )}
          </button>

          {/* Login Link */}
          <div className="text-center">
            <p className="text-gray-600">
              Hai già un account?{' '}
              <Link to="/login" className="text-matte-gold hover:text-deep-sea-blue font-semibold transition-colors">
                Accedi qui
              </Link>
            </p>
          </div>
        </form>

        {/* Welcome Message */}
        <div className="mt-8 bg-white rounded-[20px] p-6 mediterranean-shadow">
          <p className="text-center text-deep-sea-blue font-cormorant font-semibold text-lg mb-2">
            "Benvenuto nel Desideri di Puglia Club 🌿"
          </p>
          <p className="text-center text-gray-600 text-sm">
            La tua avventura comincia qui. Ogni momento condiviso è un passo verso esperienze autentiche.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;