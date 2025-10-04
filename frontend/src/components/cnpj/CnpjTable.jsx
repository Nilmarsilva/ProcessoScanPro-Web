import { FileText, Download } from 'lucide-react';
import { Button } from '../ui/button';

export default function CnpjTable({ data, columns, onExport }) {
  if (!data || data.length === 0) {
    return (
      <div className="text-center py-12">
        <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <p className="text-muted-foreground">
          Nenhum dado para exibir. Faça upload de uma planilha para começar.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header com botão de exportar */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">
            Exibindo {data.length} registro(s)
          </p>
        </div>
        {onExport && (
          <Button onClick={onExport} variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Exportar
          </Button>
        )}
      </div>

      {/* Tabela */}
      <div className="border rounded-lg overflow-hidden">
        <div className="overflow-auto max-h-[600px]">
          <table className="w-full">
            <thead className="bg-muted sticky top-0">
              <tr>
                {columns.map((column, index) => (
                  <th
                    key={index}
                    className="px-2 py-2 text-left text-xs font-medium text-muted-foreground whitespace-nowrap"
                  >
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y">
              {data.map((row, rowIndex) => (
                <tr
                  key={rowIndex}
                  className="hover:bg-muted/50 transition-colors"
                >
                  {columns.map((column, colIndex) => {
                    const value = row[column];
                    // Converte Date para string
                    const displayValue = value instanceof Date 
                      ? value.toLocaleDateString('pt-BR')
                      : value || '-';
                    
                    return (
                      <td
                        key={colIndex}
                        className="px-2 py-2 text-xs whitespace-nowrap"
                      >
                        {displayValue}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
