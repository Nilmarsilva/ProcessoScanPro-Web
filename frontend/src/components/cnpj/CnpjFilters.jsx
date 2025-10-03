import { useState } from 'react';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Search, X } from 'lucide-react';

export default function CnpjFilters({ onFilter, columns }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedColumn, setSelectedColumn] = useState('');

  const handleSearch = () => {
    if (onFilter) {
      onFilter({
        term: searchTerm,
        column: selectedColumn
      });
    }
  };

  const handleClear = () => {
    setSearchTerm('');
    setSelectedColumn('');
    if (onFilter) {
      onFilter({ term: '', column: '' });
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="flex flex-wrap items-center gap-3">
      {/* Seletor de coluna */}
      {columns && columns.length > 0 && (
        <select
          value={selectedColumn}
          onChange={(e) => setSelectedColumn(e.target.value)}
          className="px-3 py-2 border rounded-md bg-background text-sm min-w-[150px]"
        >
          <option value="">Todas as colunas</option>
          {columns.map((column, index) => (
            <option key={index} value={column}>
              {column}
            </option>
          ))}
        </select>
      )}

      {/* Campo de busca */}
      <div className="flex-1 min-w-[200px] relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          type="text"
          placeholder="Buscar..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={handleKeyPress}
          className="pl-10"
        />
      </div>

      {/* Botões */}
      <div className="flex gap-2">
        <Button onClick={handleSearch} size="sm">
          Buscar
        </Button>
        {(searchTerm || selectedColumn) && (
          <Button onClick={handleClear} variant="outline" size="sm">
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  );
}
