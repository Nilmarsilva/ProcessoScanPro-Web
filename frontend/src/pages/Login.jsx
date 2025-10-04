import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { FileSearch, Lock, User, AlertCircle, Loader2 } from 'lucide-react';

export default function Login() {
  const navigate = useNavigate();
  const { login, isLoading, error, isAuthenticated, clearError } = useAuthStore();
  
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    return () => clearError();
  }, [clearError]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await login(formData.username, formData.password);
    if (result.success) {
      navigate('/dashboard');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8" style={{ backgroundColor: '#0F172A' }}>
      <div className="w-full max-w-md">
        {/* Login Card */}
        <div className="bg-white rounded-lg shadow-xl p-8 space-y-8">
          {/* Logo and Title */}
          <div className="text-center">
            <div className="flex justify-center mb-4">
              <div className="p-3 bg-primary/10 rounded-full">
                <FileSearch className="h-12 w-12 text-primary" />
              </div>
            </div>
            <h2 className="text-3xl font-bold tracking-tight">
              ProcessoScanPro
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Sistema de Consulta de Processos Judiciais
            </p>
          </div>

          {/* Login Form */}
          <div className="space-y-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Error Message */}
              {error && (
                <div className="flex items-center gap-2 p-3 text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-md">
                  <AlertCircle className="h-4 w-4" />
                  <span>{error}</span>
                </div>
              )}

              {/* Username Field */}
              <div className="space-y-2">
                <Label htmlFor="username">Usuário</Label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="username"
                    name="username"
                    type="text"
                    required
                    className="pl-10"
                    placeholder="Digite seu usuário"
                    value={formData.username}
                    onChange={handleChange}
                    disabled={isLoading}
                  />
                </div>
              </div>

              {/* Password Field */}
              <div className="space-y-2">
                <Label htmlFor="password">Senha</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    required
                    className="pl-10"
                    placeholder="Digite sua senha"
                    value={formData.password}
                    onChange={handleChange}
                    disabled={isLoading}
                  />
                </div>
              </div>

              {/* Remember Me and Forgot Password */}
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    id="remember-me"
                    name="remember-me"
                    type="checkbox"
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <label htmlFor="remember-me" className="ml-2 block text-sm text-muted-foreground">
                    Lembrar-me
                  </label>
                </div>

                <div className="text-sm">
                  <a href="#" className="font-medium text-primary hover:text-primary/80">
                    Esqueceu a senha?
                  </a>
                </div>
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                className="w-full"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Entrando...
                  </>
                ) : (
                  'Entrar'
                )}
              </Button>
            </form>

            {/* Register Link */}
            <div className="text-center text-sm">
              <span className="text-muted-foreground">Não tem uma conta? </span>
              <Link to="/register" className="font-medium text-primary hover:text-primary/80">
                Registre-se
              </Link>
            </div>
          </div>

          {/* Footer */}
          <div className="text-center text-xs text-muted-foreground">
            <p>© 2025 ProcessoScanPro. Todos os direitos reservados.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
