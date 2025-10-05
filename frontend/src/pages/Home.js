import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Users, Trophy, Gift, MapPin } from 'lucide-react';

const Home = () => {
  return (
    <div className="min-h-screen bg-brand-light">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Background with maximum contrast */}
        <div className="absolute inset-0 z-0">
          <div className="w-full h-full bg-gradient-to-br from-gray-900 via-black to-gray-800">
            {/* Animated Wave Effect with gold accent */}
            <div className="absolute inset-0 opacity-30">
              <svg className="absolute bottom-0 left-0 w-full h-32" viewBox="0 0 1200 120" preserveAspectRatio="none">
                <path d="M0,60 C300,90 900,30 1200,60 L1200,120 L0,120 Z" fill="rgba(212, 175, 55, 0.4)" className="animate-pulse"/>
              </svg>
            </div>
            {/* Additional overlay for extra contrast */}
            <div className="absolute inset-0 bg-black bg-opacity-20"></div>
          </div>
        </div>

        {/* Content */}
        <div className="relative z-10 text-center px-4 max-w-4xl mx-auto">
          <div className="mb-8">
            {/* Logo e Branding */}
            <div className="flex items-center justify-center mb-8">
              <img 
                src="https://customer-assets.emergentagent.com/job_idea-showcase-6/artifacts/xc7s59ph_Progetto_senza_titolo__3_-removebg-preview.png" 
                alt="Desideri di Puglia Logo" 
                className="w-32 h-32 mr-6"
              />
              <div className="text-center">
                <h3 className="text-3xl font-cormorant font-bold text-white mb-2">Desideri di Puglia</h3>
                <h4 className="text-xl font-poppins text-brand-accent font-semibold">Club</h4>
              </div>
            </div>
            
            <div className="inline-flex items-center justify-center w-24 h-24 bg-brand-accent rounded-full mb-8 animate-float shadow-2xl">
              <span className="text-5xl">🏆</span>
            </div>
            <h1 className="text-6xl md:text-8xl font-cormorant font-bold text-white mb-8 drop-shadow-lg">
              Vivi la Puglia.
            </h1>
            <h2 className="text-3xl md:text-5xl font-poppins font-light text-white mb-10 drop-shadow-md">
              Guadagna momenti. Vinci esperienze reali.
            </h2>
            <p className="text-xl md:text-2xl text-white font-medium max-w-3xl mx-auto mb-10 drop-shadow-sm leading-relaxed">
              Entra nel Desideri di Puglia Club e trasforma ogni momento vissuto in Puglia in punti per vincere premi autentici.
            </p>
          </div>

          <div className="space-y-6 sm:space-y-0 sm:flex sm:space-x-6 justify-center">
            <Link 
              to="/register" 
              className="inline-flex items-center px-10 py-5 bg-brand-accent hover:bg-yellow-500 text-black font-bold text-lg rounded-[25px] transition-all duration-300 shadow-2xl hover:shadow-3xl hover:scale-105 group border-2 border-brand-accent"
            >
              <span>Partecipa alla Sfida</span>
              <span className="ml-3 text-3xl">🏆</span>
              <ArrowRight className="ml-3 group-hover:translate-x-2 transition-transform" size={24} />
            </Link>
            <Link 
              to="/login" 
              className="inline-flex items-center px-10 py-5 bg-white hover:bg-gray-100 text-black font-bold text-lg rounded-[25px] transition-all duration-300 shadow-2xl hover:shadow-3xl hover:scale-105 border-2 border-white"
            >
              Accedi al Club
            </Link>
          </div>

          {/* Current Challenge Banner */}
          <div className="mt-12 bg-white/10 backdrop-blur-sm rounded-[20px] p-6 border border-brand-accent/30">
            <div className="flex items-center justify-center space-x-2 text-white">
              <Trophy className="text-brand-accent" size={24} />
              <span className="text-lg font-semibold">🍇 {new Date().toLocaleDateString('it-IT', { month: 'long', year: 'numeric' }).replace(/^\w/, c => c.toUpperCase())}: Live Puglia Challenge</span>
            </div>
            <p className="text-white/90 mt-2">
              Vivi e condividi la Puglia autentica. I primi 3 vincono premi reali!
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-cormorant font-bold text-deep-sea-blue mb-6">
              Come Funziona il Club
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Un gioco mensile che trasforma la tua esperienza pugliese in momenti indimenticabili
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="puglia-card text-center group hover:transform hover:scale-105 transition-all duration-300">
              <div className="w-16 h-16 bg-terracotta rounded-full flex items-center justify-center mx-auto mb-4 group-hover:animate-bounce">
                <Users className="text-white" size={32} />
              </div>
              <h3 className="text-xl font-semibold text-deep-sea-blue mb-3 font-cormorant">
                Vivi & Condividi
              </h3>
              <p className="text-gray-600">
                Condividi la tua esperienza pugliese sui social, visita partner locali e accumula punti autentici
              </p>
            </div>

            <div className="puglia-card text-center group hover:transform hover:scale-105 transition-all duration-300">
              <div className="w-16 h-16 bg-matte-gold rounded-full flex items-center justify-center mx-auto mb-4 group-hover:animate-bounce">
                <Trophy className="text-white" size={32} />
              </div>
              <h3 className="text-xl font-semibold text-deep-sea-blue mb-3 font-cormorant">
                Compete & Scala
              </h3>
              <p className="text-gray-600">
                Ogni mese una nuova sfida. Scala la classifica e diventa Ambassador o Legend del club
              </p>
            </div>

            <div className="puglia-card text-center group hover:transform hover:scale-105 transition-all duration-300">
              <div className="w-16 h-16 bg-deep-sea-blue rounded-full flex items-center justify-center mx-auto mb-4 group-hover:animate-bounce">
                <Gift className="text-white" size={32} />
              </div>
              <h3 className="text-xl font-semibold text-deep-sea-blue mb-3 font-cormorant">
                Vinci & Godi
              </h3>
              <p className="text-gray-600">
                I primi 3 ogni mese vincono notti al B&B, cene gourmet e drink experience autentici
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-deep-sea-blue relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="stone-texture w-full h-full"></div>
        </div>
        <div className="relative z-10 max-w-4xl mx-auto text-center px-4">
          <h2 className="text-3xl md:text-4xl font-cormorant font-bold text-white mb-6">
            La Puglia ti aspetta
          </h2>
          <p className="text-lg text-sand-white/90 mb-8 max-w-2xl mx-auto">
            Unisciti alla community che vive e racconta la Puglia autentica. Ogni storia condivisa è un passo verso il tuo prossimo premio.
          </p>
          <div className="flex items-center justify-center space-x-2 text-sand-white mb-8">
            <MapPin className="text-matte-gold" size={20} />
            <span>Barletta, Via Borgovecchio 65 - Puglia, Italia</span>
          </div>
          <Link 
            to="/register" 
            className="inline-flex items-center px-8 py-4 bg-matte-gold hover:bg-opacity-90 text-white font-semibold rounded-[20px] transition-all duration-200 mediterranean-shadow hover:shadow-lg group"
          >
            <span>Inizia la tua avventura</span>
            <ArrowRight className="ml-2 group-hover:translate-x-1 transition-transform" size={20} />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 bg-white border-t border-gray-100">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="w-8 h-8 bg-matte-gold rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-sm">🌿</span>
            </div>
            <span className="font-cormorant text-xl font-semibold text-deep-sea-blue">
              Desideri di Puglia Club
            </span>
          </div>
          <p className="text-gray-600 text-sm">
            © 2025 Desideri di Puglia B&B. Vivi la Puglia, vinci esperienze autentiche.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Home;