import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { 
  User, 
  Trophy, 
  Calendar, 
  Star,
  Gift,
  TrendingUp,
  Clock,
  MapPin
} from 'lucide-react';

const PublicProfile = () => {
  const { user_id } = useParams();
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPublicProfile();
  }, [user_id]);

  const fetchPublicProfile = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/club/profile/${user_id}`);
      setProfileData(response.data);
    } catch (error) {
      console.error('Error fetching public profile:', error);
      setError('Profilo non trovato o non disponibile');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-sand-light to-sand-medium flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-deep-sea-blue mx-auto mb-4"></div>
          <p className="text-gray-600">Caricamento profilo Club...</p>
        </div>
      </div>
    );
  }

  if (error || !profileData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-sand-light to-sand-medium flex items-center justify-center">
        <div className="bg-white rounded-[20px] p-8 shadow-lg border border-matte-gold text-center max-w-md">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <User className="text-red-500" size={32} />
          </div>
          <h2 className="text-xl font-bold text-deep-sea-blue mb-2">Profilo Non Trovato</h2>
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  const { user_info, stats, status, prizes } = profileData;

  return (
    <div className="min-h-screen bg-gradient-to-br from-sand-light to-sand-medium">
      {/* Header */}
      <div className="bg-white shadow-md border-b border-matte-gold">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-r from-matte-gold to-yellow-600 rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-lg">🌿</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-deep-sea-blue" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
                Desideri di Puglia Club
              </h1>
              <p className="text-sm text-gray-600">Profilo Pubblico</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* User Profile Card */}
        <div className="bg-white rounded-[20px] p-8 shadow-lg border border-matte-gold mb-8">
          <div className="flex items-center space-x-6 mb-6">
            {/* Avatar */}
            {user_info.avatar ? (
              <img
                src={`data:image/jpeg;base64,${user_info.avatar}`}
                alt="Avatar"
                className="w-24 h-24 rounded-full border-4 border-matte-gold object-cover shadow-lg"
              />
            ) : (
              <div className="w-24 h-24 bg-gradient-to-br from-matte-gold to-yellow-600 rounded-full flex items-center justify-center text-white font-bold text-2xl shadow-lg border-4 border-matte-gold">
                {user_info.name?.charAt(0) || '?'}
              </div>
            )}

            {/* User Info */}
            <div className="flex-1">
              <h2 className="text-3xl font-bold text-deep-sea-blue mb-2">{user_info.name}</h2>
              <div className="flex items-center space-x-4 mb-3">
                <div className="flex items-center space-x-2">
                  <Star className="text-matte-gold fill-current" size={18} />
                  <span className="text-lg font-medium text-matte-gold">{user_info.level}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-deep-sea-blue">{user_info.club_card_code}</span>
                </div>
              </div>
              <div className="flex items-center space-x-2 text-gray-600">
                <Calendar size={16} />
                <span className="text-sm">
                  Membro dal {user_info.join_date ? new Date(user_info.join_date).toLocaleDateString('it-IT') : 'N/A'}
                </span>
              </div>
            </div>
          </div>

          {/* Dynamic Status Message */}
          <div className={`p-4 rounded-lg mb-6 ${
            status.type === 'winner' ? 'bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200' :
            status.type === 'active' ? 'bg-gradient-to-r from-green-50 to-blue-50 border border-green-200' :
            'bg-gradient-to-r from-gray-50 to-blue-50 border border-gray-200'
          }`}>
            
            {/* Current Month Active */}
            {status.type === 'active' && (
              <p className="text-lg font-medium text-green-800">
                🌿 Attualmente sei al posto <span className="font-bold">#{stats.current_rank}</span> con <span className="font-bold">{stats.current_points} punti</span> nella classifica di {stats.month_year}.
              </p>
            )}

            {/* Current Month Winner */}
            {status.type === 'winner' && prizes.current_prize && (
              <div>
                <p className="text-lg font-medium text-orange-800 mb-2">
                  🏆 Congratulazioni! Sei tra i Top 3 del mese di {prizes.current_prize.month_name || stats.month_year}.
                </p>
                <div className="mt-2 p-3 bg-white rounded-lg border border-yellow-300">
                  <p className="text-sm font-medium text-yellow-800">
                    🎁 Premio: {prizes.current_prize.prize_name} — vinto il {prizes.current_prize.win_date}
                  </p>
                </div>
              </div>
            )}

            {/* Month Concluded - Not Winner */}
            {status.type === 'concluded' && !prizes.current_month_winner && (
              <p className="text-lg font-medium text-gray-700">
                📅 Il mese di {stats.month_year} è concluso. Hai ottenuto {stats.current_points} punti e posizione #{stats.current_rank}.
              </p>
            )}

            {/* Default message */}
            {!['active', 'winner', 'concluded'].includes(status.type) && (
              <p className="text-lg font-medium text-gray-700">
                {status.message_it || `🌿 Benvenuto nel profilo di ${user_info.name}!`}
              </p>
            )}
          </div>
        </div>

        {/* Statistics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-[20px] p-6 shadow-lg border border-matte-gold text-center">
            <div className="w-12 h-12 bg-deep-sea-blue rounded-full flex items-center justify-center mx-auto mb-3">
              <Trophy className="text-white" size={24} />
            </div>
            <div className="text-2xl font-bold text-deep-sea-blue mb-1">{stats.total_points}</div>
            <div className="text-sm text-gray-600">Punti Totali</div>
          </div>

          <div className="bg-white rounded-[20px] p-6 shadow-lg border border-matte-gold text-center">
            <div className="w-12 h-12 bg-matte-gold rounded-full flex items-center justify-center mx-auto mb-3">
              <TrendingUp className="text-white" size={24} />
            </div>
            <div className="text-2xl font-bold text-deep-sea-blue mb-1">{stats.current_points}</div>
            <div className="text-sm text-gray-600">Punti Questo Mese</div>
          </div>

          <div className="bg-white rounded-[20px] p-6 shadow-lg border border-matte-gold text-center">
            <div className="w-12 h-12 bg-terracotta rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-white font-bold">#</span>
            </div>
            <div className="text-2xl font-bold text-deep-sea-blue mb-1">
              {stats.current_rank || '-'}
            </div>
            <div className="text-sm text-gray-600">Posizione Attuale</div>
          </div>

          <div className="bg-white rounded-[20px] p-6 shadow-lg border border-matte-gold text-center">
            <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-3">
              <Clock className="text-white" size={24} />
            </div>
            <div className="text-2xl font-bold text-deep-sea-blue mb-1">{stats.mission_completions}</div>
            <div className="text-sm text-gray-600">Missioni Complete</div>
          </div>
        </div>

        {/* Prizes Section */}
        {(prizes.current_month_winner || prizes.has_won_before) && (
          <div className="bg-white rounded-[20px] p-8 shadow-lg border border-matte-gold">
            <h3 className="text-xl font-bold text-deep-sea-blue mb-6 flex items-center">
              <Gift className="mr-3" size={24} />
              🏅 Premi e Riconoscimenti
            </h3>

            {/* Current Month Prize */}
            {prizes.current_month_winner && prizes.current_prize && (
              <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg p-4 mb-6">
                <h4 className="font-semibold text-orange-800 mb-2">
                  🏆 Premio del Mese Corrente - {prizes.current_prize.place} Posto
                </h4>
                <p className="text-orange-700">{prizes.current_prize.prize_name}</p>
                {prizes.current_prize.win_date && (
                  <p className="text-sm text-orange-600 mt-1">
                    Vinto il {prizes.current_prize.win_date}
                  </p>
                )}
              </div>
            )}

            {/* Past Prizes */}
            {prizes.past_prizes.length > 0 && (
              <div>
                <h4 className="font-semibold text-deep-sea-blue mb-4">🏅 Premi Precedenti</h4>
                <div className="space-y-3">
                  {prizes.past_prizes.map((prize, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border">
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">
                          {prize.prize_name} - {prize.place} Posto
                        </div>
                        <div className="text-sm text-gray-600">
                          {prize.month_name} • Vinto il {prize.win_date}
                        </div>
                      </div>
                      {prize.use_date && (
                        <div className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded">
                          Utilizzato il {prize.use_date}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* No Prizes Yet */}
        {!prizes.current_month_winner && !prizes.has_won_before && (
          <div className="bg-white rounded-[20px] p-8 shadow-lg border border-matte-gold text-center">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Gift className="text-gray-400" size={32} />
            </div>
            <h3 className="text-lg font-medium text-gray-700 mb-2">🌿 Nessun premio ancora</h3>
            <p className="text-gray-600">Continua a giocare per vincere fantastici premi!</p>
          </div>
        )}

        {/* Footer */}
        <div className="text-center mt-8 py-6">
          <p className="text-sm text-gray-500">
            Scansiona il QR code sulla Card per visitare questo profilo • Desideri di Puglia Club 🌿
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Ultimo aggiornamento: {new Date(profileData.last_updated).toLocaleString('it-IT')}
          </p>
        </div>
      </div>
    </div>
  );
};

export default PublicProfile;