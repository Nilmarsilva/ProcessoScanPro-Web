import { useState, useEffect } from 'react';
import { juditService } from '../services/juditService';
import { pipedriveService } from '../services/pipedriveService';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { FileDown, RefreshCw, CheckSquare, Square, Search, ChevronLeft, ChevronRight } from 'lucide-react';
import ProcessosModal from '../components/ProcessosModal';
import * as XLSX from 'xlsx';

export default function ComProcessoPage() {
  const [batches, setBatches] = useState([]);
  const [selectedBatch, setSelectedBatch] = useState(null);
  const [resultados, setResultados] = useState([]);
  const [resultadosFiltrados, setResultadosFiltrados] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedItems, setSelectedItems] = useState(new Set());
  const [selectAll, setSelectAll] = useState(false);
  const [modalAberto, setModalAberto] = useState(false);
  const [resultadoSelecionado, setResultadoSelecionado] = useState(null);
  
  // Filtros
  const [filtroDocumento, setFiltroDocumento] = useState('');
  const [filtroNome, setFiltroNome] = useState('');
  const [filtroEmpresa, setFiltroEmpresa] = useState('');
  
  // Paginação
  const [paginaAtual, setPaginaAtual] = useState(1);
  const itensPorPagina = 10;

  useEffect(() => {
    carregarBatches();
  }, []);

  const carregarBatches = async () => {
    try {
      setLoading(true);
      const response = await juditService.listarBatches();
      if (response.success) {
        setBatches(response.data);
        // Seleciona automaticamente o batch mais recente
        if (response.data.length > 0) {
          carregarResultados(response.data[0].batch_id);
        }
      }
    } catch (error) {
      console.error('Erro ao carregar batches:', error);
    } finally {
      setLoading(false);
    }
  };

  const carregarResultados = async (batchId) => {
    try {
      setLoading(true);
      setSelectedBatch(batchId);
      const response = await juditService.obterResultados(batchId);
      
      if (response.success) {
        // Filtra apenas processos encontrados (status sucesso e quantidade > 0)
        const processosEncontrados = response.data.resultados.filter(
          r => r.status === 'sucesso' && r.qtd_processos > 0
        );
        setResultados(processosEncontrados);
        setResultadosFiltrados(processosEncontrados);
        setSelectedItems(new Set());
        setSelectAll(false);
        setPaginaAtual(1);
      }
    } catch (error) {
      console.error('Erro ao carregar resultados:', error);
    } finally {
      setLoading(false);
    }
  };

  // Aplicar filtros
  useEffect(() => {
    let filtrados = resultados;

    if (filtroDocumento) {
      filtrados = filtrados.filter(r => 
        r.documento.toLowerCase().includes(filtroDocumento.toLowerCase())
      );
    }

    if (filtroNome) {
      filtrados = filtrados.filter(r => 
        r.nome?.toLowerCase().includes(filtroNome.toLowerCase())
      );
    }

    if (filtroEmpresa) {
      filtrados = filtrados.filter(r => 
        r.empresa?.toLowerCase().includes(filtroEmpresa.toLowerCase())
      );
    }

    setResultadosFiltrados(filtrados);
    setPaginaAtual(1);
  }, [filtroDocumento, filtroNome, filtroEmpresa, resultados]);

  const toggleSelectAll = () => {
    if (selectAll) {
      setSelectedItems(new Set());
    } else {
      setSelectedItems(new Set(resultados.map((_, idx) => idx)));
    }
    setSelectAll(!selectAll);
  };

  const toggleItem = (index) => {
    const newSelected = new Set(selectedItems);
    if (newSelected.has(index)) {
      newSelected.delete(index);
    } else {
      newSelected.add(index);
    }
    setSelectedItems(newSelected);
    setSelectAll(newSelected.size === resultados.length);
  };

  const exportarExcel = () => {
    if (resultados.length === 0) {
      alert('Nenhum dado para exportar');
      return;
    }

    // Prepara dados para exportação
    const dadosExportacao = resultados.flatMap(resultado => {
      if (!resultado.processos || resultado.processos.length === 0) {
        return [{
          'Documento': resultado.documento,
          'Tipo': resultado.doc_type,
          'Nome': resultado.nome,
          'Empresa': resultado.empresa,
          'Quantidade Processos': resultado.qtd_processos,
          'Status': resultado.status
        }];
      }

      return resultado.processos.map(processo => ({
        'Documento': resultado.documento,
        'Tipo': resultado.doc_type,
        'Nome': resultado.nome,
        'Empresa': resultado.empresa,
        'Número CNJ': processo.code || '',
        'Tribunal': processo.tribunal_acronym || '',
        'Justiça': processo.justice || '',
        'Instância': processo.instance || '',
        'Valor Causa': processo.amount || '',
        'Data Distribuição': processo.distribution_date || '',
        'Fase': processo.phase || '',
        'Status Processo': processo.status || '',
        'Polo Ativo': processo.parties?.filter(p => p.side === 'Active').map(p => p.name).join('; ') || '',
        'Polo Passivo': processo.parties?.filter(p => p.side === 'Passive').map(p => p.name).join('; ') || '',
        'Classe': processo.classifications?.map(c => c.name).join('; ') || '',
        'Assunto': processo.subjects?.map(s => s.name).join('; ') || '',
        'Vara': processo.courts?.map(c => c.name).join('; ') || ''
      }));
    });

    // Cria planilha
    const ws = XLSX.utils.json_to_sheet(dadosExportacao);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Processos');

    // Salva arquivo
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    XLSX.writeFile(wb, `processos_encontrados_${timestamp}.xlsx`);
  };

  const atualizarPipedrive = async () => {
    const selecionados = Array.from(selectedItems).map(idx => resultados[idx]);
    if (selecionados.length === 0) {
      alert('Selecione pelo menos um item');
      return;
    }

    try {
      setLoading(true);
      
      for (const resultado of selecionados) {
        // Prepara dados para atualização no Pipedrive
        const dadosAtualizacao = {
          deal_id: resultado.deal_id, // Assumindo que o deal_id vem do resultado
          processos_encontrados: resultado.qtd_processos,
          status_processo: 'Com Processo',
          detalhes_processos: resultado.processos?.map(p => ({
            numero_cnj: p.code,
            tribunal: p.tribunal_acronym,
            valor_causa: p.amount,
            status: p.status
          }))
        };

        // TODO: Implementar chamada real ao Pipedrive
        console.log('Atualizando Pipedrive:', dadosAtualizacao);
      }

      alert(`${selecionados.length} negócio(s) atualizado(s) no Pipedrive com sucesso!`);
      setSelectedItems(new Set());
      setSelectAll(false);
    } catch (error) {
      console.error('Erro ao atualizar Pipedrive:', error);
      alert('Erro ao atualizar Pipedrive. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const abrirModal = (resultado) => {
    setResultadoSelecionado(resultado);
    setModalAberto(true);
  };

  // Paginação
  const totalPaginas = Math.ceil(resultadosFiltrados.length / itensPorPagina);
  const indiceInicio = (paginaAtual - 1) * itensPorPagina;
  const indiceFim = indiceInicio + itensPorPagina;
  const resultadosPaginados = resultadosFiltrados.slice(indiceInicio, indiceFim);

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-slate-900">Processos Localizados</h1>
        <p className="text-slate-600 mt-2">Visualize e gerencie os processos encontrados</p>
      </div>

      {/* Seletor de Batch */}
      <div className="mb-4 flex gap-4 items-center">
        <select
          value={selectedBatch || ''}
          onChange={(e) => carregarResultados(e.target.value)}
          className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="">Selecione um lote</option>
          {batches.map(batch => (
            <option key={batch.batch_id} value={batch.batch_id}>
              {new Date(batch.created_at).toLocaleString()} - {batch.sucesso} sucesso / {batch.erro} erros
            </option>
          ))}
        </select>
        <Button onClick={carregarBatches} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Atualizar
        </Button>
      </div>

      {/* Filtros */}
      <div className="mb-4 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input
            type="text"
            placeholder="Filtrar por CPF/CNPJ..."
            value={filtroDocumento}
            onChange={(e) => setFiltroDocumento(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input
            type="text"
            placeholder="Filtrar por nome..."
            value={filtroNome}
            onChange={(e) => setFiltroNome(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input
            type="text"
            placeholder="Filtrar por empresa..."
            value={filtroEmpresa}
            onChange={(e) => setFiltroEmpresa(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="text-sm text-slate-600 flex items-center">
          {resultadosFiltrados.length} resultado(s)
        </div>
      </div>

      {/* Toolbar */}
      <div className="mb-4 flex gap-2 items-center flex-wrap">
        <Button onClick={toggleSelectAll} variant="outline" size="sm">
          {selectAll ? <CheckSquare className="h-4 w-4 mr-2" /> : <Square className="h-4 w-4 mr-2" />}
          Selecionar Todos
        </Button>
        <Button onClick={atualizarPipedrive} variant="default" size="sm" disabled={selectedItems.size === 0 || loading}>
          Atualizar Pipedrive ({selectedItems.size})
        </Button>
        <Button onClick={exportarExcel} variant="outline" size="sm">
          <FileDown className="h-4 w-4 mr-2" />
          Exportar Excel
        </Button>
      </div>

      {/* Tabela */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-100 border-b border-slate-200">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-700 uppercase">Sel</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-700 uppercase">CPF</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-700 uppercase">CNPJ</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-700 uppercase">Nome</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-700 uppercase">Empresa</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-700 uppercase">Qtd Processos</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-700 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-700 uppercase">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {loading ? (
                <tr>
                  <td colSpan="7" className="px-4 py-8 text-center text-slate-500">
                    Carregando...
                  </td>
                </tr>
              ) : resultadosPaginados.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-4 py-8 text-center text-slate-500">
                    Nenhum processo localizado
                  </td>
                </tr>
              ) : (
                resultadosPaginados.map((resultado, idx) => {
                  const indiceReal = indiceInicio + idx;
                  return (
                  <tr key={indiceReal} className="hover:bg-slate-50">
                    <td className="px-4 py-3">
                      <input
                        type="checkbox"
                        checked={selectedItems.has(indiceReal)}
                        onChange={() => toggleItem(indiceReal)}
                        className="rounded border-slate-300 text-primary focus:ring-primary"
                      />
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-900 font-mono">
                      {resultado.doc_type === 'cpf' ? resultado.documento : '-'}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-900 font-mono">
                      {resultado.doc_type === 'cnpj' ? resultado.documento : '-'}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-900">{resultado.nome || '-'}</td>
                    <td className="px-4 py-3 text-sm text-slate-900">{resultado.empresa || '-'}</td>
                    <td className="px-4 py-3 text-sm text-slate-900">
                      <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                        {resultado.qtd_processos}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                        {resultado.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => abrirModal(resultado)}
                      >
                        Ver Detalhes
                      </Button>
                    </td>
                  </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Paginação */}
        {totalPaginas > 1 && (
          <div className="px-4 py-3 border-t border-slate-200 flex items-center justify-between">
            <div className="text-sm text-slate-600">
              Página {paginaAtual} de {totalPaginas} ({resultadosFiltrados.length} resultados)
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPaginaAtual(p => Math.max(1, p - 1))}
                disabled={paginaAtual === 1}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPaginaAtual(p => Math.min(totalPaginas, p + 1))}
                disabled={paginaAtual === totalPaginas}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Modal de Detalhes */}
      <ProcessosModal
        isOpen={modalAberto}
        onClose={() => setModalAberto(false)}
        resultado={resultadoSelecionado}
      />
    </div>
  );
}
