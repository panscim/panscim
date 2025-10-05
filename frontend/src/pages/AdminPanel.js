import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Users, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Eye, 
  Shield,
  BarChart3,
  Settings,
  AlertTriangle,
  ExternalLink,
  Calendar,
  Trophy,
  Mail,
  Target,
  Plus,
  Edit3,
  ToggleLeft,
  ToggleRight
} from 'lucide-react';

const AdminPanel = () => {
  const [activeTab, setActiveTab] = useState('pending');
  const [data, setData] = useState({
    pendingActions: [],
    stats: {
      totalUsers: 0,
      totalActions: 0,
      pendingActions: 0,
      monthlyPoints: 0
    }
  });
  const [loading, setLoading] = useState(true);
  const [actionDetails, setActionDetails] = useState(null);
  
  // Email Admin State
  const [users, setUsers] = useState([]);
  const [emailForm, setEmailForm] = useState({
    recipients: [],
    subject: '',
    body: ''
  });
  const [emailLogs, setEmailLogs] = useState([]);
  const [emailLoading, setEmailLoading] = useState(false);
  const [testEmailAddress, setTestEmailAddress] = useState('');
  
  // Mission Management State
  const [missions, setMissions] = useState([]);
  const [missionStats, setMissionStats] = useState(null);
  const [missionForm, setMissionForm] = useState({
    title: '',
    description: '',
    points: 0,
    frequency: 'one-time',
    daily_limit: 0,
    weekly_limit: 0,
    is_active: true,
    requires_description: true,
    requires_photo: false,
    photo_source: 'both',
    requires_link: false,
    requires_approval: true
  });
  const [editingMission, setEditingMission] = useState(null);
  const [missionLoading, setMissionLoading] = useState(false);

  useEffect(() => {
    fetchAdminData();
  }, []);

  useEffect(() => {
    if (activeTab === 'email') {
      fetchUsers();
      fetchEmailLogs();
    } else if (activeTab === 'missions') {
      fetchMissions();
      fetchMissionStats();
    }
  }, [activeTab]);

  const fetchAdminData = async () => {
    try {
      const response = await axios.get('/admin/actions/pending');
      setData(prev => ({
        ...prev,
        pendingActions: response.data
      }));
      
      // Calculate basic stats from pending actions
      const stats = {
        totalUsers: new Set(response.data.map(a => a.user_id)).size,
        totalActions: response.data.length,
        pendingActions: response.data.filter(a => a.verification_status === 'pending').length,
        monthlyPoints: response.data.reduce((sum, a) => sum + (a.points_earned || 0), 0)
      };
      setData(prev => ({ ...prev, stats }));
    } catch (error) {
      console.error('Error fetching admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const verifyAction = async (actionId, status) => {
    try {
      await axios.put(`/admin/actions/${actionId}/verify?status=${status}`);
      fetchAdminData();
      setActionDetails(null);
      
      const message = status === 'approved' ? 'Azione approvata! 🌿' : 'Azione rifiutata.';
      alert(message);
    } catch (error) {
      alert('Errore nella verifica: ' + (error.response?.data?.detail || 'Errore sconosciuto'));
    }
  };

  // Email Admin Functions
  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/admin/users/list`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const fetchEmailLogs = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/admin/email/logs`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEmailLogs(response.data);
    } catch (error) {
      console.error('Error fetching email logs:', error);
    }
  };

  const sendTestEmail = async () => {
    if (!testEmailAddress) {
      alert('Inserisci un indirizzo email per il test');
      return;
    }
    
    setEmailLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/admin/email/test`, 
        { test_email: testEmailAddress },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('📩 Email di test inviata con successo!');
      setTestEmailAddress('');
    } catch (error) {
      alert('Errore invio test: ' + (error.response?.data?.detail || 'Errore sconosciuto'));
    } finally {
      setEmailLoading(false);
    }
  };

  const sendEmail = async () => {
    if (emailForm.recipients.length === 0) {
      alert('Seleziona almeno un destinatario');
      return;
    }
    if (!emailForm.subject.trim()) {
      alert('Inserisci un oggetto');
      return;
    }
    if (!emailForm.body.trim()) {
      alert('Inserisci il contenuto del messaggio');
      return;
    }

    setEmailLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/admin/email/send`, {
        recipients: emailForm.recipients,
        subject: emailForm.subject,
        body: emailForm.body
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert('📩 Email inviata con successo!');
      setEmailForm({ recipients: [], subject: '', body: '' });
      fetchEmailLogs(); // Refresh logs
    } catch (error) {
      alert('Errore invio email: ' + (error.response?.data?.detail || 'Errore sconosciuto'));
    } finally {
      setEmailLoading(false);
    }
  };

  // Mission Management Functions
  const fetchMissions = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/admin/missions`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMissions(response.data);
    } catch (error) {
      console.error('Error fetching missions:', error);
    }
  };

  const fetchMissionStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/admin/missions/statistics`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMissionStats(response.data);
    } catch (error) {
      console.error('Error fetching mission stats:', error);
    }
  };

  const createMission = async () => {
    if (!missionForm.title.trim() || !missionForm.description.trim() || missionForm.points <= 0) {
      alert('Compila tutti i campi richiesti');
      return;
    }

    setMissionLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/admin/missions`, missionForm, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert('🎯 Missione creata con successo!');
      setMissionForm({
        title: '',
        description: '',
        points: 0,
        frequency: 'one-time',
        daily_limit: 0,
        weekly_limit: 0,
        is_active: true
      });
      fetchMissions();
      fetchMissionStats();
    } catch (error) {
      alert('Errore creazione missione: ' + (error.response?.data?.detail || 'Errore sconosciuto'));
    } finally {
      setMissionLoading(false);
    }
  };

  const updateMission = async (missionId, updateData) => {
    setMissionLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.put(`${process.env.REACT_APP_BACKEND_URL}/api/admin/missions/${missionId}`, updateData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert('✅ Missione aggiornata con successo!');
      setEditingMission(null);
      fetchMissions();
      fetchMissionStats();
    } catch (error) {
      alert('Errore aggiornamento: ' + (error.response?.data?.detail || 'Errore sconosciuto'));
    } finally {
      setMissionLoading(false);
    }
  };

  const toggleMissionStatus = async (missionId, currentStatus) => {
    await updateMission(missionId, { is_active: !currentStatus });
  };

  const getActionIcon = (actionTypeId) => {
    const icons = {
      'like_post': '👍',
      'comment_post': '💬',
      'share_story': '📢',
      'post_hashtag': '#️⃣',
      'google_review': '⭐',
      'visit_partner': '🏢',
      'tag_bnb_photo': '📷',
      'invite_friend': '👥'
    };
    return icons[actionTypeId] || '🎯';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('it-IT', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    });
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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-12 h-12 bg-red-500 rounded-full flex items-center justify-center">
              <Shield className="text-white" size={24} />
            </div>
            <div>
              <h1 className="text-3xl font-cormorant font-bold text-deep-sea-blue">Admin Panel</h1>
              <p className="text-gray-600">Gestione Desideri di Puglia Club</p>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-[20px] p-4 mediterranean-shadow text-center">
              <div className="text-2xl font-bold text-blue-600">{data.stats.totalUsers}</div>
              <div className="text-sm text-gray-600">Utenti attivi</div>
            </div>
            <div className="bg-white rounded-[20px] p-4 mediterranean-shadow text-center">
              <div className="text-2xl font-bold text-green-600">{data.stats.totalActions}</div>
              <div className="text-sm text-gray-600">Azioni totali</div>
            </div>
            <div className="bg-white rounded-[20px] p-4 mediterranean-shadow text-center">
              <div className="text-2xl font-bold text-yellow-600">{data.stats.pendingActions}</div>
              <div className="text-sm text-gray-600">In attesa</div>
            </div>
            <div className="bg-white rounded-[20px] p-4 mediterranean-shadow text-center">
              <div className="text-2xl font-bold text-matte-gold">{data.stats.monthlyPoints}</div>
              <div className="text-sm text-gray-600">Punti mese</div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="mb-8">
          <div className="flex space-x-1 bg-white rounded-[20px] p-2 mediterranean-shadow overflow-x-auto">
            {[
              { id: 'pending', label: 'Azioni in attesa', icon: Clock, count: data.stats.pendingActions },
              { id: 'stats', label: 'Statistiche', icon: BarChart3 },
              { id: 'users', label: 'Utenti', icon: Users },
              { id: 'email', label: 'Email Admin', icon: Mail },
              { id: 'missions', label: 'Missioni', icon: Target },
              { id: 'settings', label: 'Impostazioni', icon: Settings }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-[16px] font-medium transition-all whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'bg-red-500 text-white shadow-md'
                      : 'text-deep-sea-blue hover:bg-gray-50'
                  }`}
                >
                  <Icon size={18} />
                  <span>{tab.label}</span>
                  {tab.count > 0 && (
                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                      activeTab === tab.id ? 'bg-red-600 text-white' : 'bg-red-100 text-red-700'
                    }`}>
                      {tab.count}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'pending' && (
          <div className="space-y-6">
            {data.pendingActions.length === 0 ? (
              <div className="text-center py-12">
                <CheckCircle className="mx-auto text-green-500 mb-4" size={64} />
                <h3 className="text-xl font-semibold text-gray-600 mb-2">Tutto approvato!</h3>
                <p className="text-gray-500">Non ci sono azioni in attesa di verifica.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {data.pendingActions.map((action) => (
                  <div key={action.id} className="bg-white rounded-[20px] p-6 mediterranean-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-4 flex-1">
                        {/* Action Icon */}
                        <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center text-2xl">
                          {getActionIcon(action.action_type_id)}
                        </div>
                        
                        {/* Action Details */}
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <h3 className="font-semibold text-deep-sea-blue">{action.action_name}</h3>
                            <span className="text-lg font-bold text-matte-gold">+{action.points_earned} pts</span>
                          </div>
                          
                          <div className="space-y-2">
                            <div className="flex items-center space-x-2 text-sm text-gray-600">
                              <Users size={16} />
                              <span><strong>{action.user_name}</strong> (@{action.username})</span>
                            </div>
                            
                            <div className="flex items-center space-x-2 text-sm text-gray-600">
                              <Calendar size={16} />
                              <span>{formatDate(action.created_at)}</span>
                            </div>
                            
                            <div className="bg-gray-50 rounded-lg p-3 mt-3">
                              <div className="text-sm font-medium text-gray-700 mb-1">Descrizione:</div>
                              <div className="text-sm text-gray-600">{action.description}</div>
                              
                              {action.submission_url && (
                                <div className="mt-2">
                                  <a 
                                    href={action.submission_url} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center space-x-1 text-blue-600 hover:text-blue-800 text-sm"
                                  >
                                    <ExternalLink size={14} />
                                    <span>Visualizza link</span>
                                  </a>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      {/* Action Buttons */}
                      <div className="flex flex-col space-y-2 ml-4">
                        <button
                          onClick={() => verifyAction(action.id, 'approved')}
                          className="flex items-center space-x-2 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-[12px] transition-colors"
                        >
                          <CheckCircle size={16} />
                          <span>Approva</span>
                        </button>
                        
                        <button
                          onClick={() => verifyAction(action.id, 'rejected')}
                          className="flex items-center space-x-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-[12px] transition-colors"
                        >
                          <XCircle size={16} />
                          <span>Rifiuta</span>
                        </button>
                        
                        <button
                          onClick={() => setActionDetails(action)}
                          className="flex items-center space-x-2 px-4 py-2 border border-gray-300 text-gray-700 hover:bg-gray-50 rounded-[12px] transition-colors"
                        >
                          <Eye size={16} />
                          <span>Dettagli</span>
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'stats' && (
          <div className="space-y-6">
            <div className="bg-white rounded-[20px] p-6 mediterranean-shadow">
              <h3 className="text-lg font-semibold text-deep-sea-blue mb-4 flex items-center">
                <BarChart3 className="mr-2" size={20} />
                Panoramica Mensile
              </h3>
              
              <div className="text-center py-12">
                <Trophy className="mx-auto text-matte-gold mb-4" size={64} />
                <h4 className="text-lg font-semibold text-gray-600 mb-2">Statistiche Avanzate</h4>
                <p className="text-gray-500">Dashboard analitiche in fase di sviluppo</p>
                <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl mx-auto">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{data.stats.totalUsers}</div>
                    <div className="text-sm text-gray-600">Utenti Registrati</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{data.stats.totalActions}</div>
                    <div className="text-sm text-gray-600">Azioni Inviate</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-yellow-600">{data.stats.pendingActions}</div>
                    <div className="text-sm text-gray-600">In Verifica</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-matte-gold">{data.stats.monthlyPoints}</div>
                    <div className="text-sm text-gray-600">Punti Totali</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <div className="bg-white rounded-[20px] p-6 mediterranean-shadow">
            <h3 className="text-lg font-semibold text-deep-sea-blue mb-4 flex items-center">
              <Users className="mr-2" size={20} />
              Gestione Utenti
            </h3>
            
            <div className="text-center py-12">
              <Users className="mx-auto text-gray-400 mb-4" size={64} />
              <h4 className="text-lg font-semibold text-gray-600 mb-2">Gestione Utenti</h4>
              <p className="text-gray-500">Funzionalità di gestione utenti in fase di sviluppo</p>
            </div>
          </div>
        )}

        {activeTab === 'missions' && (
          <div className="space-y-6">
            {/* Mission Statistics */}
            {missionStats && (
              <div className="bg-white rounded-[20px] p-6 mediterranean-shadow">
                <h3 className="text-lg font-semibold text-deep-sea-blue mb-4 flex items-center">
                  <BarChart3 className="mr-2" size={20} />
                  Statistiche Missioni - {missionStats.month_year}
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-blue-50 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-blue-600">{missionStats.overview.total_missions}</div>
                    <div className="text-sm text-blue-600">Missioni Totali</div>
                  </div>
                  <div className="bg-green-50 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-green-600">{missionStats.overview.active_missions}</div>
                    <div className="text-sm text-green-600">Missioni Attive</div>
                  </div>
                  <div className="bg-yellow-50 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-yellow-600">{missionStats.overview.total_completions}</div>
                    <div className="text-sm text-yellow-600">Completamenti</div>
                  </div>
                  <div className="bg-purple-50 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-purple-600">{missionStats.overview.total_points_awarded}</div>
                    <div className="text-sm text-purple-600">Punti Assegnati</div>
                  </div>
                </div>
              </div>
            )}

            {/* Create New Mission */}
            <div className="bg-white rounded-[20px] p-6 mediterranean-shadow">
              <h3 className="text-lg font-semibold text-deep-sea-blue mb-4 flex items-center">
                <Plus className="mr-2" size={20} />
                Crea Nuova Missione
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Titolo *</label>
                  <input
                    type="text"
                    value={missionForm.title}
                    onChange={(e) => setMissionForm(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="Nome della missione"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deep-sea-blue focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Punti *</label>
                  <input
                    type="number"
                    value={missionForm.points}
                    onChange={(e) => setMissionForm(prev => ({ ...prev, points: parseInt(e.target.value) || 0 }))}
                    placeholder="Punti da assegnare"
                    min="1"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deep-sea-blue focus:border-transparent"
                  />
                </div>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Descrizione *</label>
                <textarea
                  value={missionForm.description}
                  onChange={(e) => setMissionForm(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Descrivi cosa deve fare l'utente per completare la missione..."
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deep-sea-blue focus:border-transparent"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Frequenza</label>
                  <select
                    value={missionForm.frequency}
                    onChange={(e) => setMissionForm(prev => ({ ...prev, frequency: e.target.value }))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deep-sea-blue focus:border-transparent"
                  >
                    <option value="one-time">Una volta sola</option>
                    <option value="daily">Giornaliera</option>
                    <option value="weekly">Settimanale</option>
                  </select>
                </div>
                {missionForm.frequency === 'daily' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Limite Giornaliero</label>
                    <input
                      type="number"
                      value={missionForm.daily_limit}
                      onChange={(e) => setMissionForm(prev => ({ ...prev, daily_limit: parseInt(e.target.value) || 0 }))}
                      placeholder="0 = nessun limite"
                      min="0"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deep-sea-blue focus:border-transparent"
                    />
                  </div>
                )}
                {missionForm.frequency === 'weekly' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Limite Settimanale</label>
                    <input
                      type="number"
                      value={missionForm.weekly_limit}
                      onChange={(e) => setMissionForm(prev => ({ ...prev, weekly_limit: parseInt(e.target.value) || 0 }))}
                      placeholder="0 = nessun limite"
                      min="0"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deep-sea-blue focus:border-transparent"
                    />
                  </div>
                )}
                <div className="flex items-center">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={missionForm.is_active}
                      onChange={(e) => setMissionForm(prev => ({ ...prev, is_active: e.target.checked }))}
                      className="rounded text-deep-sea-blue"
                    />
                    <span className="text-sm font-medium text-gray-700">Attiva subito</span>
                  </label>
                </div>
              </div>

              {/* Verification Requirements */}
              <div className="border-t pt-4 mb-4">
                <h4 className="text-md font-semibold text-gray-700 mb-3">Requisiti di Verifica</h4>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div className="space-y-2">
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={missionForm.requires_description}
                        onChange={(e) => setMissionForm(prev => ({ ...prev, requires_description: e.target.checked }))}
                        className="rounded text-deep-sea-blue"
                      />
                      <span className="text-sm text-gray-700">Richiede descrizione</span>
                    </label>
                    
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={missionForm.requires_photo}
                        onChange={(e) => setMissionForm(prev => ({ ...prev, requires_photo: e.target.checked }))}
                        className="rounded text-deep-sea-blue"
                      />
                      <span className="text-sm text-gray-700">Richiede foto</span>
                    </label>
                    
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={missionForm.requires_link}
                        onChange={(e) => setMissionForm(prev => ({ ...prev, requires_link: e.target.checked }))}
                        className="rounded text-deep-sea-blue"
                      />
                      <span className="text-sm text-gray-700">Richiede link</span>
                    </label>
                  </div>
                  
                  <div className="space-y-2">
                    {missionForm.requires_photo && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Fonte foto</label>
                        <select
                          value={missionForm.photo_source}
                          onChange={(e) => setMissionForm(prev => ({ ...prev, photo_source: e.target.value }))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deep-sea-blue focus:border-transparent"
                        >
                          <option value="both">Galleria o Camera</option>
                          <option value="gallery">Solo Galleria</option>
                          <option value="camera">Solo Camera Live</option>
                        </select>
                      </div>
                    )}
                    
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={missionForm.requires_approval}
                        onChange={(e) => setMissionForm(prev => ({ ...prev, requires_approval: e.target.checked }))}
                        className="rounded text-deep-sea-blue"
                      />
                      <span className="text-sm text-gray-700">Richiede approvazione admin</span>
                    </label>
                  </div>
                </div>
              </div>

              <button
                onClick={createMission}
                disabled={missionLoading}
                className="w-full bg-deep-sea-blue text-white py-3 px-4 rounded-lg font-medium hover:bg-opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                <Target size={18} />
                <span>{missionLoading ? 'Creazione in corso...' : 'Crea Missione'}</span>
              </button>
            </div>

            {/* Missions List */}
            <div className="bg-white rounded-[20px] p-6 mediterranean-shadow">
              <h3 className="text-lg font-semibold text-deep-sea-blue mb-4 flex items-center">
                <Target className="mr-2" size={20} />
                Gestione Missioni ({missions.length})
              </h3>
              
              {missions.length === 0 ? (
                <div className="text-center py-8">
                  <Target className="mx-auto text-gray-400 mb-4" size={48} />
                  <p className="text-gray-500">Nessuna missione creata ancora</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {missions.map((mission) => (
                    <div key={mission.id} className={`border rounded-lg p-4 ${!mission.is_active ? 'bg-gray-50 opacity-75' : 'bg-white'}`}>
                      {editingMission === mission.id ? (
                        // Edit mode
                        <div className="space-y-4">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <input
                              type="text"
                              defaultValue={mission.title}
                              placeholder="Titolo missione"
                              className="px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-deep-sea-blue focus:border-transparent"
                              id={`edit-title-${mission.id}`}
                            />
                            <input
                              type="number"
                              defaultValue={mission.points}
                              placeholder="Punti"
                              min="1"
                              className="px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-deep-sea-blue focus:border-transparent"
                              id={`edit-points-${mission.id}`}
                            />
                          </div>
                          <textarea
                            defaultValue={mission.description}
                            placeholder="Descrizione"
                            rows={2}
                            className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-deep-sea-blue focus:border-transparent"
                            id={`edit-description-${mission.id}`}
                          />
                          <div className="flex space-x-2">
                            <button
                              onClick={() => {
                                const title = document.getElementById(`edit-title-${mission.id}`).value;
                                const description = document.getElementById(`edit-description-${mission.id}`).value;
                                const points = parseInt(document.getElementById(`edit-points-${mission.id}`).value);
                                updateMission(mission.id, { title, description, points });
                              }}
                              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 flex items-center space-x-1"
                            >
                              <CheckCircle size={16} />
                              <span>Salva</span>
                            </button>
                            <button
                              onClick={() => setEditingMission(null)}
                              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 flex items-center space-x-1"
                            >
                              <XCircle size={16} />
                              <span>Annulla</span>
                            </button>
                          </div>
                        </div>
                      ) : (
                        // View mode
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-2">
                              <h4 className="font-semibold text-gray-900">{mission.title}</h4>
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                mission.frequency === 'one-time' ? 'bg-blue-100 text-blue-800' :
                                mission.frequency === 'daily' ? 'bg-green-100 text-green-800' :
                                'bg-purple-100 text-purple-800'
                              }`}>
                                {mission.frequency === 'one-time' ? 'Una volta' :
                                 mission.frequency === 'daily' ? 'Giornaliera' : 'Settimanale'}
                              </span>
                              <span className="text-sm font-medium text-yellow-600">
                                {mission.points} punti
                              </span>
                              {!mission.is_active && (
                                <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs">
                                  Disattivata
                                </span>
                              )}
                            </div>
                            <p className="text-gray-600 text-sm mb-2">{mission.description}</p>
                            <div className="flex items-center space-x-4 text-xs text-gray-500">
                              <span>📊 {mission.completion_count} completamenti</span>
                              {mission.created_at && (
                                <span>📅 {new Date(mission.created_at).toLocaleDateString('it-IT')}</span>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center space-x-2 ml-4">
                            <button
                              onClick={() => setEditingMission(mission.id)}
                              className="p-2 text-blue-600 hover:bg-blue-100 rounded"
                              title="Modifica missione"
                            >
                              <Edit3 size={16} />
                            </button>
                            <button
                              onClick={() => toggleMissionStatus(mission.id, mission.is_active)}
                              className={`p-2 rounded ${mission.is_active ? 'text-red-600 hover:bg-red-100' : 'text-green-600 hover:bg-green-100'}`}
                              title={mission.is_active ? 'Disattiva missione' : 'Attiva missione'}
                            >
                              {mission.is_active ? <ToggleRight size={16} /> : <ToggleLeft size={16} />}
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="space-y-6">
            <div className="bg-white rounded-[20px] p-6 mediterranean-shadow">
              <h3 className="text-lg font-semibold text-deep-sea-blue mb-4 flex items-center">
                <Settings className="mr-2" size={20} />
                Impostazioni Sistema
              </h3>
              
              <div className="space-y-4">
                <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex items-start space-x-3">
                    <AlertTriangle className="text-yellow-600 mt-1" size={20} />
                    <div>
                      <div className="font-semibold text-yellow-800 mb-1">Reset Mensile Automatico</div>
                      <div className="text-yellow-700 text-sm">
                        Il sistema resetterà automaticamente le classifiche il 1° di ogni mese.
                        I vincitori verranno notificati via email.
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-start space-x-3">
                    <Shield className="text-blue-600 mt-1" size={20} />
                    <div>
                      <div className="font-semibold text-blue-800 mb-1">Sicurezza</div>
                      <div className="text-blue-700 text-sm">
                        Tutte le azioni degli utenti richiedono verifica manuale prima dell'assegnazione dei punti.
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'email' && (
          <div className="space-y-6">
            {/* Email Configuration Test */}
            <div className="bg-white rounded-[20px] p-6 mediterranean-shadow">
              <h3 className="text-lg font-semibold text-deep-sea-blue mb-4 flex items-center">
                <Settings className="mr-2" size={20} />
                Test Configurazione Email
              </h3>
              <div className="flex space-x-4 items-end">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email di test
                  </label>
                  <input
                    type="email"
                    value={testEmailAddress}
                    onChange={(e) => setTestEmailAddress(e.target.value)}
                    placeholder="inserisci@email.com"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deep-sea-blue focus:border-transparent"
                  />
                </div>
                <button
                  onClick={sendTestEmail}
                  disabled={emailLoading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
                >
                  <Mail size={16} />
                  <span>{emailLoading ? 'Invio...' : 'Test'}</span>
                </button>
              </div>
            </div>

            {/* Compose Email */}
            <div className="bg-white rounded-[20px] p-6 mediterranean-shadow">
              <h3 className="text-lg font-semibold text-deep-sea-blue mb-4 flex items-center">
                <Mail className="mr-2" size={20} />
                Componi Email
              </h3>
              
              <div className="space-y-4">
                {/* Recipients Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Destinatari ({emailForm.recipients.length} selezionati)
                  </label>
                  <div className="max-h-48 overflow-y-auto border border-gray-300 rounded-lg p-3">
                    {users.length === 0 ? (
                      <p className="text-gray-500 text-sm">Caricamento utenti...</p>
                    ) : (
                      <div className="space-y-2">
                        {users.map(user => (
                          <label key={user.id} className="flex items-center space-x-3 p-2 hover:bg-gray-50 rounded cursor-pointer">
                            <input
                              type="checkbox"
                              checked={emailForm.recipients.includes(user.id)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setEmailForm(prev => ({
                                    ...prev,
                                    recipients: [...prev.recipients, user.id]
                                  }));
                                } else {
                                  setEmailForm(prev => ({
                                    ...prev,
                                    recipients: prev.recipients.filter(id => id !== user.id)
                                  }));
                                }
                              }}
                              className="rounded text-deep-sea-blue"
                            />
                            <div className="flex-1">
                              <div className="font-medium text-gray-900">{user.name}</div>
                              <div className="text-sm text-gray-500">{user.email} • {user.current_points} punti</div>
                            </div>
                          </label>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="mt-2 flex space-x-2">
                    <button
                      onClick={() => setEmailForm(prev => ({ ...prev, recipients: users.map(u => u.id) }))}
                      className="text-sm text-deep-sea-blue hover:underline"
                    >
                      Seleziona tutti
                    </button>
                    <button
                      onClick={() => setEmailForm(prev => ({ ...prev, recipients: [] }))}
                      className="text-sm text-gray-500 hover:underline"
                    >
                      Deseleziona tutti
                    </button>
                  </div>
                </div>

                {/* Subject */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Oggetto
                  </label>
                  <input
                    type="text"
                    value={emailForm.subject}
                    onChange={(e) => setEmailForm(prev => ({ ...prev, subject: e.target.value }))}
                    placeholder="🌿 Oggetto dell'email..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deep-sea-blue focus:border-transparent"
                  />
                </div>

                {/* Body */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Messaggio
                  </label>
                  <div className="mb-2 text-xs text-gray-500">
                    Variabili disponibili: {'{{user_name}}'}, {'{{user_points}}'}, {'{{user_level}}'}, {'{{points_to_top3}}'}
                  </div>
                  <textarea
                    value={emailForm.body}
                    onChange={(e) => setEmailForm(prev => ({ ...prev, body: e.target.value }))}
                    placeholder="Ciao {{user_name}}, hai attualmente {{user_points}} punti..."
                    rows={8}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-deep-sea-blue focus:border-transparent"
                  />
                </div>

                {/* Send Button */}
                <button
                  onClick={sendEmail}
                  disabled={emailLoading || emailForm.recipients.length === 0}
                  className="w-full bg-deep-sea-blue text-white py-3 px-4 rounded-lg font-medium hover:bg-opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  <Mail size={18} />
                  <span>{emailLoading ? 'Invio in corso...' : `Invia a ${emailForm.recipients.length} utenti`}</span>
                </button>
              </div>
            </div>

            {/* Email Logs */}
            <div className="bg-white rounded-[20px] p-6 mediterranean-shadow">
              <h3 className="text-lg font-semibold text-deep-sea-blue mb-4 flex items-center">
                <Calendar className="mr-2" size={20} />
                Cronologia Email
              </h3>
              
              {emailLogs.length === 0 ? (
                <div className="text-center py-8">
                  <Mail className="mx-auto text-gray-400 mb-4" size={48} />
                  <p className="text-gray-500">Nessuna email inviata ancora</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {emailLogs.map((log, index) => (
                    <div key={log.id || index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900">{log.subject}</h4>
                          <div className="text-sm text-gray-500 mt-1">
                            {log.recipient_count} destinatari • {log.sent_at ? new Date(log.sent_at).toLocaleString('it-IT') : 'N/A'}
                          </div>
                        </div>
                        <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                          log.status === 'sent' ? 'bg-green-100 text-green-800' : 
                          log.status === 'partial' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {log.status === 'sent' ? '✓ Inviata' : 
                           log.status === 'partial' ? '⚠ Parziale' : 
                           '✗ Fallita'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Action Details Modal */}
      {actionDetails && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-[20px] p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-deep-sea-blue">Dettagli Azione</h3>
              <button
                onClick={() => setActionDetails(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                <XCircle size={24} />
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Utente</label>
                  <div className="text-deep-sea-blue font-semibold">{actionDetails.user_name}</div>
                  <div className="text-sm text-gray-600">@{actionDetails.username}</div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Azione</label>
                  <div className="text-deep-sea-blue font-semibold">{actionDetails.action_name}</div>
                  <div className="text-sm text-matte-gold">+{actionDetails.points_earned} punti</div>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Descrizione</label>
                <div className="bg-gray-50 p-3 rounded-lg text-sm">{actionDetails.description}</div>
              </div>
              
              {actionDetails.submission_url && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Link di verifica</label>
                  <a 
                    href={actionDetails.submission_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="inline-flex items-center space-x-1 text-blue-600 hover:text-blue-800"
                  >
                    <ExternalLink size={16} />
                    <span>Apri in una nuova scheda</span>
                  </a>
                </div>
              )}
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Data invio</label>
                  <div className="text-sm text-gray-600">{formatDate(actionDetails.created_at)}</div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Stato</label>
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                    <Clock size={12} className="mr-1" />
                    In attesa
                  </span>
                </div>
              </div>
            </div>
            
            <div className="flex space-x-3 mt-6 pt-4 border-t border-gray-200">
              <button
                onClick={() => verifyAction(actionDetails.id, 'approved')}
                className="flex-1 btn-primary bg-green-500 hover:bg-green-600 flex items-center justify-center space-x-2"
              >
                <CheckCircle size={18} />
                <span>Approva Azione</span>
              </button>
              <button
                onClick={() => verifyAction(actionDetails.id, 'rejected')}
                className="flex-1 px-4 py-3 bg-red-500 hover:bg-red-600 text-white rounded-[20px] font-semibold flex items-center justify-center space-x-2"
              >
                <XCircle size={18} />
                <span>Rifiuta Azione</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPanel;