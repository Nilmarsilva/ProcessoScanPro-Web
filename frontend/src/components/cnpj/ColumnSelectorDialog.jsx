import { useState } from 'react';
import { Button } from '../ui/button';
import { X, Check } from 'lucide-react';

export default function ColumnSelectorDialog({ 
  isOpen, 
  onClose, 
  columns, 
  title, 
  description,
  onApply 
}) {
  const [selectedColumns, setSelectedColumns] = useState([]);

  const toggleColumn = (column) => {
    setSelectedColumns(prev => 
      prev.includes(column) 
        ? prev.filter(c => c !== column)
        : [...prev, column]
    );
  };

  const handleApply = () => {
    if (selectedColumns.length === 0) {
      alert('Selecione pelo menos uma coluna!');
      return;
    }
    onApply(selectedColumns);
    setSelectedColumns([]);
    onClose();
  };

  const handleClose = () => {
    setSelectedColumns([]);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-card border rounded-lg shadow-lg max-w-2xl w-full mx-4 max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="p-4 border-b flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold">{title}</h3>
            <p className="text-sm text-muted-foreground">{description}</p>
          </div>
          <Button variant="ghost" size="icon" onClick={handleClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Content */}
        <div className="p-4 overflow-y-auto flex-1">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {columns.map((column, index) => (
              <button
                key={index}
                onClick={() => toggleColumn(column)}
                className={`
                  p-3 rounded-md border text-left transition-all
                  ${selectedColumns.includes(column)
                    ? 'bg-primary text-primary-foreground border-primary'
                    : 'bg-background hover:bg-accent border-border'
                  }
                `}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium truncate">{column}</span>
                  {selectedColumns.includes(column) && (
                    <Check className="h-4 w-4 flex-shrink-0 ml-2" />
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            {selectedColumns.length} coluna(s) selecionada(s)
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleClose}>
              Cancelar
            </Button>
            <Button onClick={handleApply}>
              Aplicar Formatação
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
