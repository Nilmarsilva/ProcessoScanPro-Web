import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuthStore } from './store/authStore';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import CnpjPage from './pages/CnpjPage';
import DadosPage from './pages/DadosPage';
import PipedrivePage from './pages/PipedrivePage';
import ProcessarJuditPage from './pages/ProcessarJuditPage';

// Protected Route Component
function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

// Public Route Component (redirect to dashboard if already authenticated)
function PublicRoute({ children }) {
  const { isAuthenticated } = useAuthStore();
  return !isAuthenticated ? children : <Navigate to="/dashboard" replace />;
}

function App() {
  const { checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          }
        />

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/cnpj"
          element={
            <ProtectedRoute>
              <CnpjPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dados"
          element={
            <ProtectedRoute>
              <DadosPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/pipedrive"
          element={
            <ProtectedRoute>
              <PipedrivePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/processar-judit"
          element={
            <ProtectedRoute>
              <ProcessarJuditPage />
            </ProtectedRoute>
          }
        />

        {/* Default Route */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        
        {/* 404 Route */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
