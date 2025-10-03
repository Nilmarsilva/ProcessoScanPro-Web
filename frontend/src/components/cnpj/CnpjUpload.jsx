import { useState, useRef } from 'react';
import { Button } from '../ui/button';
import { Upload, FileSpreadsheet, X, AlertCircle } from 'lucide-react';

export default function CnpjUpload({ onFileUpload, isLoading }) {
  const [file, setFile] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Valida tipo de arquivo
      const validTypes = [
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/csv'
      ];
      
      if (!validTypes.includes(selectedFile.type) && 
          !selectedFile.name.match(/\.(xlsx|xls|csv)$/i)) {
        setError('Formato inválido. Use apenas arquivos Excel (.xlsx, .xls) ou CSV');
        return;
      }

      // Valida tamanho (max 10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('Arquivo muito grande. Tamanho máximo: 10MB');
        return;
      }

      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = () => {
    if (file && onFileUpload) {
      onFileUpload(file);
    }
  };

  const handleRemove = () => {
    setFile(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      const fakeEvent = { target: { files: [droppedFile] } };
      handleFileSelect(fakeEvent);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  return (
    <div className="space-y-4">
      {/* Drop Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className="border-2 border-dashed rounded-lg p-8 text-center hover:border-primary transition-colors cursor-pointer"
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".xlsx,.xls,.csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,text/csv"
          onChange={handleFileSelect}
          className="hidden"
          disabled={isLoading}
        />
        
        <div className="flex flex-col items-center gap-4">
          <div className="p-4 bg-primary/10 rounded-full">
            <Upload className="h-8 w-8 text-primary" />
          </div>
          
          <div>
            <p className="text-lg font-medium mb-1">
              Clique ou arraste um arquivo aqui
            </p>
            <p className="text-sm text-muted-foreground">
              Formatos aceitos: .xlsx, .xls, .csv (máx. 10MB)
            </p>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="flex items-center gap-2 p-3 bg-destructive/10 border border-destructive/20 rounded-md text-destructive text-sm">
          <AlertCircle className="h-4 w-4" />
          <span>{error}</span>
        </div>
      )}

      {/* Selected File */}
      {file && (
        <div className="flex items-center justify-between p-4 bg-accent rounded-lg">
          <div className="flex items-center gap-3">
            <FileSpreadsheet className="h-5 w-5 text-primary" />
            <div>
              <p className="font-medium">{file.name}</p>
              <p className="text-sm text-muted-foreground">
                {(file.size / 1024).toFixed(2)} KB
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              onClick={handleUpload}
              disabled={isLoading}
              size="sm"
            >
              {isLoading ? 'Processando...' : 'Processar'}
            </Button>
            <Button
              onClick={handleRemove}
              disabled={isLoading}
              variant="ghost"
              size="icon"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
