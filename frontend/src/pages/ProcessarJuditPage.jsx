import { useState, useRef, useEffect } from 'react';
import MainLayout from '../components/layout/MainLayout';
import { FileSearch, Play, Pause, Save, RotateCcw, Upload, Database } from 'lucide-react';
import { Button } from '../components/ui/button';
import * as XLSX from 'xlsx';
import { juditService } from '../services/juditService';

export default function ProcessarJuditPage() {
  // Recupera dados salvos do localStorage
  const [arquivo, setArquivo] = useState(() => {
    const saved = localStorage.getItem('processar_arquivo');
    return saved ? JSON.parse(saved) : null;
  });
  const [colunas, setColunas] = useState(() => {
    const saved = localStorage.getItem('processar_colunas');
    return saved ? JSON.parse(saved) : [];
  });
  const [dadosCarregados, setDadosCarregados] = useState(() => {
    const saved = localStorage.getItem('processar_dados');
    return saved ? JSON.parse(saved) : [];
  });
  const [mapeamento, setMapeamento] = useState(() => {
    const saved = localStorage.getItem('processar_mapeamento');
    return saved ? JSON.parse(saved) : {
      nome: '',
      empresa: '',
      cpf: '',
      cnpj: ''
    };
  });
  const [processando, setProcessando] = useState(false);
  const [pausado, setPausado] = useState(false);
  const [resultados, setResultados] = useState(() => {
    const saved = localStorage.getItem('processar_resultados');
    return saved ? JSON.parse(saved) : [];
  });
  const [logs, setLogs] = useState(() => {
    const saved = localStorage.getItem('processar_logs');
    return saved ? JSON.parse(saved) : [];
  });
  const [modalTipoBuscaAberto, setModalTipoBuscaAberto] = useState(false);
  const [batchId, setBatchId] = useState(null);
  const [statusProcessamento, setStatusProcessamento] = useState(null);
  const fileInputRef = useRef(null);
  const pollingIntervalRef = useRef(null);

  // Salva estados no localStorage
  useEffect(() => {
    if (arquivo) localStorage.setItem('processar_arquivo', JSON.stringify(arquivo));
  }, [arquivo]);

  useEffect(() => {
    if (colunas.length > 0) localStorage.setItem('processar_colunas', JSON.stringify(colunas));
  }, [colunas]);

  useEffect(() => {
    if (dadosCarregados.length > 0) localStorage.setItem('processar_dados', JSON.stringify(dadosCarregados));
  }, [dadosCarregados]);

  useEffect(() => {
    localStorage.setItem('processar_mapeamento', JSON.stringify(mapeamento));
  }, [mapeamento]);

  useEffect(() => {
    if (resultados.length > 0) localStorage.setItem('processar_resultados', JSON.stringify(resultados));
  }, [resultados]);

  useEffect(() => {
    if (logs.length > 0) localStorage.setItem('processar_logs', JSON.stringify(logs));
  }, [logs]);

  const addLog = (mensagem, tipo = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { timestamp, mensagem, tipo }]);
  };

  // Carrega dados do Pipedrive automaticamente se existirem
  useEffect(() => {
    const dadosPipedrive = localStorage.getItem('dados_processar');
    const origem = localStorage.getItem('origem_dados');
    
    if (dadosPipedrive && origem === 'pipedrive') {
      try {
        const dados = JSON.parse(dadosPipedrive);
        
        // Extrai as colunas
        const colunasData = Object.keys(dados[0] || {});
        setColunas(colunasData);
        setDadosCarregados(dados);
        
        // Mapeamento automático
        const novoMapeamento = {
          nome: 'Título',
          empresa: 'Organização',
          cpf: 'CPF',
          cnpj: 'CNPJ'
        };
        
        setMapeamento(novoMapeamento);
        setArquivo({ name: 'Dados do Pipedrive' });
        
        // Limpa dados anteriores de processamento
        setResultados([]);
        setBatchId(null);
        setStatusProcessamento(null);
        localStorage.removeItem('processar_resultados');
        
        addLog(`${dados.length} registros carregados do Pipedrive`, 'success');
        addLog('Colunas mapeadas automaticamente', 'success');
        
        // Limpa o localStorage para não carregar novamente
        localStorage.removeItem('dados_processar');
        localStorage.removeItem('origem_dados');
      } catch (error) {
        addLog(`Erro ao carregar dados do Pipedrive: ${error.message}`, 'error');
      }
    }
  }, []);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      addLog(`Lendo arquivo: ${file.name}...`, 'info');
      
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = new Uint8Array(e.target.result);
          const workbook = XLSX.read(data, { type: 'array' });
          const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
          const jsonData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 });
          
          // Primeira linha contém os nomes das colunas
          const colunasExcel = jsonData[0] || [];
          setColunas(colunasExcel);
          
          // Mapeamento automático
          const novoMapeamento = {
            nome: '',
            empresa: '',
            cpf: '',
            cnpj: ''
          };
          
          colunasExcel.forEach((coluna, index) => {
            const colunaLower = coluna.toLowerCase();
            if (colunaLower === 'titulo' || colunaLower === 'nome') {
              novoMapeamento.nome = coluna;
            }
            if (colunaLower === 'organização' || colunaLower === 'empresa' || colunaLower === 'organizacao') {
              novoMapeamento.empresa = coluna;
            }
            if (colunaLower === 'cpf') {
              novoMapeamento.cpf = coluna;
            }
            if (colunaLower === 'cnpj') {
              novoMapeamento.cnpj = coluna;
            }
          });
          
          setMapeamento(novoMapeamento);
          setArquivo(file);
          addLog(`Arquivo carregado: ${file.name}`, 'success');
          addLog(`${colunasExcel.length} colunas encontradas`, 'info');
          addLog('Colunas mapeadas automaticamente', 'success');
        } catch (error) {
          addLog(`Erro ao ler arquivo: ${error.message}`, 'error');
        }
      };
      
      reader.readAsArrayBuffer(file);
    } catch (error) {
      addLog(`Erro ao carregar arquivo: ${error.message}`, 'error');
    }
  };

  const handleProcessar = () => {
    if (!arquivo) {
      addLog('Por favor, carregue uma planilha para processar', 'error');
      return;
    }

    // Verifica se todas as colunas foram mapeadas
    if (!mapeamento.nome || !mapeamento.empresa || !mapeamento.cpf || !mapeamento.cnpj) {
      addLog('Por favor, mapeie todas as colunas (Nome, Empresa, CPF e CNPJ)', 'error');
      return;
    }

    // Abre modal para selecionar tipo de busca
    setModalTipoBuscaAberto(true);
  };

  const processarComTempoReal = async () => {
    setModalTipoBuscaAberto(false);
    setProcessando(true);
    setPausado(false);
    addLog('Iniciando busca em TEMPO REAL (on-demand)...', 'info');
    addLog('⚠️ Esse processo pode demorar alguns minutos', 'warning');
    addLog(`Total de registros: ${dadosCarregados.length}`, 'info');

    try {
      // Transforma dados mapeando as colunas corretamente
      const dadosFormatados = dadosCarregados.map(item => ({
        'Título': item[mapeamento.nome] || '',
        'Pessoa': item[mapeamento.nome] || '',
        'Organização': item[mapeamento.empresa] || '',
        'CPF': item[mapeamento.cpf] || '',
        'CNPJ': item[mapeamento.cnpj] || ''
      }));

      addLog('Enviando dados para API Judit.io...', 'info');
      
      // Envia dados para processamento
      const response = await juditService.processar(dadosFormatados, true, true);
      
      if (response.success) {
        const newBatchId = response.batch_id;
        setBatchId(newBatchId);
        addLog(`✓ Batch iniciado: ${newBatchId}`, 'success');
        addLog(`✓ ${response.message}`, 'success');
        addLog('Aguardando respostas via webhook...', 'info');
        
        // Inicia polling para verificar status
        iniciarPolling(newBatchId);
      } else {
        addLog('Erro ao iniciar processamento', 'error');
        setProcessando(false);
      }
    } catch (error) {
      addLog(`Erro: ${error.message}`, 'error');
      setProcessando(false);
    }
  };

  const processarComBancoDeDados = async () => {
    setModalTipoBuscaAberto(false);
    setProcessando(true);
    setPausado(false);
    addLog('Iniciando busca no BANCO DE DADOS (até 30 dias de defasagem)...', 'info');
    addLog('✓ Esse processo é mais rápido', 'success');
    addLog(`Total de registros: ${dadosCarregados.length}`, 'info');

    try {
      // Transforma dados mapeando as colunas corretamente
      const dadosFormatados = dadosCarregados.map(item => ({
        'Título': item[mapeamento.nome] || '',
        'Pessoa': item[mapeamento.nome] || '',
        'Organização': item[mapeamento.empresa] || '',
        'CPF': item[mapeamento.cpf] || '',
        'CNPJ': item[mapeamento.cnpj] || ''
      }));

      addLog('Enviando dados para API Judit.io...', 'info');
      
      // Envia dados para processamento
      const response = await juditService.processar(dadosFormatados, false, true);
      
      if (response.success) {
        const newBatchId = response.batch_id;
        setBatchId(newBatchId);
        addLog(`✓ Batch iniciado: ${newBatchId}`, 'success');
        addLog(`✓ ${response.message}`, 'success');
        addLog('Consultando banco de dados da Judit.io...', 'info');
        
        // Inicia polling para verificar status
        iniciarPolling(newBatchId);
      } else {
        addLog('Erro ao iniciar processamento', 'error');
        setProcessando(false);
      }
    } catch (error) {
      addLog(`Erro: ${error.message}`, 'error');
      setProcessando(false);
    }
  };

  const iniciarPolling = (batchId) => {
    // Limpa polling anterior se existir
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }

    // Polling a cada 3 segundos
    pollingIntervalRef.current = setInterval(async () => {
      try {
        const response = await juditService.obterStatus(batchId);
        
        if (response.success) {
          const status = response.data;
          setStatusProcessamento(status);
          
          const { total, processados, sucesso, erro } = status;
          addLog(`Status: ${processados}/${total} processados (${sucesso} sucesso, ${erro} erros)`, 'info');
          
          // Se concluído, para o polling
          if (status.status === 'concluído' || status.status === 'erro') {
            clearInterval(pollingIntervalRef.current);
            setProcessando(false);
            
            if (status.status === 'concluído') {
              addLog(`✓ Processamento concluído! Total: ${sucesso} sucessos, ${erro} erros`, 'success');
              
              // Carrega resultados
              const resultadosResponse = await juditService.obterResultados(batchId);
              if (resultadosResponse.success) {
                setResultados(resultadosResponse.data.resultados);
                addLog(`Resultados carregados: ${resultadosResponse.data.resultados.length} registros`, 'success');
              }
            } else {
              addLog('Processamento finalizado com erro', 'error');
            }
          }
        }
      } catch (error) {
        console.error('Erro no polling:', error);
      }
    }, 3000);
  };

  // Limpa polling ao desmontar componente
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  const handlePausar = () => {
    setPausado(!pausado);
    addLog(pausado ? 'Processamento retomado' : 'Processamento pausado', 'warning');
  };

  const handleSalvar = () => {
    if (resultados.length === 0) {
      addLog('Nenhum resultado para salvar', 'warning');
      return;
    }
    addLog('Salvando resultados...', 'info');
    // TODO: Implementar salvamento
  };

  const handleNovaBusca = () => {
    setArquivo(null);
    setColunas([]);
    setDadosCarregados([]);
    setMapeamento({
      nome: '',
      empresa: '',
      cpf: '',
      cnpj: ''
    });
    setResultados([]);
    setLogs([]);
    setProcessando(false);
    setPausado(false);
    setBatchId(null);
    setStatusProcessamento(null);
    
    // Limpa polling se estiver ativo
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
    
    // LIMPA TUDO DO LOCALSTORAGE
    localStorage.removeItem('processar_arquivo');
    localStorage.removeItem('processar_colunas');
    localStorage.removeItem('processar_dados');
    localStorage.removeItem('processar_mapeamento');
    localStorage.removeItem('processar_resultados');
    localStorage.removeItem('processar_logs');
    
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    
    const novoLog = [{ 
      timestamp: new Date().toLocaleTimeString(), 
      mensagem: 'Nova busca iniciada - dados anteriores limpos', 
      tipo: 'success' 
    }];
    setLogs(novoLog);
  };

  return (
    <MainLayout title="Processar Judit">
      <div className="p-6">
        {/* Status */}
        <div className="mb-6">
          <p className="text-muted-foreground">
            Sistema de processamento de processos jurídicos
          </p>
        </div>

        {/* Upload de Planilha - Mostra apenas se não houver arquivo carregado */}
        {!arquivo && (
          <div className="mb-6">
            <div className="p-6 border rounded-lg bg-card">
              <h3 className="text-lg font-semibold mb-4">Upload de Planilha Excel</h3>
              <div className="border-2 border-dashed rounded-lg p-8 text-center">
                <Upload className="h-12 w-12 mx-auto mb-3 text-muted-foreground" />
                <p className="mb-3 text-muted-foreground">
                  Arraste um arquivo Excel ou clique para selecionar
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="file-upload"
                  disabled={processando}
                />
                <Button 
                  onClick={() => fileInputRef.current?.click()}
                  disabled={processando}
                >
                  Selecionar Arquivo
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Informação do arquivo carregado */}
        {arquivo && (
          <>
            <div className="mb-6 p-4 border rounded-lg bg-card flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 rounded">
                  <FileSearch className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <p className="font-medium">Arquivo carregado</p>
                  <p className="text-sm text-muted-foreground">{arquivo.name}</p>
                </div>
              </div>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => {
                  setArquivo(null);
                  setColunas([]);
                  setMapeamento({ nome: '', empresa: '', cpf: '', cnpj: '' });
                  if (fileInputRef.current) {
                    fileInputRef.current.value = '';
                  }
                  addLog('Arquivo removido', 'info');
                }}
                disabled={processando}
              >
                Remover
              </Button>
            </div>

            {/* Mapeamento de Colunas */}
            <div className="mb-6 p-6 border rounded-lg bg-card">
              <h3 className="text-lg font-semibold mb-4">Mapeamento de Colunas</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Nome:</label>
                  <select
                    value={mapeamento.nome}
                    onChange={(e) => setMapeamento({...mapeamento, nome: e.target.value})}
                    className="w-full p-2 border rounded-md"
                    disabled={processando}
                  >
                    <option value="">Selecione...</option>
                    {colunas.map((col, idx) => (
                      <option key={idx} value={col}>{col}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Empresa:</label>
                  <select
                    value={mapeamento.empresa}
                    onChange={(e) => setMapeamento({...mapeamento, empresa: e.target.value})}
                    className="w-full p-2 border rounded-md"
                    disabled={processando}
                  >
                    <option value="">Selecione...</option>
                    {colunas.map((col, idx) => (
                      <option key={idx} value={col}>{col}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">CPF:</label>
                  <select
                    value={mapeamento.cpf}
                    onChange={(e) => setMapeamento({...mapeamento, cpf: e.target.value})}
                    className="w-full p-2 border rounded-md"
                    disabled={processando}
                  >
                    <option value="">Selecione...</option>
                    {colunas.map((col, idx) => (
                      <option key={idx} value={col}>{col}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">CNPJ:</label>
                  <select
                    value={mapeamento.cnpj}
                    onChange={(e) => setMapeamento({...mapeamento, cnpj: e.target.value})}
                    className="w-full p-2 border rounded-md"
                    disabled={processando}
                  >
                    <option value="">Selecione...</option>
                    {colunas.map((col, idx) => (
                      <option key={idx} value={col}>{col}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Action Buttons */}
        <div className="mb-6 flex gap-3 justify-end">
          <Button
            onClick={handleProcessar}
            disabled={processando}
            className="bg-green-600 hover:bg-green-700"
          >
            <Play className="h-4 w-4 mr-2" />
            {processando ? 'Processando...' : 'Processar'}
          </Button>
          <Button
            onClick={handlePausar}
            disabled={!processando}
            className="bg-yellow-600 hover:bg-yellow-700"
          >
            <Pause className="h-4 w-4 mr-2" />
            {pausado ? 'Retomar' : 'Pausar'}
          </Button>
          <Button
            onClick={handleSalvar}
            disabled={processando || resultados.length === 0}
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Save className="h-4 w-4 mr-2" />
            Salvar Resultado
          </Button>
          <Button
            onClick={handleNovaBusca}
            className="bg-purple-600 hover:bg-purple-700"
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Nova Busca
          </Button>
        </div>

        {/* Status do Processamento */}
        {statusProcessamento && processando && (
          <div className="mb-6 border rounded-lg bg-card p-4">
            <h3 className="font-semibold mb-3">Status do Processamento</h3>
            <div className="grid grid-cols-4 gap-4 mb-3">
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">{statusProcessamento.total}</p>
                <p className="text-sm text-muted-foreground">Total</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-yellow-600">{statusProcessamento.processados}</p>
                <p className="text-sm text-muted-foreground">Processados</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">{statusProcessamento.sucesso}</p>
                <p className="text-sm text-muted-foreground">Sucesso</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-red-600">{statusProcessamento.erro}</p>
                <p className="text-sm text-muted-foreground">Erros</p>
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${(statusProcessamento.processados / statusProcessamento.total) * 100}%` }}
              />
            </div>
          </div>
        )}

        {/* Results Table */}
        {resultados.length > 0 && (
          <div className="mb-6 border rounded-lg bg-card">
            <div className="p-4 border-b bg-muted/50">
              <h3 className="font-semibold">Resultados ({resultados.length} registros)</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="p-3 text-left font-medium border-b">Nome</th>
                    <th className="p-3 text-left font-medium border-b">Documento</th>
                    <th className="p-3 text-left font-medium border-b">Empresa</th>
                    <th className="p-3 text-left font-medium border-b">Qtd Processos</th>
                    <th className="p-3 text-left font-medium border-b">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {resultados.map((resultado, index) => (
                    <tr key={index} className="border-b hover:bg-muted/30">
                      <td className="p-3">{resultado.nome || '-'}</td>
                      <td className="p-3 font-mono text-xs">
                        {resultado.documento || '-'}
                        {resultado.doc_type && (
                          <span className="ml-2 text-xs text-muted-foreground">({resultado.doc_type.toUpperCase()})</span>
                        )}
                      </td>
                      <td className="p-3">{resultado.empresa || '-'}</td>
                      <td className="p-3 text-center">
                        {resultado.status === 'sucesso' ? (
                          <span className={`font-bold ${resultado.qtd_processos > 0 ? 'text-orange-600' : 'text-green-600'}`}>
                            {resultado.qtd_processos}
                          </span>
                        ) : (
                          '-'
                        )}
                      </td>
                      <td className="p-3">
                        {resultado.status === 'sucesso' ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            ✓ Sucesso
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            ✗ Erro
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Log Console */}
        <div className="border rounded-lg bg-card">
          <div className="p-4 border-b bg-muted/50">
            <h3 className="font-semibold">Log de Processamento</h3>
          </div>
          <div className="p-4 bg-black text-green-400 font-mono text-sm h-64 overflow-y-auto">
            {logs.length === 0 ? (
              <p className="text-gray-500">Aguardando processamento...</p>
            ) : (
              logs.map((log, index) => (
                <div key={index} className={`mb-1 ${
                  log.tipo === 'error' ? 'text-red-400' :
                  log.tipo === 'success' ? 'text-green-400' :
                  log.tipo === 'warning' ? 'text-yellow-400' :
                  'text-blue-400'
                }`}>
                  [{log.timestamp}] {log.mensagem}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Modal de Seleção de Tipo de Busca */}
        {modalTipoBuscaAberto && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-card border rounded-lg p-6 max-w-2xl w-full mx-4">
              <h3 className="text-xl font-bold mb-4">Selecione o Tipo de Busca</h3>
              <p className="text-muted-foreground mb-6">
                Escolha como deseja processar os dados na API Judit.io:
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                {/* Opção 1: Tempo Real */}
                <button
                  onClick={processarComTempoReal}
                  className="p-6 border-2 rounded-lg hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-950 transition-all text-left"
                >
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded">
                      <FileSearch className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                      <h4 className="font-bold text-lg mb-2">Busca em Tempo Real</h4>
                      <p className="text-sm text-muted-foreground mb-3">
                        Consulta diretamente nos tribunais (on-demand)
                      </p>
                      <div className="space-y-1 text-sm">
                        <p className="text-yellow-600 dark:text-yellow-400">⚠️ Processo mais demorado</p>
                        <p className="text-green-600 dark:text-green-400">✓ Dados mais atualizados</p>
                        <p className="text-blue-600 dark:text-blue-400">ℹ️ Pode levar vários minutos ou horas</p>
                      </div>
                    </div>
                  </div>
                </button>

                {/* Opção 2: Banco de Dados */}
                <button
                  onClick={processarComBancoDeDados}
                  className="p-6 border-2 rounded-lg hover:border-green-500 hover:bg-green-50 dark:hover:bg-green-950 transition-all text-left"
                >
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-green-100 dark:bg-green-900 rounded">
                      <Database className="h-6 w-6 text-green-600 dark:text-green-400" />
                    </div>
                    <div>
                      <h4 className="font-bold text-lg mb-2">Banco de Dados</h4>
                      <p className="text-sm text-muted-foreground mb-3">
                        Consulta no banco da Judit.io
                      </p>
                      <div className="space-y-1 text-sm">
                        <p className="text-green-600 dark:text-green-400">✓ Processo rápido</p>
                        <p className="text-yellow-600 dark:text-yellow-400">⚠️ Até 30 dias de defasagem</p>
                        <p className="text-blue-600 dark:text-blue-400">ℹ️ Recomendado para grandes volumes</p>
                      </div>
                    </div>
                  </div>
                </button>
              </div>

              <div className="flex justify-end">
                <Button
                  variant="outline"
                  onClick={() => setModalTipoBuscaAberto(false)}
                >
                  Cancelar
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
