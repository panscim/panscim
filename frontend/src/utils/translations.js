// Centralized translations system
const translations = {
  it: {
    // Navigation
    home: 'Home',
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
    
    // Auth
    login: 'Accedi',
    register: 'Registrati',
    logout: 'Esci',
    email: 'Email',
    password: 'Password',
    name: 'Nome',
    username: 'Username',
    
    // Missions
    mission_completed: 'Missione completata 🌿',
    complete_mission: 'Completa Missione',
    mission_description: 'Descrizione della missione',
    daily_missions: 'Missioni Giornaliere',
    weekly_missions: 'Missioni Settimanali',
    
    // Prizes  
    monthly_rewards: 'Premi del mese',
    first_place: '1° Posto',
    second_place: '2° Posto', 
    third_place: '3° Posto',
    
    // Profile
    my_profile: 'Il mio Profilo',
    my_club_card: 'La mia Card',
    total_points: 'Punti totali',
    current_points: 'Punti questo mese',
    current_position: 'Posizione attuale',
    
    // Club Card
    club_card_ready: 'La tua Card Desideri di Puglia è pronta.',
    download_card: 'Scarica Card',
    scan_qr: 'Scansiona il tuo QR per condividere il tuo profilo o mostrare la tua appartenenza al Club.',
    
    // Admin
    pending_actions: 'Azioni in attesa',
    statistics: 'Statistiche',
    users: 'Utenti',
    email_admin: 'Email Admin',
    settings: 'Impostazioni',
    
    // Messages
    language_updated: '🌿 Lingua aggiornata: Italiano',
    prize_updated: '🌿 Premio aggiornato con successo!',
    mission_created: '🎯 Missione creata con successo!',
    email_sent: '📩 Email inviata con successo!'
  },
  
  en: {
    // Navigation  
    home: 'Home',
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
    
    // Auth
    login: 'Login',
    register: 'Register',
    logout: 'Logout',
    email: 'Email',
    password: 'Password',
    name: 'Name',
    username: 'Username',
    
    // Missions
    mission_completed: 'Mission accomplished 🌿',
    complete_mission: 'Complete Mission', 
    mission_description: 'Mission description',
    daily_missions: 'Daily Missions',
    weekly_missions: 'Weekly Missions',
    
    // Prizes
    monthly_rewards: 'Monthly Rewards',
    first_place: '1st Place',
    second_place: '2nd Place',
    third_place: '3rd Place',
    
    // Profile
    my_profile: 'My Profile',
    my_club_card: 'My Club Card', 
    total_points: 'Total Points',
    current_points: 'Points this month',
    current_position: 'Current Position',
    
    // Club Card
    club_card_ready: 'Your Desideri di Puglia Card is ready.',
    download_card: 'Download Card',
    scan_qr: 'Scan your QR to share your profile or show your Club membership.',
    
    // Admin
    pending_actions: 'Pending Actions',
    statistics: 'Statistics', 
    users: 'Users',
    email_admin: 'Email Admin',
    settings: 'Settings',
    
    // Messages
    language_updated: '🌿 Language updated: English',
    prize_updated: '🌿 Prize updated successfully!',
    mission_created: '🎯 Mission created successfully!',
    email_sent: '📩 Email sent successfully!'
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