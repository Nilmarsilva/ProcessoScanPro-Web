import { useState, useMemo } from 'react';
import MainLayout from '../components/layout/MainLayout';
import CnpjUpload from '../components/cnpj/CnpjUpload';
import CnpjPagination from '../components/cnpj/CnpjPagination';
import { Building2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import * as XLSX from 'xlsx';
import { dadosService } from '../services/dadosService';

export default function CnpjPage() {
  const [data, setData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedRows, setSelectedRows] = useState(new Set());
  
  const recordsPerPage = 1000; // Igual ao desktop

  // Processa o arquivo Excel
  const handleFileUpload = async (file) => {
    setIsLoading(true);
    try {
      const arrayBuffer = await file.arrayBuffer();
      const workbook = XLSX.read(arrayBuffer, { 
        type: 'array',
        cellDates: true
      });
      
      const firstSheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[firstSheetName];
      const jsonData = XLSX.utils.sheet_to_json(worksheet, {
        raw: true,
        defval: ''
      });
      
      if (jsonData.length === 0) {
        alert('A planilha está vazia!');
        return;
      }
      
      setColumns(Object.keys(jsonData[0]));
      setData(jsonData);
      setCurrentPage(1);
      
      console.log(`Arquivo processado: ${file.name}, Total: ${jsonData.length}`);
    } catch (error) {
      console.error('Erro ao processar arquivo:', error);
      alert('Erro ao processar arquivo: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAssertivaClick = async () => {
    if (data.length === 0) {
      alert('Carregue uma planilha primeiro!');
      return;
    }

    const colunaCNPJ = prompt('Nome da coluna com CNPJ:', columns.find(c => c.toLowerCase().includes('cnpj')) || '');
    if (!colunaCNPJ) return;
    
    setIsLoading(true);
    try {
      const result = await dadosService.assertivaCNPJ(data, colunaCNPJ);
      setData(result.data);
      setColumns(Object.keys(result.data[0]));
      alert(`Consulta Assertiva concluída!\n\nEncontrados: ${result.encontrados}\nErros: ${result.erros}`);
    } catch (error) {
      console.error('Erro:', error);
      alert('Erro ao consultar Assertiva: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInvertextoClick = async () => {
    if (data.length === 0) {
      alert('Carregue uma planilha primeiro!');
      return;
    }

    const colunaCNPJ = prompt('Nome da coluna com CNPJ:', columns.find(c => c.toLowerCase().includes('cnpj')) || '');
    if (!colunaCNPJ) return;
    
    setIsLoading(true);
    try {
      const result = await dadosService.invertextoCNPJ(data, colunaCNPJ);
      setData(result.data);
      setColumns(Object.keys(result.data[0]));
      alert(`Consulta Invertexto concluída!\n\nEncontrados: ${result.encontrados}\nErros: ${result.erros}`);
    } catch (error) {
      console.error('Erro:', error);
      alert('Erro ao consultar Invertexto: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePipedriveClick = async () => {
    alert('Funcionalidade de atualização do Pipedrive');
  };

  // Paginação
  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * recordsPerPage;
    const endIndex = startIndex + recordsPerPage;
    return data.slice(startIndex, endIndex);
  }, [data, currentPage, recordsPerPage]);

  const totalPages = Math.ceil(data.length / recordsPerPage);

  // Funções de seleção
  const toggleSelectAll = () => {
    if (selectedRows.size === data.length) {
      setSelectedRows(new Set());
    } else {
      setSelectedRows(new Set(data.map((_, index) => index)));
    }
  };

  const toggleSelectRow = (index) => {
    const newSelected = new Set(selectedRows);
    if (newSelected.has(index)) {
      newSelected.delete(index);
    } else {
      newSelected.add(index);
    }
    setSelectedRows(newSelected);
  };

  const isAllSelected = data.length > 0 && selectedRows.size === data.length;
  const isIndeterminate = selectedRows.size > 0 && selectedRows.size < data.length;

  const handleExport = () => {
    if (data.length === 0) return;
    
    try {
      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.json_to_sheet(data);
      XLSX.utils.book_append_sheet(wb, ws, 'CNPJs');
      
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
      const filename = `cnpjs_${timestamp}.xlsx`;
      XLSX.writeFile(wb, filename);
      
      alert(`Arquivo exportado: ${filename}`);
    } catch (error) {
      console.error('Erro ao exportar:', error);
      alert('Erro ao exportar: ' + error.message);
    }
  };

  return (
    <MainLayout title="Consultas de CNPJ">
      <div className="p-6">
        <div className="w-full">
          {/* Status */}
          <div className="mb-6">
            <p className="text-muted-foreground">
              {data.length > 0 ? `${data.length} registro(s) carregado(s)` : 'Carregue uma planilha para começar'}
            </p>
          </div>

          {/* Upload Section */}
          <div className="mb-6 p-6 border rounded-lg bg-card">
            <CnpjUpload onFileUpload={handleFileUpload} isLoading={isLoading} />
          </div>

          {/* Action Buttons */}
          {data.length > 0 && (
            <div className="mb-6 flex gap-3">
              <Button 
                onClick={handleAssertivaClick}
                disabled={isLoading}
                className="bg-green-600 hover:bg-green-700 text-white"
              >
                Assertiva CNPJ
              </Button>
              <Button 
                onClick={handleInvertextoClick}
                disabled={isLoading}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                Invertexto CNPJ
              </Button>
              <Button 
                onClick={handlePipedriveClick}
                disabled={isLoading}
                className="bg-purple-600 hover:bg-purple-700 text-white"
              >
                Atualizar Pipedrive
              </Button>
            </div>
          )}

          {/* Checkbox Selecionar Todos */}
          {data.length > 0 && (
            <div className="mb-4 flex items-center gap-4">
              <label className="flex items-center gap-2">
                <input 
                  type="checkbox" 
                  checked={isAllSelected}
                  ref={(el) => el && (el.indeterminate = isIndeterminate)}
                  onChange={toggleSelectAll}
                  className="w-4 h-4"
                />
                <span className="text-sm font-medium">Selecionar Todos</span>
              </label>
              <span className="text-sm text-muted-foreground">
                {selectedRows.size} de {data.length} selecionado(s)
              </span>
            </div>
          )}

          {/* Table Section */}
          {data.length > 0 && (
            <div className="border rounded-lg bg-card">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="p-3 text-left font-medium w-12">
                        <input 
                          type="checkbox" 
                          checked={isAllSelected}
                          ref={(el) => el && (el.indeterminate = isIndeterminate)}
                          onChange={toggleSelectAll}
                          className="w-4 h-4"
                        />
                      </th>
                      {columns.map((col, index) => (
                        <th key={index} className="p-3 text-left font-medium border-b">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {paginatedData.map((row, rowIndex) => {
                      const globalIndex = (currentPage - 1) * recordsPerPage + rowIndex;
                      return (
                        <tr 
                          key={rowIndex} 
                          className={`border-b hover:bg-muted/30 ${selectedRows.has(globalIndex) ? 'bg-blue-50' : ''}`}
                        >
                          <td className="p-3">
                            <input 
                              type="checkbox" 
                              checked={selectedRows.has(globalIndex)}
                              onChange={() => toggleSelectRow(globalIndex)}
                              className="w-4 h-4"
                            />
                          </td>
                          {columns.map((col, colIndex) => (
                            <td key={colIndex} className="p-3 border-b">
                              {row[col]}
                            </td>
                          ))}
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              
              {/* Pagination */}
              {totalPages > 1 && (
                <div className="p-4 border-t">
                  <CnpjPagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    totalRecords={data.length}
                    recordsPerPage={recordsPerPage}
                    onPageChange={setCurrentPage}
                  />
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
}
