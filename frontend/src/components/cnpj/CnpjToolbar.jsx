import { Button } from '../ui/button';
import { 
  FileText, 
  Phone, 
  Mail, 
  CreditCard, 
  Building2,
  MapPin,
  Calendar,
  Type,
  ArrowUpAZ,
  Users
} from 'lucide-react';

export default function CnpjToolbar({ onFormatAction, hasData }) {
  const formatActions = [
    {
      label: 'CPF',
      icon: CreditCard,
      action: 'format_cpf',
      tooltip: 'Formatar CPF (xxx.xxx.xxx-xx)'
    },
    {
      label: 'CNPJ',
      icon: Building2,
      action: 'format_cnpj',
      tooltip: 'Formatar CNPJ (xx.xxx.xxx/xxxx-xx)'
    },
    {
      label: 'Telefone',
      icon: Phone,
      action: 'format_phone',
      tooltip: 'Formatar telefone (XX) XXXXX-XXXX'
    },
    {
      label: 'Email',
      icon: Mail,
      action: 'format_email',
      tooltip: 'Normalizar email (minúsculas)'
    },
    {
      label: 'CEP',
      icon: MapPin,
      action: 'format_cep',
      tooltip: 'Formatar CEP (xxxxx-xxx)'
    },
    {
      label: 'Data',
      icon: Calendar,
      action: 'format_date',
      tooltip: 'Formatar data (dd/mm/aaaa)'
    },
    {
      label: 'Maiúsculas',
      icon: Type,
      action: 'uppercase',
      tooltip: 'Converter para MAIÚSCULAS'
    },
    {
      label: 'Ordenar A-Z',
      icon: ArrowUpAZ,
      action: 'sort_az',
      tooltip: 'Ordenar alfabeticamente'
    },
    {
      label: 'Gênero',
      icon: Users,
      action: 'format_gender',
      tooltip: 'Formatar gênero (M/F → Masculino/Feminino)'
    },
    {
      label: 'Organização',
      icon: Building2,
      action: 'format_organization',
      tooltip: 'Padronizar razão social'
    }
  ];

  return (
    <div className="p-4 border rounded-lg bg-card">
      <div className="mb-3">
        <h3 className="text-sm font-semibold mb-1">Ferramentas de Formatação</h3>
        <p className="text-xs text-muted-foreground">
          Clique em um botão para selecionar as colunas que deseja formatar
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {formatActions.map((action, index) => (
          <Button
            key={index}
            onClick={() => onFormatAction(action.action)}
            disabled={!hasData}
            variant="outline"
            size="sm"
            className="flex items-center gap-2"
            title={action.tooltip}
          >
            <action.icon className="h-4 w-4" />
            {action.label}
          </Button>
        ))}
      </div>
    </div>
  );
}
