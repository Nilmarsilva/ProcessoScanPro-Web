import { Button } from '../ui/button';
import { 
  Search,
  Building2,
  FileText,
  Download,
  Trash2,
  Copy
} from 'lucide-react';

export default function CnpjActionsToolbar({ onAction, hasData }) {
  const actions = [
    {
      label: 'Checar Pipedrive',
      icon: Search,
      action: 'check_pipedrive',
      tooltip: 'Verificar dados no Pipedrive CRM',
      color: 'green'
    },
    {
      label: 'Assertiva CNPJ',
      icon: Building2,
      action: 'assertiva_cnpj',
      tooltip: 'Consultar CNPJs na API Assertiva',
      color: 'green'
    },
    {
      label: 'Invertexto CNPJ',
      icon: FileText,
      action: 'invertexto_cnpj',
      tooltip: 'Consultar CNPJs na API Invertexto',
      color: 'green'
    },
    {
      label: 'Exportar',
      icon: Download,
      action: 'export',
      tooltip: 'Exportar dados para Excel',
      color: 'green'
    },
    {
      label: 'Excluir Colunas',
      icon: Trash2,
      action: 'delete_columns',
      tooltip: 'Excluir colunas selecionadas',
      color: 'red'
    },
    {
      label: 'Remover Duplicatas',
      icon: Copy,
      action: 'remove_duplicates',
      tooltip: 'Remover linhas duplicadas',
      color: 'red'
    }
  ];

  const getButtonClass = (color) => {
    if (color === 'green') {
      return 'bg-green-600 hover:bg-green-700 text-white';
    } else if (color === 'red') {
      return 'bg-red-600 hover:bg-red-700 text-white';
    }
    return 'bg-blue-600 hover:bg-blue-700 text-white';
  };

  return (
    <div className="p-4 border rounded-lg bg-card">
      <div className="mb-3">
        <h3 className="text-sm font-semibold mb-1">Ações e Pesquisas</h3>
        <p className="text-xs text-muted-foreground">
          Ferramentas para consulta de APIs e manipulação de dados
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {actions.map((item, index) => (
          <Button
            key={index}
            onClick={() => onAction(item.action)}
            disabled={!hasData}
            className={`flex items-center gap-2 ${getButtonClass(item.color)}`}
            size="sm"
            title={item.tooltip}
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </Button>
        ))}
      </div>
    </div>
  );
}
