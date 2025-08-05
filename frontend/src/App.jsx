import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from '@/components/layout/Layout';
import Dashboard from '@/pages/Dashboard';
import SecurityDetail from '@/pages/SecurityDetail';
import TechnicalAnalysis from '@/pages/TechnicalAnalysis';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="securities/:symbol" element={<SecurityDetail />} />
          <Route path="technical-analysis" element={<TechnicalAnalysis />} />
          <Route path="etf-analysis" element={<Dashboard />} />
          <Route path="options-analysis" element={<Dashboard />} />
          <Route path="market-structure" element={<Dashboard />} />
          <Route path="watchlists" element={<Dashboard />} />
          <Route path="settings" element={<Dashboard />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;

