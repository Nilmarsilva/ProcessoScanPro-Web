import { useState, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../components/layout/MainLayout';
import { ExternalLink, Send } from 'lucide-react';
import { Button } from '../components/ui/button';
import * as XLSX from 'xlsx';
import { pipedriveService } from '../services/pipedriveService';

export default function PipedrivePage() {
  const navigate = useNavigate();
  
  // Recupera dados do localStorage ao iniciar
  const [data, setData] = useState(() => {
    const saved = localStorage.getItem('pipedrive_data');
    return saved ? JSON.parse(saved) : [];
  });
  const [funis, setFunis] = useState([]);
  const [filtros, setFiltros] = useState([]);
  const [selectedFunil, setSelectedFunil] = useState('');
  const [selectedFiltro, setSelectedFiltro] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  
  const recordsPerPage = 50;

  // Salva dados no localStorage sempre que mudar
  useEffect(() => {
    if (data.length > 0) {
      localStorage.setItem('pipedrive_data', JSON.stringify(data));
    }
  }, [data]);

  // Carrega funis e filtros ao montar o componente
  useEffect(() => {
    carregarFunisEFiltros();
  }, []);

  const carregarFunisEFiltros = async () => {
    try {
      const [resultFunis, resultFiltros] = await Promise.all([
        pipedriveService.listarFunis(),
        pipedriveService.listarFiltros()
      ]);

      setFunis(resultFunis.funis || []);
      setFiltros(resultFiltros.filtros || []);
    } catch (error) {
      console.error('Erro ao carregar funis/filtros:', error);
      alert('Erro ao carregar funis e filtros: ' + error.message);
    }
  };

  // Paginação
  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * recordsPerPage;
    const endIndex = startIndex + recordsPerPage;
    return data.slice(startIndex, endIndex);
  }, [data, currentPage, recordsPerPage]);

  const totalPages = Math.ceil(data.length / recordsPerPage);

  const handleCarregar = async () => {
    setIsLoading(true);
    try {
      const funilId = selectedFunil ? parseInt(selectedFunil) : null;
      const filtroId = selectedFiltro ? parseInt(selectedFiltro) : null;

      const result = await pipedriveService.carregarNegocios(funilId, filtroId);
      
      setData(result.negocios || []);
      setCurrentPage(1);
      
      alert(`${result.total} negócio(s) carregado(s) com sucesso!`);
    } catch (error) {
      console.error('Erro:', error);
      alert('Erro ao carregar negócios: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBuscar = async () => {
    if (!searchTerm.trim()) {
      alert('Digite um nome para buscar!');
      return;
    }
    
    setIsLoading(true);
    try {
      const result = await pipedriveService.buscarPorNome(searchTerm);
      
      setData(result.negocios || []);
      setCurrentPage(1);
      
      alert(`${result.total} negócio(s) encontrado(s)!`);
    } catch (error) {
      console.error('Erro:', error);
      alert('Erro ao buscar negócios: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLimpar = () => {
    setData([]);
    setSearchTerm('');
    setCurrentPage(1);
  };

  const handleEnviarParaProcessar = () => {
    if (data.length === 0) {
      alert('Nenhum dado para enviar! Carregue os negócios primeiro.');
      return;
    }

    try {
      // Formata os dados no formato esperado pela tela Processar Judit
      const dadosFormatados = data.map(item => ({
        'ID': item.id || '',  // ID do negócio no Pipedrive
        'Título': item.title || '',
        'Pessoa': item.person_name || '',
        'CPF': item.cpf || '',
        'Organização': item.org_name || '',
        'CNPJ': item.cnpj || ''
      }));

      // Salva no localStorage para a tela Processar Judit
      localStorage.setItem('dados_processar', JSON.stringify(dadosFormatados));
      localStorage.setItem('origem_dados', 'pipedrive');
      
      // Navega para a tela Processar Judit
      navigate('/processar-judit');
      
    } catch (error) {
      console.error('Erro ao enviar dados:', error);
      alert('Erro ao enviar dados: ' + error.message);
    }
  };

  return (
    <MainLayout title="Pipedrive - Gerenciador de Negócios">
      <div className="p-6">
        <div className="w-full">
          {/* Status */}
          <div className="mb-6">
            <p className="text-muted-foreground">
              {data.length > 0 ? `${data.length} negócio(s) carregado(s)` : 'Configure os filtros e carregue os negócios'}
            </p>
          </div>

          {/* Filtros */}
          <div className="mb-6 p-6 border rounded-lg bg-card">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium mb-2">Funil:</label>
                <select 
                  value={selectedFunil}
                  onChange={(e) => setSelectedFunil(e.target.value)}
                  className="w-full p-2 border rounded-md"
                  disabled={isLoading}
                >
                  <option value="">Todos os funis</option>
                  {funis.map((funil) => (
                    <option key={funil.id} value={funil.id}>
                      {funil.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Filtro:</label>
                <select 
                  value={selectedFiltro}
                  onChange={(e) => setSelectedFiltro(e.target.value)}
                  className="w-full p-2 border rounded-md"
                  disabled={isLoading}
                >
                  <option value="">Sem filtro</option>
                  {filtros.map((filtro) => (
                    <option key={filtro.id} value={filtro.id}>
                      {filtro.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Buscar por nome:</label>
                <input 
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Digite o nome..."
                  className="w-full p-2 border rounded-md"
                />
              </div>
            </div>

            {/* Botões */}
            <div className="flex gap-3 justify-end">
              <Button 
                onClick={handleCarregar}
                disabled={isLoading}
                className="bg-green-600 hover:bg-green-700"
              >
                {isLoading ? 'Carregando...' : 'Carregar Negócios'}
              </Button>
              <Button 
                onClick={handleBuscar}
                disabled={isLoading}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {isLoading ? 'Buscando...' : 'Buscar Nome'}
              </Button>
              <Button 
                onClick={handleLimpar}
                disabled={isLoading}
                className="bg-red-600 hover:bg-red-700"
              >
                Limpar
              </Button>
              <Button 
                onClick={handleEnviarParaProcessar}
                disabled={isLoading || data.length === 0}
                className="bg-orange-600 hover:bg-orange-700 gap-2"
              >
                <Send className="h-4 w-4" />
                Enviar para Processar
              </Button>
            </div>
          </div>

          {/* Mensagem quando não há dados */}
          {data.length === 0 && (
            <div className="text-center py-12 text-muted-foreground">
              Selecione os filtros e clique em "Carregar Negócios" para começar
            </div>
          )}

          {/* Tabela (placeholder para quando houver dados) */}
          {data.length > 0 && (
            <div className="border rounded-lg bg-card">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="p-3 text-left font-medium border-b">ID</th>
                      <th className="p-3 text-left font-medium border-b">Título</th>
                      <th className="p-3 text-left font-medium border-b">Pessoa</th>
                      <th className="p-3 text-left font-medium border-b">CPF</th>
                      <th className="p-3 text-left font-medium border-b">Organização</th>
                      <th className="p-3 text-left font-medium border-b">CNPJ</th>
                      <th className="p-3 text-left font-medium border-b">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {paginatedData.map((row, index) => (
                      <tr key={index} className="border-b hover:bg-muted/30">
                        <td className="p-3">{row.id}</td>
                        <td className="p-3">{row.title}</td>
                        <td className="p-3">{row.person_name}</td>
                        <td className="p-3">{row.cpf || '-'}</td>
                        <td className="p-3">{row.org_name}</td>
                        <td className="p-3">{row.cnpj || '-'}</td>
                        <td className="p-3">{row.status}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Paginação */}
              {totalPages > 1 && (
                <div className="p-4 border-t flex justify-between items-center">
                  <Button 
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                  >
                    Anterior
                  </Button>
                  <span className="text-sm">
                    Página {currentPage} de {totalPages} - Total: {data.length} registro(s)
                  </span>
                  <Button 
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                  >
                    Próxima
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
}
