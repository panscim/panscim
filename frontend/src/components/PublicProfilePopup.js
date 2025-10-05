import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  X, 
  Trophy, 
  Calendar, 
  Star,
  Gift,
  TrendingUp,
  Clock
} from 'lucide-react';
import { t } from '../utils/translations';

const PublicProfilePopup = ({ isOpen, onClose, userId }) => {
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen && userId) {
      fetchPublicProfile();
    }
  }, [isOpen, userId]);

  const fetchPublicProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/club/profile/${userId}`);
      setProfileData(response.data);
    } catch (error) {
      console.error('Error fetching public profile:', error);
      setError('Impossibile caricare il profilo');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-[20px] max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        {/* Header with close button */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-matte-gold to-yellow-600 rounded-full flex items-center justify-center">
              <span className="text-white font-bold">🌿</span>
            </div>
            <div>
              <h2 className="text-xl font-bold text-deep-sea-blue" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
                Desideri di Puglia Club
              </h2>
              <p className="text-sm text-gray-600">{t('public_profile')}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X size={20} className="text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-deep-sea-blue mx-auto mb-4"></div>
              <p className="text-gray-600">{t('loading_profile')}</p>
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <X className="text-red-500" size={32} />
              </div>
              <h3 className="text-lg font-medium text-gray-700 mb-2">{t('profile_not_found')}</h3>
              <p className="text-gray-600">{error}</p>
            </div>
          ) : profileData ? (
            <div className="space-y-6">
              {/* User Profile Section */}
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 rounded-full border-3 border-matte-gold flex items-center justify-center text-white font-bold text-lg" style={{ 
                  borderWidth: '3px',
                  background: profileData.user_info.level === 'Explorer' ? 'linear-gradient(135deg, #CFAE6C, #DAB973)' :
                             profileData.user_info.level === 'Adventurer' ? 'linear-gradient(135deg, #2E4A5C, #3A5A6E)' :
                             profileData.user_info.level === 'Master' ? 'linear-gradient(135deg, #8B4513, #A0522D)' :
                             profileData.user_info.level === 'Legend' ? 'linear-gradient(135deg, #800080, #9932CC)' :
                             'linear-gradient(135deg, #CFAE6C, #DAB973)'
                }}>
                  {profileData.user_info.level === 'Explorer' ? '🌱' :
                   profileData.user_info.level === 'Adventurer' ? '🗺️' :
                   profileData.user_info.level === 'Master' ? '👑' :
                   profileData.user_info.level === 'Legend' ? '🏆' :
                   '🌱'}
                </div>
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-deep-sea-blue">{profileData.user_info.name}</h3>
                  <div className="flex items-center space-x-2 mb-1">
                    <Star className="text-matte-gold fill-current" size={16} />
                    <span className="text-lg font-medium text-matte-gold">{profileData.user_info.level}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-gray-600">
                    <Calendar size={14} />
                    <span className="text-sm">
                      {t('member_since')} {profileData.user_info.join_date ? new Date(profileData.user_info.join_date).toLocaleDateString('it-IT') : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Dynamic Status Message */}
              <div className={`p-4 rounded-lg ${
                profileData.status.type === 'winner' ? 'bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200' :
                profileData.status.type === 'active' ? 'bg-gradient-to-r from-green-50 to-blue-50 border border-green-200' :
                'bg-gradient-to-r from-gray-50 to-blue-50 border border-gray-200'
              }`}>
                {profileData.status.type === 'active' && (
                  <p className="text-green-800 font-medium">
                    🌿 Attualmente sei al posto <span className="font-bold">#{profileData.stats.current_rank}</span> con <span className="font-bold">{profileData.stats.current_points} punti</span> nella classifica di {profileData.stats.month_year}.
                  </p>
                )}
                {profileData.status.type === 'winner' && (
                  <div>
                    <p className="text-orange-800 font-medium mb-2">
                      🏆 Congratulazioni! Sei tra i Top 3 del mese di {profileData.stats.month_year}.
                    </p>
                    {profileData.status.prize_info && (
                      <div className="mt-2 p-3 bg-white rounded-lg border border-yellow-300">
                        <p className="text-sm font-medium text-yellow-800">
                          🎁 Premio: {profileData.status.prize_info.prize_name} — vinto il {profileData.status.prize_info.win_date}
                        </p>
                      </div>
                    )}
                  </div>
                )}
                {(!['active', 'winner'].includes(profileData.status.type)) && (
                  <p className="text-gray-700 font-medium">
                    🌿 Benvenuto nel profilo di {profileData.user_info.name}!
                  </p>
                )}
              </div>

              {/* Statistics */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <div className="text-xl font-bold text-matte-gold">{profileData.stats.total_points}</div>
                  <div className="text-sm text-gray-600">{t('total_points')}</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <div className="text-xl font-bold text-deep-sea-blue">{profileData.stats.current_points}</div>
                  <div className="text-sm text-gray-600">{t('current_points')}</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <div className="text-xl font-bold text-terracotta">#{profileData.stats.current_rank || '-'}</div>
                  <div className="text-sm text-gray-600">{t('current_rank')}</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <div className="text-xl font-bold text-green-600">{profileData.stats.mission_completions}</div>
                  <div className="text-sm text-gray-600">{t('missions_completed')}</div>
                </div>
              </div>

              {/* Prizes Section */}
              {(profileData.prizes.past_prizes && profileData.prizes.past_prizes.length > 0) && (
                <div className="border-t border-gray-200 pt-6">
                  <h4 className="text-lg font-semibold text-deep-sea-blue mb-4 flex items-center">
                    <Gift className="mr-2" size={18} />
                    🏅 {t('past_prizes')}
                  </h4>
                  <div className="space-y-2">
                    {profileData.prizes.past_prizes.slice(0, 3).map((prize, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded border">
                        <div className="flex-1">
                          <div className="font-medium text-gray-900">• {prize.prize_name}</div>
                          <div className="text-sm text-gray-600">vinto il {prize.win_date}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* No Prizes */}
              {(!profileData.prizes.past_prizes || profileData.prizes.past_prizes.length === 0) && (
                <div className="border-t border-gray-200 pt-6 text-center">
                  <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <Gift className="text-gray-400" size={24} />
                  </div>
                  <p className="text-gray-600">{t('no_prizes_message')}</p>
                </div>
              )}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default PublicProfilePopup;