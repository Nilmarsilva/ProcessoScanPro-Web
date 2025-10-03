import { useState, useMemo } from 'react';
import MainLayout from '../components/layout/MainLayout';
import CnpjUpload from '../components/cnpj/CnpjUpload';
import CnpjTable from '../components/cnpj/CnpjTable';
import CnpjPagination from '../components/cnpj/CnpjPagination';
import CnpjToolbar from '../components/cnpj/CnpjToolbar';
import CnpjActionsToolbar from '../components/cnpj/CnpjActionsToolbar';
import ColumnSelectorDialog from '../components/cnpj/ColumnSelectorDialog';
import { Button } from '../components/ui/button';
import { Database } from 'lucide-react';
import * as formatters from '../utils/formatters';
import * as XLSX from 'xlsx';
import { dadosService } from '../services/dadosService';

export default function DadosPage() {
  const [data, setData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [currentAction, setCurrentAction] = useState(null);
  const [deleteColumnsDialogOpen, setDeleteColumnsDialogOpen] = useState(false);
  
  const recordsPerPage = 50;

  // Processa o arquivo Excel
  const handleFileUpload = async (file) => {
    setIsLoading(true);
    try {
      // Lê o arquivo como ArrayBuffer
      const arrayBuffer = await file.arrayBuffer();
      
      // Lê o workbook sem forçar codepage (deixa a biblioteca detectar)
      const workbook = XLSX.read(arrayBuffer, { 
        type: 'array',
        cellDates: true,
        cellNF: false,
        cellText: false
        // Removido codepage para deixar a biblioteca detectar automaticamente
      });
      
      // Pega a primeira planilha
      const firstSheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[firstSheetName];
      
      // Converte para JSON usando raw: true para preservar valores originais
      const jsonData = XLSX.utils.sheet_to_json(worksheet, {
        raw: true, // Mantém valores originais sem conversão
        defval: '',
        blankrows: false
      });
      
      if (jsonData.length === 0) {
        alert('A planilha está vazia!');
        return;
      }
      
      // Função para corrigir encoding de caracteres especiais
      const fixEncoding = (text) => {
        if (typeof text !== 'string') return text;
        
        // Mapa completo de correções de encoding UTF-8 mal interpretado
        const fixes = {
          // Minúsculas com til
          'Ã£': 'ã', 'ã': 'ã', 'Ã£o': 'ão', 'Ã£es': 'ães',
          'Ãµ': 'õ', 'Ãµes': 'ões',
          // Minúsculas com acento agudo
          'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
          // Minúsculas com acento circunflexo
          'Ã¢': 'â', 'Ãª': 'ê', 'Ã´': 'ô',
          // Minúsculas com acento grave
          'Ã ': 'à',
          // Cedilha
          'Ã§': 'ç',
          // Maiúsculas com til
          'Ã': 'Ã', 'Ã•': 'Õ',
          // Maiúsculas com acento agudo
          'Ã': 'Á', 'Ã‰': 'É', 'Ã': 'Í', 'Ã"': 'Ó', 'Ãš': 'Ú',
          // Maiúsculas com acento circunflexo
          'Ã‚': 'Â', 'ÃŠ': 'Ê', 'Ã"': 'Ô',
          // Maiúsculas com acento grave
          'Ã€': 'À',
          // Cedilha maiúscula
          'Ã‡': 'Ç',
          // Outros símbolos
          'Â°': '°', 'Âº': 'º', 'Âª': 'ª',
          'Ã‚Â°': '°', 'Ã‚Âº': 'º', 'Ã‚Âª': 'ª',
          // Padrões específicos encontrados
          'SÃ£o': 'São',
          'JoÃ£o': 'João',
          'TaboÃ£o': 'Taboão',
          'sÃ£o': 'são',
          'joÃ£o': 'joão',
          'taboÃ£o': 'taboão'
        };
        
        let fixed = text;
        
        // Aplica as correções em ordem (mais específicas primeiro)
        const sortedKeys = Object.keys(fixes).sort((a, b) => b.length - a.length);
        sortedKeys.forEach(wrong => {
          if (fixed.includes(wrong)) {
            fixed = fixed.split(wrong).join(fixes[wrong]);
          }
        });
        
        return fixed;
      };
      
      // Converte valores para string e corrige encoding
      const processedData = jsonData.map(row => {
        const newRow = {};
        Object.keys(row).forEach(key => {
          const value = row[key];
          if (value !== null && value !== undefined) {
            const strValue = String(value);
            newRow[key] = fixEncoding(strValue);
          } else {
            newRow[key] = '';
          }
        });
        return newRow;
      });
      
      // Define colunas e dados
      setColumns(Object.keys(processedData[0]));
      setData(processedData);
      setCurrentPage(1);
      
      console.log(`Arquivo processado: ${file.name}`);
      console.log(`Total de registros: ${processedData.length}`);
      console.log(`Colunas: ${Object.keys(processedData[0]).join(', ')}`);
    } catch (error) {
      console.error('Erro ao processar arquivo:', error);
      alert('Erro ao processar arquivo: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Sem filtros - retorna todos os dados
  const filteredData = useMemo(() => {
    return data;
  }, [data]);

  // Paginação
  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * recordsPerPage;
    const endIndex = startIndex + recordsPerPage;
    return filteredData.slice(startIndex, endIndex);
  }, [filteredData, currentPage, recordsPerPage]);

  const totalPages = Math.ceil(filteredData.length / recordsPerPage);

  const handleExport = () => {
    if (data.length === 0) {
      alert('Nenhum dado para exportar!');
      return;
    }

    try {
      // Cria um novo workbook
      const wb = XLSX.utils.book_new();
      
      // Converte os dados para worksheet
      const ws = XLSX.utils.json_to_sheet(filteredData);
      
      // Adiciona a worksheet ao workbook
      XLSX.utils.book_append_sheet(wb, ws, 'Dados');
      
      // Gera o nome do arquivo com data/hora
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
      const filename = `dados_exportados_${timestamp}.xlsx`;
      
      // Salva o arquivo
      XLSX.writeFile(wb, filename);
      
      console.log(`Arquivo exportado: ${filename}`);
      alert(`Dados exportados com sucesso!\nArquivo: ${filename}`);
    } catch (error) {
      console.error('Erro ao exportar:', error);
      alert('Erro ao exportar dados: ' + error.message);
    }
  };

  const handleFormatAction = (action) => {
    setCurrentAction(action);
    setDialogOpen(true);
  };

  const applyFormatting = (selectedColumns) => {
    let formattedData = [...data];

    try {
      selectedColumns.forEach(column => {
        switch (currentAction) {
          case 'format_cpf':
            formattedData = formattedData.map(row => ({
              ...row,
              [column]: formatters.formatCPF(row[column])
            }));
            break;
          
          case 'format_cnpj':
            formattedData = formattedData.map(row => ({
              ...row,
              [column]: formatters.formatCNPJ(row[column])
            }));
            break;
          
          case 'format_phone':
            formattedData = formattedData.map(row => ({
              ...row,
              [column]: formatters.formatPhone(row[column])
            }));
            break;
          
          case 'format_email':
            formattedData = formattedData.map(row => ({
              ...row,
              [column]: formatters.formatEmail(row[column])
            }));
            break;
          
          case 'format_cep':
            formattedData = formattedData.map(row => ({
              ...row,
              [column]: formatters.formatCEP(row[column])
            }));
            break;
          
          case 'format_date':
            formattedData = formattedData.map(row => ({
              ...row,
              [column]: formatters.formatDate(row[column])
            }));
            break;
          
          case 'uppercase':
            formattedData = formattedData.map(row => ({
              ...row,
              [column]: row[column]?.toString().toUpperCase() || ''
            }));
            break;
          
          case 'sort_az':
            // Ordenação só funciona com uma coluna
            if (selectedColumns.length === 1) {
              formattedData.sort((a, b) => {
                const valA = (a[column] || '').toString().toLowerCase();
                const valB = (b[column] || '').toString().toLowerCase();
                return valA.localeCompare(valB);
              });
            }
            break;
          
          case 'format_gender':
            formattedData = formattedData.map(row => ({
              ...row,
              [column]: formatters.formatGender(row[column])
            }));
            break;
          
          case 'format_organization':
            formattedData = formattedData.map(row => ({
              ...row,
              [column]: formatters.formatOrganization(row[column])
            }));
            break;
          
          default:
            console.log('Ação não implementada:', currentAction);
        }
      });

      setData(formattedData);
      setCurrentPage(1);
      console.log(`Formatação aplicada em ${selectedColumns.length} coluna(s)`);
    } catch (error) {
      console.error('Erro ao aplicar formatação:', error);
      alert('Erro ao aplicar formatação: ' + error.message);
    }
  };

  const getDialogTitle = () => {
    const titles = {
      'format_cpf': 'Formatar CPF',
      'format_cnpj': 'Formatar CNPJ',
      'format_phone': 'Formatar Telefone',
      'format_email': 'Formatar Email',
      'format_cep': 'Formatar CEP',
      'format_date': 'Formatar Data',
      'uppercase': 'Converter para Maiúsculas',
      'sort_az': 'Ordenar Alfabeticamente',
      'format_gender': 'Formatar Gênero',
      'format_organization': 'Formatar Organização'
    };
    return titles[currentAction] || 'Selecionar Colunas';
  };

  const getDialogDescription = () => {
    return 'Selecione uma ou mais colunas para aplicar a formatação';
  };

  const handleAction = (action) => {
    switch (action) {
      case 'check_pipedrive':
        handleCheckPipedrive();
        break;
      
      case 'assertiva_cnpj':
        handleAssertivaConsult();
        break;
      
      case 'invertexto_cnpj':
        handleInvertextoConsult();
        break;
      
      case 'export':
        handleExport();
        break;
      
      case 'delete_columns':
        handleDeleteColumns();
        break;
      
      case 'remove_duplicates':
        handleRemoveDuplicates();
        break;
      
      default:
        console.log('Ação não implementada:', action);
    }
  };

  const handleCheckPipedrive = async () => {
    // Seleciona colunas
    const colunaNome = prompt('Nome da coluna com NOME:', columns.find(c => c.toLowerCase().includes('nome')) || columns[0]);
    const colunaCPF = prompt('Nome da coluna com CPF:', columns.find(c => c.toLowerCase().includes('cpf')) || '');
    const colunaOrg = prompt('Nome da coluna com ORGANIZAÇÃO (deixe vazio se não tiver):', '');
    
    if (!colunaNome || !colunaCPF) {
      alert('É necessário informar as colunas de Nome e CPF!');
      return;
    }
    
    setIsLoading(true);
    try {
      const result = await dadosService.checkPipedrive(data, {
        nome: colunaNome,
        cpf: colunaCPF,
        org: colunaOrg || null
      });
      
      setData(result.data);
      alert(`Verificação concluída!\n\nCPFs encontrados: ${result.cpfs_encontrados}\nTotal: ${result.total}`);
    } catch (error) {
      console.error('Erro:', error);
      alert('Erro ao verificar Pipedrive: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAssertivaConsult = async () => {
    const colunaCNPJ = prompt('Nome da coluna com CNPJ:', columns.find(c => c.toLowerCase().includes('cnpj')) || '');
    
    if (!colunaCNPJ) {
      alert('É necessário informar a coluna de CNPJ!');
      return;
    }
    
    setIsLoading(true);
    try {
      const result = await dadosService.assertivaCNPJ(data, colunaCNPJ);
      
      setData(result.data);
      setColumns(Object.keys(result.data[0]));
      alert(`Consulta Assertiva concluída!\n\nEncontrados: ${result.encontrados}\nErros: ${result.erros}\nTotal: ${result.total}`);
    } catch (error) {
      console.error('Erro:', error);
      alert('Erro ao consultar Assertiva: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInvertextoConsult = async () => {
    const colunaCNPJ = prompt('Nome da coluna com CNPJ:', columns.find(c => c.toLowerCase().includes('cnpj')) || '');
    
    if (!colunaCNPJ) {
      alert('É necessário informar a coluna de CNPJ!');
      return;
    }
    
    setIsLoading(true);
    try {
      const result = await dadosService.invertextoCNPJ(data, colunaCNPJ);
      
      setData(result.data);
      setColumns(Object.keys(result.data[0]));
      alert(`Consulta Invertexto concluída!\n\nEncontrados: ${result.encontrados}\nErros: ${result.erros}\nTotal: ${result.total}`);
    } catch (error) {
      console.error('Erro:', error);
      alert('Erro ao consultar Invertexto: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteColumns = () => {
    setDeleteColumnsDialogOpen(true);
  };

  const applyDeleteColumns = (selectedColumns) => {
    if (selectedColumns.length === 0) return;

    // Remove as colunas selecionadas
    const newData = data.map(row => {
      const newRow = { ...row };
      selectedColumns.forEach(col => {
        delete newRow[col];
      });
      return newRow;
    });

    // Atualiza as colunas
    const newColumns = columns.filter(col => !selectedColumns.includes(col));

    setData(newData);
    setColumns(newColumns);
    setCurrentPage(1);

    console.log(`${selectedColumns.length} coluna(s) excluída(s): ${selectedColumns.join(', ')}`);
    alert(`${selectedColumns.length} coluna(s) excluída(s) com sucesso!`);
  };

  const handleRemoveDuplicates = () => {
    if (data.length === 0) return;
    
    const uniqueData = [];
    const seen = new Set();
    
    data.forEach(row => {
      const key = JSON.stringify(row);
      if (!seen.has(key)) {
        seen.add(key);
        uniqueData.push(row);
      }
    });
    
    const removed = data.length - uniqueData.length;
    setData(uniqueData);
    setCurrentPage(1);
    
    alert(`${removed} linha(s) duplicada(s) removida(s)`);
    console.log(`Duplicatas removidas: ${removed}`);
  };

  return (
    <MainLayout title="Gerenciamento de Dados">
      <div className="p-6">
        <div className="w-full">
          {/* Status e ações */}
          <div className="mb-6 flex items-center justify-between">
            <p className="text-muted-foreground">
              {data.length > 0 
                ? `${data.length} registro(s) carregado(s)` 
                : 'Faça upload e formate seus dados'}
            </p>
            
            {/* Botão para carregar novo arquivo */}
            {data.length > 0 && (
              <Button
                onClick={() => {
                  setData([]);
                  setColumns([]);
                  setCurrentPage(1);
                  setFilterConfig({ term: '', column: '' });
                }}
                variant="outline"
              >
                Carregar Novo Arquivo
              </Button>
            )}
          </div>

          {/* Content Area */}
          <div className="space-y-6">
            {/* Upload Section - só aparece se não houver dados */}
            {data.length === 0 && (
              <div className="p-6 border rounded-lg bg-card">
                <h3 className="text-lg font-semibold mb-4">Upload de Planilha</h3>
                <CnpjUpload onFileUpload={handleFileUpload} isLoading={isLoading} />
              </div>
            )}

            {/* Toolbar Section - Formatação */}
            {data.length > 0 && (
              <CnpjToolbar 
                onFormatAction={handleFormatAction}
                hasData={data.length > 0}
              />
            )}

            {/* Toolbar Section - Ações e Pesquisas */}
            {data.length > 0 && (
              <CnpjActionsToolbar 
                onAction={handleAction}
                hasData={data.length > 0}
              />
            )}

            {/* Table Section */}
            <div className="border rounded-lg bg-card">
              <div className="p-6">
                <CnpjTable 
                  data={paginatedData} 
                  columns={columns}
                  onExport={handleExport}
                />
              </div>
              
              {/* Pagination */}
              {filteredData.length > 0 && (
                <CnpjPagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  totalRecords={filteredData.length}
                  recordsPerPage={recordsPerPage}
                  onPageChange={setCurrentPage}
                />
              )}
            </div>
          </div>

          {/* Column Selector Dialog - Formatação */}
          <ColumnSelectorDialog
            isOpen={dialogOpen}
            onClose={() => setDialogOpen(false)}
            columns={columns}
            title={getDialogTitle()}
            description={getDialogDescription()}
            onApply={applyFormatting}
          />

          {/* Column Selector Dialog - Excluir Colunas */}
          <ColumnSelectorDialog
            isOpen={deleteColumnsDialogOpen}
            onClose={() => setDeleteColumnsDialogOpen(false)}
            columns={columns}
            title="Excluir Colunas"
            description="Selecione as colunas que deseja excluir permanentemente"
            onApply={applyDeleteColumns}
          />
        </div>
      </div>
    </MainLayout>
  );
}
