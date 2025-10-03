const API_URL = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/judit`;

export const juditService = {
  // Inicia processamento
  async processar(dados, onDemand = false, withAttachments = true) {
    try {
      const response = await fetch(`${API_URL}/processar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          dados,
          on_demand: onDemand,
          with_attachments: withAttachments
        })
      });
      
      if (!response.ok) {
        throw new Error(`Erro ao processar: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Erro ao processar:', error);
      throw error;
    }
  },

  // Consulta status do processamento
  async obterStatus(batchId) {
    try {
      const response = await fetch(`${API_URL}/status/${batchId}`);
      
      if (!response.ok) {
        throw new Error(`Erro ao obter status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Erro ao obter status:', error);
      throw error;
    }
  },

  // Obtém resultados
  async obterResultados(batchId) {
    try {
      const response = await fetch(`${API_URL}/resultados/${batchId}`);
      
      if (!response.ok) {
        throw new Error(`Erro ao obter resultados: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Erro ao obter resultados:', error);
      throw error;
    }
  }
};
