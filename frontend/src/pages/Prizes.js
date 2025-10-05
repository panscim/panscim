import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { t } from '@/utils/translations';
import axios from 'axios';
import { Gift, Trophy, Star, MapPin, Clock, CheckCircle } from 'lucide-react';

const Prizes = () => {
  const { user } = useAuth();
  const [prizes, setPrizes] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPrizesData();
  }, []);

  const fetchPrizesData = async () => {
    try {
      const [prizesRes, leaderboardRes] = await Promise.all([
        axios.get('/prizes'),
        axios.get('/leaderboard')
      ]);
      
      setPrizes(prizesRes.data);
      setLeaderboard(leaderboardRes.data.leaderboard);
    } catch (error) {
      console.error('Error fetching prizes data:', error);
    } finally {
      setLoading(false);
    }
  };

  const userPosition = leaderboard.findIndex(u => u.user_id === user.id) + 1;
  const isInTop3 = userPosition > 0 && userPosition <= 3;
  const pointsToTop3 = leaderboard[2] ? Math.max(0, leaderboard[2].points - user.current_points + 1) : 0;

  // Check if current month is concluded (after 28th of the month)
  const currentDate = new Date();
  const isMonthConcluded = currentDate.getDate() > 28;

  const getPrizeIcon = (position) => {
    const icons = {
      1: { emoji: '🥇', bg: 'bg-yellow-100', border: 'border-yellow-300', text: 'text-yellow-700' },
      2: { emoji: '🥈', bg: 'bg-gray-100', border: 'border-gray-300', text: 'text-gray-700' },
      3: { emoji: '🥉', bg: 'bg-orange-100', border: 'border-orange-300', text: 'text-orange-700' }
    };
    return icons[position] || icons[1];
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-sand-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-deep-sea-blue"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-sand-white py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-matte-gold rounded-full mb-4 animate-float">
            <Gift className="text-white" size={32} />
          </div>
          <h1 className="text-3xl font-cormorant font-bold text-deep-sea-blue mb-2">
            Premi Live Puglia
          </h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            {t('top_3_monthly_description')} 
            Vivi, condividi e vinci momenti indimenticabili.
          </p>
        </div>

        {/* Current Status */}
        <div className="mb-8">
          <div className={`rounded-[20px] p-6 mediterranean-shadow ${
            isInTop3 ? 'bg-green-50 border border-green-200' : 'bg-blue-50 border border-blue-200'
          }`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                  isInTop3 ? 'bg-green-100' : 'bg-blue-100'
                }`}>
                  {isInTop3 ? (
                    <Trophy className="text-green-600" size={24} />
                  ) : (
                    <Star className="text-blue-600" size={24} />
                  )}
                </div>
                <div>
                  <div className={`font-semibold ${
                    isInTop3 ? 'text-green-800' : 'text-blue-800'
                  }`}>
                    {isInTop3 ? (
                      `🏆 Sei in Top 3! Posizione #${userPosition}`
                    ) : userPosition > 0 ? (
                      `Posizione attuale: #${userPosition}`
                    ) : (
                      'Inizia a guadagnare punti per entrare in classifica'
                    )}
                  </div>
                  <div className={`text-sm ${
                    isInTop3 ? 'text-green-600' : 'text-blue-600'
                  }`}>
                    {isInTop3 && isMonthConcluded ? (
                      'Hai vinto un premio questo mese!'
                    ) : isInTop3 ? (
                      'Sei in posizione di vincita per questo mese!'
                    ) : pointsToTop3 > 0 ? (
                      `Ti servono +${pointsToTop3} punti per entrare in Top 3`
                    ) : (
                      'Completa le missioni per scalare la classifica'
                    )}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-matte-gold">{user.current_points}</div>
                <div className="text-sm text-gray-600">punti questo mese</div>
              </div>
            </div>
          </div>
        </div>

        {/* Monthly Prizes */}
        <div className="mb-8">
          <h2 className="text-2xl font-cormorant font-bold text-deep-sea-blue mb-6 text-center">
            Premi di {new Date().toLocaleDateString('it-IT', { month: 'long', year: 'numeric' }).replace(/^\w/, c => c.toUpperCase())}
          </h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            {prizes.map((prize) => {
              const prizeStyle = getPrizeIcon(prize.position);
              // User has won only if month is concluded AND they're in the winning position
              const hasWon = isMonthConcluded && isInTop3 && userPosition === prize.position;
              
              return (
                <div 
                  key={prize.position} 
                  className={`puglia-card relative overflow-hidden group hover:transform hover:scale-105 transition-all duration-300 ${
                    hasWon ? 'ring-2 ring-green-400 ring-opacity-50' : ''
                  }`}
                >
                  {/* Prize Badge */}
                  <div className={`absolute top-4 right-4 w-12 h-12 rounded-full flex items-center justify-center ${prizeStyle.bg} ${prizeStyle.border} border-2`}>
                    <span className="text-2xl">{prizeStyle.emoji}</span>
                  </div>
                  
                  {hasWon && (
                    <div className="absolute top-4 left-4">
                      <div className="bg-green-500 text-white px-2 py-1 rounded-full text-xs font-semibold flex items-center space-x-1">
                        <CheckCircle size={14} />
                        <span>Vinto!</span>
                      </div>
                    </div>
                  )}
                  
                  <div className="pt-8">
                    {/* Prize Image Placeholder */}
                    <div className="w-full h-48 bg-gradient-to-br from-deep-sea-blue to-blue-600 rounded-[16px] mb-4 flex items-center justify-center relative overflow-hidden">
                      <div className="absolute inset-0 bg-black bg-opacity-20"></div>
                      <div className="relative z-10 text-center text-white">
                        <div className="text-4xl mb-2">
                          {prize.position === 1 && '🏨'}
                          {prize.position === 2 && '🍽️'}
                          {prize.position === 3 && '🍸'}
                        </div>
                        <div className="text-lg font-semibold">{prize.position}° Posto</div>
                      </div>
                      
                      {/* Floating Elements */}
                      <div className="absolute top-4 left-4 text-white opacity-20">
                        <div className="w-4 h-4 bg-white rounded-full animate-float"></div>
                      </div>
                      <div className="absolute bottom-4 right-4 text-white opacity-20">
                        <div className="w-3 h-3 bg-white rounded-full animate-float" style={{animationDelay: '1s'}}></div>
                      </div>
                    </div>
                    
                    {/* Prize Details */}
                    <div className="space-y-3">
                      <h3 className="text-lg font-semibold text-deep-sea-blue">{prize.title}</h3>
                      <p className="text-gray-600 text-sm leading-relaxed">{prize.description}</p>
                      
                      {/* Prize Value & Details */}
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <MapPin size={16} className="text-matte-gold" />
                          <span>Barletta e partner locali</span>
                        </div>
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <Clock size={16} className="text-matte-gold" />
                          <span>Validità: 3 mesi dal vincita</span>
                        </div>
                      </div>
                      
                      {/* Prize Status */}
                      <div className="pt-3 border-t border-gray-100">
                        {hasWon ? (
                          <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
                            <div className="text-green-800 font-semibold text-sm mb-1">
                              🎉 Congratulazioni!
                            </div>
                            <div className="text-green-600 text-xs">
                              Il premio è tuo! Riceverai le istruzioni via email.
                            </div>
                          </div>
                        ) : isMonthConcluded ? (
                          <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-center">
                            <div className="text-gray-600 text-sm mb-1">
                              Premio assegnato
                            </div>
                            <div className="text-gray-500 text-xs">
                              Mese concluso - vinto da altro utente
                            </div>
                          </div>
                        ) : isInTop3 && userPosition === prize.position ? (
                          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-center">
                            <div className="text-blue-800 font-semibold text-sm mb-1">
                              🏆 Sei in posizione di vincita!
                            </div>
                            <div className="text-blue-600 text-xs">
                              Mantieni la posizione fino alla fine del mese.
                            </div>
                          </div>
                        ) : isInTop3 ? (
                          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-center">
                            <div className="text-yellow-800 font-semibold text-sm mb-1">
                              🥇 Sei in Top 3!
                            </div>
                            <div className="text-yellow-600 text-xs">
                              Continua così per vincere un premio questo mese.
                            </div>
                          </div>
                        ) : (
                          <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-center">
                            <div className="text-gray-600 text-sm mb-1">
                              Partecipa alla competizione
                            </div>
                            <div className="text-gray-500 text-xs">
                              {pointsToTop3 > 0 ? `${pointsToTop3} punti per entrare in Top 3` : 'Completa le missioni per qualificarti'}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Next Month Message */}
        <div className="bg-gradient-to-r from-sand-light to-sand-medium rounded-[20px] p-8 mediterranean-shadow text-center">
          <h3 className="text-xl font-cormorant font-bold text-black mb-4">
            Il Prossimo Mese Ti Aspetta! 🌿
          </h3>
          <p className="text-black mb-4 leading-relaxed">
            Ogni mese nuovi premi, nuove sfide, nuove opportunità di vivere la Puglia autentica.
          </p>
          <div className="inline-flex items-center bg-white bg-opacity-50 rounded-lg px-4 py-2">
            <span className="text-black font-semibold">Reset: 1° Novembre</span>
          </div>
        </div>

        {/* How Prizes Work */}
        <div className="bg-white rounded-[20px] p-8 mediterranean-shadow">
          <h3 className="text-xl font-cormorant font-bold text-deep-sea-blue mb-6 text-center">
            {t('how_prizes_work')}
          </h3>
          
          <div className="grid md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <h4 className="font-semibold text-deep-sea-blue flex items-center">
                <Trophy className="mr-2 text-matte-gold" size={20} />
                Selezione Vincitori
              </h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start space-x-2">
                  <span className="text-matte-gold mt-1">•</span>
                  <span>I primi 3 in classifica il 30 di ogni mese vincono</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-matte-gold mt-1">•</span>
                  <span>Classifica si azzera automaticamente ogni mese</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-matte-gold mt-1">•</span>
                  <span>Vincitori contattati entro 48 ore via email</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-matte-gold mt-1">•</span>
                  <span>Ogni mese è una nuova opportunità!</span>
                </li>
              </ul>
            </div>
            
            <div className="space-y-4">
              <h4 className="font-semibold text-deep-sea-blue flex items-center">
                <Gift className="mr-2 text-matte-gold" size={20} />
                Riscatto Premi
              </h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start space-x-2">
                  <span className="text-matte-gold mt-1">•</span>
                  <span>Premi validi per 3 mesi dalla vincita</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-matte-gold mt-1">•</span>
                  <span>Prenotazione diretta con partner locali</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-matte-gold mt-1">•</span>
                  <span>Assistenza dedicata per prenotazioni</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-matte-gold mt-1">•</span>
                  <span>Esperienza autentica garantita</span>
                </li>
              </ul>
            </div>
          </div>
          
          <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start space-x-3">
              <div className="text-blue-500 mt-1">
                💡
              </div>
              <div>
                <div className="font-semibold text-blue-800 text-sm mb-1">Suggerimento</div>
                <div className="text-blue-600 text-sm">
                  I premi vengono offerti in collaborazione con partner locali selezionati, 
                  garantendo esperienze autentiche e di qualità nella splendida Puglia.
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Next Month Preview */}
        <div className="mt-8 text-center">
          <div className="bg-gradient-to-r from-matte-gold to-yellow-500 rounded-[20px] p-8 text-white">
            <h3 className="text-xl font-cormorant font-bold mb-3">
              Il Prossimo Mese Ti Aspetta! 🌿
            </h3>
            <p className="text-sand-white/90 mb-4">
              Ogni mese nuovi premi, nuove sfide, nuove opportunità di vivere la Puglia autentica.
            </p>
            <div className="text-sm text-sand-white/80">
              Reset: 1° {new Date(new Date().setMonth(new Date().getMonth() + 1)).toLocaleDateString('it-IT', { month: 'long' }).replace(/^\w/, c => c.toUpperCase())}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Prizes;