import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import { 
  Trophy, 
  Target, 
  Gift, 
  Activity, 
  Bell, 
  Plus, 
  Star,
  Camera,
  CheckCircle,
  Clock,
  XCircle
} from 'lucide-react';

const Dashboard = () => {
  const { user, updateUser } = useAuth();
  const [activeTab, setActiveTab] = useState('missioni');
  const [data, setData] = useState({
    actionTypes: [],
    leaderboard: [],
    notifications: [],
    actionHistory: [],
    prizes: [],
    missions: []
  });
  const [loading, setLoading] = useState(true);
  const [submissionForm, setSubmissionForm] = useState({
    show: false,
    actionType: null,
    description: '',
    submissionUrl: ''
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [actionTypesRes, leaderboardRes, notificationsRes, historyRes, prizesRes] = await Promise.all([
        axios.get('/actions/types'),
        axios.get('/leaderboard'),
        axios.get('/notifications'),
        axios.get('/actions/history'),
        axios.get('/prizes')
      ]);

      setData({
        actionTypes: actionTypesRes.data,
        leaderboard: leaderboardRes.data.leaderboard,
        notifications: notificationsRes.data,
        actionHistory: historyRes.data,
        prizes: prizesRes.data
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const submitAction = async () => {
    try {
      const formData = new FormData();
      formData.append('action_type_id', submissionForm.actionType.id);
      formData.append('description', submissionForm.description);
      if (submissionForm.submissionUrl) {
        formData.append('submission_url', submissionForm.submissionUrl);
      }

      await axios.post('/actions/submit', formData);
      
      setSubmissionForm({ show: false, actionType: null, description: '', submissionUrl: '' });
      fetchDashboardData();
      
      alert('✨ Azione inviata! Riceverai i punti una volta approvata.');
    } catch (error) {
      alert(error.response?.data?.detail || 'Errore nell\'invio dell\'azione');
    }
  };

  const markNotificationRead = async (notificationId) => {
    try {
      await axios.put(`/notifications/${notificationId}/read`);
      fetchDashboardData();
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-sand-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-deep-sea-blue"></div>
      </div>
    );
  }

  const userPosition = data.leaderboard.findIndex(u => u.user_id === user.id) + 1;
  const nextLevelPoints = {
    'Explorer': 500,
    'Local Friend': 1000,
    'Ambassador': 2000,
    'Legend': 0
  };
  const pointsToNext = nextLevelPoints[user.level] - user.total_points;

  return (
    <div className="min-h-screen bg-sand-white py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-cormorant font-bold text-deep-sea-blue">
                Ciao, {user.name}! 🌿
              </h1>
              <p className="text-gray-600 mt-1">
                La tua avventura pugliese continua
              </p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-brand-dark">{user.current_points} pts</div>
              <div className="text-sm text-brand-accent font-medium">{user.level}</div>
              {userPosition > 0 && (
                <div className="text-xs text-gray-500">#{userPosition} in classifica</div>
              )}
            </div>
          </div>
          
          {/* Progress Bar */}
          {user.level !== 'Legend' && (
            <div className="mt-4 bg-white rounded-[20px] p-4 mediterranean-shadow">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-deep-sea-blue">Prossimo livello</span>
                <span className="text-sm text-matte-gold font-medium">+{pointsToNext} punti</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-matte-gold h-2 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min((user.total_points / nextLevelPoints[user.level]) * 100, 100)}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>

        {/* Navigation Tabs */}
        <div className="mb-8">
          <div className="flex space-x-1 bg-white rounded-[20px] p-2 mediterranean-shadow overflow-x-auto">
            {[
              { id: 'missioni', label: 'Missioni', icon: Target },
              { id: 'classifica', label: 'Classifica', icon: Trophy },
              { id: 'premi', label: 'Premi', icon: Gift },
              { id: 'attivita', label: 'Attività', icon: Activity },
              { id: 'notifiche', label: 'Notifiche', icon: Bell }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-[16px] font-medium transition-all whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'bg-matte-gold text-white shadow-md'
                      : 'text-deep-sea-blue hover:bg-gray-50'
                  }`}
                >
                  <Icon size={18} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'missioni' && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.actionTypes.map((action) => (
              <div key={action.id} className="puglia-card hover:transform hover:scale-105 transition-all duration-200">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="font-semibold text-deep-sea-blue mb-1">{action.name}</h3>
                    <p className="text-sm text-gray-600 mb-2">{action.description}</p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      {action.max_per_day > 0 && (
                        <span>{action.max_per_day}/giorno</span>
                      )}
                      {action.max_per_week > 0 && (
                        <span>{action.max_per_week}/settimana</span>
                      )}
                      {action.max_per_month > 0 && (
                        <span>{action.max_per_month}/mese</span>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-matte-gold">+{action.points}</div>
                    <div className="text-xs text-gray-500">punti</div>
                  </div>
                </div>
                <button
                  onClick={() => setSubmissionForm({ show: true, actionType: action, description: '', submissionUrl: '' })}
                  className="w-full btn-secondary text-sm py-2 flex items-center justify-center space-x-1"
                >
                  <Plus size={16} />
                  <span>Completa</span>
                </button>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'classifica' && (
          <div className="space-y-6">
            {/* Top 3 */}
            {data.leaderboard.slice(0, 3).length > 0 && (
              <div className="bg-white rounded-[20px] p-6 mediterranean-shadow">
                <h3 className="text-xl font-cormorant font-bold text-deep-sea-blue mb-6 text-center">
                  🏆 Top 3 del Mese
                </h3>
                <div className="flex items-end justify-center space-x-8">
                  {/* 2nd Place */}
                  {data.leaderboard[1] && (
                    <div className="text-center">
                      <div className="w-16 h-16 mx-auto mb-2 relative">
                        {data.leaderboard[1].avatar_url ? (
                          <img 
                            src={data.leaderboard[1].avatar_url} 
                            alt={data.leaderboard[1].name}
                            className="w-full h-full object-cover rounded-full border-4 border-gray-300"
                          />
                        ) : (
                          <div className="w-full h-full bg-gray-200 rounded-full border-4 border-gray-300 flex items-center justify-center">
                            <span className="text-gray-500 text-lg">{data.leaderboard[1].name.charAt(0)}</span>
                          </div>
                        )}
                        <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-gray-400 rounded-full flex items-center justify-center text-white text-xs font-bold">
                          2
                        </div>
                      </div>
                      <div className="font-semibold text-deep-sea-blue">{data.leaderboard[1].username}</div>
                      <div className="text-sm text-matte-gold font-medium">{data.leaderboard[1].points} pts</div>
                    </div>
                  )}

                  {/* 1st Place */}
                  {data.leaderboard[0] && (
                    <div className="text-center">
                      <div className="w-20 h-20 mx-auto mb-2 relative">
                        {data.leaderboard[0].avatar_url ? (
                          <img 
                            src={data.leaderboard[0].avatar_url} 
                            alt={data.leaderboard[0].name}
                            className="w-full h-full object-cover rounded-full border-4 border-yellow-400"
                          />
                        ) : (
                          <div className="w-full h-full bg-gray-200 rounded-full border-4 border-yellow-400 flex items-center justify-center">
                            <span className="text-gray-500 text-xl">{data.leaderboard[0].name.charAt(0)}</span>
                          </div>
                        )}
                        <div className="absolute -bottom-1 -right-1 w-8 h-8 bg-yellow-400 rounded-full flex items-center justify-center text-white font-bold">
                          1
                        </div>
                      </div>
                      <div className="font-bold text-deep-sea-blue">{data.leaderboard[0].username}</div>
                      <div className="text-sm text-matte-gold font-medium">{data.leaderboard[0].points} pts</div>
                      <div className="text-xs text-yellow-600 font-semibold">🌿 Leader</div>
                    </div>
                  )}

                  {/* 3rd Place */}
                  {data.leaderboard[2] && (
                    <div className="text-center">
                      <div className="w-16 h-16 mx-auto mb-2 relative">
                        {data.leaderboard[2].avatar_url ? (
                          <img 
                            src={data.leaderboard[2].avatar_url} 
                            alt={data.leaderboard[2].name}
                            className="w-full h-full object-cover rounded-full border-4 border-orange-400"
                          />
                        ) : (
                          <div className="w-full h-full bg-gray-200 rounded-full border-4 border-orange-400 flex items-center justify-center">
                            <span className="text-gray-500 text-lg">{data.leaderboard[2].name.charAt(0)}</span>
                          </div>
                        )}
                        <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-orange-400 rounded-full flex items-center justify-center text-white text-xs font-bold">
                          3
                        </div>
                      </div>
                      <div className="font-semibold text-deep-sea-blue">{data.leaderboard[2].username}</div>
                      <div className="text-sm text-matte-gold font-medium">{data.leaderboard[2].points} pts</div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Full Leaderboard */}
            <div className="bg-white rounded-[20px] mediterranean-shadow">
              <div className="p-6 border-b border-gray-100">
                <h3 className="text-lg font-semibold text-deep-sea-blue">Classifica Completa</h3>
              </div>
              <div className="divide-y divide-gray-100">
                {data.leaderboard.slice(0, 10).map((user, index) => (
                  <div key={user.user_id} className="p-4 flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="text-lg font-bold text-gray-400 w-8">#{index + 1}</div>
                      {user.avatar_url ? (
                        <img 
                          src={user.avatar_url} 
                          alt={user.name}
                          className="w-10 h-10 object-cover rounded-full avatar-ring"
                        />
                      ) : (
                        <div className="w-10 h-10 bg-gray-200 rounded-full avatar-ring flex items-center justify-center">
                          <span className="text-gray-500">{user.name.charAt(0)}</span>
                        </div>
                      )}
                      <div>
                        <div className="font-semibold text-deep-sea-blue">{user.username}</div>
                        <div className="text-sm text-gray-600">{user.country} • {user.level}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-matte-gold">{user.points} pts</div>
                      {index < 3 && (
                        <div className="text-xs text-gray-500">Top 3 🏆</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'premi' && (
          <div className="grid md:grid-cols-3 gap-6">
            {data.prizes.map((prize) => (
              <div key={prize.position} className="puglia-card text-center">
                <div className="mb-4">
                  {prize.position === 1 && <div className="text-4xl mb-2">🥇</div>}
                  {prize.position === 2 && <div className="text-4xl mb-2">🥈</div>}
                  {prize.position === 3 && <div className="text-4xl mb-2">🥉</div>}
                  <h3 className="font-semibold text-deep-sea-blue mb-2">{prize.title}</h3>
                  <p className="text-sm text-gray-600">{prize.description}</p>
                </div>
                {userPosition <= 3 && userPosition === prize.position ? (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                    <CheckCircle className="text-green-500 mx-auto mb-2" size={24} />
                    <div className="text-green-800 font-semibold text-sm">Hai vinto questo premio!</div>
                  </div>
                ) : (
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                    <div className="text-gray-500 text-sm">Solo per i Top 3 🌿</div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {activeTab === 'attivita' && (
          <div className="space-y-4">
            {data.actionHistory.length === 0 ? (
              <div className="text-center py-12">
                <Activity className="mx-auto text-gray-400 mb-4" size={48} />
                <h3 className="text-lg font-semibold text-gray-600 mb-2">Nessuna attività ancora</h3>
                <p className="text-gray-500">Inizia a completare le missioni per vedere la tua cronologia!</p>
              </div>
            ) : (
              data.actionHistory.map((action) => (
                <div key={action.id} className="puglia-card flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      action.verification_status === 'approved' ? 'bg-green-100' :
                      action.verification_status === 'rejected' ? 'bg-red-100' : 'bg-yellow-100'
                    }`}>
                      {action.verification_status === 'approved' && <CheckCircle className="text-green-600" size={20} />}
                      {action.verification_status === 'rejected' && <XCircle className="text-red-600" size={20} />}
                      {action.verification_status === 'pending' && <Clock className="text-yellow-600" size={20} />}
                    </div>
                    <div>
                      <div className="font-semibold text-deep-sea-blue">{action.action_name}</div>
                      <div className="text-sm text-gray-600">{action.description}</div>
                      <div className="text-xs text-gray-500">
                        {new Date(action.created_at).toLocaleDateString('it-IT', {
                          day: 'numeric',
                          month: 'long',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`font-bold ${
                      action.verification_status === 'approved' ? 'text-green-600' :
                      action.verification_status === 'rejected' ? 'text-red-600' : 'text-yellow-600'
                    }`}>
                      {action.verification_status === 'approved' && '+' + action.points_earned + ' pts'}
                      {action.verification_status === 'rejected' && 'Rifiutata'}
                      {action.verification_status === 'pending' && 'In verifica'}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'notifiche' && (
          <div className="space-y-4">
            {data.notifications.length === 0 ? (
              <div className="text-center py-12">
                <Bell className="mx-auto text-gray-400 mb-4" size={48} />
                <h3 className="text-lg font-semibold text-gray-600 mb-2">Nessuna notifica</h3>
                <p className="text-gray-500">Le tue notifiche appariranno qui!</p>
              </div>
            ) : (
              data.notifications.map((notification) => (
                <div 
                  key={notification.id} 
                  className={`puglia-card cursor-pointer ${
                    !notification.read ? 'border-l-4 border-matte-gold' : ''
                  }`}
                  onClick={() => !notification.read && markNotificationRead(notification.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-semibold text-deep-sea-blue mb-1">{notification.title}</h4>
                      <p className="text-gray-600 text-sm mb-2">{notification.message}</p>
                      <div className="text-xs text-gray-500">
                        {new Date(notification.created_at).toLocaleDateString('it-IT', {
                          day: 'numeric',
                          month: 'long',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                    </div>
                    {!notification.read && (
                      <div className="w-2 h-2 bg-matte-gold rounded-full"></div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Action Submission Modal */}
      {submissionForm.show && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-[20px] p-6 max-w-md w-full max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-semibold text-deep-sea-blue mb-4">
              Completa: {submissionForm.actionType?.name}
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-deep-sea-blue mb-2">
                  Descrizione dell'azione
                </label>
                <textarea
                  value={submissionForm.description}
                  onChange={(e) => setSubmissionForm({...submissionForm, description: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-200 rounded-[20px] focus:ring-2 focus:ring-matte-gold focus:border-transparent"
                  placeholder="Descrivi cosa hai fatto..."
                  rows={3}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-deep-sea-blue mb-2">
                  Link/URL (opzionale)
                </label>
                <input
                  type="url"
                  value={submissionForm.submissionUrl}
                  onChange={(e) => setSubmissionForm({...submissionForm, submissionUrl: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-200 rounded-[20px] focus:ring-2 focus:ring-matte-gold focus:border-transparent"
                  placeholder="Link al post, foto, recensione..."
                />
              </div>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <p className="text-yellow-800 text-sm">
                  💡 <strong>Ricorda:</strong> Fornisci dettagli accurati per una verifica più veloce!
                </p>
              </div>
            </div>
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setSubmissionForm({...submissionForm, show: false})}
                className="flex-1 px-4 py-3 border border-gray-300 rounded-[20px] text-gray-700 font-medium hover:bg-gray-50"
              >
                Annulla
              </button>
              <button
                onClick={submitAction}
                disabled={!submissionForm.description.trim()}
                className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Invia 🌿
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;