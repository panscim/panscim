import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { t } from '@/utils/translations';
import axios from 'axios';
import { Trophy, Medal, Star, Users, Calendar } from 'lucide-react';

const Leaderboard = () => {
  const { user } = useAuth();
  const [leaderboardData, setLeaderboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedMonth, setSelectedMonth] = useState('');

  useEffect(() => {
    fetchLeaderboard();
  }, [selectedMonth]);

  const fetchLeaderboard = async () => {
    try {
      const params = selectedMonth ? { month_year: selectedMonth } : {};
      const response = await axios.get('/leaderboard', { params });
      setLeaderboardData(response.data);
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateMonthOptions = () => {
    const options = [];
    const currentDate = new Date();
    
    // Current month
    const currentMonth = currentDate.toISOString().slice(0, 7);
    options.push({
      value: currentMonth,
      label: `${currentDate.toLocaleDateString('it-IT', { month: 'long', year: 'numeric' }).replace(/^\w/, c => c.toUpperCase())} (Corrente)`
    });
    
    // Previous months (last 6 months)
    for (let i = 1; i <= 6; i++) {
      const date = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1);
      const monthYear = date.toISOString().slice(0, 7);
      options.push({
        value: monthYear,
        label: date.toLocaleDateString('it-IT', { month: 'long', year: 'numeric' }).replace(/^\w/, c => c.toUpperCase())
      });
    }
    
    return options;
  };

  const getPodiumPosition = (position) => {
    if (position === 1) return { emoji: '🥇', color: 'border-yellow-400 bg-yellow-50', textColor: 'text-yellow-600' };
    if (position === 2) return { emoji: '🥈', color: 'border-gray-400 bg-gray-50', textColor: 'text-gray-600' };
    if (position === 3) return { emoji: '🥉', color: 'border-orange-400 bg-orange-50', textColor: 'text-orange-600' };
    return { emoji: '', color: 'border-gray-200 bg-white', textColor: 'text-gray-600' };
  };

  const monthOptions = generateMonthOptions();
  const userPosition = leaderboardData?.leaderboard.findIndex(u => u.user_id === user.id) + 1 || 0;

  if (loading) {
    return (
      <div className="min-h-screen bg-sand-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-deep-sea-blue"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-sand-white py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-matte-gold rounded-full mb-4 animate-float">
            <Trophy className="text-white" size={32} />
          </div>
          <h1 className="text-3xl font-cormorant font-bold text-deep-sea-blue mb-2">
            Classifica Live Puglia
          </h1>
          <p className="text-gray-600">
            Vedi chi sta vivendo e condividendo di più la Puglia autentica
          </p>
        </div>

        {/* Month Filter */}
        <div className="mb-8">
          <div className="bg-white rounded-[20px] p-4 mediterranean-shadow">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center space-x-2">
                <Calendar className="text-deep-sea-blue" size={20} />
                <span className="font-medium text-deep-sea-blue">Periodo:</span>
              </div>
              <select
                value={selectedMonth}
                onChange={(e) => setSelectedMonth(e.target.value)}
                className="px-4 py-2 border border-gray-200 rounded-[12px] focus:ring-2 focus:ring-matte-gold focus:border-transparent"
              >
                {monthOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            {leaderboardData && (
              <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
                <div className="flex items-center space-x-2">
                  <Users size={16} />
                  <span>{leaderboardData.total_participants} partecipanti attivi</span>
                </div>
                {userPosition > 0 && (
                  <div className="flex items-center space-x-2">
                    <Star size={16} className="text-matte-gold" />
                    <span>{t('your_position')}: <strong>#{userPosition}</strong></span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {leaderboardData?.leaderboard.length === 0 ? (
          <div className="text-center py-12">
            <Trophy className="mx-auto text-gray-400 mb-4" size={64} />
            <h3 className="text-xl font-semibold text-gray-600 mb-2">Nessun dato per questo periodo</h3>
            <p className="text-gray-500">{t('be_first_earn_points')}</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Podium - Top 3 */}
            {leaderboardData?.leaderboard.slice(0, 3).length > 0 && (
              <div className="bg-white rounded-[20px] p-8 mediterranean-shadow">
                <h2 className="text-xl font-cormorant font-bold text-deep-sea-blue mb-8 text-center">
                  🏆 Podio del Mese
                </h2>
                
                <div className="flex items-end justify-center space-x-4 md:space-x-8">
                  {/* 2nd Place */}
                  {leaderboardData.leaderboard[1] && (
                    <div className="text-center">
                      <div className="relative mb-4">
                        <div className="w-20 h-20 mx-auto">
                          {leaderboardData.leaderboard[1].avatar_url ? (
                            <img 
                              src={leaderboardData.leaderboard[1].avatar_url} 
                              alt={leaderboardData.leaderboard[1].name}
                              className="w-full h-full object-cover rounded-full border-4 border-gray-400"
                            />
                          ) : (
                            <div className="w-full h-full bg-gray-200 rounded-full border-4 border-gray-400 flex items-center justify-center">
                              <span className="text-gray-500 text-2xl">{leaderboardData.leaderboard[1].name.charAt(0)}</span>
                            </div>
                          )}
                        </div>
                        <div className="absolute -bottom-1 -right-1 w-8 h-8 bg-gray-400 rounded-full flex items-center justify-center text-white font-bold">
                          2
                        </div>
                      </div>
                      <div className="bg-gray-50 rounded-[16px] px-4 py-6 min-h-[120px] flex flex-col justify-center">
                        <div className="text-4xl mb-2">🥈</div>
                        <div className="font-bold text-deep-sea-blue">{leaderboardData.leaderboard[1].username}</div>
                        <div className="text-sm text-gray-600 mb-1">{leaderboardData.leaderboard[1].country}</div>
                        <div className="text-lg font-bold text-matte-gold">{leaderboardData.leaderboard[1].points} pts</div>
                        <div className="text-xs text-gray-500 mt-1">{leaderboardData.leaderboard[1].level}</div>
                      </div>
                    </div>
                  )}

                  {/* 1st Place */}
                  {leaderboardData.leaderboard[0] && (
                    <div className="text-center">
                      <div className="relative mb-4">
                        <div className="w-24 h-24 mx-auto">
                          {leaderboardData.leaderboard[0].avatar_url ? (
                            <img 
                              src={leaderboardData.leaderboard[0].avatar_url} 
                              alt={leaderboardData.leaderboard[0].name}
                              className="w-full h-full object-cover rounded-full border-4 border-yellow-400 animate-gold-glow"
                            />
                          ) : (
                            <div className="w-full h-full bg-gray-200 rounded-full border-4 border-yellow-400 animate-gold-glow flex items-center justify-center">
                              <span className="text-gray-500 text-3xl">{leaderboardData.leaderboard[0].name.charAt(0)}</span>
                            </div>
                          )}
                        </div>
                        <div className="absolute -bottom-1 -right-1 w-10 h-10 bg-yellow-400 rounded-full flex items-center justify-center text-white font-bold text-lg">
                          1
                        </div>
                      </div>
                      <div className="bg-yellow-50 rounded-[16px] px-4 py-6 min-h-[140px] flex flex-col justify-center border-2 border-yellow-200">
                        <div className="text-5xl mb-2">🥇</div>
                        <div className="font-bold text-deep-sea-blue text-lg">{leaderboardData.leaderboard[0].username}</div>
                        <div className="text-sm text-gray-600 mb-1">{leaderboardData.leaderboard[0].country}</div>
                        <div className="text-xl font-bold text-matte-gold">{leaderboardData.leaderboard[0].points} pts</div>
                        <div className="text-sm text-yellow-600 font-semibold mt-1">🌿 Champion</div>
                      </div>
                    </div>
                  )}

                  {/* 3rd Place */}
                  {leaderboardData.leaderboard[2] && (
                    <div className="text-center">
                      <div className="relative mb-4">
                        <div className="w-20 h-20 mx-auto">
                          {leaderboardData.leaderboard[2].avatar_url ? (
                            <img 
                              src={leaderboardData.leaderboard[2].avatar_url} 
                              alt={leaderboardData.leaderboard[2].name}
                              className="w-full h-full object-cover rounded-full border-4 border-orange-400"
                            />
                          ) : (
                            <div className="w-full h-full bg-gray-200 rounded-full border-4 border-orange-400 flex items-center justify-center">
                              <span className="text-gray-500 text-2xl">{leaderboardData.leaderboard[2].name.charAt(0)}</span>
                            </div>
                          )}
                        </div>
                        <div className="absolute -bottom-1 -right-1 w-8 h-8 bg-orange-400 rounded-full flex items-center justify-center text-white font-bold">
                          3
                        </div>
                      </div>
                      <div className="bg-orange-50 rounded-[16px] px-4 py-6 min-h-[120px] flex flex-col justify-center">
                        <div className="text-4xl mb-2">🥉</div>
                        <div className="font-bold text-deep-sea-blue">{leaderboardData.leaderboard[2].username}</div>
                        <div className="text-sm text-gray-600 mb-1">{leaderboardData.leaderboard[2].country}</div>
                        <div className="text-lg font-bold text-matte-gold">{leaderboardData.leaderboard[2].points} pts</div>
                        <div className="text-xs text-gray-500 mt-1">{leaderboardData.leaderboard[2].level}</div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Full Rankings */}
            <div className="bg-white rounded-[20px] mediterranean-shadow">
              <div className="p-6 border-b border-gray-100">
                <h3 className="text-lg font-semibold text-deep-sea-blue flex items-center">
                  <Medal className="mr-2" size={20} />
                  {t('complete_leaderboard')}
                </h3>
              </div>
              
              <div className="divide-y divide-gray-100">
                {leaderboardData?.leaderboard.map((participant, index) => {
                  const podium = getPodiumPosition(index + 1);
                  const isCurrentUser = participant.user_id === user.id;
                  
                  return (
                    <div 
                      key={participant.user_id} 
                      className={`p-4 flex items-center justify-between transition-colors ${
                        isCurrentUser ? 'bg-blue-50 border-l-4 border-blue-500' : 'hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center space-x-4">
                        {/* Position */}
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg ${
                          index < 3 ? podium.color : 'bg-gray-100 text-gray-600'
                        }`}>
                          {index < 3 ? podium.emoji : `#${index + 1}`}
                        </div>
                        
                        {/* Avatar */}
                        <div className="relative">
                          {participant.avatar_url ? (
                            <img 
                              src={participant.avatar_url} 
                              alt={participant.name}
                              className="w-12 h-12 object-cover rounded-full avatar-ring"
                            />
                          ) : (
                            <div className="w-12 h-12 bg-gray-200 rounded-full avatar-ring flex items-center justify-center">
                              <span className="text-gray-500 font-semibold">{participant.name.charAt(0)}</span>
                            </div>
                          )}
                          {isCurrentUser && (
                            <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                              <Star className="text-white" size={12} />
                            </div>
                          )}
                        </div>
                        
                        {/* User Info */}
                        <div>
                          <div className={`font-semibold ${
                            isCurrentUser ? 'text-blue-600' : 'text-deep-sea-blue'
                          }`}>
                            {participant.username}
                            {isCurrentUser && <span className="text-blue-500 ml-2">(Tu)</span>}
                          </div>
                          <div className="text-sm text-gray-600 flex items-center space-x-2">
                            <span>{participant.country}</span>
                            <span className="text-gray-400">•</span>
                            <span className="level-badge text-xs px-2 py-0.5">{participant.level}</span>
                          </div>
                        </div>
                      </div>
                      
                      {/* Points */}
                      <div className="text-right">
                        <div className="text-xl font-bold text-matte-gold">{participant.points}</div>
                        <div className="text-sm text-gray-500">{t('points')}</div>
                        {index < 3 && (
                          <div className="text-xs text-green-600 font-medium mt-1">
                            🏆 Premio garantito
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Your Position (if not in top 10) */}
            {userPosition > 10 && (
              <div className="bg-blue-50 border border-blue-200 rounded-[20px] p-6">
                <h3 className="text-lg font-semibold text-blue-800 mb-3 flex items-center">
                  <Star className="mr-2" size={20} />
                  {t('your_position')}
                </h3>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl font-bold text-blue-600">#{userPosition}</div>
                    <div>
                      <div className="font-semibold text-blue-800">{user.name}</div>
                      <div className="text-sm text-blue-600">{user.current_points} {t('points')}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-blue-600 mb-1">Per entrare in Top 3:</div>
                    <div className="font-bold text-blue-800">
                      {leaderboardData.leaderboard[2] ? 
                        `+${Math.max(0, leaderboardData.leaderboard[2].points - user.current_points + 1)} ${t('points')}` :
                        'Disponibile'
                      }
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Motivational CTA */}
        <div className="mt-8 text-center">
          <div className="bg-gradient-to-r from-deep-sea-blue to-blue-600 rounded-[20px] p-8 text-white">
            <h3 className="text-xl font-cormorant font-bold mb-3">
              Continua a Vivere la Puglia! 🌿
            </h3>
            <p className="text-sand-white/90 mb-4">
              Ogni post condiviso, ogni esperienza vissuta è un passo verso il podio.
            </p>
            <div className="text-sm text-sand-white/80">
              Reset classifica: 1° del mese prossimo
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Leaderboard;