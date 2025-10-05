import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { QrCode, Download, Copy, Calendar, Star } from 'lucide-react';

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

      {/* Digital Club Card */}
      <div className="flex justify-center">
        <div 
          ref={cardRef}
          className="relative bg-gradient-to-br from-sand-light to-sand-medium rounded-[18px] p-6 shadow-lg border-2 border-matte-gold"
          style={{
            width: '400px',
            height: '250px',
            background: 'linear-gradient(135deg, #F4EFEA 0%, #E8DDD4 100%)',
            fontFamily: 'Poppins, sans-serif',
            position: 'relative',
            overflow: 'hidden'
          }}
        >
          {/* Background Texture */}
          <div 
            className="absolute inset-0 opacity-10"
            style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='0.1'%3E%3Ccircle cx='7' cy='7' r='1'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
            }}
          />
          
          {/* Logo and Title */}
          <div className="text-center mb-4">
            <h1 className="text-lg font-bold text-deep-sea-blue" style={{ fontFamily: 'Cormorant Garamond, serif' }}>
              Desideri di Puglia Club
            </h1>
            <div className="h-0.5 bg-matte-gold mx-8 mt-1"></div>
          </div>

          {/* User Info */}
          <div className="flex items-center justify-between h-full">
            {/* Left Side - User Info */}
            <div className="flex-1">
              {/* Avatar */}
              <div className="flex items-center space-x-3 mb-3">
                {cardData.avatar_url ? (
                  <img
                    src={`data:image/jpeg;base64,${cardData.avatar_url}`}
                    alt="Avatar"
                    className="w-12 h-12 rounded-full border-2 border-matte-gold object-cover"
                  />
                ) : (
                  <div className="w-12 h-12 bg-matte-gold rounded-full flex items-center justify-center text-deep-sea-blue font-semibold">
                    {cardData.name?.charAt(0) || '?'}
                  </div>
                )}
                <div>
                  <h2 className="font-semibold text-deep-sea-blue text-lg">{cardData.name}</h2>
                  <div className="flex items-center space-x-2 text-xs">
                    <span className="text-matte-gold font-medium">{cardData.level}</span>
                    <Star size={12} className="text-matte-gold" />
                  </div>
                </div>
              </div>

              {/* Bottom Left Info */}
              <div className="absolute bottom-4 left-6">
                <div className="text-xs text-deep-sea-blue space-y-1">
                  <div className="flex items-center space-x-1">
                    <span className="font-medium">{cardData.club_card_code}</span>
                    <button onClick={copyCode} className="text-matte-gold hover:text-deep-sea-blue">
                      <Copy size={10} />
                    </button>
                  </div>
                  <div className="flex items-center space-x-1 text-gray-600">
                    <Calendar size={10} />
                    <span>
                      {cardData.join_date 
                        ? new Date(cardData.join_date).toLocaleDateString('it-IT')
                        : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Side - QR Code */}
            <div className="flex flex-col items-center">
              {qrCodeUrl ? (
                <img
                  src={qrCodeUrl}
                  alt="QR Code"
                  className="w-20 h-20 border border-deep-sea-blue rounded"
                />
              ) : (
                <div className="w-20 h-20 bg-gray-200 rounded flex items-center justify-center">
                  <QrCode size={40} className="text-gray-500" />
                </div>
              )}
              <p className="text-xs text-gray-600 mt-1 text-center">Scansiona per<br />il tuo profilo</p>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-4 justify-center">
        <button
          onClick={downloadCard}
          className="px-6 py-3 bg-deep-sea-blue text-white rounded-lg font-medium hover:bg-opacity-90 flex items-center space-x-2"
        >
          <Download size={18} />
          <span>📲 Scarica Card</span>
        </button>
        
        <button
          onClick={() => {
            if (cardData.club_card_qr_url) {
              window.open(cardData.club_card_qr_url, '_blank');
            }
          }}
          className="px-6 py-3 border border-deep-sea-blue text-deep-sea-blue rounded-lg font-medium hover:bg-deep-sea-blue hover:text-white flex items-center space-x-2"
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