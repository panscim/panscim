// Centralized translations system
const translations = {
  it: {
    // Navigation
    home: 'Home',
    dashboard: 'Dashboard',
    leaderboard: 'Classifica',
    prizes: 'Premi',
    missions: 'Missioni', 
    profile: 'Profilo',
    admin_panel: 'Pannello Admin',
    
    // Common
    welcome: 'Benvenuto',
    points: 'punti',
    level: 'Livello',
    loading: 'Caricamento...',
    save: 'Salva',
    cancel: 'Annulla',
    confirm: 'Conferma', 
    delete: 'Elimina',
    edit: 'Modifica',
    create: 'Crea',
    view: 'Visualizza',
    download: 'Scarica',
    upload: 'Carica',
    send: 'Invia',
    close: 'Chiudi',
    
    // Auth
    login: 'Accedi',
    register: 'Registrati',
    logout: 'Esci',
    email: 'Email',
    password: 'Password',
    name: 'Nome',
    username: 'Username',
    
    // Missions & Actions
    mission_completed: 'Missione completata 🌿',
    complete_mission: 'Completa Missione',
    submit_mission: 'Invia Missione', 
    mission_description: 'Descrizione della missione',
    daily_missions: 'Missioni Giornaliere',
    weekly_missions: 'Missioni Settimanali',
    special_missions: 'Missioni Speciali',
    social_actions: 'Azioni Social',
    pending_approval: 'In verifica',
    limit_reached: 'Limite raggiunto',
    completed: 'Completata',
    available: 'Disponibile',
    
    // Prizes  
    monthly_rewards: 'Premi del mese',
    current_prizes: 'Premi Attuali',
    first_place: '1° Posto',
    second_place: '2° Posto', 
    third_place: '3° Posto',
    no_prizes_yet: 'Nessun premio disponibile',
    
    // Profile & Dashboard
    my_profile: 'Il mio Profilo',
    my_club_card: 'La mia Card',
    total_points: 'Punti totali',
    current_points: 'Punti questo mese',
    current_position: 'Posizione attuale',
    notifications: 'Notifiche',
    action_history: 'Cronologia Azioni',
    
    // Club Card
    club_card_ready: 'La tua nuova Card Desideri di Puglia è pronta — elegante e interattiva come te 🌿',
    download_card: 'Scarica Card',
    add_to_wallet: 'Aggiungi al Wallet',
    scan_qr: 'Scansiona per visualizzare il tuo profilo 🌿',
    official_member_card: 'Official Member Card',
    member_since: 'Membro dal',
    club_statistics: 'Le tue statistiche',
    
    // Admin
    pending_actions: 'Azioni in attesa',
    statistics: 'Statistiche',
    users: 'Utenti',
    email_admin: 'Email Admin',
    missions_admin: 'Missioni',
    prizes_admin: 'Premi',
    settings: 'Impostazioni',
    approve: 'Approva',
    reject: 'Rifiuta',
    restore_defaults: 'Ripristina Default',
    
    // Messages & Notifications
    language_updated: '🌿 Lingua aggiornata in tempo reale: Italiano',
    prize_updated: '🌿 Premio aggiornato con successo e visibile agli utenti 🌿',
    mission_created: '🎯 Missione creata con successo!',
    email_sent: '📩 Email inviata con successo!',
    success: 'Successo',
    error: 'Errore',
    
    // Public Profile
    public_profile: 'Profilo Pubblico',
    profile_not_found: 'Profilo Non Trovato',
    loading_profile: 'Caricamento profilo Club...',
    current_rank: 'Posizione Attuale',
    missions_completed: 'Missioni Complete',
    prizes_and_awards: 'Premi e Riconoscimenti',
    current_month_prize: 'Premio del Mese Corrente',
    past_prizes: 'Premi Precedenti',
    no_prizes_message: 'Nessun premio ancora — continua a giocare!',
    
    // Wallet
    wallet_coming_soon: 'Aggiungi al Wallet — Presto disponibile'
  },
  
  en: {
    // Navigation  
    home: 'Home',
    dashboard: 'Dashboard',
    leaderboard: 'Leaderboard',
    prizes: 'Prizes',
    missions: 'Missions',
    profile: 'Profile', 
    admin_panel: 'Admin Panel',
    
    // Common
    welcome: 'Welcome',
    points: 'points',
    level: 'Level',
    loading: 'Loading...',
    save: 'Save',
    cancel: 'Cancel',
    confirm: 'Confirm',
    delete: 'Delete',
    edit: 'Edit',
    create: 'Create',
    view: 'View',
    download: 'Download',
    upload: 'Upload',
    send: 'Send',
    close: 'Close',
    
    // Auth
    login: 'Login',
    register: 'Register',
    logout: 'Logout',
    email: 'Email',
    password: 'Password',
    name: 'Name',
    username: 'Username',
    
    // Missions & Actions
    mission_completed: 'Mission accomplished 🌿',
    complete_mission: 'Complete Mission',
    submit_mission: 'Submit Mission', 
    mission_description: 'Mission description',
    daily_missions: 'Daily Missions',
    weekly_missions: 'Weekly Missions',
    special_missions: 'Special Missions',
    social_actions: 'Social Actions',
    pending_approval: 'Pending approval',
    limit_reached: 'Limit reached',
    completed: 'Completed',
    available: 'Available',
    
    // Prizes
    monthly_rewards: 'Monthly Rewards',
    current_prizes: 'Current Prizes',
    first_place: '1st Place',
    second_place: '2nd Place',
    third_place: '3rd Place',
    no_prizes_yet: 'No prizes available yet',
    
    // Profile & Dashboard
    my_profile: 'My Profile',
    my_club_card: 'My Club Card', 
    total_points: 'Total Points',
    current_points: 'Points this month',
    current_position: 'Current Position',
    notifications: 'Notifications',
    action_history: 'Action History',
    
    // Club Card
    club_card_ready: 'Your new Desideri di Puglia Card is ready — elegant and interactive like you 🌿',
    download_card: 'Download Card',
    add_to_wallet: 'Add to Wallet',
    scan_qr: 'Scan to view your profile 🌿',
    official_member_card: 'Official Member Card',
    member_since: 'Member since',
    club_statistics: 'Your statistics',
    
    // Admin
    pending_actions: 'Pending Actions',
    statistics: 'Statistics', 
    users: 'Users',
    email_admin: 'Email Admin',
    missions_admin: 'Missions',
    prizes_admin: 'Prizes',
    settings: 'Settings',
    approve: 'Approve',
    reject: 'Reject',
    restore_defaults: 'Restore Defaults',
    
    // Messages & Notifications
    language_updated: '🌿 Language updated in real time: English',
    prize_updated: '🌿 Prize updated successfully and visible to users 🌿',
    mission_created: '🎯 Mission created successfully!',
    email_sent: '📩 Email sent successfully!',
    success: 'Success',
    error: 'Error',
    
    // Public Profile
    public_profile: 'Public Profile',
    profile_not_found: 'Profile Not Found',
    loading_profile: 'Loading Club profile...',
    current_rank: 'Current Rank',
    missions_completed: 'Missions Completed',
    prizes_and_awards: 'Prizes and Awards',
    current_month_prize: 'Current Month Prize',
    past_prizes: 'Past Prizes',
    no_prizes_message: 'No prizes yet — keep playing!',
    
    // Wallet
    wallet_coming_soon: 'Add to Wallet — Coming Soon'
  }
};

// Default language
let currentLanguage = localStorage.getItem('preferred_language') || 'it';

// Translation function
export const t = (key) => {
  return translations[currentLanguage]?.[key] || translations['it'][key] || key;
};

// Set language function
export const setLanguage = (language) => {
  if (language === 'it' || language === 'en') {
    currentLanguage = language;
    localStorage.setItem('preferred_language', language);
    
    // Trigger custom event for components to update
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language } }));
    
    return true;
  }
  return false;
};

// Get current language
export const getCurrentLanguage = () => {
  return currentLanguage;
};

// Get all available languages
export const getAvailableLanguages = () => {
  return [
    { code: 'it', name: 'Italiano', flag: '🇮🇹' },
    { code: 'en', name: 'English', flag: '🇬🇧' }
  ];
};

export default translations;