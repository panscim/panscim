import React, { useState, useRef } from 'react';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import { 
  User, 
  Camera, 
  Edit2, 
  Save, 
  X, 
  Star, 
  Trophy, 
  Calendar,
  Globe,
  Mail,
  Shield,
  Download,
  Share2
} from 'lucide-react';

const Profile = () => {
  const { user, updateUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [isUploadingAvatar, setIsUploadingAvatar] = useState(false);
  const [editForm, setEditForm] = useState({
    name: user?.name || '',
    username: user?.username || '',
    country: user?.country || ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const fileInputRef = useRef(null);

  const countries = [
    { code: 'IT', name: 'Italia', flag: '🇮🇹' },
    { code: 'US', name: 'Stati Uniti', flag: '🇺🇸' },
    { code: 'GB', name: 'Regno Unito', flag: '🇬🇧' },
    { code: 'DE', name: 'Germania', flag: '🇩🇪' },
    { code: 'FR', name: 'Francia', flag: '🇫🇷' },
    { code: 'ES', name: 'Spagna', flag: '🇪🇸' },
    { code: 'NL', name: 'Paesi Bassi', flag: '🇳🇱' },
    { code: 'BE', name: 'Belgio', flag: '🇧🇪' },
    { code: 'CH', name: 'Svizzera', flag: '🇬🇭' },
    { code: 'AT', name: 'Austria', flag: '🇦🇹' },
    { code: 'OTHER', name: 'Altro', flag: '🌍' }
  ];

  const getUserFlag = (countryCode) => {
    const country = countries.find(c => c.code === countryCode);
    return country ? country.flag : '🌍';
  };

  const getLevelIcon = (level) => {
    const levels = {
      'Explorer': { icon: '🗺️', color: 'bg-blue-100 text-blue-700', description: 'Nuovo esploratore pugliese' },
      'Local Friend': { icon: '🤝', color: 'bg-green-100 text-green-700', description: 'Amico della comunità' },
      'Ambassador': { icon: '🌟', color: 'bg-purple-100 text-purple-700', description: 'Ambasciatore della Puglia' },
      'Legend': { icon: '🏆', color: 'bg-yellow-100 text-yellow-700', description: 'Leggenda del club' }
    };
    return levels[level] || levels['Explorer'];
  };

  const handleAvatarUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Seleziona un file immagine valido');
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('L\'immagine deve essere inferiore a 5MB');
      return;
    }

    setIsUploadingAvatar(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post('/auth/upload-avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      updateUser({ avatar_url: response.data.avatar_url });
      setSuccess('Avatar aggiornato con successo! 🌿');
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      setError(error.response?.data?.detail || 'Errore nel caricamento dell\'avatar');
    } finally {
      setIsUploadingAvatar(false);
    }
  };

  const handleProfileUpdate = async () => {
    setError('');
    setSuccess('');

    try {
      await axios.put('/user/profile', editForm);
      updateUser(editForm);
      setIsEditing(false);
      setSuccess('Profilo aggiornato con successo! 🌿');
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      setError(error.response?.data?.detail || 'Errore nell\'aggiornamento del profilo');
    }
  };

  const generateShareableProfile = () => {
    const profileData = {
      name: user.name,
      username: user.username,
      level: user.level,
      points: user.current_points,
      country: user.country
    };
    
    const shareText = `🌿 Guarda il mio profilo Desideri di Puglia Club!

👤 ${profileData.name} (@${profileData.username})
🏆 Livello: ${profileData.level}
⭐ Punti: ${profileData.points}
${getUserFlag(profileData.country)} ${countries.find(c => c.code === profileData.country)?.name || 'Mondo'}

Vivi la Puglia autentica con noi!`;
    
    if (navigator.share) {
      navigator.share({
        title: 'Il mio profilo Desideri di Puglia',
        text: shareText
      });
    } else {
      navigator.clipboard.writeText(shareText);
      setSuccess('Profilo copiato negli appunti! 💷');
      setTimeout(() => setSuccess(''), 3000);
    }
  };

  const levelInfo = getLevelIcon(user?.level);
  const nextLevelPoints = {
    'Explorer': 500,
    'Local Friend': 1000,
    'Ambassador': 2000,
    'Legend': 0
  };
  const pointsToNext = user?.level !== 'Legend' ? nextLevelPoints[user?.level] - user?.total_points : 0;

  return (
    <div className="min-h-screen bg-sand-white py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Success/Error Messages */}
        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-green-800 text-sm">{success}</p>
          </div>
        )}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {/* Profile Header */}
        <div className="bg-white rounded-[20px] p-8 mediterranean-shadow mb-8">
          <div className="flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-8">
            {/* Avatar Section */}
            <div className="relative">
              <div className="text-center">
                <div className="w-32 h-32 mx-auto mb-4">
                  {user?.avatar_url ? (
                    <img 
                      src={user.avatar_url} 
                      alt={user.name}
                      className="w-full h-full object-cover rounded-full avatar-ring"
                    />
                  ) : (
                    <div className="w-full h-full bg-gradient-to-br from-brand-accent to-yellow-500 rounded-full avatar-ring flex items-center justify-center">
                      <span className="text-white text-4xl font-bold">{user?.name?.charAt(0)}</span>
                    </div>
                  )}
                  
                  {/* Upload Button */}
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isUploadingAvatar}
                    className="absolute bottom-2 right-2 w-10 h-10 bg-brand-accent hover:bg-opacity-90 rounded-full flex items-center justify-center text-white transition-colors disabled:opacity-50"
                  >
                    {isUploadingAvatar ? (
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    ) : (
                      <Camera size={18} />
                    )}
                  </button>
                  
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleAvatarUpload}
                    className="hidden"
                  />
                </div>
                
                {/* Level Badge - Now below the photo */}
                <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium ${levelInfo.color} mb-4`}>
                  <span className="mr-2 text-lg">{levelInfo.icon}</span>
                  {user?.level}
                </div>
              </div>
            </div>

            {/* Profile Info */}
            <div className="flex-1 text-center md:text-left">
              {isEditing ? (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-deep-sea-blue mb-1">Nome completo</label>
                    <input
                      type="text"
                      value={editForm.name}
                      onChange={(e) => setEditForm({...editForm, name: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-200 rounded-[12px] focus:ring-2 focus:ring-matte-gold focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-deep-sea-blue mb-1">Username</label>
                    <input
                      type="text"
                      value={editForm.username}
                      onChange={(e) => setEditForm({...editForm, username: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-200 rounded-[12px] focus:ring-2 focus:ring-matte-gold focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-deep-sea-blue mb-1">Paese</label>
                    <select
                      value={editForm.country}
                      onChange={(e) => setEditForm({...editForm, country: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-200 rounded-[12px] focus:ring-2 focus:ring-matte-gold focus:border-transparent"
                    >
                      {countries.map((country) => (
                        <option key={country.code} value={country.code}>
                          {country.flag} {country.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="flex space-x-3">
                    <button onClick={handleProfileUpdate} className="btn-primary flex items-center space-x-1">
                      <Save size={16} />
                      <span>Salva</span>
                    </button>
                    <button 
                      onClick={() => {
                        setIsEditing(false);
                        setEditForm({ name: user.name, username: user.username, country: user.country });
                        setError('');
                      }}
                      className="px-4 py-2 border border-gray-300 rounded-[12px] text-gray-700 hover:bg-gray-50 flex items-center space-x-1"
                    >
                      <X size={16} />
                      <span>Annulla</span>
                    </button>
                  </div>
                </div>
              ) : (
                <div>
                  <div className="flex items-center justify-center md:justify-start space-x-3 mb-2">
                    <h1 className="text-2xl font-cormorant font-bold text-deep-sea-blue">{user?.name}</h1>
                    <button
                      onClick={() => setIsEditing(true)}
                      className="text-matte-gold hover:text-deep-sea-blue transition-colors"
                    >
                      <Edit2 size={18} />
                    </button>
                  </div>
                  
                  <div className="space-y-2 text-gray-600">
                    <div className="flex items-center justify-center md:justify-start space-x-2">
                      <User size={16} />
                      <span>@{user?.username}</span>
                    </div>
                    <div className="flex items-center justify-center md:justify-start space-x-2">
                      <Globe size={16} />
                      <span>{getUserFlag(user?.country)} {countries.find(c => c.code === user?.country)?.name}</span>
                    </div>
                    <div className="flex items-center justify-center md:justify-start space-x-2">
                      <Mail size={16} />
                      <span>{user?.email}</span>
                    </div>
                    <div className="flex items-center justify-center md:justify-start space-x-2">
                      <Calendar size={16} />
                      <span>Membro dal {new Date(user?.created_at).toLocaleDateString('it-IT', { month: 'long', year: 'numeric' })}</span>
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-500 mt-3 italic">{levelInfo.description}</p>
                </div>
              )}
            </div>

            {/* Actions */}
            {!isEditing && (
              <div className="flex flex-col space-y-3">
                <button
                  onClick={generateShareableProfile}
                  className="btn-secondary flex items-center space-x-2"
                >
                  <Share2 size={16} />
                  <span>Condividi</span>
                </button>
                
                {user?.is_admin && (
                  <div className="flex items-center space-x-2 text-sm text-matte-gold">
                    <Shield size={16} />
                    <span>Admin</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Points */}
          <div className="puglia-card text-center">
            <div className="w-12 h-12 bg-matte-gold rounded-full flex items-center justify-center mx-auto mb-3">
              <Star className="text-white" size={24} />
            </div>
            <div className="text-2xl font-bold text-deep-sea-blue mb-1">{user?.current_points}</div>
            <div className="text-sm text-gray-600">Punti questo mese</div>
          </div>

          {/* Total Points */}
          <div className="puglia-card text-center">
            <div className="w-12 h-12 bg-deep-sea-blue rounded-full flex items-center justify-center mx-auto mb-3">
              <Trophy className="text-white" size={24} />
            </div>
            <div className="text-2xl font-bold text-deep-sea-blue mb-1">{user?.total_points}</div>
            <div className="text-sm text-gray-600">Punti totali</div>
          </div>

          {/* Level Progress */}
          <div className="puglia-card text-center">
            <div className={`w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3 ${levelInfo.color}`}>
              <span className="text-xl">{levelInfo.icon}</span>
            </div>
            <div className="text-lg font-bold text-deep-sea-blue mb-1">{user?.level}</div>
            <div className="text-sm text-gray-600">
              {user?.level !== 'Legend' ? `${pointsToNext} al prossimo` : 'Livello massimo'}
            </div>
          </div>

          {/* Position */}
          <div className="puglia-card text-center">
            <div className="w-12 h-12 bg-terracotta rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-white font-bold">#</span>
            </div>
            <div className="text-2xl font-bold text-deep-sea-blue mb-1">{user?.position || '-'}</div>
            <div className="text-sm text-gray-600">Posizione attuale</div>
          </div>
        </div>

        {/* Level Progress Bar */}
        {user?.level !== 'Legend' && (
          <div className="bg-white rounded-[20px] p-6 mediterranean-shadow mb-8">
            <h3 className="text-lg font-semibold text-deep-sea-blue mb-4 flex items-center">
              <Star className="mr-2 text-matte-gold" size={20} />
              Progresso verso il prossimo livello
            </h3>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Livello attuale: {user?.level}</span>
                <span className="text-sm text-matte-gold font-medium">+{pointsToNext} punti necessari</span>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="bg-gradient-to-r from-matte-gold to-yellow-500 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min((user?.total_points / nextLevelPoints[user?.level]) * 100, 100)}%` }}
                ></div>
              </div>
              
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>0 punti</span>
                <span>{nextLevelPoints[user?.level]} punti</span>
              </div>
            </div>
            
            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-blue-800 text-sm">
                💡 <strong>Suggerimento:</strong> Completa le missioni quotidiane per guadagnare punti più velocemente!
              </p>
            </div>
          </div>
        )}

        {/* Achievements & Badges */}
        <div className="bg-white rounded-[20px] p-6 mediterranean-shadow">
          <h3 className="text-lg font-semibold text-deep-sea-blue mb-4 flex items-center">
            <Trophy className="mr-2 text-matte-gold" size={20} />
            Riconoscimenti
          </h3>
          
          {user?.badges && user.badges.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {user.badges.map((badge, index) => (
                <div key={index} className="text-center p-4 bg-gray-50 rounded-[12px]">
                  <div className="text-2xl mb-2">🏅</div>
                  <div className="text-sm font-medium text-deep-sea-blue">{badge}</div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-4xl mb-3">🌟</div>
              <h4 className="font-semibold text-gray-600 mb-2">Nessun badge ancora</h4>
              <p className="text-gray-500 text-sm">
                Continua a completare le missioni per sbloccare i tuoi primi riconoscimenti!
              </p>
            </div>
          )}
        </div>

        {/* Activity Timeline Preview */}
        <div className="mt-8 bg-white rounded-[20px] p-6 mediterranean-shadow">
          <h3 className="text-lg font-semibold text-deep-sea-blue mb-4">La Tua Journey Pugliese</h3>
          
          <div className="text-center py-8">
            <Calendar className="mx-auto text-gray-400 mb-3" size={48} />
            <h4 className="font-semibold text-gray-600 mb-2">Timeline in arrivo</h4>
            <p className="text-gray-500 text-sm">
              Presto potrai vedere la cronologia completa delle tue avventure pugliesi!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;