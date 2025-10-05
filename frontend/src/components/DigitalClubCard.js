import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { QrCode, Download, Copy, Calendar, Star } from 'lucide-react';
import { t } from '../utils/translations';

const DigitalClubCard = () => {
  const [cardData, setCardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [qrCodeUrl, setQrCodeUrl] = useState('');
  const cardRef = useRef(null);

  useEffect(() => {
    fetchCardData();
  }, []);

  const fetchCardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/club-card`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCardData(response.data);
      
      // Generate QR code URL
      if (response.data.club_card_qr_url) {
        setQrCodeUrl(`https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=${encodeURIComponent(response.data.club_card_qr_url)}`);
      }
    } catch (error) {
      console.error('Error fetching card data:', error);
    } finally {
      setLoading(false);
    }
  };

  const downloadCard = async () => {
    if (!cardRef.current) return;

    try {
      // Use html2canvas to convert the card to image
      const html2canvas = (await import('html2canvas')).default;
      const canvas = await html2canvas(cardRef.current, {
        backgroundColor: '#F4EFEA',
        scale: 2,
        width: 400,
        height: 250
      });
      
      // Create download link
      const link = document.createElement('a');
      link.download = `desideri-puglia-card-${cardData.club_card_code}.png`;
      link.href = canvas.toDataURL();
      link.click();
      
      alert('📲 Card scaricata con successo!');
    } catch (error) {
      console.error('Error downloading card:', error);
      alert('Errore nel download della card');
    }
  };

  const copyCode = () => {
    if (cardData?.club_card_code) {
      navigator.clipboard.writeText(cardData.club_card_code);
      alert('📋 Codice copiato!');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-deep-sea-blue mx-auto"></div>
          <p className="text-gray-600 mt-4">Caricamento card...</p>
        </div>
      </div>
    );
  }

  if (!cardData) {
    return (
      <div className="text-center p-8">
        <p className="text-gray-600">Errore nel caricamento della club card</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Card Preview Message */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-blue-800 text-sm">
          🎟️ <strong>La tua Card Desideri di Puglia è pronta.</strong><br />
          📲 Scansiona il tuo QR per condividere il tuo profilo o mostrare la tua appartenenza al Club.
        </p>
      </div>

      {/* Premium Digital Club Card - Hidden on Mobile */}
      <div className="hidden lg:flex justify-center">
        <div 
          ref={cardRef}
          className="relative rounded-[20px] shadow-2xl border border-matte-gold overflow-hidden"
          style={{
            width: '480px',
            height: '320px',
            background: `
              radial-gradient(circle at 20% 80%, #F4EFEA 0%, transparent 50%),
              radial-gradient(circle at 80% 20%, #E8DDD4 0%, transparent 50%),
              linear-gradient(135deg, #F4EFEA 0%, #EFE7DC 100%)
            `,
            backgroundImage: `
              url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23CFAE6C' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")
            `,
            fontFamily: 'Poppins, sans-serif',
            position: 'relative',
            boxShadow: '0 8px 32px rgba(0,0,0,0.1), inset 0 1px 0 rgba(255,255,255,0.2)'
          }}
        >
          <div className="p-8 h-full flex flex-col">
            {/* Header - Club Title */}
            <div className="text-center mb-6">
              <h1 
                className="text-2xl font-bold text-matte-gold mb-1" 
                style={{ fontFamily: 'Cormorant Garamond, serif' }}
              >
                Desideri di Puglia Club
              </h1>
              <div className="h-px bg-gradient-to-r from-transparent via-matte-gold to-transparent mx-8"></div>
              <p className="text-xs text-deep-sea-blue mt-1 opacity-70">Official Member Card</p>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 flex items-start justify-between">
              {/* Left Side - User Information */}
              <div className="flex-1 pr-6">
                {/* Avatar and Name */}
                <div className="flex items-center space-x-4 mb-6">
                  {cardData.avatar ? (
                    <img
                      src={`data:image/jpeg;base64,${cardData.avatar}`}
                      alt="Avatar"
                      className="w-20 h-20 rounded-full border-3 border-matte-gold object-cover shadow-md"
                      style={{ borderWidth: '3px' }}
                    />
                  ) : (
                    <div className="w-20 h-20 bg-gradient-to-br from-matte-gold to-yellow-600 rounded-full flex items-center justify-center text-deep-sea-blue font-bold text-xl shadow-md border-3 border-matte-gold" style={{ borderWidth: '3px' }}>
                      {cardData.name?.charAt(0) || '?'}
                    </div>
                  )}
                  <div className="flex-1">
                    <h2 className="text-xl font-bold text-deep-sea-blue mb-1" style={{ fontFamily: 'Poppins, sans-serif' }}>
                      {cardData.name}
                    </h2>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-matte-gold">{cardData.level}</span>
                      <Star size={14} className="text-matte-gold fill-current" />
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Side - QR Code */}
              <div className="flex flex-col items-center">
                {qrCodeUrl ? (
                  <div className="p-2 bg-white rounded-lg shadow-md border border-gray-200">
                    <img
                      src={qrCodeUrl}
                      alt="QR Code"
                      className="w-24 h-24"
                    />
                  </div>
                ) : (
                  <div className="w-28 h-28 bg-white rounded-lg shadow-md border border-gray-200 flex items-center justify-center">
                    <QrCode size={48} className="text-gray-400" />
                  </div>
                )}
                <p className="text-xs text-gray-600 mt-2 text-center leading-tight">
                  Scansiona per visualizzare<br />il tuo profilo 🌿
                </p>
              </div>
            </div>

            {/* Bottom Info Bar */}
            <div className="flex items-center justify-between pt-4 border-t border-matte-gold border-opacity-30">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-1">
                  <span className="text-sm font-bold text-deep-sea-blue">{cardData.club_card_code}</span>
                  <button onClick={copyCode} className="text-matte-gold hover:text-deep-sea-blue transition-colors">
                    <Copy size={12} />
                  </button>
                </div>
                <div className="flex items-center space-x-1 text-gray-600">
                  <Calendar size={12} />
                  <span className="text-xs">
                    {cardData.join_date 
                      ? new Date(cardData.join_date).toLocaleDateString('it-IT')
                      : 'N/A'}
                  </span>
                </div>
              </div>
              
              <div className="text-right">
                <div className="text-xs text-gray-500">Membro dal</div>
                <div className="text-sm font-medium text-deep-sea-blue">
                  {cardData.join_date 
                    ? new Date(cardData.join_date).getFullYear()
                    : 'N/A'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Card Info - Only on Mobile */}
      <div className="lg:hidden bg-white rounded-lg p-4 border border-gray-200">
        <div className="flex items-center space-x-4 mb-4">
          {cardData.avatar ? (
            <img
              src={`data:image/jpeg;base64,${cardData.avatar}`}
              alt="Avatar"
              className="w-16 h-16 rounded-full border-2 border-matte-gold object-cover"
            />
          ) : (
            <div className="w-16 h-16 bg-gradient-to-br from-matte-gold to-yellow-600 rounded-full flex items-center justify-center text-deep-sea-blue font-bold text-lg border-2 border-matte-gold">
              {cardData.name?.charAt(0) || '?'}
            </div>
          )}
          <div>
            <h3 className="text-lg font-bold text-deep-sea-blue">{cardData.name}</h3>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-matte-gold">{cardData.level}</span>
              <Star size={14} className="text-matte-gold fill-current" />
            </div>
            <p className="text-xs text-gray-600 mt-1">
              Codice: <span className="font-mono font-semibold">{cardData.club_card_code}</span>
            </p>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4 text-center">
          <div>
            <div className="text-lg font-bold text-matte-gold">{cardData.total_points || 0}</div>
            <div className="text-xs text-gray-600">Punti Totali</div>
          </div>
          <div>
            <div className="text-lg font-bold text-deep-sea-blue">
              {cardData.join_date 
                ? new Date(cardData.join_date).getFullYear()
                : 'N/A'}
            </div>
            <div className="text-xs text-gray-600">Membro dal</div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-4 justify-center">
        <button
          onClick={downloadCard}
          className="px-6 py-3 bg-deep-sea-blue text-white rounded-lg font-medium hover:bg-opacity-90 flex items-center space-x-2 transition-all"
        >
          <Download size={18} />
          <span>📲 Scarica Card</span>
        </button>
        
        <button
          onClick={() => {
            // Wallet integration placeholder
            alert('📲 Aggiungi al Wallet — Presto disponibile');
          }}
          className="px-6 py-3 bg-gradient-to-r from-matte-gold to-yellow-600 text-white rounded-lg font-medium hover:from-yellow-600 hover:to-matte-gold flex items-center space-x-2 transition-all"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <path d="M18.71,19.5C17.88,20.74 17,21.95 15.66,21.97C14.32,22 13.89,21.18 12.37,21.18C10.84,21.18 10.37,21.95 9.1,22C7.79,22.05 6.8,20.68 5.96,19.47C4.25,17 2.94,12.45 4.7,9.39C5.57,7.87 7.13,6.91 8.82,6.88C10.1,6.86 11.32,7.75 12.11,7.75C12.89,7.75 14.37,6.68 15.92,6.84C16.57,6.87 18.39,7.1 19.56,8.82C19.47,8.88 17.39,10.19 17.41,12.63C17.44,15.65 20.06,16.66 20.09,16.67C20.06,16.74 19.67,18.11 18.71,19.5M13,3.5C13.73,2.67 14.94,2.04 15.94,2C16.07,3.17 15.6,4.35 14.9,5.19C14.21,6.04 13.07,6.7 11.95,6.61C11.8,5.46 12.36,4.26 13,3.5Z"/>
          </svg>
          <span>Aggiungi al Wallet</span>
        </button>
        
        <button
          onClick={() => {
            if (cardData.club_card_qr_url) {
              window.open(cardData.club_card_qr_url, '_blank');
            }
          }}
          className="px-6 py-3 border border-deep-sea-blue text-deep-sea-blue rounded-lg font-medium hover:bg-deep-sea-blue hover:text-white flex items-center space-x-2 transition-all"
        >
          <QrCode size={18} />
          <span>Vedi Profilo Pubblico</span>
        </button>
      </div>

      {/* User Stats */}
      <div className="bg-white rounded-lg p-4 border border-gray-200">
        <h3 className="font-semibold text-deep-sea-blue mb-3">📊 Le tue statistiche</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-matte-gold">{cardData.total_points || 0}</div>
            <div className="text-sm text-gray-600">Punti Totali</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-deep-sea-blue">{cardData.level || 'Novizio'}</div>
            <div className="text-sm text-gray-600">Livello Attuale</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DigitalClubCard;