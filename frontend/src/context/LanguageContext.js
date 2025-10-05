import React, { createContext, useContext, useState, useEffect } from 'react';
import { t, setLanguage, getCurrentLanguage } from '../utils/translations';
import axios from 'axios';

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

export const LanguageProvider = ({ children }) => {
  const [currentLang, setCurrentLang] = useState(getCurrentLanguage());
  const [isChanging, setIsChanging] = useState(false);

  useEffect(() => {
    // Listen for language change events
    const handleLanguageChange = (event) => {
      setCurrentLang(event.detail.language);
    };
    
    window.addEventListener('languageChanged', handleLanguageChange);
    return () => window.removeEventListener('languageChanged', handleLanguageChange);
  }, []);

  const changeLanguage = async (newLanguage) => {
    if (newLanguage === currentLang) return;
    
    setIsChanging(true);
    
    try {
      // Update local language
      setLanguage(newLanguage);
      
      // Update backend if user is logged in
      const token = localStorage.getItem('token');
      if (token) {
        try {
          await axios.put(`${process.env.REACT_APP_BACKEND_URL}/api/user/language`, 
            { language: newLanguage },
            { headers: { Authorization: `Bearer ${token}` }}
          );
        } catch (error) {
          console.warn('Failed to update language preference in backend:', error);
        }
      }
      
      setCurrentLang(newLanguage);
      
      // Show success message
      const message = newLanguage === 'it' 
        ? '🌿 Lingua aggiornata: Italiano'
        : '🌿 Language updated: English';
      
      // You could show this in a toast/notification instead
      setTimeout(() => {
        // This could be replaced with a proper notification system
        console.log(message);
      }, 100);
      
    } catch (error) {
      console.error('Error changing language:', error);
    } finally {
      // Add smooth transition delay
      setTimeout(() => {
        setIsChanging(false);
      }, 300);
    }
  };

  const value = {
    currentLanguage: currentLang,
    changeLanguage,
    isChanging,
    t // Translation function
  };

  return (
    <LanguageContext.Provider value={value}>
      <div 
        className={`transition-opacity duration-300 ${isChanging ? 'opacity-70' : 'opacity-100'}`}
      >
        {children}
      </div>
    </LanguageContext.Provider>
  );
};

export default LanguageContext;