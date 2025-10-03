import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const juditService = {
  // Inicia processamento
  async processar(dados, onDemand = false, withAttachments = true) {
    try {
      const response = await axios.post(`${API_URL}/api/judit/processar`, {
        dados,
        on_demand: onDemand,
        with_attachments: withAttachments
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao processar:', error);
      throw error;
    }
  },

  // Consulta status do processamento
  async obterStatus(batchId) {
    try {
      const response = await axios.get(`${API_URL}/api/judit/status/${batchId}`);
      return response.data;
    } catch (error) {
      console.error('Erro ao obter status:', error);
      throw error;
    }
  },

  // Obtém resultados
  async obterResultados(batchId) {
    try {
      const response = await axios.get(`${API_URL}/api/judit/resultados/${batchId}`);
      return response.data;
    } catch (error) {
      console.error('Erro ao obter resultados:', error);
      throw error;
    }
  }
};
