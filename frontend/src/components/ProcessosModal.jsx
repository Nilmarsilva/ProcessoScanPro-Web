import { useState } from 'react';
import { X, ChevronLeft, Scale, DollarSign, Calendar, Users, FileText, MapPin, Building } from 'lucide-react';
import { Button } from './ui/button';

export default function ProcessosModal({ isOpen, onClose, resultado }) {
  const [processoSelecionado, setProcessoSelecionado] = useState(null);

  if (!isOpen || !resultado) return null;

  const processos = resultado.processos || [];
  
  // Funções de formatação
  const formatarCPF = (cpf) => {
    if (!cpf) return '-';
    const cleaned = cpf.replace(/\D/g, '');
    if (cleaned.length !== 11) return cpf;
    return cleaned.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  };

  const formatarCNPJ = (cnpj) => {
    if (!cnpj) return '-';
    const cleaned = cnpj.replace(/\D/g, '');
    if (cleaned.length !== 14) return cnpj;
    return cleaned.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
  };
  
  // Valida se CPF e CNPJ aparecem juntos no processo
  const validarCorrespondenciaExata = (processo) => {
    if (!processo.parties || !resultado.cpf || !resultado.cnpj) return false;
    
    let cpfEncontrado = false;
    let cnpjEncontrado = false;
    
    for (const party of processo.parties) {
      const documento = party.document || '';
      const documentoLimpo = documento.replace(/\D/g, '');
      
      if (documentoLimpo === resultado.cpf) cpfEncontrado = true;
      if (documentoLimpo === resultado.cnpj) cnpjEncontrado = true;
      
      if (cpfEncontrado && cnpjEncontrado) return true;
    }
    
    return false;
  };

  const formatarValor = (valor) => {
    if (!valor) return 'Não informado';
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor);
  };

  const formatarData = (data) => {
    if (!data) return 'Não informado';
    return new Date(data).toLocaleDateString('pt-BR');
  };

  const renderListaProcessos = () => (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Resultados encontrados</h2>
          <p className="text-slate-600">Total de {processos.length} processo(s)</p>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose}>
          <X className="h-5 w-5" />
        </Button>
      </div>

      <div className="mb-4 p-4 bg-slate-50 rounded-lg">
        <div className="space-y-3">
          <div>
            <p className="text-lg font-bold text-slate-900">
              {resultado.nome} 
              {resultado.cpf && (
                <span className="ml-3 text-base font-mono text-slate-600">
                  CPF: {formatarCPF(resultado.cpf)}
                </span>
              )}
            </p>
          </div>
          {resultado.empresa && (
            <div>
              <p className="text-base font-semibold text-slate-700">
                {resultado.empresa}
                {resultado.cnpj && (
                  <span className="ml-3 text-sm font-mono text-slate-600">
                    CNPJ: {formatarCNPJ(resultado.cnpj)}
                  </span>
                )}
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="space-y-3 max-h-[500px] overflow-y-auto">
        {processos.map((processo, idx) => {
          const isValido = validarCorrespondenciaExata(processo);
          
          return (
          <div
            key={idx}
            onClick={() => setProcessoSelecionado(processo)}
            className={`p-4 border rounded-lg hover:bg-slate-50 cursor-pointer transition-colors ${
              isValido 
                ? 'border-green-300 bg-green-50' 
                : 'border-orange-300 bg-orange-50'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="font-semibold text-slate-900">
                    {processo.name || 'Processo sem nome'}
                  </h3>
                  {isValido ? (
                    <span className="px-2 py-0.5 bg-green-600 text-white rounded text-xs font-medium">
                      ✓ Válido
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 bg-orange-600 text-white rounded text-xs font-medium">
                      ⚠ Sem correspondência
                    </span>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <p className="text-slate-600">Processo</p>
                    <p className="font-mono text-slate-900">{processo.code || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-slate-600">Tribunal</p>
                    <p className="text-slate-900">{processo.tribunal_acronym || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-slate-600">Grau</p>
                    <p className="text-slate-900">{processo.instance}º Grau</p>
                  </div>
                  <div>
                    <p className="text-slate-600">Última Movimentação</p>
                    <p className="text-slate-900">
                      {processo.last_step?.step_date ? formatarData(processo.last_step.step_date) : 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-slate-600">Documento</p>
                    <p className="font-mono text-slate-900">{resultado.documento}</p>
                  </div>
                  <div>
                    <p className="text-slate-600">Status</p>
                    <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs font-medium">
                      {processo.status || 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
              <ChevronLeft className="h-5 w-5 text-slate-400 rotate-180" />
            </div>
          </div>
          );
        })}
      </div>
    </div>
  );

  const renderDetalheProcesso = () => (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => setProcessoSelecionado(null)}>
            <ChevronLeft className="h-5 w-5" />
          </Button>
          <div>
            <p className="text-sm text-slate-600">
              {processoSelecionado.code} • {processoSelecionado.instance}º GRAU • Última movimentação em{' '}
              {processoSelecionado.last_step?.step_date ? formatarData(processoSelecionado.last_step.step_date) : 'N/A'}
            </p>
          </div>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose}>
          <X className="h-5 w-5" />
        </Button>
      </div>

      <h2 className="text-2xl font-bold text-slate-900 mb-6">
        {processoSelecionado.name || 'Processo sem nome'}
      </h2>

      {/* Cards de Resumo */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="p-4 bg-green-50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Scale className="h-5 w-5 text-green-600" />
            <p className="text-sm text-green-600">Tribunal</p>
          </div>
          <p className="font-bold text-green-900">{processoSelecionado.tribunal_acronym || 'N/A'}</p>
        </div>

        <div className="p-4 bg-blue-50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <DollarSign className="h-5 w-5 text-blue-600" />
            <p className="text-sm text-blue-600">Valor da causa</p>
          </div>
          <p className="font-bold text-blue-900">{formatarValor(processoSelecionado.amount)}</p>
        </div>

        <div className="p-4 bg-purple-50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Calendar className="h-5 w-5 text-purple-600" />
            <p className="text-sm text-purple-600">Distribuído em</p>
          </div>
          <p className="font-bold text-purple-900">{formatarData(processoSelecionado.distribution_date)}</p>
        </div>

        <div className="p-4 bg-orange-50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Users className="h-5 w-5 text-orange-600" />
            <p className="text-sm text-orange-600">Partes</p>
          </div>
          <p className="font-bold text-orange-900">
            {processoSelecionado.parties?.length || 0} Partes
          </p>
        </div>
      </div>

      {/* Abas de Informações */}
      <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
        <div className="border-b border-slate-200 bg-slate-50 px-6 py-3">
          <h3 className="font-semibold text-slate-900">Informações</h3>
        </div>

        <div className="p-6 space-y-6 max-h-[400px] overflow-y-auto">
          {/* Dados do Processo */}
          <div>
            <h4 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
              <FileText className="h-4 w-4" />
              DADOS DO PROCESSO
            </h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-slate-600">Tribunal de origem:</p>
                <p className="font-medium text-slate-900">{processoSelecionado.tribunal_acronym || 'N/A'}</p>
              </div>
              <div>
                <p className="text-slate-600">Comarca:</p>
                <p className="font-medium text-slate-900">
                  {processoSelecionado.courts?.[0]?.name || 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-slate-600">Cidade:</p>
                <p className="font-medium text-slate-900">N/A</p>
              </div>
              <div>
                <p className="text-slate-600">Estado:</p>
                <p className="font-medium text-slate-900">N/A</p>
              </div>
              <div>
                <p className="text-slate-600">Segmento da justiça:</p>
                <p className="font-medium text-slate-900">
                  {processoSelecionado.justice === '5' ? 'DIREITO DO TRABALHO' : 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-slate-600">Fase:</p>
                <p className="font-medium text-slate-900">{processoSelecionado.phase || 'Inicial'}</p>
              </div>
              <div className="col-span-2">
                <p className="text-slate-600">Valor da causa:</p>
                <p className="font-medium text-slate-900">{formatarValor(processoSelecionado.amount)}</p>
              </div>
              <div className="col-span-2">
                <p className="text-slate-600">Classe processual:</p>
                <p className="font-medium text-slate-900">
                  {processoSelecionado.classifications?.map(c => `(${c.code}) ${c.name}`).join(', ') || 'N/A'}
                </p>
              </div>
            </div>
          </div>

          {/* Órgão Julgador */}
          <div>
            <h4 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
              <Building className="h-4 w-4" />
              Órgão julgador
            </h4>
            <p className="text-sm text-slate-900">
              {processoSelecionado.courts?.[0]?.name || 'N/A'}
            </p>
          </div>

          {/* Assuntos */}
          <div>
            <h4 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Assuntos
            </h4>
            <p className="text-sm text-slate-900">
              {processoSelecionado.subjects?.map(s => `${s.name}`).join(', ') || 'N/A'}
            </p>
          </div>

          {/* Partes do Processo */}
          <div>
            <h4 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
              <Users className="h-4 w-4" />
              PARTES DO PROCESSO
            </h4>

            {/* Polo Ativo */}
            <div className="mb-4">
              <p className="font-medium text-slate-900 mb-2">Polo ativo</p>
              {processoSelecionado.parties
                ?.filter(p => p.side === 'Active')
                .map((parte, idx) => (
                  <div key={idx} className="ml-4 mb-2">
                    <p className="text-sm">
                      <span className="font-medium">Autor:</span> {parte.name} - {parte.document || 'N/A'}
                    </p>
                    {parte.lawyers && parte.lawyers.length > 0 && (
                      <p className="text-sm text-slate-600 ml-4">
                        Advogado: {parte.lawyers.map(l => l.name).join(', ')}
                      </p>
                    )}
                  </div>
                ))}
            </div>

            {/* Polo Passivo */}
            <div>
              <p className="font-medium text-slate-900 mb-2">Polo passivo</p>
              {processoSelecionado.parties
                ?.filter(p => p.side === 'Passive')
                .map((parte, idx) => (
                  <div key={idx} className="ml-4 mb-2">
                    <p className="text-sm">
                      <span className="font-medium">Réu:</span> {parte.name} - {parte.document || 'N/A'}
                    </p>
                    {parte.lawyers && parte.lawyers.length > 0 && (
                      <p className="text-sm text-slate-600 ml-4">
                        Advogado: {parte.lawyers.map(l => l.name).join(', ')}
                      </p>
                    )}
                  </div>
                ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-5xl w-full max-h-[90vh] overflow-y-auto">
        {processoSelecionado ? renderDetalheProcesso() : renderListaProcessos()}
      </div>
    </div>
  );
}
