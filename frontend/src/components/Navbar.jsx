import React, { useState, useEffect } from 'react';
import { Database, Activity, Menu, Clock, Sparkles } from 'lucide-react';
import { apiService } from '../services/api';

export const Navbar = ({ toggleSidebar }) => {
  const [dbStatus, setDbStatus] = useState('checking');
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString());
    }, 1000);

    const checkHealth = async () => {
      try {
        await apiService.checkHealth();
        setDbStatus('connected');
      } catch {
        setDbStatus('disconnected');
      }
    };

    checkHealth();
    const healthInterval = setInterval(checkHealth, 30000);

    return () => {
      clearInterval(timer);
      clearInterval(healthInterval);
    };
  }, []);

  return (
    <header className="sticky top-0 z-30 h-16 bg-slate-900/80 backdrop-blur-md border-b border-slate-800/80 px-4 sm:px-6 flex items-center justify-between shadow-sm">
      <div className="flex items-center space-x-3">
        <button
          onClick={toggleSidebar}
          className="lg:hidden p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
          title="Toggle Navigation"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                SHOPLYTICS
              </span>
            </h1>
            <span className="hidden sm:inline-flex items-center gap-1 text-[11px] font-semibold tracking-wider text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded-full border border-indigo-500/20">
              <Sparkles className="w-3 h-3" /> BIG DATA
            </span>
          </div>
          <p className="text-[11px] text-slate-400 hidden sm:block">
            Distributed Big Data Analytics Platform for E-Commerce
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-4 text-xs">
        <div className="hidden md:flex items-center space-x-1.5 text-slate-400 font-mono bg-slate-950/60 px-3 py-1.5 rounded-lg border border-slate-800">
          <Clock className="w-3.5 h-3.5 text-indigo-400" />
          <span>{currentTime}</span>
        </div>

        <div className="flex items-center space-x-2 bg-slate-950/60 px-3 py-1.5 rounded-lg border border-slate-800">
          <Database className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-slate-400 hidden sm:inline">PostgreSQL:</span>
          {dbStatus === 'connected' && (
            <span className="flex items-center space-x-1 text-emerald-400 font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>Live</span>
            </span>
          )}
          {dbStatus === 'disconnected' && (
            <span className="flex items-center space-x-1 text-rose-400 font-semibold">
              <span className="w-2 h-2 rounded-full bg-rose-400" />
              <span>Offline</span>
            </span>
          )}
          {dbStatus === 'checking' && (
            <span className="text-amber-400">Connecting...</span>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
