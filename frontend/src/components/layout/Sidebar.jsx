import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { Button } from '../ui/button';
import { 
  FileSearch,
  X,
  Settings,
  Archive,
  ExternalLink,
  Eye,
  Database,
  Building2,
  ChevronDown,
  ChevronRight
} from 'lucide-react';

export default function Sidebar({ isOpen, onClose }) {
  const navigate = useNavigate();
  const { logout } = useAuthStore();
  const [openMenus, setOpenMenus] = useState({});

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const toggleMenu = (menuTitle) => {
    setOpenMenus(prev => ({
      ...prev,
      [menuTitle]: !prev[menuTitle]
    }));
  };

  const menuItems = [
    {
      title: 'Processar Judit',
      icon: FileSearch,
      action: () => navigate('/processar-judit')
    },
    {
      title: 'Pipedrive',
      icon: ExternalLink,
      action: () => navigate('/pipedrive')
    },
    {
      title: 'Visualizar',
      icon: Eye,
      submenu: true,
      items: [
        { label: 'Com Processo', action: () => navigate('/com-processo') },
        { label: 'Sem Processo', action: () => navigate('/sem-processo') }
      ]
    },
    {
      title: 'Dados',
      icon: Database,
      action: () => navigate('/dados')
    },
    {
      title: 'CNPJ',
      icon: Building2,
      action: () => navigate('/cnpj')
    }
  ];

  return (
    <aside 
      className={`${isOpen ? 'w-64' : 'w-0'} transition-all duration-300 bg-slate-900 text-slate-100 overflow-hidden flex-shrink-0`}
      style={{ backgroundColor: '#0F172A' }}
    >
      <div className="h-screen flex flex-col">
        <div className="p-4 border-b border-slate-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileSearch className="h-6 w-6 text-primary" />
            <span className="font-bold text-white">Menu</span>
          </div>
          <Button 
            variant="ghost" 
            size="icon"
            onClick={onClose}
            className="lg:hidden"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        <nav className="p-4 space-y-2 overflow-y-auto flex-1">
          {menuItems.map((item, index) => (
            <div key={index}>
              {item.items ? (
                <div>
                  <button
                    onClick={() => toggleMenu(item.title)}
                    className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-slate-800 transition-colors text-left"
                  >
                    <div className="flex items-center gap-3">
                      <item.icon className="h-5 w-5 text-slate-400" />
                      <span className="font-medium text-slate-200">{item.title}</span>
                    </div>
                    {openMenus[item.title] ? <ChevronDown className="h-4 w-4 text-slate-400" /> : <ChevronRight className="h-4 w-4 text-slate-400" />}
                  </button>
                  {openMenus[item.title] && (
                    <div className="ml-8 mt-1 space-y-1">
                      {item.items.map((subItem, subIndex) => (
                        <button
                          key={subIndex}
                          onClick={subItem.action}
                          className="w-full text-left p-2 rounded-md hover:bg-slate-800 text-sm text-slate-400 hover:text-slate-200 transition-colors"
                        >
                          {subItem.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <button
                  onClick={item.action}
                  className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-slate-800 transition-colors"
                >
                  <item.icon className="h-5 w-5 text-slate-400" />
                  <span className="font-medium text-slate-200">{item.title}</span>
                </button>
              )}
            </div>
          ))}
        </nav>
      </div>
    </aside>
  );
}
