import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import WorksPage from './pages/WorksPage';
import WorkDetailPage from './pages/WorkDetailPage';
import CoveragePage from './pages/CoveragePage';
import StatusPage from './pages/StatusPage';
import NotFoundPage from './pages/NotFoundPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans selection:bg-blue-700 selection:text-white">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/works" element={<WorksPage />} />
            <Route path="/works/:workId" element={<WorkDetailPage />} />
            <Route path="/coverage" element={<CoveragePage />} />
            <Route path="/status" element={<StatusPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </main>
        <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-600">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-800">MPLAD Integrity Engine</span>
              <span>•</span>
              <span>AI-Powered Civic Anomaly Radar</span>
            </div>
            <div className="text-slate-500 text-[11px]">
              Strict Truthfulness Standard • Unobserved records flagged as <span className="text-slate-700 italic">Not publicly observed</span>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
