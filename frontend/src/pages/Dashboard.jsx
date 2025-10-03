import MainLayout from '../components/layout/MainLayout';
import { Upload, Search, FileText } from 'lucide-react';

export default function Dashboard() {
  return (
    <MainLayout title="ProcessoScanPro">
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
            <div className="mb-8">
              <h2 className="text-3xl font-bold mb-2">Dashboard</h2>
              <p className="text-muted-foreground">
                Bem-vindo ao sistema de consulta de processos judiciais
              </p>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="p-6 border rounded-lg hover:shadow-lg transition-shadow cursor-pointer bg-card">
                <div className="flex items-center gap-4 mb-4">
                  <div className="p-3 bg-primary/10 rounded-full">
                    <Upload className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="text-lg font-semibold">Upload Planilha</h3>
                </div>
                <p className="text-sm text-muted-foreground">
                  Faça upload de uma planilha com CPFs/CNPJs para consulta em lote
                </p>
              </div>

              <div className="p-6 border rounded-lg hover:shadow-lg transition-shadow cursor-pointer bg-card">
                <div className="flex items-center gap-4 mb-4">
                  <div className="p-3 bg-primary/10 rounded-full">
                    <Search className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="text-lg font-semibold">Consulta Individual</h3>
                </div>
                <p className="text-sm text-muted-foreground">
                  Consulte processos de um CPF/CNPJ específico
                </p>
              </div>

              <div className="p-6 border rounded-lg hover:shadow-lg transition-shadow cursor-pointer bg-card">
                <div className="flex items-center gap-4 mb-4">
                  <div className="p-3 bg-primary/10 rounded-full">
                    <FileText className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="text-lg font-semibold">Relatórios</h3>
                </div>
                <p className="text-sm text-muted-foreground">
                  Visualize e exporte relatórios de consultas anteriores
                </p>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="p-6 border rounded-lg bg-card">
                <div className="text-2xl font-bold mb-1">0</div>
                <div className="text-sm text-muted-foreground">Consultas Hoje</div>
              </div>
              <div className="p-6 border rounded-lg bg-card">
                <div className="text-2xl font-bold mb-1">0</div>
                <div className="text-sm text-muted-foreground">Processos Encontrados</div>
              </div>
              <div className="p-6 border rounded-lg bg-card">
                <div className="text-2xl font-bold mb-1">0</div>
                <div className="text-sm text-muted-foreground">Planilhas Processadas</div>
              </div>
              <div className="p-6 border rounded-lg bg-card">
                <div className="text-2xl font-bold mb-1">0</div>
                <div className="text-sm text-muted-foreground">Relatórios Gerados</div>
              </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
