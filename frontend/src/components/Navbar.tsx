import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  ShieldAlert,
  LayoutDashboard,
  Database,
  Radar,
  Activity,
  Menu,
  X,
  ExternalLink,
} from 'lucide-react';
import { checkHealth, fetchStatus } from '../services/api';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isBackendOnline, setIsBackendOnline] = useState<boolean | null>(null);
  const [worksCount, setWorksCount] = useState<number | null>(null);

  useEffect(() => {
    const pingStatus = async () => {
      const online = await checkHealth();
      setIsBackendOnline(online);
      if (online) {
        const status = await fetchStatus();
        if (status) {
          setWorksCount(status.total_works);
        }
      }
    };
    pingStatus();
    const interval = setInterval(pingStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Work Explorer', path: '/works', icon: Database },
    { name: 'Detector Coverage', path: '/coverage', icon: Radar },
    { name: 'System Telemetry', path: '/status', icon: Activity },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/95 backdrop-blur-md shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Tag */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-blue-700 to-indigo-800 text-white shadow-sm group-hover:shadow-md group-hover:from-blue-800 group-hover:to-indigo-900 transition-all">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-base font-extrabold tracking-tight text-slate-900 group-hover:text-blue-700 transition-colors">
                  MPLAD <span className="text-blue-700">INTEGRITY</span>
                </span>
                <span className="hidden sm:inline-block px-1.5 py-0.5 text-[10px] font-mono font-bold uppercase tracking-wider rounded bg-blue-50 text-blue-800 border border-blue-200">
                  ENGINE v0.1
                </span>
              </div>
              <p className="text-[11px] text-slate-500 font-medium tracking-wide">
                Civic Anomaly & Expenditure Radar
              </p>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
                    isActive
                      ? 'bg-blue-50 text-blue-800 border border-blue-200 shadow-xs font-semibold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50 border border-transparent'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-blue-700' : 'text-slate-400'}`} />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* Right Status Beacon */}
          <div className="hidden lg:flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-200 text-xs">
              <span className="relative flex h-2 w-2">
                <span
                  className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                    isBackendOnline ? 'bg-emerald-400' : 'bg-rose-400'
                  }`}
                ></span>
                <span
                  className={`relative inline-flex rounded-full h-2 w-2 ${
                    isBackendOnline ? 'bg-emerald-500' : 'bg-rose-500'
                  }`}
                ></span>
              </span>
              <span className="text-slate-700 font-mono text-[11px]">
                {isBackendOnline ? (
                  <>
                    <span className="text-emerald-700 font-bold">ONLINE</span>
                    {worksCount !== null && (
                      <span className="text-slate-500 ml-1.5">({worksCount} in DB)</span>
                    )}
                  </>
                ) : (
                  <span className="text-rose-700 font-bold">OFFLINE</span>
                )}
              </span>
            </div>

            <a
              href="https://dataful.in/datasets/22567/"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white hover:bg-slate-50 text-slate-700 hover:text-blue-700 text-xs font-medium border border-slate-200 shadow-xs transition-colors"
              title="Official eSAKSHI source dataset registry"
            >
              <span>eSAKSHI Data</span>
              <ExternalLink className="w-3 h-3 text-slate-400" />
            </a>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 focus:outline-none"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-slate-200 bg-white px-4 pt-2 pb-4 space-y-1 shadow-md">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium ${
                  isActive
                    ? 'bg-blue-50 text-blue-800 border border-blue-200 font-semibold'
                    : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                <Icon className="w-4 h-4 text-blue-700" />
                {item.name}
              </Link>
            );
          })}
          <div className="pt-3 border-t border-slate-100 flex justify-between items-center text-xs text-slate-500">
            <span>Server: {isBackendOnline ? 'Connected' : 'Disconnected'}</span>
            <span>{worksCount !== null ? `${worksCount} works in DB` : ''}</span>
          </div>
        </div>
      )}
    </header>
  );
};

export default Navbar;
