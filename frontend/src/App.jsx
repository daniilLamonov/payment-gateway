import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import PaymentPage from './components/Payment/PaymentPage';
import AdminPanel from './components/AdminPanel/AdminPanel';
import PaymentError from "./components/ErrorPage/PaymentError";
import Login from './components/Login/Login';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/payment-error" element={<PaymentError />} />
          <Route path="/" element={<PaymentPage />} />
          {/* Адрес, который админка отдаёт как gateway_url и который получают плательщики */}
          <Route path="/pay" element={<PaymentPage />} />
          <Route path="/login" element={<Login />} />
          <Route
            path="/admin"
            element={
              <ProtectedRoute>
                <AdminPanel />
              </ProtectedRoute>
            }
          />
          {/* Без этого любой неизвестный путь рендерил пустую страницу */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
