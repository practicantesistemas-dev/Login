import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { isAuthenticated as hasStoredSession } from './services/authService';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import AdminDashboard from './pages/AdminDashboard';
import { verifySession } from './services/authService';

const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(hasStoredSession());
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const checkSession = async (): Promise<void> => {
      const valid = await verifySession();
      setIsAuthenticated(valid);
      setIsLoading(false);
    };

    if (hasStoredSession()) {
      void checkSession();
    } else {
      setIsLoading(false);
    }
  }, []);

  if (isLoading) {
    return (
      <div className="loading-container" style={{ minHeight: '100vh' }}>
        <span className="spinner" />
        Cargando...
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={
            isAuthenticated ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <Login onLoginSuccess={() => setIsAuthenticated(true)} />
            )
          }
        />

        <Route
          path="/dashboard"
          element={
            isAuthenticated ? (
              <Dashboard onLogout={() => setIsAuthenticated(false)} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="/admin"
          element={
            isAuthenticated ? (
              <AdminDashboard onLogout={() => setIsAuthenticated(false)} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="*"
          element={<Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />}
        />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
